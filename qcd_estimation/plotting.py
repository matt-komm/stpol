from init_data import *
from util_scripts import *
from Variable import *
from ROOT import *
from array import array

def make_stack(var, stackName, MC_groups, data_group, open_files, syst, iso, lumis, cutsMC, cutsData, cutsQCD, extra = "", qcd=None, absolute=False):
   print "making stack "+iso + " "+syst + " "+extra
   #print "MC", cutsMC
   #print "data", cutsData
   make_histograms(var, MC_groups, data_group, open_files, syst, iso, lumis, cutsMC, cutsData, cutsQCD,extra, absolute)
   stack = THStack("Stack"+var.shortName+syst+iso, stackName)
   if qcd is not None:
      qcd.SetFillColor(dgQCD.getColor())
      #qcd.SetLineColor(dgQCD.getColor())
      stack.Add(qcd)
   for group in reversed(MC_groups):
      his = TH1D(group.getHistogram(var, syst, iso, extra))
      his.SetFillColor(group.getColor())
      stack.Add(his)
   return stack

def draw_stack(var, stack, MC_groups, data_group, syst="", iso="iso", name="", maxY=10000, save=True):
   cst = TCanvas("Histogram_"+var.shortName,"_"+var.shortName,10,10,1800,1000)
   stack_data = data_group.getHistogram(var, syst, iso)
   stack_data.Draw("E1")
   stack.Draw("same hist")
   stack_data.SetAxisRange(0,maxY,"Y")  
   stack_data.SetMarkerStyle(20)     
   stack_data.Draw("E1 same")
   
   stack_data.GetXaxis().SetTitle(var.displayName)   

   leg = TLegend(0.81,0.27,0.93,0.90)
   leg.SetTextSize(0.037)
   leg.SetBorderSize(0)
   leg.SetLineStyle(0)
   leg.SetTextSize(0.04)
   leg.SetFillColor(0)
       
   leg.AddEntry(stack_data,"Data","pl")
   for group in MC_groups:
      group.getHistogram(var, syst, iso).SetFillColor(group.getColor())
      leg.AddEntry(group.getHistogram(var, syst, iso),group.getName(),"f")
        
   leg.Draw()


   cst.Update()
   cst.SaveAs("plots/stack_"+var.shortName+"_"+name+"_"+syst+"_"+iso+".png")
   cst.SaveAs("plots/stack_"+var.shortName+"_"+name+"_"+syst+"_"+iso+".pdf")
   return cst

def draw_final(var, stack, MC_groups, data_group, syst="", iso="iso", name="", maxY=10000, save=True, qcd=None):
   cst = TCanvas("Histogram_"+var.shortName,"_"+var.shortName,10,10,1000,1000)
   gROOT.SetStyle("Plain")
   gStyle.SetOptStat(1000000000)
   cst.SetLeftMargin(1)
   cst.SetRightMargin(0.25)
           
   stack_data = data_group.getHistogram(var, syst, iso)
   stack_data.GetXaxis().SetNdivisions(505, 1)
   stack_data.Draw("E1")
   stack.GetHists().GetSize()
   stack.Draw("same hist")
   stack_data.SetAxisRange(0,maxY,"Y")
   stack_data.SetMarkerStyle(20)       
   stack_data.Draw("E1 same")
   
   stack_data.GetXaxis().SetTitle(var.displayName)   
   leg = TLegend(0.76,0.27,0.93,0.90)
   leg.SetTextSize(0.037)
   leg.SetBorderSize(0)
   leg.SetLineStyle(0)
   leg.SetTextSize(0.04)
   leg.SetFillColor(0)
       
   leg.AddEntry(stack_data,"Data","pl")
   for group in MC_groups:
      group.getHistogram(var, syst, iso).SetFillColor(group.getColor())
      leg.AddEntry(group.getHistogram(var, syst, iso),group.getName(),"f")
   leg.AddEntry(qcd,"QCD","f")     
      
   leg.Draw()
   stack.GetHists().GetSize()
   cst.Update()
   cst.SaveAs("plots/final_plot_"+var.shortName+".png")
   cst.SaveAs("plots/final_plot_"+var.shortName+".pdf")
   return cst


def make_histograms(var, MC_groups, data_group, open_files, syst, iso, lumis, cutsMC, cutsData, cutsQCD, extra = "", absolute=False):
   all_groups = []
   all_groups.extend(MC_groups)
   total = TH1D("total", "total", var.bins, var.lbound, var.ubound)
   total.Sumw2()
   if data_group is not None:
      all_groups.append(data_group)
   for group in all_groups:
      name = group.getName()
      histo_name = name+"_"+var.shortName+"_"+syst+"_"+iso+"_"+extra
      group.setTitle(name)
      h = TH1D(histo_name, group.getTitle(), var.bins, var.lbound, var.ubound)
      h.Sumw2()
      for ds in group.getDatasets():
         if(True):#ds.hasBranch(branch) or ds.isMC()):
            his_name = "histo"+"_"+ds.getName()+"_"+var.shortName+"_"+syst+iso+"_"+extra
            his = TH1D(his_name, his_name, var.bins, var.lbound, var.ubound)
            his.Sumw2()
            f = ds.getFile(syst, iso)
            tdir = f.Get("trees")
            #print ds.getName()+" "+ds.getTree()+"_"+syst
            mytree = tdir.Get("Events")
            mytree.AddFriend("trees/WJets_weights")
            if group.getName()=="QCD":
                weight = cutsQCD            
            elif group.isMC():
               weight = cutsMC               
            else:
               weight = cutsData
            #print "weight", weight
            if absolute:
               mytree.Project(his_name, "abs("+var.name+")", weight,"same")
            else:
               mytree.Project(his_name, var.name, weight,"same")
            if group.isMC():
               his.Scale(ds.scaleToData(lumis.getDataLumi(iso), syst, iso))               
               #print ds.scaleToData(lumis.getDataLumi(iso, syst))
            else:
               #print group, ds.preScale()
               his.Scale(ds.preScale())
            h.Add(his)
      error = array('d',[0.])
      print group.getName(), group.getTitle(), var.shortName, syst, iso, extra, h.GetEntries(), h.IntegralAndError(0,100,error), "+-", error[0]
      group.addHistogram(h, var, syst, iso, extra)
      if group.isMC():
         total.Add(h)
   error = array('d',[0.])
   print "total MC",total.IntegralAndError(0,100,error)," +- ", error[0]


def make_histogram(var, group, title, open_files, lumis, syst="", iso="iso", weight="1", extra="", absolute=False):
   name = group.getName()
   histo_name = name+"_"+var.shortName+"_"+syst+"_"+extra
   h = TH1D(histo_name, title, var.bins, var.lbound, var.ubound)
   h.Sumw2()
   for ds in group.getDatasets():
         his_name = "histo"+"_"+ds.getName()+"_"+var.shortName+"_"+syst+iso+extra
         his = TH1D(his_name, his_name, var.bins, var.lbound, var.ubound)
         his.Sumw2()
         f = ds.getFile(syst, iso)
         tdir = f.Get("trees")
         mytree = tdir.Get("Events")
         if absolute:
             mytree.Project(his_name, "abs("+var.name+")", weight,"same")
         else:
             mytree.Project(his_name, var.name, weight,"same")
         if group.isMC():
            his.Scale(ds.scaleToData(lumis.getDataLumi(iso), syst, iso))
         else:
            his.Scale(ds.preScale())
         h.Add(his)
         group.addHistogram(h, var, syst, iso, extra)
