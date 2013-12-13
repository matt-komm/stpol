import ROOT, os, sys
from array import array
import ROOT
import plots
from plots.common.distribution_plot import plot_hists
from plots.common.odict import OrderedDict
import plots.common.pretty_names as pretty_names
from plots.common.sample_style import Styling
from plots.common.cross_sections import xs, lumi_iso
from plots.common.utils import lumi_textbox
from plots.common.legend import legend
from plots.common.cuts import *
from plots.common.tdrstyle import tdrstyle
from datetime import date
import random


def make_beamer_header():
    header = """
\documentclass{beamer}
\usetheme{default}
"""
    header+="""
\\title{Systematics in final selection}
\date{"""+str(date.today())+"""}
\\begin{document}
\maketitle
"""
    return header

def make_plot_slide(process, canvas):
    try:
        os.mkdir("systematics_plots")
        os.mkdir("tex_output")
    except OSError:
        pass
    canvas.SaveAs("systematics_plots/"+process+".pdf")        
    canvas.SaveAs("systematics_plots/"+process+".png")
    tex = """\\begin{frame}[fragile]
    \\begin{center}
        \includegraphics[width=250pt]{../systematics_plots/"""+process+""".pdf}
    \end{center}    
\end{frame}
    """
    return tex

"""
Makes plots with systematic variation and creates slides with beamer
"""
if __name__ == "__main__":
    try:
        sys.path.append(os.environ["STPOL_DIR"] )
    except KeyError:
        print "Could not find the STPOL_DIR environment variable, did you run `source setenv.sh` in the code base directory?"
        sys.exit(1)

    outf = open('tex_output/systematics.tex', 'w')
    outf.write(make_beamer_header())

    weight = "pu_weight*b_weight_nominal*muon_IsoWeight*muon_IDWeight*muon_TriggerWeight"
    cutstring = str(Cuts.hlt_isomu * Cuts.mu * Cuts.final(2,1))

    infilePath = "~andres/single_top/stpol/out_step3_06_01/iso/Nominal/"
    infilePathSys = "~andres/single_top/stpol/out_step3_06_01/iso/"

    mcFiles = {
        "T_t_ToLeptons": "T_t_ToLeptons.root",
        "Tbar_t_ToLeptons": "Tbar_t_ToLeptons.root",
        "T_tW": "T_tW.root",
        "Tbar_tW": "Tbar_tW.root",
        "T_s": "T_s.root",
        "Tbar_s": "Tbar_s.root",
        
        "WW": "WW.root",
        "WZ": "WZ.root",
        "ZZ": "ZZ.root",

        "W1Jets_exclusive": "W1Jets_exclusive.root",
        "W2Jets_exclusive": "W2Jets_exclusive.root",
        "W3Jets_exclusive": "W3Jets_exclusive.root",
        "W4Jets_exclusive": "W4Jets_exclusive.root",
        
        "TTJets_SemiLept": "TTJets_SemiLept.root",
        "TTJets_FullLept": "TTJets_FullLept.root",

    #    "GJets1": "GJets1.root",
    #    "GJets2": "GJets2.root",
    }

    files_mc = {}
    syst = ["En", "Res", "UnclusteredEn"]
    systType = ["Up", "Down"]
    for key in mcFiles:
        filename = mcFiles[key]
        infile = infilePath + filename
        files_mc[key] = {}
        files_mc[key]["Nominal"] = ROOT.TFile(infile)

    for s in syst:
        for st in systType:
            for key in mcFiles:
                filename = mcFiles[key]
                infile = infilePathSys + s + st +"/" +filename
                files_mc[key][s + st] = ROOT.TFile(infile)

                  
    # ----------------------get trees-----------------------
    trees_data = {}
    trees_mc = {}

    hist_def = {
        #"met": ["met", (100, 0, 200)],
        #"top_mass": ["top_mass", (100, 50, 300)],
        #"eta_lj": ["eta_lj", (100, 0, 5.0)],
        #"pt_lj": ["pt_lj",(100, 0, 200)],
        #"cos_theta": ["cos(#Theta *)", (8, -1.0, 1.0)],
        "cos_theta": ["cos_theta", (8, -1.0, 1.0)],
        #"n_jets": ["n_jets", (8, 0.5, 8.5)],
        }

    for key in files_mc:
        trees_mc[key] = {}
        for s in files_mc[key]:
            trees_mc[key][s] = files_mc[key][s].Get("trees").Get("Events")
            
    #cut_qcd_template = cuts[cutstring_qcd_template]

    histos = {}
    hist_final = {}
    error = array('d',[0.])

    for hist_name in hist_def:
        for process in trees_mc:    
            #print("Get " + hist_name + " histograms:")
            histToPlot = hist_def[hist_name][0]
            hRange = hist_def[hist_name][1]
            
            histos[hist_name+"_"+process] = OrderedDict()
            #hist_final[hist_name+"_"+process] = {}
            
            for subproc in trees_mc[process]:
                    N = files_mc[process][subproc].Get("trees").Get("count_hist").GetBinContent(1) #total number of analyzed MC events
                    w = lumi_iso["mu"]*xs[process]/N
                    #print("Loading:" + str(N) + " events of " +process + " with xs = " + str(xs[process])+ " and MC ev. weight = " + str(w))
                
                    histName = "h_" + hist_name + "_" + process +" "+ subproc
                    title = process + " "+ subproc
                    h = ROOT.TH1F( histName, title, hRange[0], hRange[1], hRange[2] )
                    h.Sumw2() # remember weights - not sure of the use
             
                    trees_mc[process][subproc].Draw( histToPlot + ">>" + histName, str(w)+ "*" + weight + "*" +  cutstring, "goff" )
                    #print str(w)+ "*" + weight + "*" +  cut
                    print "%s %s %.1f +- %.1f" % (process, subproc,h.IntegralAndError(0,100,error), error[0])
                    histos[hist_name+"_"+process][subproc] = h                

        outfile = "Histograms/" + hist_name + ".root"
        #outfile = "testing.root"
        p = ROOT.TFile(outfile,"recreate")
        print "writing output to file: " + outfile

        dirs = {} # make a directory for each process

        for process in histos:
            dirs[process] = p.mkdir(process)

        #print histos
        for process in histos:
            dirs[process].cd()
            for subproc in histos[process]:
                histos[process][subproc].Write(hist_name+subproc)
                print process, subproc, hist_name
                #for subproc in histos[process]:
                #    dirs[process] = p.mkdir(process)

        p.Close()

        tdrstyle()

        canvases = {}
        for process in histos:
            #Create the canvas
            canv = ROOT.TCanvas("c"+process, "c")
            canv.SetWindowSize(1000, 1000)
            canv.SetCanvasSize(1000, 1000)

            outf.write("\\begin{frame}[fragile]\n")
            outf.write("\\begin{verbatim}"+process+"\\end{verbatim}\n")
            outf.write("""\\begin{center}
            \\begin{tabular}{ l || c | c | r }
            \hline
            """)
            outf.write("Systematic & yield & Chi2/NDF & p-value \\\\ \hline\n")
            
            #print histos[process].items()[1]
            #print histos[process].items()[3]
            #print histos[process].items()
            
            #for name,histo in histos[process].items():
            #for i in [2,1,5,4,3,0,6]:
            #for i in [2,1,0]:
            for name, histo in histos[process].items():
                #(name, histo) = histos[process].items()[i]
                if name != "Nominal":
                    outf.write(" %s & $%.1f \pm %.1f $ & %.2f & %.3f \\\\ \hline\n" % (name, histo.IntegralAndError(0,100,error), error[0], histo.Chi2Test(histos[process]["Nominal"], "WW CHI2/NDF"),histo.Chi2Test(histos[process]["Nominal"], "WW")))
                else:
                    outf.write("%s & $%.1f \pm %.1f$ & & \\\\ \hline\n" % (name, histo.IntegralAndError(0,100,error), error[0]))
            outf.write("""
            \hline
            \end{tabular}
            \end{center}    
\end{frame}
            """)

            for name,histo in histos[process].items():
                if name != "Nominal":
                    print "Chi2 %s %s %.2f %.3f" %(process,name,histo.Chi2Test(histos[process]["Nominal"], "WW CHI2/NDF"),histo.Chi2Test(histos[process]["Nominal"], "WW"))

            canv = plot_hists(canv, histos[process],
                x_label="cos(#Theta *)",
                title=process,
                max_bin_mult=1.6
            )
            
            #Draws the lumi box
            lumibox = lumi_textbox(lumi_iso["mu"])
            
            #Draw the legend
            leg = legend(
                histos[process].values(), # <<< need to reverse MC order here, mc3 is top-most
                styles=["l"],
                width=0.3,
                text_size=0.015
            )

            outf.write(make_plot_slide(process, canv))

    outf.write("\end{document}")
    outf.close()
