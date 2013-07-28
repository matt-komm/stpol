"""Utility methods for the MVA library."""

import pickle
import ROOT
from plots.common import cross_sections

def write_TObject(name, obj, directory, overwrite=True):
	pString = pickle.dumps(obj)
	directory.WriteTObject(ROOT.TObjString(pString), name, 'Overwrite' if overwrite else '')
	
def read_TObject(name, directory):
	tObj = directory.Get(name)
	pString = tObj.String().Data()
	return pickle.loads(pString)

def scale_factor(channel, sample, eventcount, fraction=1.0):
	return (cross_sections.xs[sample]*cross_sections.lumi_iso[channel])/(fraction*eventcount)
