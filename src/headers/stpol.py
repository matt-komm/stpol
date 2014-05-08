from DataFormats.FWLite import Events, Handle, Lumis
import numpy
PROCESS = "STPOLSEL2"

#A placeholder for a missing value. NaN is good but not ideal.
#In particular, it's only applicable for ints and some algorithms/libraries start behaving subtly wrong on NaN.
NA = float("nan")

def is_na(x):
    """
    Checks if a value was NA.
    """

    #check for non-primitive type
    if not (isinstance(x, float) or isinstance(x, int)):
        return False

    #check for NaN
    return x!=x

def _int(x):
    """
    Convert value to int or NA
    """
    if is_na(x):
        return NA
    else:
        return int(x)


class SimpleHandle:
    """
    A simple interface tying fwlite::Handle<T> and a 3-tuple for a label.
    """

    def make_handle(self, dtype):
        if dtype=="vfloat":
            self.handle = Handle("std::vector<float>")
        elif dtype=="float":
            self.handle = Handle("float")
        elif dtype=="double":
            self.handle = Handle("double")
        elif dtype=="int":
            self.handle = Handle("int")
        else:
            raise ValueError("Undefined type: %s" % dtype)

    def __init__(self, dtype, label, instance, process):
        self.dtype = dtype
        self.label = label
        self.instance = instance
        self.process = process
        self.make_handle(self.dtype)

    def get(self, events):
        """
        Returns the product of a handle if valid, ValueError if invalid.
        """

        exc = None
        try:
            events.getByLabel((self.label, self.instance, self.process), self.handle)
        except Exception as e:
            exc = e
            self.make_handle(self.dtype)

        if not exc and self.handle.isValid():
            return self.handle.product()
        else:
            return NA
            #import pdb; pdb.set_trace()
            #raise ValueError("Could not get product: %s:%s:%s to handle %s" % (self.label, self.instance, self.process, self.handle))

class Getter(object):
    def _getval(self, events, name, n=0):
        x = getattr(self, name).get(events)
        dt = getattr(self, name).dtype

        if is_na(x):
            return NA

        if (dt == "vfloat" or dt== "vdouble"):
            if len(x)==n+1:
                return x[n]
            else:
                return NA
        elif dt == "int" or dt=="float" or dt=="double":
            return self.bufconv(x, dt)
        else:
            raise TypeError("unhandled type: %s" % dt)

    def bufconv(self, x, dt):
        if dt=="int":
            return numpy.frombuffer(x, "int32", 1)
        elif dt=="float":
            return numpy.frombuffer(x, "float32", 1)[0]
        elif dt=="double":
            return numpy.frombuffer(x, "float64", 1)[0]
        else:
            raise TypeError("unhandled type: %s" % dt)

class Weights(Getter):

    class Pileup(Getter):
        _nominal = SimpleHandle("double", "puWeightProducer", "PUWeightNtrue", PROCESS)
        def nominal(self, event):
            return self._getval(event, "_nominal")

    class TopPt(Getter):
        _nominal = SimpleHandle("double", "ttbarTopWeight", "weight", PROCESS)
        def nominal(self, event):
            return self._getval(event, "_nominal")

    class Generator(Getter):
        _nominal = SimpleHandle("double", "genWeightProducer", "w", PROCESS)
        def nominal(self, event):
            return self._getval(event, "_nominal")

    def __init__(self):
        self.pileup = self.Pileup()
        self.toppt = self.TopPt()
        self.generator = self.Generator()

