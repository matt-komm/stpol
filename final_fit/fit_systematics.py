import ROOT
import math


def get_type(name, name2 = None):
    if name2 is not None:
        return "corr"
    elif name in ["beta_signal", "tchan", "qcd", "top", "wzjets"]:
        return "rate"
    else:
        return "shape"

# export sorted fit values
def write_results(fitresults):
    try:
        os.makedirs("results")
    except:
        pass
    f = open('results/nominal.txt','w')
        
    for key in sorted(fitresults.keys()):
        st_type = get_type(key)
        line = '%s, costheta__%s, %f, %f\n' % (st_type, key.replace("beta_signal", "tchan"), fitresults[key][0], fitresults[key][1])
        
        print line,
    f.write(line)
    f.close()



def doCovMatrix(cov, pars):
    # write out covariance matrix
    ROOT.gStyle.SetOptStat(0)
    
    n = len(pars)
    print pars

    fcov = ROOT.TFile("cov.root","RECREATE")
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

    h.Draw("COLZ TEXT")
    try:
        os.makedirs("plots")
    except:
        pass
    canvas.Print("plots/cov.png")
    canvas.Print("plots/cov.pdf")
    #fcov.Close()

    for i in range(n):
        for j in range(n):
            cor.SetBinContent(i+1,j+1,cov[i][j]/math.sqrt(cov[i][i]*cov[j][j]))
            #print i, j, cov[i][j], cov[i][i], cov[j][j], math.sqrt(cov[i][i]*cov[j][j]), cov[i][j]/math.sqrt(cov[i][i]*cov[j][j])
    
    #canvas2 = ROOT.TCanvas("c1","Correlation")
    #fcorr = ROOT.TFile("corr.root","RECREATE")
    cor.Draw("COLZ TEXT")
    try:
        os.makedirs("plots")
    except:
        pass
    canvas.Print("plots/corr.png")
    canvas.Print("plots/corr.pdf")
    cor.Write()
    h.Write()
    fcov.Close()


