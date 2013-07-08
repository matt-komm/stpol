#!/usr/bin/python
import ROOT

bgs = [
	{'ch': 'bg_uno', 'fr': 0.6},
	{'ch': 'bg_dos', 'fr': 0.4}
]
sig = {'ch': 'signal', 'fr': 1.2}

datasets = bgs + [sig]
for dt in datasets:
	dt['tfile'] = ROOT.TFile('%s.root'%dt['ch'])
	dt['tree'] = dt['tfile'].Get("trees/Events")

fout = ROOT.TFile('output.root', 'RECREATE')
fac = ROOT.TMVA.Factory('jobname', fout)

fac.AddSignalTree(sig['tree'], sig['fr'])
for bg in bgs:
	fac.AddBackgroundTree(bg['tree'], bg['fr'])

fac.AddVariable('x', 'F')
fac.AddVariable('y', 'F')

cutstring = 'x>1'
#fac.PrepareTrainingAndTestTree(ROOT.TCut(cutstring), '');

fac.BookMethod(ROOT.TMVA.Types.kLikelihood, 'LikelihoodD', '!H:!V:!TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmooth=5:NAvEvtPerBin=50:VarTransform=Decorrelate');

fac.TrainAllMethods()
fac.TestAllMethods()
fac.EvaluateAllMethods()