class File:
    def __init__(self):
        pass

    def total_processed(self, fn):
        """
        Returns the total (unskimmed/filtered) count of events processed per this file.
        Only correct when lumi-blocks are never split.
        Loops over the lumi blocks in the file, so is not particularly fast.
        """
        lumis = Lumis(fn)
        tot = 0
        handle = Handle("edm::MergeableCounter")
        for lumi in lumis:
            lumi.getByLabel("singleTopPathStep1MuPreCount", handle)
            if handle.isValid():
                tot += handle.product().value
            else:
                raise Exception("counter not found")
        return tot

    def sample_type(self, fn, prefix="file:/hdfs/cms/store/user/"):
        """
        Returns the sample dictionary corresponding to a filename.
        file:/hdfs/cms/store/user/joosep/Oct3_nomvacsv_nopuclean_e224b5/antiiso/nominal/QCD_Pt_80_170_BCtoE/output_1_1_KCj.root
        """
        m = re.match(prefix+"(.*)/(.*)/(.*)/(.*)/(.*)/(output_.*)\.root", fn)
        if m:
            caps = m.groups()
            tag = caps[1]
            iso = caps[2]
            syst = caps[3]
            samp = caps[4]
        else:
            raise Exception("Could not match %s to pattern" % fn)
        return {"tag": tag, "isolation": iso, "systematic": syst, "sample": samp}



class CosTheta(Getter):
    def __init__(self, src):
        self._costheta_lj = SimpleHandle("double", src, "cosThetaLightJet", PROCESS)
        self._costheta_bl = SimpleHandle("double", src, "cosThetaEtaBeamline", PROCESS)

    def lj(self, events):
        return self._getval(events, "_costheta_lj")

    def bl(self, events):
        return self._getval(events, "_costheta_bl")

#class TriggerResults(Getter):
#    #event.getByLabel(hlt_src, trig_results);

class Event(Getter):

    class VetoLepton(Getter):
        _nmuons = SimpleHandle("int", "looseVetoMuCount", "", PROCESS)
        _nelectrons = SimpleHandle("int", "looseVetoEleCount", "", PROCESS)

        def nmuons(self, events):
            return _int(self._getval(events, "_nmuons"))

        def nelectrons(self, events):
            return _int(self._getval(events, "_nelectrons"))

    def __init__(self):
        self._met = SimpleHandle("vfloat", "patMETNTupleProducer", "Pt", PROCESS)
        self._centrality = SimpleHandle("double", "eventShapeVars", "C", PROCESS)
        self._d = SimpleHandle("double", "eventShapeVars", "D", PROCESS)
        self._circularity = SimpleHandle("double", "eventShapeVars", "circularity", PROCESS)
        self._aplanarity = SimpleHandle("double", "eventShapeVars", "aplanarity", PROCESS)
        self._isotropy = SimpleHandle("double", "eventShapeVars", "isotropy", PROCESS)
        self._thrust = SimpleHandle("double", "eventShapeVars", "thrust", PROCESS)

        self._njets = SimpleHandle("int", "goodJetCount", "", PROCESS)
        self._ntags = SimpleHandle("int", "bJetCount", "", PROCESS)

        self._nmuons = SimpleHandle("int", "muonCount", "", PROCESS)
        self._nelectrons = SimpleHandle("int", "electronCount", "", PROCESS)


        #Reco
        self.costheta = CosTheta("cosTheta")

        #Gen
        self.costheta_gen = CosTheta("cosThetaProducerTrueAll")

        self.vetolepton = self.VetoLepton()

    def met(self, events):
        """
        Returns the transverse component of the missing momentum (MET)
        """
        return self._getval(events, "_met")

    def id(self, events):
        """
        Returns the (run, lumi, event) tuple of the current event
        """
        x = events.object().event().id()
        return long(x.run()), long(x.luminosityBlock()), long(x.event())

    def c(self, events):
        """
        The centrality of the event.
        """
        return self._getval(events, "_centrality")

    def d(self, events):
        return self._getval(events, "_d")

    def circularity(self, events):
        return self._getval(events, "_circularity")

    def aplanarity(self, events):
        return self._getval(events, "_aplanarity")

    def isotropy(self, events):
        return self._getval(events, "_isotropy")

    def thrust(self, events):
        return self._getval(events, "_thrust")

    def njets(self, events):
        return _int(self._getval(events, "_njets"))

    def ntags(self, events):
        return _int(self._getval(events, "_ntags"))

    def nmuons(self, events):
        return _int(self._getval(events, "_nmuons"))

    def nelectrons(self, events):
        return _int(self._getval(events, "_nelectrons"))

    def file_index(self, events):
        return events.fileIndex()

    def file_name(self, events):
        return events._filenames[events.fileIndex()]

    def size(self, events):
        return events.size()

