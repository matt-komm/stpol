import argparse, glob, sys, os, os.path, re
import ROOT
import common
import plots.common.colors, plots.common.cuts

parser = argparse.ArgumentParser()
parser.add_argument('dir', default='step3_latest/mu/iso/nominal', help = 'input dir')
parser.add_argument('-v', '--var', default='costheta', help = 'plot variable (costheta, bdt)')
args = parser.parse_args()

# Default plot = costheta
if args.var=='costheta':
	var = 'cos_theta'
	cut = str(plots.common.cuts.Cuts.final(2, 1))
	histparam = (20, -1, 1)
elif args.var=='bdt':
	cut = '((((rms_lj < 0.025) && (mt_mu > 50)) && (n_jets == 2)) && (n_tags == 1))'
	var = 'mva_BDT'
	histparam = (10, 0.4, 0.9)
else:
	print 'Bad --var: (%s)'%args.var
	exit(1)

print 'Var:', var
print 'Cut:', cut
print 'Hpa:', histparam

infiles = glob.glob(os.path.join(args.dir, '*'))

def parseTree(chName, data=False):
	print 'Sample:', chName
	
	ret = {}
	ret['name'] = chName
	ret['fName'] = os.path.join(args.dir, chName+'.root')
	ret['tfile'] = ROOT.TFile(ret['fName'])
	ret['tree'] = ret['tfile'].Get('trees/Events')
	
	ret['init_evs'] = ret['tfile'].Get("trees/count_hist").GetBinContent(1)
	
	ret['h'] = ROOT.TH1D(ret['name'], ret['name'], *histparam)
	ret['tree'].Draw('{0} >> {1}'.format(var, ret['name']), cut, 'goff')
	if not data:
		ret['h'].Scale(common.getSCF('mu', ret['name'], ret['init_evs']))
	
	return ret

bgnames = common.samples.signal + common.samples.WJets + common.samples.other
print 'Backgrounds:', bgnames
bgs = map(parseTree, bgnames)
dt = parseTree('SingleMu', data=True)

stack = common.HStack('stack', var)
for bg in bgs:
	bg['h'].SetFillColor(plots.common.colors.sample_colors_same[bg['name']])
	stack.Add(bg['h'])

maxval = max(dt['h'].GetMaximum(), stack.GetMaximum())
stack.SetMaximum(maxval)

cvs = ROOT.TCanvas()
stack.Draw()
dt['h'].SetMarkerStyle(ROOT.kFullDotLarge)
dt['h'].Draw('SAME E1')
