
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
    hlt_isomu = Cut("(HLT_IsoMu24_eta2p1_v11 == 1 || HLT_IsoMu24_eta2p1_v12 == 1 || HLT_IsoMu24_eta2p1_v13 == 1 || HLT_IsoMu24_eta2p1_v14 == 1 || HLT_IsoMu24_eta2p1_v15 == 1 || HLT_IsoMu24_eta2p1_v16 == 1  || HLT_IsoMu24_eta2p1_v17 == 1)")
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
    mu_antiiso = Cut("mu_iso>0.2 && mu_iso<0.5")
    electron_antiiso = Cut("el_iso > 0.1 & el_iso < 0.5")
    met = Cut('met > 45')
    no_cut = Cut("1")

    @staticmethod
    def lepton(lepton):
        if lepton=="mu":
            cut = Cuts.one_muon*Cuts.lepton_veto
        elif lepton=="ele":
            cut = Cuts.one_electron*Cuts.lepton_veto
        return cut

    @staticmethod
    def mt_or_met(lepton):
        if lepton=="mu":
            cut = Cuts.mt_mu
        elif lepton=="ele":
            cut = Cuts.met
        return cut

    @staticmethod
    def n_jets(n):
        return Cut("n_jets == %d" % int(n))
    
    @staticmethod
    def hlt(lepton):
        if lepton=="mu":
            return Cuts.hlt_isomu
        elif lepton=="ele":
            return Cuts.hlt_isoele
        else:
            raise ValueError("lepton must be mu or ele:%s" % lepton)

    @staticmethod
    def hlt(lepton):
        if lepton == "mu":
            return Cuts.hlt_isomu
        elif lepton == "ele":
            return Cuts.hlt_isoele
        else:
            raise ValueError("lepton must be mu or ele:%s" % lepton)

    @staticmethod
    def antiiso(lepton):
        if lepton == "mu":
            return Cuts.mu_antiiso
        elif lepton == "ele":
            return Cuts.electron_antiiso
        else:
            raise ValueError("lepton must be mu or ele:%s" % lepton)
    
    @staticmethod
    def deltaR(x):
        return Cut("deltaR_bj>{0} && deltaR_lj>{0}".format(x))

    @staticmethod
    def n_tags(n):
        return Cut("n_tags == %d" % int(n))

    @staticmethod
    def metmt(lepton):
        if lepton=="mu":
            return Cuts.mt_mu
        elif lepton=="ele":
            return Cuts.met
        else:
            raise ValueError("lepton must be mu or ele:%s" % lepton)
    
    @staticmethod
    def single_lepton(lepton):
        if lepton=="mu":
            return Cuts.one_muon*Cuts.lepton_veto
        elif lepton=="ele":
            return Cuts.one_electron*Cuts.lepton_veto
        else:
            raise ValueError("lepton must be mu or ele:%s" % lepton)

    @staticmethod
    def final_jet(n, lepton="mu"):
        if lepton not in ["mu", "ele"]:
            raise ValueError("lepton must be mu or ele:%s" % lepton)
        return Cuts.lepton(lepton)*Cuts.rms_lj*Cuts.mt_or_met(lepton)*Cuts.n_jets(n)*Cuts.eta_lj*Cuts.top_mass_sig
    
    @staticmethod
    def eta_fit(lepton, nj=2, nb=1):
        if lepton not in ["mu", "ele"]:
            raise ValueError("lepton must be mu or ele:%s" % lepton)
        return Cuts.hlt(lepton)*Cuts.lepton(lepton)*Cuts.rms_lj*Cuts.mt_or_met(lepton)*Cuts.n_jets(nj)*Cuts.n_tags(nb)*Cuts.top_mass_sig

    @staticmethod
    def eta_fit_antiiso(lepton="mu", nj=2, nb=1):   #relaxed top mass
        if lepton not in ["mu", "ele"]:
            raise ValueError("lepton must be mu or ele:%s" % lepton)
        return Cuts.hlt(lepton)*Cuts.lepton(lepton)*Cuts.rms_lj*Cuts.mt_or_met(lepton)*Cuts.n_jets(nj)*Cuts.n_tags(nb)*Cuts.deltaR(0.3)*Cuts.antiiso(lepton)

    @staticmethod
    def final_jet(n, lepton="mu"):
        if lepton=="mu":
            cut = Cuts.one_muon*Cuts.lepton_veto
        elif lepton=="ele":
            cut = Cuts.one_electron*Cuts.lepton_veto
        else:
            raise ValueError("lepton must be mu or ele:%s" % lepton)

        return cut*Cuts.metmt(lepton)*Cuts.rms_lj*Cuts.n_jets(n)*Cuts.eta_lj*Cuts.top_mass_sig
    @staticmethod
    def final(n, m, lepton="mu"):
        return Cuts.final_jet(n, lepton)*Cuts.n_tags(m)

    @staticmethod
    def final_antiiso(lepton="mu", nj=2, nb=1):
        return Cuts.eta_fit_antiiso(lepton, nj, nb) # * Cuts.eta_lj - relaxed

    @staticmethod
    def final_iso(lepton="mu", nj=2, nb=1):
        return Cuts.eta_fit(lepton, nj, nb) * Cuts.eta_lj 


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