class Particle(Getter):
    def __init__(self, label):
        for x in ["Pt", "Eta", "Phi", "Mass"]:
            h = SimpleHandle("vfloat", label, x, PROCESS)
            setattr(self, "_"+x, h)

    def pt(self, events):
        """
        The pt of the particle.
        """
        return self._getval(events, "_Pt")

    def eta(self, events):
        """
        The eta of the particle.
        """
        return self._getval(events, "_Eta")

    def phi(self, events):
        """
        The phi of the particle.
        """
        return self._getval(events, "_Phi")

    def mass(self, events):
        """
        The mass of the particle.
        """
        return self._getval(events, "_Mass")


class Lepton(Particle):
    def __init__(self, label, mtwlabel):
        Particle.__init__(self, label)
        for x in ["relIso", "pdgId"]:
            h = SimpleHandle("vfloat", label, x, PROCESS)
            setattr(self, "_"+x, h)
        self._mtw = SimpleHandle("double", mtwlabel, "", PROCESS)

    def iso(self, events):
        """
        The relative isolation of the lepton.
        """
        return self._getval(events, "_relIso")

    def id(self, events):
        """
        The PDG-ID of the particle
        """
        return self._getval(events, "_pdgId")

    def mtw(self, events):
        """
        The transverse mass of the combined system of this particle and the MET.
        """
        return self._getval(events, "_mtw")

class Jet(Particle):
    def __init__(self, label):
        Particle.__init__(self, label)
        for x in ["partonFlavour", "deltaR", "puMva", "bDiscriminatorCSV", "bDiscriminatorTCHP", "rms"]:
            h = SimpleHandle("vfloat", label, x, PROCESS)
            setattr(self, "_"+x, h)

    def pt(self, events):
        return self._getval(events, "_Pt")

    def eta(self, events):
        return self._getval(events, "_Eta")

    def phi(self, events):
        return self._getval(events, "_Phi")

    def mass(self, events):
        return self._getval(events, "_Mass")

    def id(self, events):
        return _int(self._getval(events, "_partonFlavour"))

    def dr(self, events):
        return self._getval(events, "_deltaR")

    def pu_mvaid(self, events):
        return self._getval(events, "_puMva")

    def bd_csv(self, events):
        return self._getval(events, "_bDiscriminatorCSV")

    def bd_tchp(self, events):
        return self._getval(events, "_bDiscriminatorTCHP")

    def rms(self, events):
        return self._getval(events, "_rms")

class Muon(Lepton):
    def __init__(self):
        Lepton.__init__(self, "goodSignalMuonsNTupleProducer", "muMTW")

class Electron(Lepton):
    def __init__(self):
        Lepton.__init__(self, "goodSignalElectronsNTupleProducer", "eleMTW")

class stpol:
    class stable:
        event = Event()
        weights = Weights()
        file = File()
        class tchan:
            muon = Muon()
            electron = Electron()
            bjet = Jet("highestBTagJetNTupleProducer")
            specjet1 = Jet("lowestBTagJetNTupleProducer")
            top = Particle("recoTopNTupleProducer")

def list_methods(obj):
    """
    Prints out the public methods with their docstrings of an instance of some object.
    """
    import inspect
    print obj
    for fname, x in inspect.getmembers(obj, predicate=inspect.ismethod):
        if fname.startswith("_"):
            continue
        print fname, getattr(obj, fname).__doc__
