import argparse, glob, os, os.path, re
import ROOT
import common
#import plots.common.cross_sections
import plots.common.colors
import plots.common.cuts

parser = argparse.ArgumentParser()
parser.add_argument('dir', default='step3_latest/mu/iso/nominal', help = 'input dir')
args = parser.parse_args()

cut = '((((rms_lj < 0.025) && (mt_mu > 50)) && (n_jets == 2)) && (n_tags == 1))'
#cut = str(plots.common.cuts.Cuts.final(2, 1)); print 'Cut:', cut
var = 'mva_BDT'
histparam = (10, 0.4, 0.9)

infiles = glob.glob(os.path.join(args.dir, '*'))

def parseTree(chName, data=False):
	ret = {}
	#ret['name']  = re.search('([A-Za-z0-9_]*)\.root$', fName).group(1)
	ret['name'] = chName
	#print 'Sample:', ret['name']
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

#stack = ROOT.THStack('stack', var)
stack = common.HStack('stack', var)
for bg in bgs:
	bg['h'].SetFillColor(plots.common.colors.sample_colors_same[bg['name']])
	stack.Add(bg['h'])

cvs = ROOT.TCanvas()
stack.Draw()
dt['h'].SetMarkerStyle(ROOT.kFullDotLarge)
dt['h'].Draw('SAME E1')
