import ROOT, numpy

ROOT.gROOT.SetBatch(True)

f1 = ROOT.TFile("/Users/joosep/Dropbox/kbfi/top/stpol/results/ntuples/csvt/T_t_ToLeptons/844/output.root")
f2 = ROOT.TFile("/Users/joosep/Dropbox/kbfi/top/stpol/results/ntuples/csvt/T_t_ToLeptons/844/output.root.added")

t1 = f1.Get("dataframe")
t2 = f1.Get("dataframe")

t1.AddFriend(t2)

print t1.Draw("lepton_pt", "(n_signal_mu==1)*(n_signal_ele==0)*(n_veto_mu==0)*(n_veto_ele==0)*(hlt_mu==1)*(njets==2)*(ntags==1)*(lepton_type==13)*pu_weight")

t1.SetEstimate(t1.GetEntries())
for w in ["ljet_eta", "lepton_weight__id", "lepton_weight__trigger", "lepton_weight__iso", "b_weight"]:
    n = t1.Draw(w, "(n_signal_mu==1)*(n_signal_ele==0)*(n_veto_mu==0)*(n_veto_ele==0)*(hlt_mu==1)*(njets==2)*(ntags==1)*(lepton_type==13)*pu_weight", "goff")
    arr = numpy.frombuffer(t1.GetV1(), numpy.float64, n)
    print(w, arr, min(arr), max(arr), sum(arr)/float(n))
