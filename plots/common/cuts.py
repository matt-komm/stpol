from plots.common.utils import escape
from plots.common.utils import NestedDict

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
        return "<Cut(%s)>" % self.cut_str

    def __str__(self):
        return '('+self.cut_str+')'

class SystematicException(Exception):
    def __init__(self, syst):
        self.msg = "Incorrect systematic specified: " + str(syst)
class ChannelException(Exception):
    def __init__(self, chan):
        self.msg = "Incorrect lepton channel: " + str(chan)

#FIXME: Find a better way than static methods
class Cuts:
    hlt_isomu = Cut("(HLT_IsoMu24_eta2p1_v11 == 1 || HLT_IsoMu24_eta2p1_v12 == 1 || HLT_IsoMu24_eta2p1_v13 == 1 || HLT_IsoMu24_eta2p1_v14 == 1 || HLT_IsoMu24_eta2p1_v15 == 1 || HLT_IsoMu24_eta2p1_v16 == 1  || HLT_IsoMu24_eta2p1_v17 == 1)")
    hlt_isoele = Cut("( (HLT_Ele27_WP80_v10 ==1) || (HLT_Ele27_WP80_v11 == 1) || (HLT_Ele27_WP80_v9==1) || (HLT_Ele27_WP80_v8==1) )")
    eta_lj = Cut("abs(eta_lj) > 2.5")

    @staticmethod    
    def mt_mu(syst="nominal"):
        if syst == "nominal":
            return Cut("mt_mu > 50")
        elif syst == "up":
            return Cut("mt_mu > 70")   
        elif syst == "down":
            return Cut("mt_mu > 30")
        raise SystematicException(syst)

    #mt_mu = Cut("mt_mu > 50")
    rms_lj = Cut("rms_lj < 0.025")
    eta_jet = Cut("abs(eta_lj) < 4.5")*Cut("abs(eta_bj) < 4.5")
    pt_jet = Cut("pt_lj > 40")*Cut("pt_bj > 40")
    top_mass_sig = Cut("top_mass > 130 && top_mass < 220")
    one_muon = Cut("n_muons==1 && n_eles==0")
    one_electron = Cut("n_muons==0 && n_eles==1")
    lepton_veto = Cut("n_veto_mu==0 && n_veto_ele==0")
    electron_iso = Cut("el_mva > 0.9 & el_reliso < 0.1")
    mu_antiiso = Cut("mu_iso>0.2 && mu_iso<0.5")
    electron_antiiso = Cut("el_iso > 0.15 & el_iso < 0.5")

    #MVA variable names
    mva_vars = {}
    mva_vars['ele'] = 'mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj'
    mva_vars['mu'] = 'mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj'
    mva_vars_qcd = {}
    mva_vars_qcd['ele']='mva_anti_QCD_MVA'
    mva_vars_qcd['mu']='mva_anti_QCD_MVA'

    #MVA working points
    #FIXME: put a reference to where they came from
    mva_wps = NestedDict()
    mva_wps['bdt']['mu']['loose'] = 0.06
    mva_wps['bdt']['mu']['tight'] = 0.6
    mva_wps['bdt']['ele']['loose'] = 0.13
    mva_wps['bdt']['ele']['tight'] = 0.6
    mva_wps['bdt']['mu_qcd']=0.97
    mva_wps['bdt']['ele_qcd']=0.74
    mva_wps = mva_wps.as_dict()


    #met = Cut('met > 45')
    
    @staticmethod
    def met(syst="nominal"):
        if syst=="nominal":
            return Cut("met>45")
        elif syst=="up":
            return Cut("met>60")
        elif syst=="down":
            return Cut("met<30")

    no_cut = Cut("1")

    @staticmethod
    def true_lepton(lep):
        if lep=="mu":
            return Cut("abs(true_lepton_pdgId)==13")
        elif lep=="ele":
            return Cut("abs(true_lepton_pdgId)==11")
        else:
            raise ChannelException(lep)

    @staticmethod
    def lepton(lepton):
        if lepton=="mu":
            cut = Cuts.one_muon*Cuts.lepton_veto
        elif lepton=="ele":
            cut = Cuts.one_electron*Cuts.lepton_veto
        else:
            raise ChannelException(lepton)
        return cut

    @staticmethod
    def mt_or_met(lepton):
        if lepton=="mu":
            cut = Cuts.mt_mu()
        elif lepton=="ele":
            cut = Cuts.met()
        else:
            raise ChannelException(lepton)
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
            raise ChannelException(lepton)

    @staticmethod
    def antiiso(lepton):
        if lepton == "mu":
            return Cuts.mu_antiiso
        elif lepton == "ele":
            return Cuts.electron_antiiso
        else:
            raise ChannelException(lepton)

    @staticmethod
    def deltaR(x):
        return Cut("deltaR_bj>{0} && deltaR_lj>{0}".format(x))

    @staticmethod
    def n_tags(n):
        return Cut("n_tags == %d" % int(n))

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
        return Cuts.lepton(lepton)*Cuts.rms_lj*Cuts.mt_or_met(lepton)*Cuts.n_jets(n)*Cuts.eta_lj*Cuts.top_mass_sig
        
    @staticmethod
    def mva_cut(cut, mva_var = "mva_BDT"):
        if cut <= -1:
            return Cut("1")
        else:
            return Cut("%s >= %s" % (mva_var, cut))    

    @staticmethod
    def mva_iso(lepton, mva_cut="-1", mva_var="mva_BDT"):
        return Cuts.hlt(lepton)*Cuts.lepton(lepton)*Cuts.rms_lj*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.mt_or_met(lepton)*Cuts.mva_cut(mva_cut, mva_var)

    @staticmethod
    def mva_antiiso(lepton, mva_cut="-1", mva_var="mva_BDT"):
        return Cuts.hlt(lepton)*Cuts.lepton(lepton)*Cuts.rms_lj*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.deltaR(0.3)*Cuts.antiiso(lepton)*Cuts.mt_or_met(lepton)*Cuts.mva_cut(mva_cut, mva_var)

    @staticmethod
    def eta_fit(lepton, nj=2, nb=1):
        return Cuts.hlt(lepton)*Cuts.lepton(lepton)*Cuts.rms_lj*Cuts.mt_or_met(lepton)*Cuts.n_jets(nj)*Cuts.n_tags(nb)*Cuts.top_mass_sig

    @staticmethod
    def eta_fit_antiiso(lepton="mu", nj=2, nb=1):   #relaxed top mass
        return Cuts.hlt(lepton)*Cuts.lepton(lepton)*Cuts.rms_lj*Cuts.mt_or_met(lepton)*Cuts.n_jets(nj)*Cuts.n_tags(nb)*Cuts.deltaR(0.3)*Cuts.antiiso(lepton)

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
    def __init__(self, weight_str, name=None):
        if not name:
            self.name = escape(weight_str)
        else:
            self.name = name
        self.weight_str = weight_str

    def __mul__(self, other):
        weight_str = '('+self.weight_str+') * ('+other.weight_str+')'
        return Weight(weight_str, "__".join([self.name, other.name]))
    
    def __sub__(self, other):
        weight_str = '('+self.weight_str+' - '+other.weight_str+')'
        return Weight(weight_str)

    def __str__(self):
        return self.weight_str

    def __repr__(self):
        return "<Weight(%s)>" % self.weight_str

