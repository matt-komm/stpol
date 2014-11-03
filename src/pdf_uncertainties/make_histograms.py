#rom get_weights import *
from utils import sizes
import os
import math
from ROOT import TFile
from parse_input import datasets, groups

C90 = 1.64485 #Conversion factor from 90% to 68%

indir = os.path.join(os.environ["STPOL_DIR"], "src", "pdf_uncertainties", "output", "added_0508")
#indir = os.path.join(os.environ["STPOL_DIR"], "src", "pdf_uncertainties", "output_skip", "added_2107_skip_readd")

scale_factors = {}
scale_factors["CT10"] = 1 / C90
scale_factors["NNPDF23"] = 1.
scale_factors["MSTW2008CPdeutnlo68cl"] = 1.

jettags = ["2j0t", "2j1t", "3j1t", "3j2t"]
variables = ["bdt_sig_bg", "cos_theta"]
#pdfsets = ["CT10", "NNPDF23", "MSTW2008CPdeutnlo68cl"]
#pdfsets = ["NNPDF23", "NNPDF22", "NNPDF21"]
pdfsets = ["NNPDF30"]
#pdfsets = ["CT10", "MSTW2008CPdeutnlo68cl"]
channels = ["mu", "ele"]

def main():
    for ds in groups.keys():
        for ch in channels:
            for var in variables:
                for jt in jettags:
                    make_histos(ds, ch, var, jt)

def test():
    make_histos("T_t_ToLeptons", "mu", "cos_theta", "2j1t")
    #make_histos("TTJets_SemiLept", "mu", "cos_theta", "2j1t")
    #make_histos("W2Jets_Exclusive", "mu", "cos_theta", "2j1t")

def make_histos(dataset, channel, var, jettag):
    best_fits = []
    ups = []
    downs = [] 
    outdir = "histos"
    outfile = TFile(outdir + "/%s/%s_%s_%s_pdf.root" % (channel, jettag, dataset, var), "RECREATE")   
    for pdf in pdfsets:
        print pdf, dataset, channel, var, jettag
        (best_fit, up, down) = make_pdf_histos(pdf, dataset, channel, var, jettag)
        best_fits.append(best_fit)
        ups.append(up)
        downs.append(down)
        best_fit.SetNameTitle("%s_best" % pdf, "%s_best" % pdf)
        up.SetNameTitle("%s_up" % pdf, "%s_up" % pdf)
        down.SetNameTitle("%s_down" % pdf, "%s_down" % pdf)
        outfile.cd()
        best_fit.Write()
        up.Write()
        down.Write()
        print best_fit.Integral(), up.Integral(), down.Integral()
    (env_best, env_up, env_down) = make_envelope(ups, downs)
    outfile.cd()
    best_name = "%s_%s__%s__pdf__%s" % (jettag, var.replace("cos_theta", "cos_theta_lj"), groups[dataset], "bestfit")    
    env_best.SetNameTitle(best_name, best_name)
    #env_best.Write()
    up_name = "%s_%s__%s__pdf__%s" % (jettag, var.replace("cos_theta", "cos_theta_lj"), groups[dataset], "up")
    env_up.SetNameTitle(up_name, up_name)
    env_up.Write()
    down_name = "%s_%s__%s__pdf__%s" % (jettag, var.replace("cos_theta", "cos_theta_lj"), groups[dataset], "down")
    env_down.SetNameTitle(down_name, down_name)
    env_down.Write()
    outfile.Close()
    
def make_envelope(histos_up, histos_down):
    histo_up = histos_up[0].Clone()
    histo_down = histos_down[0].Clone()
    best_fit = histos_up[0].Clone()
    nmax = best_fit.GetNbinsX()
    for bin in range(0, nmax+1):
        histo_up.SetBinContent(bin, max([histos_up[i].GetBinContent(bin) for i in range(len(histos_up))]))
        histo_down.SetBinContent(bin, min([histos_down[i].GetBinContent(bin) for i in range(len(histos_down))]))
        best_fit.SetBinContent(bin, (histo_up.GetBinContent(bin) + histo_down.GetBinContent(bin)) / 2) 
    return (best_fit, histo_up, histo_down)

