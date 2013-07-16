import pickle, shutil, os
import ROOT
from plots.common import cross_sections
from plots.common import cuts
import array
import random

rootfilepath = __file__.rsplit("/", 1)[0] + "/step3_latest/"

vartypes = {
	"bdiscr_bj" : "F",
	"bdiscr_lj" : "F",
	"cos_theta" : "F",
	"deltaR_bj" : "F",
	"deltaR_lj" : "F",
	"el_mva" : "F",
	"el_pt" : "F",
	"el_reliso" : "F",
	"eta_bj" : "F",
	"eta_lj" : "F",
	"met" : "F",
	"mt_mu" : "F",
	"mu_eta" : "F",
	"mu_iso" : "F",
	"mu_pt" : "F",
	"pt_bj" : "F",
	"pt_lj" : "F",
	"rms_lj" : "F",
	"top_mass" : "F",
	"el_charge" : "I",
	"el_mother_id" : "I",
	"n_eles" : "I",
	"n_jets" : "I",
	"n_muons" : "I",
	"n_tags" : "I",
	"n_vertices" : "I",
	"n_veto_ele" : "I",
	"n_veto_mu" : "I",
	"event_id" : "I",
	"lumi_id" : "I",
	"run_id" : "I"
}

def writeTObject(name, obj, directory):
	pString = pickle.dumps(obj)
	directory.WriteTObject(ROOT.TObjString(pString), name)
	
def readTObject(name, directory):
	tObj = directory.Get(name)
	pString = tObj.String().Data()
	return pickle.loads(pString)

def getSCF(channel, sample, eventcount, fraction=1.0):
	return (cross_sections.xs[sample]*cross_sections.lumi_iso[channel])/(fraction*eventcount)

class MVA_meta:
	varlist = []
	xmlstring = ""
	method_tag = "" 
	cutstring = ""


class MVA_trainer:
	treetypes = {
		'train/signal': ('Signal', ROOT.TMVA.Types.kTraining),
		'train/background': ('Background', ROOT.TMVA.Types.kTraining),
		'test/signal': ('Signal', ROOT.TMVA.Types.kTesting),
		'test/background': ('Background', ROOT.TMVA.Types.kTesting)
	}
	
	def __init__(self, fName, ofName=None, jobname="jobname"):
		"""Class that us used to set up and run a MVA trainer.
		
		fName is the input file. If ofName = False, the input file
		is "updated". Otherwise the data is copied to a new file called
		ofName and "updated" there. If ofName is None (the default), then
		the output file will be called <jobname>_<fName>.root
		
		"""
		self.jobname = jobname
		
		if ofName == False:
			ofName = fName
		else:
			if not ofName:
				ofName_dir  = os.path.dirname(fName)
				ofName_base = '{}_{}'.format(jobname,os.path.basename(fName))
				ofName = os.path.join(ofName_dir, ofName_base)
			print 'Copy from `{}` to `{}`'.format(fName, ofName)
			shutil.copyfile(fName, ofName)
		self.tfName = ofName
		print 'Output file name:', ofName
		
		self.variables = []
		self.methods = []
		
		self.tfile = ROOT.TFile(self.tfName, "UPDATE")
		self.metadata = readTObject('meta', self.tfile)
		
		self.factory = ROOT.TMVA.Factory(jobname, self.tfile)
		
		self._prepare()

	def add_variable(self, var):
		if not var in self.variables:
			self.variables.append(var)
			self.factory.AddVariable(var, vartypes[var])
	
	def get_factory(self):
		return self.factory
	
	def _prepare(self):
		initEvs = self.metadata['initial_events']
		channel = self.metadata['lept']
		
		# Load trees
		for (typekey,(kSigBg,kTrainTest)) in self.treetypes.items():
			keylist = self.tfile.Get(typekey).GetListOfKeys()
			print typekey, kSigBg, kTrainTest
			for key in keylist:
				sName = key.GetName()
				sTree = key.ReadObj()
				sScaleFactor = getSCF(channel, sName, initEvs[sName])
				# TODO: multiply scf with fraction of train/total
				print ' > ', sName, sScaleFactor
				self.factory.AddTree(sTree, kSigBg, sScaleFactor, ROOT.TCut(''), kTrainTest)

		#for var in self.variables:
		#	self.factory.AddVariable(var, vartypes[var])
		return self.factory
	
	def book_method(self, method_type, tag, options):
		if tag in self.methods:
			print "MVA_trainer: Method tagged " + tag + " already booked. Skipping."
		self.methods.append(tag)
		self.factory.BookMethod(method_type, tag, options)
	
	def evaluate(self):
		print
		print '=== Start MVA evaluation ==='
		print
		
		print 'Calling `TMVA::Factory::TestAllMethods()`'
		self.factory.TestAllMethods()
		print 'Calling `TMVA::Factory::EvaluateAllMethods()`'
		self.factory.EvaluateAllMethods()
		
		# Evaluate all MVAs for all trees
		print
		print 'Evaluate custom trees. Creating reader.'
		reader = ROOT.TMVA.Reader()
		
		print 'Adding variables...'
		varvalues = {}
		for var in self.variables:
			print ' > Var:',var, vartypes[var].lower()
			#varvalues[var] = array.array(vartypes[var].lower(), [0])
			varvalues[var] = array.array('f', [0])
			reader.AddVariable(var, varvalues[var])
		
		print 'Booking methods...'
		for mva in self.methods:
			wName = 'weights/{0}_{1}.weights.xml'.format(self.jobname,mva)
			print ' > Method:', mva, wName
			reader.BookMVA(mva, wName)
		
		print
		print 'Modifying trees...'
		for typekey in self.treetypes:
			keylist = [key.GetName() for key in self.tfile.Get(typekey).GetListOfKeys()]
			print 'Subcategory:', typekey, keylist
			for sName in keylist:
				treepath = '{0}/{1}'.format(typekey, sName)
				sTree = self.tfile.Get(treepath)
				nentries = sTree.GetEntries()
				print ' > Key: ', sName, sTree, nentries
				
				for var in self.variables:
					print ' > > Set branch variable address:', var
					sTree.SetBranchAddress(var,varvalues[var])
				
				mva_branches = {}
				discr = array.array('f', [0])
				for mva in self.methods:
					branchName = 'mva_{0}'.format(mva)
					print ' > > New branch:', mva, branchName
					mva_branches[mva] = sTree.Branch(branchName, discr, branchName+'/F')
				
				print ' > Filling..'
				for n in range(nentries):
					sTree.GetEntry(n)
					for mva in self.methods:
						discr[0] = reader.EvaluateMVA(mva)
						mva_branches[mva].Fill()
				self.tfile.cd(typekey)
				sTree.Write(sName, ROOT.TObject.kOverwrite)
	
	def pack(self):
		mvadir = self.tfile.mkdir('MVAs')
		for meth in self.methods:
			meta = MVA_meta()
			meta.varlist = self.variables
			xmlfile = open("weights/%s_"%self.jobname+meth+".weights.xml")
			meta.xmlstring = xmlfile.read()
			meta.method_tag = meth
			meta.cutstring = self.metadata['cutstring']
			pklfile = open("weights/%s_"%self.jobname+meth+".pkl", "wb")
			pickle.dump(meta, pklfile)
			pklfile.close()
			writeTObject(meth, meta, mvadir)
	
	def finish(self):
		self.tfile.Close()

