import ROOT
from theta_auto import *
from copy import deepcopy
import logging
logger = logging.getLogger("fit.py")
logger.setLevel(logging.INFO)

class Fit:
    def __init__(self
            , filename
            , name = None
            , rates = {"tchan": inf,  "wzjets": inf, "other": 0.2}
            , shapes = ["__En", "Res", "ttbar_scale", "ttbar_matching", "iso"] 
            , correlations = [("wzjets", "top")]):
        
        self.filename = filename
        self.name = name
        if name == None:
            self.name = filename
        self.rates = rates
        self.shapes = shapes
        self.correlations = correlations
        self.rescale = {}

    @staticmethod
    def getRateSystematics():
        return {"tchan": inf,  "wzjets": inf, "other": 0.2}

    @staticmethod
    def getShapeSystematics(fit):
        systematics = ["Res", "__En", "UnclusteredEn", "ttbar_matching", "ttbar_scale", "leptonID", "leptonTrigger", "wjets_flat", "wjets_shape", "btaggingBC", "btaggingL", "tchan_scale", "wjets_scale", "wjets_matching", "iso"]
        if fit.filename.startswith("mu"):
            systematics.append("leptonIso")
        return systematics


    def setRates(self, rates):
        self.rates = rates

    def setShapes(self, shapes):
        self.shapes = shapes

    def setCorrelations(self, correlations):
        self.correlations = correlations

    def setName(self, name):
        self.name = name

    def setFileName(self, filename):
        self.filename = filename

    def add_uncertainties_to_model(self, model):
        for (channel, prior) in self.rates.items():
            if channel == "tchan":
                continue
            add_normal_uncertainty(model, channel, prior, channel)
        #add_normal_uncertainty(model, "top", 0.2, "top")
        #add_normal_uncertainty(model, "qcd", 0.2, "top")
        #add_normal_uncertainty(model, "wzjets", inf, "wzjets")

    def get_type(self, fit, name, name2 = None):
        if name2 is not None:
            return "corr"
        elif name.replace("beta_signal", "tchan") in Fit.getRateSystematics():
            return "rate"
        elif name in Fit.getShapeSystematics(fit):
            return "shape"
        else:
            raise ValueError("unknown uncertainty")

    # export sorted fit values
    def write_results(self, fitresults, cor, fit):

        fname = os.path.join("results", self.name+".txt")
        try:
            os.makedirs(
                os.path.dirname(
                    fname
                )
            )
        except:
            pass
        logging.info("Writing fit results to file %s" % fname) 
        f = open(fname, 'w')
        for (syst, prior) in Fit.getRateSystematics().items():
            st_type = self.get_type(fit, syst)
            if syst in fitresults.keys() or (syst == "tchan" and "beta_signal" in fitresults.keys()):
                line = '%s, %s, %f, %f\n' % (st_type, syst, fitresults[syst.replace("tchan", "beta_signal")][0], fitresults[syst.replace("tchan", "beta_signal")][1])
                print line,
            else:
                line = '%s, %s, %f, %f\n' % (st_type, syst, 1.0, prior)
            f.write(line)
        for syst in Fit.getShapeSystematics(fit):
            st_type = self.get_type(fit, syst)
            if syst in fitresults.keys():
                print '%s, %s, %f, %f\n' % (st_type, syst, fitresults[syst][0], fitresults[syst][1]),
            line = '%s, %s, %f, %f\n' % (st_type, syst, 0.0, 1.0)
            f.write(line)

        n = cor.GetNbinsX()
        for i in range(1, n+1):
            for j in range(1, n+1):
                xlabel = cor.GetXaxis().GetBinLabel(i).replace("beta_signal", "tchan")
                ylabel = cor.GetYaxis().GetBinLabel(j).replace("beta_signal", "tchan")
                if (xlabel, ylabel) in self.correlations:
                    cor_value = cor.GetBinContent(i,j)
                    line = 'corr, %s, %s, %f\n' % (xlabel, ylabel, cor_value)
                    f.write(line)
        f.write(self.filename + "\n")
        f.close()

    def makeCovMatrix(self, cov, pars):
    # write out covariance matrix
        n = len(pars)
        #print pars

        #fcov = ROOT.TFile("cov.root","RECREATE")
        canvas = ROOT.TCanvas("c1","Covariance")
        h = ROOT.TH2D("covariance","covariance",n,0,n,n,0,n)
        cor = ROOT.TH2D("correlation","correlation",n,0,n,n,0,n)
        
        for i in range(n):
            h.GetXaxis().SetBinLabel(i+1,pars[i]);
            h.GetYaxis().SetBinLabel(i+1,pars[i]);
            cor.GetXaxis().SetBinLabel(i+1,pars[i])
            cor.GetYaxis().SetBinLabel(i+1,pars[i])

        for i in range(n):
            for j in range(n):
                h.SetBinContent(i+1,j+1,cov[i][j])

        for i in range(n):
            for j in range(n):
                cor.SetBinContent(i+1,j+1,cov[i][j]/math.sqrt(cov[i][i]*cov[j][j]))
                #print i, j, cov[i][j], cov[i][i], cov[j][j], math.sqrt(cov[i][i]*cov[j][j]), cov[i][j]/math.sqrt(cov[i][i]*cov[j][j])
        return (h.Clone(), cor.Clone())

    def plotMatrices(self, cov, corr):
        ROOT.gStyle.SetOptStat(0)
        try:
            os.makedirs("plots")
        except:
            pass
        try:
            os.makedirs("plots/"+self.name)
        except:
            pass
        fcov = ROOT.TFile("plots/"+self.name+"/corr.root","RECREATE")
        canvas = ROOT.TCanvas("Covariance","Covariance")
        cov.Draw("COLZ TEXT")
        canvas.Print("plots/"+self.name+"/cov.png")
        canvas.Print("plots/"+self.name+"/cov.pdf")
        
        canvas2 = ROOT.TCanvas("Correlation","Correlation")
        corr.Draw("COLZ TEXT")
        canvas2.Print("plots/"+self.name+"/corr.png")
        canvas2.Print("plots/"+self.name+"/corr.pdf")
        corr.Write()
        cov.Write()
        fcov.Close()

    def histofilter(self, s):
        if '__up' in s or '__down' in s:
            if 'top__Res' in s and self.name.startswith("ele__eta"):
                return False
            for shape in self.shapes:
                if shape in s:
                    return True
            return False
        return True

    """
    A rescaling for all the histograms containing the string
    """
    def addRescale(self, name, scale):
        self.rescale[name] = scale    

    def transformHisto(self, h):
        for (name, rescale) in self.rescale.items():
            if name in h.get_name():
                return h.scale(rescale, h.get_name())
        return h



