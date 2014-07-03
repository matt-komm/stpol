#rom get_weights import *
from utils import sizes

C90 = 1.64485 #Conversion factor from 90% to 68%

scale_factors["CT10"] = 1 / C90
scale_factors["NNPDF23"] = 1.
scale_factors["MSTW2008CPdeutnlo68cl"] = 1.

jettags = ["2j0t", "2j1t", "3j1t", "3j2t"]
variables = ["bdt_sig_bg", "cos_theta"]
pdfsets = ["CT10", "NNPDF23"]#"MSTW2008CPdeutnlo68cl"
for jt in jettags:


def make_pdf_histos(pdfset, var, jettag):
    hname_up = "%s__%s__pdf__up" % (var, sn)
    hname_down = "%s__%s__pdf__down" % (var, sn)
    #outfile = File(outdir + "/%s_%s.root" % (sampn,hname), "RECREATE")
    outfile = TFile(outdir + "/%s_%s_pdf.root" % (sampn, var), "RECREATE")

    if pdfset == "CT10" or pdfset == "MSTW2008CPdeutnlo68cl":
        best_fit = inputFile.Get( "pdf__%s_%s__%s__%s" % (jettag, var, dataset, pdfset) )
        for i in range(sizes[pdfset]):
            hist = inputFile.Get( "pdf__%s_%s__%s__%s_weighted_%d" % (jettag, var, dataset, pdfset, i) )
            weighted_histos.append(hist)
        (hist_plus, hist_minus) = pdf_uncertainty(hist_std, weighted_histos, scale_factors[pdfset])
        if pdfset == "CT10":            
            alpha_down = inputFile.Get( "pdf__%s_%s__%s__%s_weighted_%d" % (jettag, var, dataset+"as", 2) )
            alpha_up = inputFile.Get( "pdf__%s_%s__%s__%s_weighted_%d" % (jettag, var, dataset+"as", 6) )
            (total_up, total_down) = CT10_total(best_fit, pdf_up, pdf_down, alpha_up, alpha_down):
        elif pdfset == "MSTW2008CPdeutnlo68cl": #Alphas incorporated
            (total_up, total_down) = (hist_plus, hist_minus)
    total_up.SetNameTitle(hname_up, hname_up)
    total_down.SetNameTitle(hname_down, hname_down)
    total_up.Write()
    total_down.Write()

    
    outfile.Write()
    outfile.Close()
    


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
            x0 = bestfit.GetBinContent(bin)
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
            (alpha_up.GetBinContent(bin) - best_fit.GetBinContent(bin)) / C90)
        
        alpha_down.SetBinContent(bin, 
            (alpha_down.GetBinContent(bin) - best_fit.GetBinContent(bin)) / C90)
    return (alpha_up, alpha_down)

def CT10_total(best_fit, pdf_up, pdf_down, alpha_up, alpha_down):
    total_up = best_fit.Clone(hname_up)
    total_down = best_fit.Clone(hname_down)
    nmax = best_fit.GetNbinsX()
    for bin in range(0, nmax+1):
        nominal = best_fit.GetBinContent(bin)
        
        total_up.SetBinContent(bin, 
            math.sqrt(pdf_up.GetBinContent(bin) ** 2 + alpha_up.GetBinContent(bin) ** 2))
        total_up.SetBinContent(bin, total_up.GetBinContent(bin) * nominal)
        
        total_down.SetBinContent(bin, 
            math.sqrt(pdf_down.GetBinContent(bin) ** 2 + alpha_down.GetBinContent(bin) ** 2))
        total_down.SetBinContent(bin, total_down.GetBinContent(bin) * nominal)
    return (total_up, total_down)

def calculate_PDF_uncertainties(bestfit, pdf_weighted, histo_plus, histo_minus, scale_to_nominal = True, orig=None):
    #http://cms.cern.ch/iCMS/jsp/openfile.jsp?tp=draft&files=AN2009_048_v1.pdf Equations 3 and 4
    # calculate relative uncertaities around bestfit histogram based on pdf_weighted replicas of the histograms
    nmax = bestfit.GetNbinsX()
    for bin in range(1, nmax+1):
        X = bestfit.GetBinContent(bin)

        # Master formula: w_plus, w_minus, w_mean || for CTEQ and MSTW
        # see http://www.hep.ucl.ac.uk/pdf4lhc/PDF4LHC_practical_guide.pdf
        nPDFSet_size_2 = len(pdf_weighted) / 2
        sum_plus	= 0.
        sum_minus	= 0.
        n_plus		= 0
        n_minus		= 0
        for i in range(nPDFSet_size_2):
            # get weighted values
            x0 = bestfit.GetBinContent(bin)
            xp = pdf_weighted[2*i].GetBinContent(bin)
            xm = pdf_weighted[2*i+1].GetBinContent(bin)
            sum_plus += max(xp - x0, xm - x0, 0) ** 2
            sum_minus += max(x0 - xp, x0 - xm, 0) ** 2

        sum_plus	= math.sqrt(sum_plus)
        sum_minus	= math.sqrt(sum_minus)
        # put to histo
        
        if X > 0.:
            if scale_to_nominal:
                #print "bin", bin, X, orig.GetBinContent(bin), sum_plus, sum_minus
                #histo_plus.SetBinContent(bin, orig.GetBinContent(bin) * (1 + sum_plus/X))
                #histo_minus.SetBinContent(bin, orig.GetBinContent(bin) * (1 - sum_minus/X))
                histo_plus.SetBinContent(bin, orig.GetBinContent(bin) * (1 + sum_plus/X))
                histo_minus.SetBinContent(bin, orig.GetBinContent(bin) * (1 - sum_minus/X))
            else:
                histo_plus.SetBinContent(bin, sum_plus/X)
                histo_minus.SetBinContent(bin, sum_minus/X)
        #print "bin", bin, X, orig.GetBinContent(bin), histo_plus.GetBinContent(bin), histo_minus.GetBinContent(bin)
    return (histo_plus, histo_minus)


if __name__ == "__main__":
    asd
