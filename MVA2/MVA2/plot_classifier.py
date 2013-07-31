import ROOT, common
import plots.common.colors
import plots.common.legend

def getKeyList(tdir, sub=None):
	directory = tdir.Get(sub) if sub else tdir
	return [k.GetName() for k in directory.GetListOfKeys()]

class HStackCopy(ROOT.THStack):
	def __init__(self, name, title):
		super(HStackCopy,self).__init__(name, title)
		self.hists = []
	def Add(self, h):
		h = ROOT.TH1F(h)
		self.hists.append(h)
		super(HStackCopy,self).Add(h)
	def Draw(self, *args):
		super(HStackCopy,self).Draw(*args)

class SampleStack:
	def __init__(self, tdir, var, meta, histopts = (20, -1.5, 1.5)):
		self.histopts = histopts
		self.todraws = []
		
		trees = list(set(getKeyList(tdir)).intersection(set(meta['fractions'].keys())))
		print 'Using trees:',trees
		
		self.groupname = '%s_%s'%(tdir.GetMotherDir().GetName(), tdir.GetName())
		print 'Group name:', self.groupname
		
		self.hs={}
		for treename in trees:
			treename_long = '%s_%s'%(self.groupname, treename)
			print 'Treename:', treename_long
			tree = tdir.Get(treename)
			self.hs[treename]=h=ROOT.TH1F(treename_long, treename_long, *self.histopts)
			tree.Draw('%s >> %s'%(var, treename_long), '', 'goff')
			h.Sumw2()
			scf = common.getSCF(meta['lept'], treename, meta['initial_events'][treename], meta['fractions'][treename])
			h.Scale(scf)

		print 'Integral (pre):', self.integral()
		self.scale(1/self.integral())
		print 'Integral (post):', self.integral()

	def _getTHStack(self, transparent=False):
		thstack_name = '%s_thstack'%(self.groupname)
		thstack = HStackCopy(thstack_name, thstack_name)
		for k,h in self.hs.items():
			h.SetFillColor(plots.common.colors.sample_colors_same[k])
			if transparent: h.SetFillStyle(3004)
			thstack.Add(h)
		return thstack
	
	def _getTH1F(self):
		ohist_name = '%s_manstack'%(self.groupname)
		ohist = ROOT.TH1F(ohist_name, ohist_name, *self.histopts)
		for k,h in self.hs.items():
			ohist.Add(h)
		return ohist

	def scale(self, c):
		for k,h in self.hs.items():
			h.Scale(c)
	
	def integral(self):
		I = 0.0
		for k,h in self.hs.items():
			I += h.Integral('width')
		return I
	
	def draw(self, error=False, same=False, split=True, transparent=False, color=ROOT.kBlack):
		todraw = None
		drawopt = ['SAME'] if same else []
		if error:
			todraw = self._getTH1F()
			todraw.SetMarkerStyle(ROOT.kFullDotLarge)
			todraw.SetMarkerColor(color)
			drawopt.append('E1')
		elif split:
			todraw = self._getTHStack(transparent=transparent)
			drawopt.append('HIST')
		else:
			todraw = self._getTH1F()
			todraw.SetFillColor(color)
			if transparent: todraw.SetFillStyle(3004)
			drawopt.append('HIST')
		
		print 'Drawopt:', drawopt
		todraw.Draw(' '.join(drawopt))
		
		self.todraws.append(todraw)
		return todraw

'''class SamePlot:
	def __init__(self):
		self.hs = []
	def add(self, h, opt):
		self.hs.append((h, opt))
	def draw(self):
		maxval = max([h.GetMaximum() for h,opt in self.hs])
		
		h,opt = self.hs[0]
		h.SetMaximum(maxval)
		h.Draw(' '.join(opt))
		
		for h,opt in self.hs[1:]:
			h.Draw(' '.join(opt+['SAME']))'''

def plotClassifiers(fName, mva='BDT'):
	ret = {}
	ret['fName'] = fName
	ret['tfile'] = tfile = ROOT.TFile(fName)
	ret['rvs'] = []
	
	meta = common.readTObject('meta', tfile)
	print meta
	
	ret['hs_test_sig'] = SampleStack(tfile.Get('test/signal'), 'mva_%s'%mva, meta)
	ret['hs_test_bg'] = SampleStack(tfile.Get('test/background'), 'mva_%s'%mva, meta)
	ret['hs_train_sig'] = SampleStack(tfile.Get('train/signal'), 'mva_%s'%mva, meta)
	ret['hs_train_bg'] = SampleStack(tfile.Get('train/background'), 'mva_%s'%mva, meta)
	
	ret['cvs'] = ROOT.TCanvas(ret['fName'], ret['fName'], 700, 500)
	bgtr  = ret['hs_train_bg'].draw(split=True, color=ROOT.kBlue)
	sigtr = ret['hs_train_sig'].draw(split=False, same=True, transparent=True, color=ROOT.kRed)
	bgte  = ret['hs_test_bg'].draw(error=True, same=True, color=ROOT.kBlack)
	sigte = ret['hs_test_sig'].draw(error=True, same=True, color=ROOT.kRed)
	
	bgtr.SetMaximum(max([h.GetMaximum() for h in [bgtr, sigtr, bgte, sigte]]))
	
	ret['cvs'].Update()

	return ret

import sys
if __name__ == "__main__":
	if len(sys.argv) > 1:
		ret = list(map(plotClassifiers, sys.argv[1:]))
	else:
		print 'No files given!'
