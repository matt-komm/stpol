
class C(object):
    @classmethod
    def _toStr(cls):
        s = "Config: " + cls.__name__ + " {"
        for k in dir(cls):
            if k[0].islower():
                s += "\n\t%s = %s" % (k, getattr(cls, k))
        # for c in cls.__bases__:
        #     if hasattr(c, "toStr"):
        #         s += c.toStr()
        s += "\n}"
        return s

"""
This is the single global static (singleton type) configuration class, that is read by the SingleTopStep2 code.
"""
class Config(C):

    #A string that gives the MC sample you are running on
    subChannel = None

#    metSource = "patMETs"
    metSource = "patType1CorrectedPFMet"

    globalTagMC = "START53_V20::All"

    #Either running over MC or Data
    isMC = True

    #Enable debugging modules
    doDebug = False

    #Whether to output CMSSW-specific trees
    skipPatTupleOutput = False

    #Whether to run over grid (without command-line arguments)
    onGrid = False

    #If using comphep-generated input
    isCompHep = False

    #If using sherpa-generated input
    isSherpa = False

    #Which systematic to use
    systematic = None

    doSync = False

    #A string to specify the dta period (RunA, RunB, RunC, RunD)
    dataRun = None

    """
    Specifies the jet configuration.
    """
    class Jets(C):
        ptCut = 40

        #etaCut=4.5
        #FIXME: where did the 4.5 come from? The reference selection is clearly 5.0. --JP
        #https://twiki.cern.ch/twiki/bin/viewauth/CMS/TWikiTopRefEventSel#Jets_and_MET
        etaCut = 5.0

        doLightJetRMSClean = False

        #Must be switched OFF for the sync!
        #Also agreed to switch OFF for the analysis
        doPUClean = False

        #source = "patJetsWithOwnRefNotOverlappingWithLeptonsForMEtUncertainty"
        source = "patJetsWithOwnRef"
        #source = "selectedPatJetsForMETtype1p2CorrEnDown"

        class BTagDiscriminant:
            TCHP = "trackCountingHighPurBJetTags"
            CSV_MVA = "combinedSecondaryVertexMVABJetTags"
        class BTagWorkingPoint:
            TCHPT = "TCHPT"
            CSVT = "CSVT"
            CSVM = "CSVM"

            WP = {"TCHPT":3.41, "CSVT":0.898, "CSVM":0.679}

        bTagDiscriminant = BTagDiscriminant.TCHP
        bTagWorkingPoint = BTagWorkingPoint.TCHPT

        @classmethod
        def BTagWorkingPointVal(c):
            return c.BTagWorkingPoint.WP[c.bTagWorkingPoint]

    class Leptons(C):
        class WTransverseMassType:
            MtW = "MtW"
            MET = "MET"

        class RelativeIsolation:
            rhoCorrRelIso = "rhoCorrRelIso"
            deltaBetaCorrRelIso = "deltaBetaCorrRelIso"

        reverseIsoCut = False
        cutOnIso = True

        transverseMassDef = 0 #Set to 0 to never throw away any MET from the analysis
        relIsoType = RelativeIsolation.rhoCorrRelIso

        relIsoCutRangeIsolatedRegion = [0.0, 0.2]
        relIsoCutRangeAntiIsolatedRegion = [0.2, 0.5]
        looseVetoRelIsoCut = 0.2


    class Muons(Leptons):
        relIsoCutRangeIsolatedRegion = [0.0, 0.12]
        relIsoCutRangeAntiIsolatedRegion = [0.2, 0.9]
        looseVetoRelIsoCut = 0.2
        source = "muonsWithID"
        triggerPath = "HLT_IsoMu24_eta2p1_v*"

    class Electrons(Leptons):
        pt = "ecalDrivenMomentum.Pt()"
        cutOnIso = True
        mvaCut = 0.9 #This defines a good signal electron, this is not a cut per se
        relIsoCutRangeIsolatedRegion = [0.0, 0.1]
        relIsoCutRangeAntiIsolatedRegion = [0.1, 0.5]
        looseVetoRelIsoCut = 0.15
        transverseMassType = "MET"
        source = "electronsWithID"
        triggerPath = "HLT_Ele27_WP80_v*"

    Electrons.relIsoType = Leptons.RelativeIsolation.rhoCorrRelIso
    Muons.relIsoType = Leptons.RelativeIsolation.deltaBetaCorrRelIso
