"""Classes and functions that are used to set up and train MVAs."""
__all__ = ['MVATrainer', 'mvatypes']

import os
import shutil
import array
import pickle
import ROOT
import mvalib.utils

mvatypes = ROOT.TMVA.Types

_vartypes = {
	'C' : 'C/F',
	'D' : 'D/F',
	'SF_total' : 'SF_total/F',
	'aplanarity' : 'aplanarity/F',
	'b_weight_nominal' : 'b_weight_nominal/F',
	'b_weight_nominal_BCdown' : 'b_weight_nominal_BCdown/F',
	'b_weight_nominal_BCup' : 'b_weight_nominal_BCup/F',
	'b_weight_nominal_Ldown' : 'b_weight_nominal_Ldown/F',
	'b_weight_nominal_Lup' : 'b_weight_nominal_Lup/F',
	'bdiscr_bj' : 'bdiscr_bj/F',
	'bdiscr_lj' : 'bdiscr_lj/F',
	'cos_theta' : 'cos_theta/F',
	'deltaR_bj' : 'deltaR_bj/F',
	'deltaR_lj' : 'deltaR_lj/F',
	'el_eta' : 'el_eta/F',
	'el_iso' : 'el_iso/F',
	'el_mva' : 'el_mva/F',
	'el_phi' : 'el_phi/F',
	'el_pt' : 'el_pt/F',
	'electron_IDWeight' : 'electron_IDWeight/F',
	'electron_IDWeight_down' : 'electron_IDWeight_down/F',
	'electron_IDWeight_up' : 'electron_IDWeight_up/F',
	'electron_TriggerWeight' : 'electron_TriggerWeight/F',
	'electron_TriggerWeight_down' : 'electron_TriggerWeight_down/F',
	'electron_TriggerWeight_up' : 'electron_TriggerWeight_up/F',
	'eta_bj' : 'eta_bj/F',
	'eta_lj' : 'eta_lj/F',
	'gen_weight' : 'gen_weight/F',
	'mass_bj' : 'mass_bj/F',
	'mass_lj' : 'mass_lj/F',
	'met' : 'met/F',
	'mt_el' : 'mt_el/F',
	'mt_mu' : 'mt_mu/F',
	'mu_chi2' : 'mu_chi2/F',
	'mu_db' : 'mu_db/F',
	'mu_dz' : 'mu_dz/F',
	'mu_eta' : 'mu_eta/F',
	'mu_iso' : 'mu_iso/F',
	'mu_phi' : 'mu_phi/F',
	'mu_pt' : 'mu_pt/F',
	'muon_IDWeight' : 'muon_IDWeight/F',
	'muon_IDWeight_down' : 'muon_IDWeight_down/F',
	'muon_IDWeight_up' : 'muon_IDWeight_up/F',
	'muon_IsoWeight' : 'muon_IsoWeight/F',
	'muon_IsoWeight_down' : 'muon_IsoWeight_down/F',
	'muon_IsoWeight_up' : 'muon_IsoWeight_up/F',
	'muon_TriggerWeight' : 'muon_TriggerWeight/F',
	'muon_TriggerWeight_down' : 'muon_TriggerWeight_down/F',
	'muon_TriggerWeight_up' : 'muon_TriggerWeight_up/F',
	'phi_bj' : 'phi_bj/F',
	'phi_lj' : 'phi_lj/F',
	'phi_met' : 'phi_met/F',
	'pt_bj' : 'pt_bj/F',
	'pt_lj' : 'pt_lj/F',
	'pu_bj' : 'pu_bj/F',
	'pu_lj' : 'pu_lj/F',
	'pu_weight' : 'pu_weight/F',
	'rms_lj' : 'rms_lj/F',
	'sphericity' : 'sphericity/F',
	'sphericity_withNu' : 'sphericity_withNu/F',
	'top_mass' : 'top_mass/F',
	'true_cos_theta' : 'true_cos_theta/F',
	'ttbar_weight' : 'ttbar_weight/F',
	'HLT_Ele27_WP80_v10' : 'HLT_Ele27_WP80_v10/I',
	'HLT_Ele27_WP80_v11' : 'HLT_Ele27_WP80_v11/I',
	'HLT_Ele27_WP80_v8' : 'HLT_Ele27_WP80_v8/I',
	'HLT_Ele27_WP80_v9' : 'HLT_Ele27_WP80_v9/I',
	'HLT_IsoMu24_eta2p1_v11' : 'HLT_IsoMu24_eta2p1_v11/I',
	'HLT_IsoMu24_eta2p1_v12' : 'HLT_IsoMu24_eta2p1_v12/I',
	'HLT_IsoMu24_eta2p1_v13' : 'HLT_IsoMu24_eta2p1_v13/I',
	'HLT_IsoMu24_eta2p1_v14' : 'HLT_IsoMu24_eta2p1_v14/I',
	'HLT_IsoMu24_eta2p1_v15' : 'HLT_IsoMu24_eta2p1_v15/I',
	'HLT_IsoMu24_eta2p1_v16' : 'HLT_IsoMu24_eta2p1_v16/I',
	'HLT_IsoMu24_eta2p1_v17' : 'HLT_IsoMu24_eta2p1_v17/I',
	'el_charge' : 'el_charge/I',
	'el_mother_id' : 'el_mother_id/I',
	'el_trigger_match' : 'el_trigger_match/I',
	'gen_flavour_bj' : 'gen_flavour_bj/I',
	'gen_flavour_lj' : 'gen_flavour_lj/I',
	'mu_charge' : 'mu_charge/I',
	'mu_gtrack' : 'mu_gtrack/I',
	'mu_itrack' : 'mu_itrack/I',
	'mu_layers' : 'mu_layers/I',
	'mu_mother_id' : 'mu_mother_id/I',
	'mu_stations' : 'mu_stations/I',
	'mu_trigger_match' : 'mu_trigger_match/I',
	'n_eles' : 'n_eles/I',
	'n_jets' : 'n_jets/I',
	'n_muons' : 'n_muons/I',
	'n_tags' : 'n_tags/I',
	'n_vertices' : 'n_vertices/I',
	'n_veto_ele' : 'n_veto_ele/I',
	'n_veto_mu' : 'n_veto_mu/I',
	'true_lepton_pdgId' : 'true_lepton_pdgId/I',
	'wjets_classification' : 'wjets_classification/I',
	'event_id' : 'event_id/I',
	'lumi_id' : 'lumi_id/I',
	'run_id' : 'run_id/I',
}