def make_pdf_histos(pdfset, dataset, channel, var, jettag):
    hname_up = "%s__%s__pdf__up" % (var, "a")
    hname_down = "%s__%s__pdf__down" % (var, "b")
    
    #outfile = File(outdir + "/%s_%s.root" % (sampn,hname), "RECREATE")
    inputFile = TFile("%s/%s/%s_%s.root" % (indir, channel, channel, dataset))
    #print "%s/%s/%s_%s.root" % (indir, channel, channel, dataset)
    
    pdfsetname = pdfset+"LHgrid"
    if pdfset == "CT10" or pdfset == "MSTW2008CPdeutnlo68cl":
        
        weighted_histos = []
        print "%s/%s/%s_%s.root" % (indir, channel, channel, dataset)
        print "pdf__%s_%s__%s__%s" % (jettag, var, dataset, pdfsetname)
        best_fit = inputFile.Get( "pdf__%s_%s__%s__%s_nominal" % (jettag, var, dataset, pdfsetname) )
        print best_fit.GetEntries(), best_fit.Integral()
        for i in range(sizes[pdfsetname]):
            hist = inputFile.Get( "pdf__%s_%s__%s__%s_weighted_%d" % (jettag, var, dataset, pdfsetname, i) )
            #print "pdf__%s_%s__%s__%s_weighted_%d" % (jettag, var, dataset, pdfsetname, i)
            #print hist.GetEntries(), hist.Integral()
            weighted_histos.append(hist)
        (pdf_up, pdf_down) = pdf_uncertainty(best_fit, weighted_histos, scale_factors[pdfset])
        print pdf_up.Integral(), pdf_down.Integral()
        if pdfset == "CT10":            
            alpha_down = inputFile.Get( "pdf__%s_%s__%s__%s_weighted_%d" % (jettag, var, dataset, pdfset+"as"+"LHgrid", 2) )
            alpha_up = inputFile.Get( "pdf__%s_%s__%s__%s_weighted_%d" % (jettag, var, dataset, pdfset+"as"+"LHgrid", 6) )
            (total_up, total_down) = CT10_total(best_fit, pdf_up, pdf_down, alpha_up, alpha_down)
        elif pdfset == "MSTW2008CPdeutnlo68cl": #Alphas incorporated
            #print "x", type(best_fit), type(pdf_up)
            (total_up, total_down) = toabsolute(best_fit, pdf_up, pdf_down)
        print total_up.Integral(), total_down.Integral()
    elif pdfset == "NNPDF23":
        weighted_histos = []
        #replicas = (1, 4, 12, 16, 12, 4, 1)
        #replicas = (5, 27, 72, 100, 72, 27, 5)
        replicas = (0, 0, 0, 100, 0, 0, 0)
        alphas= ("0116", "0117", "0118", "0119", "0120", "0121", "0122")
        for i in range(len(replicas)):
            rep = replicas[i]
            alpha = alphas[i]
            for j in range(rep):
                hist = inputFile.Get( "pdf__%s_%s__%s__%snloas%sLHgrid_weighted_%d" % (jettag, var, dataset, pdfset, alpha, j))
                #print "pdf__%s_%s__%s__%snloas%sLHgrid_weighted_%d" % (jettag, var, dataset, pdfset, alpha, j)
                #print hist.GetEntries(), hist.Integral()
                weighted_histos.append(hist)
        (best_fit, total_up, total_down) = pdf_uncertainty_nnpdf(weighted_histos)
    #print type(best_fit), type(total_up)
    best_fit.SetDirectory(0)
    total_up.SetNameTitle(hname_up, hname_up)
    total_down.SetNameTitle(hname_down, hname_down)
    total_up.SetDirectory(0)
    total_down.SetDirectory(0)
    return (best_fit, total_up, total_down)
    

def pdf_uncertainty_nnpdf(weighted_histos):
    best_fit = weighted_histos[0].Clone()
    n_rep = len(weighted_histos)
    nmax = best_fit.GetNbinsX()
    for rep in range(1, n_rep):
        best_fit.Add(weighted_histos[rep])
    best_fit.Scale(1./n_rep)    
    #sigma
    sigma = weighted_histos[0].Clone()
    for bin in range(0, nmax+1):
        binsum = 0
        
        for rep in range(n_rep):
           if bin == 12:
                print rep, weighted_histos[rep].GetBinContent(bin)
           binsum += (weighted_histos[rep].GetBinContent(bin) - best_fit.GetBinContent(bin)) ** 2
        sigma.SetBinContent(bin, math.sqrt( binsum / (n_rep - 1)))
        print "NNPDF", bin, best_fit.GetBinContent(bin), sigma.GetBinContent(bin)
    total_up = best_fit.Clone()
    total_down = best_fit.Clone()
    total_up.Add(sigma)
    total_down.Add(sigma, -1)
    return (best_fit, total_up, total_down)

        