def add_normal_uncertainty(model, u_name, rel_uncertainty, procname, obsname='*'):
    found_match = False
    par_name = u_name
    if par_name not in model.distribution.get_parameters():
        model.distribution.set_distribution(par_name, 'gauss', mean = 1.0, width = rel_uncertainty, range = [0.0, float("inf")])
    else:
        raise RuntimeError, "parameter name already used"
    for o in model.get_observables():
        if obsname != '*' and o!=obsname: continue
        for p in model.get_processes(o):
            if procname != '*' and procname != p: continue
            model.get_coeff(o,p).add_factor('id', parameter = par_name)
            found_match = True
    if not found_match: raise RuntimeError, 'did not find obname, procname = %s, %s' % (obsname, procname)


Fit.mu_mva_BDT = Fit("mu__mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj")
Fit.ele_mva_BDT = Fit("ele__mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj")

Fit.ele_mva_BDT_qcd_0 = deepcopy(Fit.ele_mva_BDT)
Fit.ele_mva_BDT_qcd_0.setName("QCD fixed to 0")
Fit.ele_mva_BDT_qcd_0.addRescale("qcd", 0.)
Fit.ele_mva_BDT_qcd_0.setRates({"tchan": inf,  "top": 0.1, "wzjets": inf, "qcd": 0.01})

Fit.ele_mva_BDT_qcd_0_5 = deepcopy(Fit.ele_mva_BDT_qcd_0)
Fit.ele_mva_BDT_qcd_0_5.setName("QCD fixed to 0.5")
Fit.ele_mva_BDT_qcd_0_5.addRescale("qcd", 0.5)

Fit.ele_mva_BDT_qcd_1_0 = deepcopy(Fit.ele_mva_BDT_qcd_0)
Fit.ele_mva_BDT_qcd_1_0.setName("QCD fixed to 1.")
Fit.ele_mva_BDT_qcd_1_0.addRescale("qcd", 1.)

Fit.ele_mva_BDT_qcd_1_5 = deepcopy(Fit.ele_mva_BDT_qcd_0)
Fit.ele_mva_BDT_qcd_1_5.setName("QCD fixed to 1.5")
Fit.ele_mva_BDT_qcd_1_5.addRescale("qcd", 1.5)

Fit.ele_mva_BDT_qcd_2_0 = deepcopy(Fit.ele_mva_BDT_qcd_0)
Fit.ele_mva_BDT_qcd_2_0.setName("QCD fixed to 2")
Fit.ele_mva_BDT_qcd_2_0.addRescale("qcd", 2.)

Fit.mu_C = Fit("mu__C")
Fit.ele_C = Fit("ele__C")
Fit.mu_eta_lj = Fit("mu__eta_lj")
Fit.ele_eta_lj = Fit("ele__eta_lj")

Fit.fits = {}
Fit.fits["mva_BDT"] = set([Fit.mu_mva_BDT, Fit.ele_mva_BDT])
Fit.fits["eta_lj"] = set([Fit.mu_eta_lj, Fit.ele_eta_lj])
Fit.fits["C"] = set([Fit.ele_C])
Fit.fits["mu"] = set([Fit.mu_mva_BDT, Fit.mu_eta_lj, Fit.mu_C])
Fit.fits["ele"] = set([Fit.ele_mva_BDT, Fit.ele_eta_lj, Fit.ele_mva_BDT_qcd_0, Fit.ele_mva_BDT_qcd_0_5, Fit.ele_mva_BDT_qcd_1_0, Fit.ele_mva_BDT_qcd_1_5, Fit.ele_mva_BDT_qcd_2_0, Fit.ele_C])

Fit.all_fits = deepcopy(Fit.fits["mu"])
Fit.all_fits = Fit.all_fits.union(Fit.fits["ele"])