_treetypes = {
	'train/signal': ('Signal', mvatypes.kTraining),
	'train/background': ('Background', mvatypes.kTraining),
	'test/signal': ('Signal', mvatypes.kTesting),
	'test/background': ('Background', mvatypes.kTesting)
}

# ================================
# Public API classes and functions
# ================================

class MVATrainer:
	"""Factory type class used to conveniently train MVAs.
	
	It sets up a TMVA::Factory, trains the trees and then outputs the files.
	It also adds some stuff the default ROOT file produced by the TMVA::Factory.
	
	"""
	def __init__(self, fName, ofName=None, jobname='jobname'):
		"""Initialize the MVATrainer with some basic parameters.

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
				ofName_base = '{0}_{1}'.format(jobname,os.path.basename(fName))
				ofName = os.path.join(ofName_dir, ofName_base)
			print 'Copy from `{0}` to `{1}`'.format(fName, ofName)
			shutil.copyfile(fName, ofName)
		self.tfName = ofName
		print 'Output file name:', ofName

		self.variables = []
		self.methods = []

		self.tfile = ROOT.TFile(self.tfName, 'UPDATE')
		self.metadata = mvalib.utils.read_TObject('meta', self.tfile)

		self.factory = ROOT.TMVA.Factory(jobname, self.tfile)

		self._prepare()

	def add_variable(self, var):
		"""Add a variable that is used for training."""
		if not var in self.variables:
			self.variables.append(var)
			self.factory.AddVariable(var, _vartypes[var])

	def get_factory(self):
		"""Returns the TMVA::Factory object."""
		return self.factory

	def _prepare(self):
		"""Loads trees to the TMVA::Factory (used by __init__)."""
		initEvs = self.metadata['initial_events']
		channel = self.metadata['channel']
		fract = self.metadata['fractions']

		# Load trees
		for (typekey,(kSigBg,kTrainTest)) in _treetypes.items():
			keylist = self.tfile.Get(typekey).GetListOfKeys()
			print typekey, kSigBg, kTrainTest
			for key in keylist:
				sName = key.GetName()
				sTree = key.ReadObj()
				if sTree.GetEntries() == 0:
					continue
				actual_fraction = fract[sName] if kTrainTest==mvatypes.kTraining else (1-fract[sName])
				sScaleFactor = mvalib.utils.scale_factor(channel, sName, initEvs[sName]) / actual_fraction
				print ' > ', sName, sScaleFactor
				self.factory.AddTree(sTree, kSigBg, sScaleFactor, ROOT.TCut(''), kTrainTest)

		return self.factory

	def book_method(self, method_type, tag, options):
		"""Book a method for training by calling the TMVA::Factory.BookMethod()."""
		if tag in self.methods:
			print 'MVA_trainer: Method tagged ' + tag + ' already booked. Skipping.'
		self.methods.append(tag)
		self.factory.BookMethod(method_type, tag, options)

	def evaluate(self):
		"""Test and evaluate the MVA."""
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
			print ' > Var:',var, _vartypes[var].lower()
			#varvalues[var] = array.array(_vartypes[var].lower(), [0])
			varvalues[var] = array.array('f', [0])
			reader.AddVariable(var, varvalues[var])

		print 'Booking methods...'
		for mva in self.methods:
			wName = 'weights/{0}_{1}.weights.xml'.format(self.jobname,mva)
			print ' > Method:', mva, wName
			reader.BookMVA(mva, wName)

		print
		print 'Modifying trees...'
		for typekey in _treetypes:
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
		"""Store all custom metadata etc."""
		self.metadata['mvas'] = self.methods
		mvalib.utils.write_TObject('meta', self.metadata, self.tfile)

		mvadir = self.tfile.mkdir('MVAs')
		for meth in self.methods:
			meta = {}
			meta['varlist'] = self.variables
			meta['method_tag'] = meth
			meta['cutstring'] = self.metadata['cutstring']
			
			xmlfile = open('weights/%s_'%self.jobname+meth+'.weights.xml')
			meta['xmlstring'] = xmlfile.read()

			pklfile = open('weights/%s_'%self.jobname+meth+'.pkl', 'wb')
			pickle.dump(meta, pklfile)
			pklfile.close()
			
			mvalib.utils.write_TObject(meth, meta, mvadir)

	def finish(self):
		"""Close up any loose ends (e.g. close files)."""
		self.tfile.Close()