def prepare_files(signals, backgrounds, ofname = "prepared.root", cutstring = str(cuts.Cuts.rms_lj*cuts.Cuts.mt_mu*cuts.Cuts.n_jets(2)*cuts.Cuts.n_tags(1)), default_ratio = 0.5, lept = "mu"):
	if not isinstance(signals, dict):
		if isinstance(signals, list):
			d = {}
			for ch in signals:
				d[ch] = default_ratio
			signals = d
		else:
			print "prepare_files: argument signals of invalid type", type(signals)
			return
	else:
		for ch in signals:
			if signals[ch] == None:
				signals[ch] = default_ratio
	
	
	if not isinstance(backgrounds, dict):
		if isinstance(backgrounds, list):
			d = {}
			for ch in backgrounds:
				d[ch] = default_ratio
			backgrounds = d
		else:
			print "prepare_files: argument backgrounds of invalid type", type(backgrounds)
			return
	else:
		for ch in backgrounds:
			if backgrounds[ch] == None:
				backgrounds[ch] = default_ratio
	
	
	ofile = ROOT.TFile(ofname, "RECREATE")
	ofile.mkdir("train/signal")
	ofile.mkdir("train/background")
	ofile.mkdir("test/signal")
	ofile.mkdir("test/background")
	
	meta = {"lept": lept, "initial_events": {}, "fractions": {}, "cutstring": cutstring}
	
	
	for ch in signals.keys() + backgrounds.keys():
		ifname = rootfilepath + lept + "/iso/nominal/" + ch + ".root"
		ifile = ROOT.TFile(ifname)
		meta["initial_events"][ch] = ifile.Get("trees/count_hist").GetBinContent(1)
		ifile.cd()
		tree = ifile.Get("trees/Events").CopyTree(cutstring)
		
		tr = array.array('i', [0])
		
		newbranch = tree.Branch("training", tr, "training/I")
		nentries = tree.GetEntries()
		
		
		ratio = signals[ch] if ch in signals else backgrounds[ch]
		meta["fractions"][ch] = ratio
		
		for n in range(nentries):
			tree.GetEntry(n)
			tr[0] = 1 if random.random() >= ratio else 0
			newbranch.Fill()
		
		ofile.cd("train/signal" if ch in signals else "train/background")
		tree_train = tree.CopyTree("(training == 1)")
		tree_train.Write(ch)
		
		ofile.cd("test/signal" if ch in signals else "test/background")
		tree_test = tree.CopyTree("(training == 0)")
		tree_test.Write(ch)
	
	ofile.cd("")
	ofile.WriteTObject(ROOT.TObjString(pickle.dumps(meta)), 'meta')
	
	ofile.Close()
	