def pdf_uncertainty(best_fit, pdf_weighted, scale_factor=1):
    histo_plus = best_fit.Clone()
    histo_minus = best_fit.Clone()
    nmax = best_fit.GetNbinsX()
    for bin in range(0, nmax+1):
        X = best_fit.GetBinContent(bin)
        # Master formula: w_plus, w_minus, w_mean || for CTEQ and MSTW
        # see http://www.hep.ucl.ac.uk/pdf4lhc/PDF4LHC_practical_guide.pdf
        nPDFSet_size_2 = len(pdf_weighted) / 2
        sum_plus	= 0.
        sum_minus	= 0.
        n_plus		= 0
        n_minus		= 0
        for i in range(nPDFSet_size_2):
            # get weighted values
            x0 = best_fit.GetBinContent(bin)
            xp = pdf_weighted[2*i].GetBinContent(bin)
            xm = pdf_weighted[2*i+1].GetBinContent(bin)
            sum_plus += max(xp - x0, xm - x0, 0) ** 2
            sum_minus += max(x0 - xp, x0 - xm, 0) ** 2

        sum_plus	= scale_factor * math.sqrt(sum_plus)
        sum_minus	= scale_factor * math.sqrt(sum_minus)
        # put to histo
        
        histo_plus.SetBinContent(bin, sum_plus)
        histo_minus.SetBinContent(bin, sum_minus)
        #histo_plus.SetBinContent(bin, sum_plus/X)
        #histo_minus.SetBinContent(bin, sum_minus/X)
                
        #if X > 0.:
        #    if scale_to_nominal:
        #        #print "bin", bin, X, orig.GetBinContent(bin), sum_plus, sum_minus
        #        #histo_plus.SetBinContent(bin, orig.GetBinContent(bin) * (1 + sum_plus/X))
        #        #histo_minus.SetBinContent(bin, orig.GetBinContent(bin) * (1 - sum_minus/X))
        #        histo_plus.SetBinContent(bin, orig.GetBinContent(bin) * (1 + sum_plus/X))
        #        histo_minus.SetBinContent(bin, orig.GetBinContent(bin) * (1 - sum_minus/X))
        #    else:
        #print "bin", bin, X, orig.GetBinContent(bin), histo_plus.GetBinContent(bin), histo_minus.GetBinContent(bin)
    return (histo_plus, histo_minus)


def CT10_alphas(best_fit, alpha_up, alpha_down):
    #alphas
    #The recommended 90 % C.L. uncertainty estimate is 0.116 - 0.120.
    #Corresponds to sets nr. 2 & 6
    nmax = best_fit.GetNbinsX()
    for bin in range(0, nmax+1):        
        alpha_up.SetBinContent(bin, 
            (alpha_up.GetBinContent(bin) - best_fit.GetBinContent(bin)) * scale_factors["CT10"])        
        alpha_down.SetBinContent(bin, 
            (alpha_down.GetBinContent(bin) - best_fit.GetBinContent(bin)) * scale_factors["CT10"])
    return (alpha_up, alpha_down)

def CT10_total(best_fit, pdf_up, pdf_down, alpha_up, alpha_down):
    total_up = best_fit.Clone("up")#hname_up)
    total_down = best_fit.Clone("down")#hname_down)
    nmax = best_fit.GetNbinsX()
    for bin in range(0, nmax+1):
        nominal = best_fit.GetBinContent(bin)
        
        total_up.SetBinContent(bin, 
            math.sqrt(pdf_up.GetBinContent(bin) ** 2 + alpha_up.GetBinContent(bin) ** 2))
        total_up.SetBinContent(bin, total_up.GetBinContent(bin))
        
        total_down.SetBinContent(bin, 
            math.sqrt(pdf_down.GetBinContent(bin) ** 2 + alpha_down.GetBinContent(bin) ** 2))
        total_down.SetBinContent(bin, total_down.GetBinContent(bin))
    return (total_up, total_down)

def toabsolute(best_fit, pdf_up, pdf_down):
    total_up = best_fit.Clone()
    total_up.Add(pdf_up)
    total_down = best_fit.Clone()
    total_down.Add(pdf_down, -1)
    #total_up.SetDirectory(0)
    #total_down.SetDirectory(0)
    return (total_up, total_down)

if __name__ == "__main__":
    #main()
    test()
