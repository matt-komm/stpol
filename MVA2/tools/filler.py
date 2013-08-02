#!/usr/bin/env python
"""Script that fills calculates the MVA values for TTrees."""

import array
import pprint
import os, os.path, shutil
import ROOT; ROOT.PyConfig.IgnoreCommandLineOptions = True
import mvalib.fill
import mvalib.utils

def fill_tree(reader, tree_ifname, tree_ofname):
	if tree_ifname == tree_ofname:
		raise Exception('Input and output is the same!')
	tfile_in  = ROOT.TFile(tree_ifname)
	tfile_out = ROOT.TFile(tree_ofname, 'UPDATE')
	tree_events = tfile_in.Get('trees/Events')

	if not tfile_out.Get('trees'):
		tfile_out.mkdir('trees')
	if not tfile_out.Get('trees/MVA'):
		tfile_out.Get('trees').cd()
		tree_mva = ROOT.TTree('MVA', 'MVA')
	else:
		tree_mva = tfile_out.Get('trees/MVA')
	reader.set_trees(tree_events, tree_mva)

	reader.fill()

	tfile_out.Get('trees').cd()
	tree_mva.SetEntries()
	tree_mva.Write('', ROOT.TObject.kOverwrite)
	tfile_out.Close()
	tfile_in.Close()

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('mva', help = 'output .root of mva trainer')
	parser.add_argument('trees', nargs = '*', help = 'list of input root files')
	parser.add_argument('-o', '--odir', default='.', help = 'output dir')
	parser.add_argument('-s', '--suf', default='mva', help = 'filename suffix')
	args = parser.parse_args()

	if not os.path.isdir(args.odir):
		os.makedirs(args.odir)

	mvas = mvalib.fill.read_mvas(args.mva)
	reader = mvalib.fill.MVAReader(mvas.items()[0][1]['varlist'])

	for name,mvameta in mvas.items():
		reader.book_method(name, mvameta)

	for tree_ifname in args.trees:
		sample_name = mvalib.utils.get_sample_name(tree_ifname)
		tree_ofname = os.path.join(args.odir, '{0}_{1}.root'.format(sample_name, args.suf))
		[tree_ifname,tree_ofname] = map(os.path.abspath, [tree_ifname,tree_ofname])
		print tree_ifname,'>',tree_ofname
		fill_tree(reader, tree_ifname, tree_ofname)