class Weight:
    def __init__(self, weight_str):
        self.weight_str = weight_str

    def __mul__(self, other):
        weight_str = '('+self.weight_str+') * ('+other.weight_str+')'
        return Weight(weight_str)

    def __str__(self):
        return self.weight_str

class Weights:
    @staticmethod
    def total(lepton, systematic="nominal"):

        #PU weight applied always
        w = Weights.pu()

        
        if lepton in ["mu", "ele"]:
            w *= getattr(Weights, lepton)
        else:
            raise ValueError("Lepton channel %s not defined" % lepton)

        w *= Weights.b_weight("systematic")

    @staticmethod
    def pu():
        return Weight("pu_weight")

    @staticmethod
    def b_weight(systematic="nominal", sys_type=""):
        if sys_type not in ["", "up", "down"]:
            raise ValueError("Wrong systematic type %s (only up or down)" % (sys_type))
        if systematic=="nominal":
            return Weight("b_weight_nominal")
        elif systematic in ["BC", "L"]:
            return Weight("b_weight_nominal_"+systematic+sys_type)
        else:
            raise ValueError("No such systematic %s!" % (systematic))

    @staticmethod
    def muon_weight(systematic="nominal", sys_type=""):
        w = Weight("1")
        if sys_type not in ["", "up", "down"]:
            raise ValueError("Wrong systematic type %s (only up or down)" % (sys_type))
        if systematic in ["ID", "Iso", "Trigger", "nominal"]:
            if systematic == "ID":
                w *= Weight("muon_IDWeight_"+sys_type)
            else:
                w *= Weight("muon_IDWeight")
            if systematic == "Iso":
                w *= Weight("muon_IsoWeight_"+sys_type)
            else:
                w *= Weight("muon_IsoWeight")
            if systematic == "Trigger":
                w *= Weight("muon_TriggerWeight_"+sys_type)
            else:
                w *= Weight("muon_TriggerWeight")
        else:
            raise ValueError("No such systematic %s!" % (systematic))
        return w

    @staticmethod
    def electron_weight(systematic="nominal", sys_type=""):
        w = Weight("1")
        if sys_type not in ["", "up", "down"]:
            raise ValueError("Wrong systematic type %s (only up or down)" % (sys_type))
        if systematic in ["ID", "Trigger", "nominal"]:
            if systematic == "ID":
                w *= Weight("electron_IDWeight_"+sys_type)
            else:
                w *= Weight("electron_IDWeight")
            if systematic == "Trigger":
                w *= Weight("electron_TriggerWeight_"+sys_type)
            else:
                w *= Weight("electron_TriggerWeight")
        else:
            raise ValueError("No such systematic %s!" % (systematic))
        return w

    @staticmethod
    def lepton_weight(lepton, systematic="nominal", sys_type=""):
        if lepton == "mu":        
            return Weights.muon_weight(systematic, sys_type)
        elif lepton == "ele":
            return Weights.electron_weight(systematic, sys_type)

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
    ele = Weight("electron_IDWeight")*Weight("electron_TriggerWeight")
    sherpa_weight = Weight("gen_weight")
    sherpa_flavour_weight = Weight("wjets_sh_flavour_flat_weight")
    
    @staticmethod
    def total_weight(lepton):
        return Weights.lepton_weight(lepton) * Weights.wjets_madgraph_flat_weight() * Weights.wjets_madgraph_shape_weight() * Weights.pu() * Weights.b_weight()

flavour_scenarios = dict()
flavour_scenarios[0] = ["Wbb", "Wcc", "Wbc", "WbX", "WcX", "WgX", "Wgg", "WXX"]
flavour_scenarios[1] = ["W_heavy", "W_light"]
flavour_scenarios[2] = ["W_HH", "W_Hl", "W_ll"]


