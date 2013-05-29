import logging
import fnmatch
bTaggingEfficiencies = dict()

class BTaggingEfficiency:
    def __init__(self, eff_b, eff_c, eff_l):
        self.eff_b = eff_b
        self.eff_c = eff_c
        self.eff_l = eff_l
    def __str__(self):
        return str(self.__dict__)

BTaggingEfficiency.default = BTaggingEfficiency(0.0, 0.0, 0.0)

eff_ex_WJets_inclusive_2J =  {
      'b': (0.35669291338582676, 0.013441710817661422)
    , 'c': (0.040322580645161289, 0.001862107290278565)
    , 'l': (0.000857968852000373, 0.00012644632742431355)
}

eff_ex_WJets_inclusive_3J =  {
    'b': (0.3881453154875717, 0.021309363356041836)
    ,'c': (0.0390625, 0.003736912733253034)
    ,'l': (0.0010174532362839477, 0.0002820471604254714)
}

eff_ex_T_t_2J =  {
      'b': (0.45728322743699362, 0.002421136180087223)
    , 'c': (0.02482876712328767, 0.0032194493651988517)
    , 'l': (0.00086048421793718469, 0.00018337690425746975)
}

eff_ex_T_t_3J =  {
    'b': (0.44567094227923038, 0.0039031848017224303)
    ,'c': (0.022750775594622543, 0.004794988098310859)
    ,'l': (0.001070154577883472, 0.0003565272697314706)
}

eff_ex_TTbar_inclusive_2J =  {
      'b': (0.45032609789339845, 0.0015047361221376771)
    , 'c': (0.036358703025369692, 0.0015416425542270076)
    , 'l': (0.0014730143766203158, 0.0002081622083535873)
}

eff_ex_TTbar_inclusive_3J =  {
    'b': (0.46066809489804017, 0.0009928191779086514)
    ,'c': (0.039426786698511851, 0.0008341454022348153)
    ,'l': (0.0014006332165053224, 9.545547317456436e-05)
}


def setEffs(eff_ex_T_t, eff_ex_TTbar, eff_ex_WJets):
    effs = dict()

    b_T_t = eff_ex_T_t["b"][0]
    c_WJets = eff_ex_WJets["c"][0]
    l_T_t = eff_ex_T_t["l"][0]
    l_WJets=eff_ex_WJets["l"][0]
    l_TTbar = eff_ex_TTbar["l"][0]

    effs["T_t*"] = BTaggingEfficiency(b_T_t, c_WJets, l_T_t)
    effs["Tbar_t*"] = BTaggingEfficiency(b_T_t, c_WJets, l_T_t)
    effs["QCD*"] = BTaggingEfficiency.default
    effs["WJets"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)
    effs["W1Jets"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)
    effs["W2Jets"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)
    effs["W3Jets"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)
    effs["W4Jets"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)
    effs["WW"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)
    effs["WZ"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)
    effs["ZZ"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)
    effs["DYJets"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)
    effs["GJets*"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)

    effs["TTbar"] = BTaggingEfficiency(b_T_t, c_WJets, l_TTbar)
    effs["T_tW"] = BTaggingEfficiency(b_T_t, c_WJets, l_TTbar)
    effs["T_s"] = BTaggingEfficiency(b_T_t, c_WJets, l_TTbar)
    effs["Tbar_tW"] = BTaggingEfficiency(b_T_t, c_WJets, l_TTbar)
    effs["Tbar_s"] = BTaggingEfficiency(b_T_t, c_WJets, l_TTbar)
    return effs


bTaggingEfficiencies = dict()
bTaggingEfficiencies[2] = setEffs(eff_ex_T_t_2J, eff_ex_TTbar_inclusive_2J, eff_ex_WJets_inclusive_2J)
bTaggingEfficiencies[3] = setEffs(eff_ex_T_t_3J, eff_ex_TTbar_inclusive_3J, eff_ex_WJets_inclusive_3J)

def getEfficiencies(nJets, sample):
    logging.debug("Looking for efficiencies %s" % sample)
    eff = bTaggingEfficiencies[nJets]
    key = None
    for key in eff.keys():
        if fnmatch.fnmatch(sample, key):
            break
    if key is None:
        raise Exception("B-tagging efficiencies not defined for sample %s" % sample)
    logging.info("Matched efficiencies for key %s: %s" % (key, eff[key]))
    return eff[key]


#The first column is logical, the second may change in the future
fnames = dict()
fnames["T_t"] = "T_t"
fnames["TTbar"] = "TTbar"
fnames["WJets"] = "WJets"

def getEffFiles(channel):
    """
    Returns the filenames to use for a particular process/channel for
    the effiencies of tagging b, c, l jets (in that order)
    """
    if channel in ["T_t", "Tbar_t"]:
        return fnames["T_t"], fnames["WJets"], fnames["T_t"]
    elif channel in ["WJets", "W1Jets", "W2Jets", "W3Jets", "W4Jets", "WW", "WZ", "ZZ", "DYJets"] or channel.startswith("GJets") or channel.startswith("QCD"):
        return fnames["T_t"], fnames["WJets"], fnames["WJets"]
    elif channel in ["TTbar", "T_tW", "T_s", "Tbar_tW", "Tbar_s"]:
        return fnames["T_t"], fnames["WJets"], fnames["TTbar"]
    else:
        raise ValueError("Undefined efficiencies for channel: %s" % channel)
