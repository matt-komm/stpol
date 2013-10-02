from DataFormats.FWLite import Events, Handle, Lumis
PROCESS = "STPOLSEL2"

#A placeholder for a missing value. NaN is good but not ideal.
NA = float("nan")

def is_na(x):
    return x!=x

class SimpleHandle:
    """
    A simple interface tying fwlite::Handle<T> and a 3-tuple for a label.
    """
    def __init__(self, dtype, label, instance, process):
        if dtype=="vfloat":
            self.handle = Handle("std::vector<float>")
        elif dtype=="float":
            self.handle = Handle("float")
        elif dtype=="double":
            self.handle = Handle("double")
        else:
            raise ValueError("Undefined type: %s" % dtype)
        self.label = label
        self.instance = instance
        self.process = process

    def get(self, events):
        """
        Returns the product of a handle if valid, ValueError if invalid.
        """
        events.getByLabel((self.label, self.instance, self.process), self.handle)
        if self.handle.isValid():
            return self.handle.product()
        else:
            raise ValueError("Could not get product: %s:%s:%s" % (self.label, self.instance, self.process))

class Getter(object):
    def _getval(self, events, name):
        x = getattr(self, name).get(events)
        if len(x)==1:
            return x[0]
        else:
            return NA

class Event(Getter):
    def __init__(self):
        self._met = SimpleHandle("vfloat", "patMETNTupleProducer", "Pt", PROCESS)

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

class Lepton(Getter):
    def __init__(self, label, mtwlabel):
        for x in ["Pt", "Eta", "relIso", "Phi", "pdgId"]:
            h = SimpleHandle("vfloat", label, x, "STPOLSEL2")
            setattr(self, "_"+x, h)
        self._mtw = SimpleHandle("double", mtwlabel, "", PROCESS)

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

class Muon(Lepton):
    def __init__(self):
        Lepton.__init__(self, "goodSignalMuonsNTupleProducer", "muAndMETMtW")

class Electron(Lepton):
    def __init__(self):
        Lepton.__init__(self, "goodSignalElectronsNTupleProducer", "eleAndMETMtW")

class stpol:
    class stable:
        event = Event()
        class signal:
            muon = Muon()
            electron = Electron()

def list_methods(obj):
    """
    Prints out the public methods with their docstrings of an instance of some object.
    """
    import inspect
    print obj
    for fname, x in inspect.getmembers(obj, predicate=inspect.ismethod):
        if fname.startswith("_"):
            continue
        print fname, getattr(stpol.stable.signal.muon, fname).__doc__