class Weights:
    no_weight = Weight("1.0")
    @staticmethod
    def total(lepton, systematic="nominal"):

        #PU weight applied always
        w = Weights.pu()

        
        if lepton in ["mu", "ele"]:
            w *= getattr(Weights, lepton)
        else:
            raise ValueError("Lepton channel %s not defined" % lepton)

        w *= Weights.b_weight(systematic)
        return w

    @staticmethod
    def pu(systematic="nominal"):
        if systematic=="nominal":
            return Weight("pu_weight")
        elif systematic=="up":
            return Weight("pu_weight_up")
        elif systematic=="down":
            return Weight("pu_weight_down")
        assert(False)

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
        else:
            raise ValueError("Lepton channel %s not defined" % lepton)

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


    muon_sel = dict()
    muon_sel["id"] = (
        Weight("muon_IDWeight"), Weight("muon_IDWeight_up"), Weight("muon_IDWeight_down")
    )   
    muon_sel["trigger"] = (
        Weight("muon_TriggerWeight"), Weight("muon_TriggerWeight_up"), Weight("muon_TriggerWeight_down")
    )
    muon_sel["iso"] = (
        Weight("muon_IsoWeight"), Weight("muon_IsoWeight_up"), Weight("muon_IsoWeight_down")
    )

    electron_sel = dict()
    electron_sel["id"] = (
        Weight("electron_IDWeight"), Weight("electron_IDWeight_up"), Weight("electron_IDWeight_down")
    )   
    electron_sel["trigger"] = (
        Weight("electron_TriggerWeight"), Weight("electron_TriggerWeight_up"), Weight("electron_TriggerWeight_down")
    )


    pu_syst = (
        Weight("pu_weight"), Weight("pu_weight_up"), Weight("pu_weight_down")
    )

    wjets_yield_syst = (
        Weight("wjets_mg_flavour_flat_weight"), Weight("wjets_mg_flavour_flat_weight_up"), Weight("wjets_mg_flavour_flat_weight_down"),
    )

    wjets_shape_syst = (
        Weight("wjets_mg_flavour_shape_weight"), Weight("wjets_mg_flavour_shape_weight_up"), Weight("wjets_mg_flavour_shape_weight_down"),
    )

    wjets_btag_syst = (
        Weight("b_weight_nominal"), Weight("b_weight_nominal_BCup"), Weight("b_weight_nominal_BCdown"), Weight("b_weight_nominal_Lup"), Weight("b_weight_nominal_Ldown"), 
    )


class Var:
    def __init__(self, varfn, binning):
        self.varfn = varfn
        self.binning = binning

def mul(l):
    return reduce(lambda x,y: x*y, l)
flavour_scenarios = dict()
flavour_scenarios[0] = ["Wbb", "Wcc", "Wbc", "WbX", "WcX", "WgX", "Wgg", "WXX"]
flavour_scenarios[1] = ["W_heavy", "W_light"]
flavour_scenarios[2] = ["W_HH", "W_Hl", "W_ll"]