import tables
import numpy

class Jet:
    dtype=numpy.dtype([
        ("pt", numpy.float32), ("eta", numpy.float32), ("phi", numpy.float32),
        ("event_id", numpy.int32), ("lumi_id", numpy.int32), ("run_id", numpy.int32)
    ])

    def __init__(self, pt):
        self.pt = pt
        self.eta = 0.0
        self.phi = 0.0
    
        self.event_id = 0
        self.lumi_id = 0
        self.run_id = 0

    def arr(self):
        return numpy.array(
        [(
            self.pt, self.eta, self.phi,
            self.event_id, self.lumi_id, self.run_id
        )],
        dtype=self.dtype)


j = Jet(0.5)
fi = tables.openFile("tab.hdf5", "w")
jet_table = fi.createTable("/", "jets", Jet.dtype)