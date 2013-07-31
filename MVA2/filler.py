import argparse, pickle, array, shutil, os, os.path
import ROOT
import common

parser = argparse.ArgumentParser()
parser.add_argument('mva', help = 'output .root of mva trainer')
parser.add_argument('trees', nargs = '*', help = 'list of input root files')
parser.add_argument('-o', '--odir', default='.', help = 'output dir')
parser.add_argument('-s', '--suf', default=None, help = 'filename suffix')
args = parser.parse_args()

mva_tfile = ROOT.TFile(args.mva, 'READ')
mva_meta = common.readTObject('meta', mva_tfile)
print mva_meta

method_metas = {}
for mva_name in mva_meta['mvas']:
	mva_meta_path = 'MVAs/{0}'.format(mva_name)
	method_metas[mva_name] = common.readTObject(mva_meta_path, mva_tfile)
print method_metas

discr = array.array('f', [0])
if not os.path.isdir(args.odir): os.mkdir(args.odir)

for inpfn in args.trees:
	outfn = os.path.join(args.odir, inpfn.split('/')[-1])
	if args.suf: outfn = outfn.replace('.root', '_'+args.suf+'.root')
	if inpfn != outfn:
		shutil.copyfile(inpfn, outfn)
	outf = ROOT.TFile(outfn, 'UPDATE')
	outf.cd('trees')
	tree = outf.Get('trees/Events')
	
	for method_name,meta in method_metas.items():
		reader = ROOT.TMVA.Reader()
		varvalues = {}
		print meta
		print meta.varlist
		for var in meta.varlist:
			if common.vartypes[var] == 'F':
				varvalues[var] = array.array('f', [0])
			elif common.vartypes[var] == 'I':
				varvalues[var] = array.array('i', [0])
			reader.AddVariable(var, varvalues[var])
			tree.SetBranchAddress(var,varvalues[var])
		tempxml = open('.temp.xml', 'w')
		tempxml.write(meta.xmlstring)
		tempxml.close()
		reader.BookMVA(meta.method_tag, '.temp.xml')
		
		newbranch = tree.Branch('mva_'+meta.method_tag, discr, 'mva_'+meta.method_tag+'/F')
		nentries = tree.GetEntries()
		
		for n in range(nentries):
			tree.GetEntry(n)
			discr[0] = reader.EvaluateMVA(meta.method_tag)
			newbranch.Fill()
		
		tree.Write('', ROOT.TObject.kOverwrite)
	
	outf.Close()
