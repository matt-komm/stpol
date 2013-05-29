
class Cut:
    def __init__(self, cut_str):
        self.cut_str = cut_str
    def __mul__(self, other):
        cut_str = '('+self.cut_str+') && ('+other.cut_str+')'
        return Cut(cut_str)
    def __repr__(self):
        return "<Cut(%s)>" % self.cut_str

    def __str__(self):
        return self.cut_str

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
    lepton_veto = Cut("n_veto_mu==0 && n_veto_ele==0")
    no_cut = Cut("1")

    @staticmethod
    def n_jets(n):
        return Cut("n_jets == %d" % int(n))
    @staticmethod
    def n_tags(n):
        return Cut("n_tags == %d" % int(n))

    @staticmethod
    def final(n, m):
        return Cuts.rms_lj*Cuts.mt_mu*Cuts.n_jets(n)*Cuts.n_tags(m)*Cuts.eta_lj*Cuts.top_mass_sig

#Cuts.final = lambda n,m: Cuts.rms_lj*Cuts.mt_mu*Cuts.n_jets(n)*Cuts.n_tags(m)*Cuts.eta_lj*Cuts.top_mass_sig
Cuts.mu = Cuts.one_muon*Cuts.lepton_veto
