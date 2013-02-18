import ROOT
import string

def th_sep(i, sep=','):
	"""Return a string representation of i with thousand separators"""
	i = abs(int(i))
	if i == 0:
		return '0'
	o = []
	while i > 0:
		o.append(i%1000)
		i /= 1000
	o.reverse()
	return str(sep).join([str(o[0])] + map(lambda x: '%03d'%x, o[1:]))

def filter_alnum(s):
	"""Filter out everything except ascii letters and digits"""
	return filter(lambda x: x in string.ascii_letters+string.digits, s)

# Class to handle (concatenate) cuts
class Cut:
	def __init__(self, cutName, cutStr):
		self.cutName = cutName
		self.cutStr = cutStr
		#self.cutSequence = [copy.deepcopy(self)]

	def __mul__(self, other):
		cutName = self.cutName + " & " + other.cutName
		cutStr = '('+self.cutStr+') && ('+other.cutStr+')'
		newCut = Cut(cutName, cutStr)
		#newCut.cutSequence = self.cutSequence + other.cutSequence
		return newCut

	def __add__(self, other):
		cutName = self.cutName + " | " + other.cutName
		cutStr = '('+self.cutStr+') || ('+other.cutStr+')'
		newCut = Cut(cutName, cutStr)
		#newCut.cutSequence = self.cutSequence + other.cutSequence
		return newCut

	def __str__(self):
		return self.cutName + ":" + self.cutStr

	def __repr__(self):
		return self.cutName

# Data and MC samples are handled by the following classes:
class Sample(object):
	"""Class representing a single sample.

	This class read the TTrees from a .root file and provide easy access
	to them. It uses TTree.AddFriend() to create a single TTree object
	(Sample.tree) that can be used to access all variables in the .root
	file.

	"""
	def __init__(self, fname, name=None, directory=None):
		self.fname = fname
		self.directory = directory
		self.name = name

		self._openTree()

	def __repr__(self):
		return self.fname

	def _openTree(self):
		fpath = (self.directory+'/' if self.directory is not None else '') + self.fname
		print 'Opening file: `%s`'%(fpath)
		self.tfile = ROOT.TFile(fpath)
		self.branches = []
		if self.tfile.IsZombie():
			raise IOError('Error: file `%s` not found!'%fpath)

		# We'll load all the trees
		keys = [x.GetName() for x in self.tfile.GetListOfKeys()]
		tree_names = filter(lambda x: x.startswith("trees"), keys)
		trees = [self.tfile.Get(k).Get("eventTree") for k in tree_names]
		self.branches += [br.GetName() for br in trees[0].GetListOfBranches()]
		for t in trees[1:]:
			trees[0].AddFriend(t)
			self.branches += [br.GetName() for br in t.GetListOfBranches()]
		self.tree = trees[0]

	def getTotalEvents(self):
		return self.tfile.Get('efficiencyAnalyzerMu').Get('muPath').GetBinContent(1)

class MCSample(Sample):
	"""Sample with a cross section."""
	def __init__(self, fname, xs, name=None, directory=None):
		super(MCSample,self).__init__(fname, name=name, directory=directory)
		self.xs = xs

class DataSample(Sample):
	"""Sample with a corresponding luminosity"""
	def __init__(self, fname, lumi, name=None, directory=None):
		super(DataSample,self).__init__(fname, name=name if name is not None else fname, directory=directory)
		self.luminosity = lumi

# Group of samples with the same color and label
class SampleGroup:
	"""Group of samples with the same color and label

	Useful to, for example, group samples in a stacked histogram.

	"""
	def __init__(self, name, color):
		self.name = name
		self.color = color

		self.samples = [] # initially there are no samples

	def add(self, s):
		self.samples.append(s)

	def getName(self):
		return self.name

	def getLabel(self):
		return self.name

	def getColor(self):
		return self.color

class SampleList:
	"""List of all sample groups"""
	def __init__(self):
		self.groups = {} # initially there are no sample groups

	def addGroup(self, g):
		self.groups[g.getName()] = g

	#def addSample(self, gn, s):
	#	self.groups[gn].add(s)

	def listSamples(self):
		for gk in self.groups:
			print gk
			g = self.groups[gk]
			for s in g.samples:
				print '> ', s

# Plot parameters
class PlotParams(object):
	"""Class that holds the information of what and how to plot."""
	def __init__(self, var, r, bins=20, name=None):
		self.var = var
		self.r = r; self.hmin = r[0]; self.hmax = r[1]
		self.bins=bins; self.hbins = bins

		self._name = name if name is not None else filter_alnum(var)

	def __repr__(self):
		return self.var

	def getName(self):
		#return filter_alnum(self._name)
		return self._name
