import array
import ROOT
import common, plot_ROC
import plots.common

tfiles = []

mvatfile = ROOT.TFile('the_best/trained.root', 'UPDATE')
mvameta = common.readTObject('meta', mvatfile)

temp_tfile = ROOT.TFile('temp.root', 'RECREATE')

s = {
	mvatfile.Get('test/signal/T_t_ToLeptons') : plots.common.cross_sections.xs['T_t_ToLeptons']/mvameta['initial_events']['T_t_ToLeptons'],
	mvatfile.Get('test/signal/Tbar_t_ToLeptons') : plots.common.cross_sections.xs['Tbar_t_ToLeptons']/mvameta['initial_events']['Tbar_t_ToLeptons'],
}
b = {
	mvatfile.Get('test/background/W1Jets_exclusive') : plots.common.cross_sections.xs['W1Jets_exclusive']/mvameta['initial_events']['W1Jets_exclusive'],
	mvatfile.Get('test/background/W2Jets_exclusive') : plots.common.cross_sections.xs['W2Jets_exclusive']/mvameta['initial_events']['W2Jets_exclusive'],
	mvatfile.Get('test/background/W3Jets_exclusive') : plots.common.cross_sections.xs['W3Jets_exclusive']/mvameta['initial_events']['W3Jets_exclusive'],
	mvatfile.Get('test/background/W4Jets_exclusive') : plots.common.cross_sections.xs['W4Jets_exclusive']/mvameta['initial_events']['W4Jets_exclusive'],
}

def getTreeDict(names):
	print names
	ret = {}
	for n in names:
		tfile = ROOT.TFile('best/'+n+'.root')
		tfiles.append(tfile)
		
		tree = tfile.Get('trees/Events')
		tree.Draw('>>elist', mvameta['cutstring'], 'entrylist');
		elist = ROOT.gDirectory.Get('elist');
		tree.SetEntryList(elist)
		#tree = tfile.Get('trees/Events').CopyTree(mvameta['cutstring'])
		#temp_tfile.WriteObject(tree, n)
		
		ret[tree] = common.getSCF('mu', n, tfile.Get('trees/count_hist').GetBinContent(1))
	return ret

vs = ['mva_Likelihood', 'mva_BDT', 'eta_lj']

plot_ROC.plot_ROC(s, b, vs, name='train_wjets', title='MVA ROC: signal vs test wjets')
plot_ROC.plot_ROC(s, getTreeDict(common.samples.WJets), vs, name='wjets', title='MVA ROC: signal vs all wjets')
plot_ROC.plot_ROC(s, getTreeDict(common.samples.ttbar), vs, name='ttbar', title='MVA ROC: signal vs ttbar')
#plot_ROC.plot_ROC(s, getTreeDict(common.samples.QCD), vs, name='qcd', title='MVA ROC: test signal vs qcd')
plot_ROC.plot_ROC(s, getTreeDict(common.samples.diboson), vs, name='diboson', title='MVA ROC: signal vs diboson')
plot_ROC.plot_ROC(s, getTreeDict(['DYJets'] + common.samples.GJets), vs, name='dygjets', title='MVA ROC: signal vs DYJets+GJets')
plot_ROC.plot_ROC(s, getTreeDict(['T_s', 'Tbar_s', 'T_tW', 'Tbar_tW']), vs, name='top', title='MVA ROC: signal vs T_s / T_tW')
plot_ROC.plot_ROC(s, getTreeDict(common.samples.signal), vs, name='signal', title='MVA ROC: signal vs signal')
