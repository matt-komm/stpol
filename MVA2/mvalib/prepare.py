"""Utilities that are used to prepare step3 datasets for MVA."""
__all__ = ['prepare']

import os
import os.path
import shutil
from glob import glob
import array
import random
import ROOT
from plots.common import cuts
import mvalib.utils

_default_cutstring = str(cuts.Cuts.rms_lj*cuts.Cuts.mt_mu*cuts.Cuts.n_jets(2)*cuts.Cuts.n_tags(1))

# ============================
# Public prepare API functions
# ============================

def prepare(signals, backgrounds, step3_path='step3_latest', odir='prepared',
            default_ratio=0.5, prep_step3=False, cutstring=_default_cutstring,
            channels=['mu', 'ele'], datatypes=['data', 'mc']):
	"""Prepares the output files from step3 for usage in the MVA.

	Takes a list of names for signals and backgrounds. They can be either a
	list or a dictionary and in the case of the latter it is expected that
	the keys are the names of the samples and the values are the fraction
	of the sampled used for training. If it is not specified the default_ratio
	is used.

	The function looks for the step3 samples in the step3_path and creates
	a new directory `odir` where the output is stored. If prep_step3 is True
	then all the trees are symlinked to the odir (retaining the directory
	structure of the step3). In addition to that, trees `<sample>_mva.root`
	are created that contain the `mva_training_weight` branch, which can be
	used to exclude training events from plotting (`mva_training_weight` is
	0.0 for training events, weighted appropriately for testing events and
	1.0 for events that do not pass the cut used to choose training events.

	"""
	step3_path = os.path.abspath(step3_path)
	if not os.path.isdir(odir):
		os.makedirs(odir)

	signals = _check_default_ratios(signals, default_ratio)
	backgrounds = _check_default_ratios(backgrounds, default_ratio)
	signal_and_bg = dict(signals.items()+backgrounds.items())

	for channel in channels:
		ofname = os.path.join(odir, 'mvaprep_{0}.root'.format(channel))
		print 'Prepping channel `{0}` to `{1}`'.format(channel, ofname)
		tfile = ROOT.TFile(ofname, 'RECREATE')

		meta = {
			'lept': channel, 'ch': channel, 'channel': channel,
			'cutstring': cutstring,
			'initial_events': {}, 'fractions': {}
		}

		_dir = tfile.mkdir('train')
		_dir.mkdir('signal'); _dir.mkdir('background')
		_dir = tfile.mkdir('test')
		_dir.mkdir('signal'); _dir.mkdir("background")

		for datatype in datatypes:
			path, samples = _find_files(step3_path, channel, datatype)
			if prep_step3 and not os.path.isdir(os.path.join(odir, path)):
				os.makedirs(os.path.join(odir, path))

			for s in samples:
				sample_ifname = os.path.join(step3_path, path, '{0}.root'.format(s))
				print '> sample `{0}` from `{1}`'.format(s, sample_ifname)
				if prep_step3:
					sample_ofname = os.path.join(odir, path, '{0}.root'.format(s))
					os.symlink(sample_ifname, sample_ofname)
				if s in signal_and_bg:
					sigbg = 'signal' if s in signals else 'background'
					fraction = signal_and_bg[s]

					tfile_sample = ROOT.TFile(sample_ifname)
					count_hist = tfile_sample.Get('trees/count_hist')
					meta['initial_events'][s] = count_hist.GetBinContent(1)
					meta['fractions'][s] = fraction

					tc = _TrainTreeCreator(tfile_sample.Get('trees/Events'),
					                       cutstring, fraction)

					tdir = tfile.Get('{0}/{1}'.format('train', sigbg))
					tc.write_train_tree(tdir, name=s)
					tdir = tfile.Get('{0}/{1}'.format('test', sigbg))
					tc.write_test_tree(tdir, name=s)

					if prep_step3:
						sample_ofname = os.path.join(odir, path, '{0}_mva.root'.format(s))
						tfile_sample_of = ROOT.TFile(sample_ofname, 'RECREATE')
						tdir = tfile_sample_of.mkdir('trees')
						tc.write_weight_tree(tdir)
						tdir.cd()
						tfile_sample_of.Close()

					del tc
					tfile_sample.Close()
		tfile.Close()


# =========================
# Internal helper functions
# =========================

def _check_default_ratios(samples, ratio):
	"""Checks if samples are a list, converts to dict and set to ratio."""
	if isinstance(samples, dict):
		return samples
	if isinstance(samples, list):
		return dict(map(lambda s: (s, ratio), samples))
	else:
		raise Exception('Bad type for samples `{0}`'.format(type(samples)))


