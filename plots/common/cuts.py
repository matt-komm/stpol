
class Cut:
    def __init__(self, cut_str):
        self.cut_str = cut_str
    def __mul__(self, other):
        cut_str = '('+self.cut_str+') && ('+other.cut_str+')'
        return Cut(cut_str)

    def __add__(self, other):
        cut_str = '('+self.cut_str+') || ('+other.cut_str+')'
        return Cut(cut_str)

    def __repr__(self):
        return "<Cut(%s)>" % '('+self.cut_str+')'

    def __str__(self):
        return '('+self.cut_str+')'

class Cuts:
    hlt_isomu = Cut("HLT_IsoMu24_eta2p1_v11 == 1 || HLT_IsoMu24_eta2p1_v12 == 1 || HLT_IsoMu24_eta2p1_v13 == 1 || HLT_IsoMu24_eta2p1_v14 == 1 || HLT_IsoMu24_eta2p1_v15 == 1 || HLT_IsoMu24_eta2p1_v16 == 1  || HLT_IsoMu24_eta2p1_v17 == 1")
    hlt_isoele = Cut("( (HLT_Ele27_WP80_v10 ==1) || (HLT_Ele27_WP80_v11 == 1) || (HLT_Ele27_WP80_v9==1) || (HLT_Ele27_WP80_v8==1) )")
    eta_lj = Cut("abs(eta_lj) > 2.5")
    mt_mu = Cut("mt_mu > 50")
    rms_lj = Cut("rms_lj < 0.025")
    eta_jet = Cut("abs(eta_lj) < 4.5")*Cut("abs(eta_bj) < 4.5")
    pt_jet = Cut("pt_lj > 40")*Cut("pt_bj > 40")
    top_mass_sig = Cut("top_mass > 130 && top_mass < 220")
    one_muon = Cut("n_muons==1 && n_eles==0")
    one_electron = Cut("n_muons==0 && n_eles==1")
    lepton_veto = Cut("n_veto_mu==0 && n_veto_ele==0")
    met = Cut('met > 45')
    no_cut = Cut("1")

    @staticmethod
    def n_jets(n):
        return Cut("n_jets == %d" % int(n))
    @staticmethod
    def n_tags(n):
        return Cut("n_tags == %d" % int(n))

    @staticmethod
    def final_jet(n, lepton="mu"):
        if lepton=="mu":
            cut = Cuts.one_muon*Cuts.lepton_veto
        elif lepton=="ele":
            cut = Cuts.one_eletron*Cuts.lepton_veto
        else:
            raise ValueError("lepton must be mu or ele:%s" % lepton)

        return cut*Cuts.rms_lj*Cuts.mt_mu*Cuts.n_jets(n)*Cuts.eta_lj*Cuts.top_mass_sig
    
    @staticmethod
    def final(n, m, lepton="mu"):
        return Cuts.final_jet(n, lepton)*Cuts.n_tags(m)

    Wbb = Cut("wjets_flavour_classification == 0")
    Wcc = Cut("wjets_flavour_classification == 1")
    WbX = Cut("wjets_flavour_classification == 2")
    WcX = Cut("wjets_flavour_classification == 3")
    WgX = Cut("wjets_flavour_classification == 4")
    Wgg = Cut("wjets_flavour_classification == 5")
    WXX = Cut("wjets_flavour_classification == 6")

    @staticmethod
    def Wflavour(s):
        if s=="W_heavy":
            return Cuts.Wbb+Cuts.Wcc+Cuts.WbX+Cuts.WcX
        elif s=="W_light":
            return Cuts.WgX+Cuts.Wgg+Cuts.WXX
        else:
            return ValueError("Did not understand flavour string %s" % s)

Cuts.mu = Cuts.one_muon*Cuts.lepton_veto
Cuts.eta_fit = Cuts.hlt_isomu*Cuts.mt_mu*Cuts.rms_lj*Cuts.eta_jet

class Weights:
    @staticmethod
    def total(systematic="nominal"):
        w = Cut("pu_weight")
        if systematic=="nominal":
            w*= Cut("b_weight_nominal")
        else:
            raise ValueError("Define b-weight for systematic %s" % systematic)
        return w

    @staticmethod
    def wjets_madgraph_weight(systematic="nominal"):
        if systematic=="nominal":
            return Cut("wjets_mg_flavour_weight")
        elif systematic=="wjets_up":
            return Cut("wjets_mg_flavour_weight_up")
        elif systematic=="wjets_down":
            return Cut("wjets_mg_flavour_weight_down")
        else:
            raise ValueError("Unrecognized systematic=%s" % systematic) 
 
    mu = Cut("muon_IsoWeight")*Cut("muon_IDWeight")*Cut("muon_TriggerWeight")

flavour_scenarios = ["W_heavy", "W_light"]


