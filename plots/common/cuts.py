
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
    electron_iso = Cut("el_mva > 0.9 & el_reliso < 0.1")
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

    Wbb = Cut("wjets_flavour_classification0 == 0")
    Wcc = Cut("wjets_flavour_classification0 == 1")
    Wbc = Cut("wjets_flavour_classification0 == 2")
    WbX = Cut("wjets_flavour_classification0 == 3")
    WcX = Cut("wjets_flavour_classification0 == 4")
    WgX = Cut("wjets_flavour_classification0 == 5")
    Wgg = Cut("wjets_flavour_classification0 == 6")
    WXX = Cut("wjets_flavour_classification0 == 7")

    W_HH = Cut("wjets_flavour_classification2 == 0")
    W_Hl = Cut("wjets_flavour_classification2 == 1")
    W_ll = Cut("wjets_flavour_classification2 == 2")

    W_heavy = Cut("wjets_flavour_classification1 == 0")
    W_light = Cut("wjets_flavour_classification1 == 1")

Cuts.mu = Cuts.one_muon*Cuts.lepton_veto
Cuts.eta_fit = Cuts.hlt_isomu*Cuts.mt_mu*Cuts.rms_lj*Cuts.eta_jet

class Weight:
    def __init__(self, weight_str):
        self.weight_str = weight_str

    def __mul__(self, other):
        weight_str = '('+self.weight_str+') * ('+other.weight_str+')'
        return Weight(weight_str)

    def __str__(self):
        return "(%s)" % self.weight_str

class Weights:
    @staticmethod
    def total(systematic="nominal"):
        w = Weight("pu_weight")
        if systematic=="nominal":
            w*= Weight("b_weight_nominal")
        else:
            raise ValueError("Define b-weight for systematic %s" % systematic)
        return w

    @staticmethod
    def wjets_madgraph_shape_weight(systematic="nominal"):
        if systematic=="nominal":
            return Weight("wjets_mg_flavour_shape_weight")
        elif systematic=="wjets_up":
            return Weight("wjets_mg_flavour_shape_weight_up")
        elif systematic=="wjets_down":
            return Weight("wjets_mg_flavour_shape_weight_down")
        else:
            raise ValueError("Unrecognized systematic=%s" % systematic)

    @staticmethod
    def wjets_madgraph_flat_weight(systematic="nominal"):
        if systematic=="nominal":
            return Weight("wjets_mg_flavour_flat_weight")
        elif systematic=="wjets_up":
            return Weight("wjets_mg_flavour_flat_weight_up")
        elif systematic=="wjets_down":
            return Weight("wjets_mg_flavour_flat_weight_down")
        else:
            raise ValueError("Unrecognized systematic=%s" % systematic) 
 
    mu = Weight("muon_IsoWeight")*Weight("muon_IDWeight")*Weight("muon_TriggerWeight")
    sherpa_weight = Weight("gen_weight")
    sherpa_flavour_weight = Weight("wjets_sh_flavour_flat_weight")
    #FIXME: put ele weight here

flavour_scenarios = dict()
flavour_scenarios[0] = ["Wbb", "Wcc", "Wbc", "WbX", "WcX", "WgX", "Wgg", "WXX"]
flavour_scenarios[1] = ["W_heavy", "W_light"]
flavour_scenarios[2] = ["W_HH", "W_Hl", "W_ll"]