def _find_files(root, channel, datatype):
	"""Finds the root files for the specified type of data."""
	_datatype_paths = {
		'mc': 'mc/iso/nominal/Jul15',
		'data': 'data/iso/Jul15'
	}

	if not channel in ['mu', 'ele']:
		raise Exception('Bad channel `{0}`'.format(channel))
	if not datatype in _datatype_paths:
		raise Exception('Bad datatype `{0}`'.format(datatype))

	path = os.path.join(root, channel, _datatype_paths[datatype])
	samples = map(_get_sample_name, glob(os.path.join(path, '*')))
	return os.path.join(channel, _datatype_paths[datatype]), samples


def _get_sample_name(fullpath):
	"""Reduce a path to a ROOT file to the sample name"""
	return '.'.join(os.path.basename(fullpath).split('.')[:-1])


class _TrainTreeCreator:
	"""Helper class that is used to create and write the training trees."""
	def __init__(self, tree, cutstring, fraction):
		self.tree = tree

		self.elist_all = ROOT.TEntryList('elist_all', '')
		self.elist_cut = ROOT.TEntryList('elist_cut', '')
		self.elist_invcut = ROOT.TEntryList('elist_invcut', '')

		self.tree.Draw('>>elist_all', '', 'entrylist')
		self.tree.Draw('>>elist_cut', cutstring, 'entrylist')
		self.elist_invcut.Add(self.elist_all)
		self.elist_invcut.Subtract(self.elist_cut)

		evids_cutall = list(mvalib.utils.iter_entrylist(self.elist_cut))
		evids_invcut = list(mvalib.utils.iter_entrylist(self.elist_invcut))
		random.shuffle(evids_cutall)
		N_train = int(fraction*len(evids_cutall))
		#print 'N_train:', N_train
		evids_train = evids_cutall[:N_train]
		evids_test  = evids_cutall[N_train:]
		
		self.elist_train = ROOT.TEntryList('elist_train', '')
		self.elist_test  = ROOT.TEntryList('elist_test', '')
		map(self.elist_train.Enter, evids_train)
		map(self.elist_test.Enter, evids_test)

		try:
			weight = float(len(evids_cutall))/float((len(evids_cutall)-N_train))
			print 'Weight:', weight
		except ZeroDivisionError as e:
			print 'Warning: ZeroDivisionError', e
			print 'len(evids_cutall):', len(evids_cutall)
			print 'N_train:', N_train
			weight = 0

		weights_test   = list(map(lambda n:(n,0.0), evids_test))
		weights_train  = list(map(lambda n:(n,weight), evids_train))
		weights_invcut = list(map(lambda n:(n,1.0), evids_invcut))
		self.weights = sorted(weights_test+weights_train+weights_invcut)

	def write_weight_tree(self, tdir, treename='mva'):
		tdir.cd()
		otree = ROOT.TTree(treename, treename)
		var_w = array.array('f', [0])
		br = otree.Branch('mva_training_weight', var_w, 'mva_training_weight/F')

		for n,var_w[0] in self.weights:
			otree.Fill()
		otree.Write()

	def write_train_tree(self, tdir, name='Events'):
		self._write_tree(tdir, self.elist_train, name)

	def write_test_tree(self, tdir, name='Events'):
		self._write_tree(tdir, self.elist_test, name)

	def _write_tree(self, tdir, elist, name):
		print 'Writing to `{0}`'.format(tdir)
		self.tree.SetEntryList(elist)
		tdir.cd()
		otree=self.tree.CopyTree('')
		otree.Write(name)
		print 'Events written:',otree.GetEntries()

# Unit testing...
if __name__ == '__main__':
	print 'Default cutstring:', _default_cutstring

	print _find_files('step3_latest', 'mu', 'mc')
	print _find_files('step3_latest', 'ele', 'data')

	try: _find_files('step3_latest', 'tau', 'mc')
	except Exception as e: print e

	try: _find_files('step3_latest', 'mu', 'fake')
	except Exception as e: print e

	_check_default_ratios({'a':2, 'b':3}, 0.3)
	_check_default_ratios(['a','b'], 9000)
	try: _check_default_ratios('Woot?', 1337)
	except Exception as e: print e

	shutil.rmtree('prep_unit', ignore_errors=True)
	prepare(['T_t_ToLeptons', 'Tbar_t_ToLeptons'], ['WW', 'WZ', 'ZZ'],
	        odir='prep_unit', prep_step3=True)
