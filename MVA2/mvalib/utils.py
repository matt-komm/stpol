"""Utility methods for the MVA library."""

import os.path
import pickle
import ROOT
from plots.common import cross_sections

def write_TObject(name, obj, directory, overwrite=True):
	"""Pickle the object `obj` and write it to a ROOT directory."""
	pString = pickle.dumps(obj)
	directory.WriteTObject(ROOT.TObjString(pString), name, 'Overwrite' if overwrite else '')


def read_TObject(name, directory):
	"""Read a pickled object from a ROOT file."""
	tObj = directory.Get(name)
	pString = tObj.String().Data()
	return pickle.loads(pString)


def scale_factor(channel, sample, eventcount, fraction=1.0):
	"""Calculate the scalefactor to scale MC to luminosity."""
	return (cross_sections.xs[sample]*cross_sections.lumi_iso[channel])/(fraction*eventcount)


def iter_entrylist(elist):
	"""Create an iterator that iterates over TEntryList elements."""
	for n in xrange(0, elist.GetN()):
		yield elist.GetEntry(n)


def get_sample_name(fullpath):
	"""Reduce a path of a ROOT file to the sample name"""
	return '.'.join(os.path.basename(fullpath).split('.')[:-1])
