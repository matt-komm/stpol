import ROOT

def getCorrelationPlots(fName):
	ROOT.gStyle.SetPalette(1)
	ROOT.gStyle.SetPaintTextFormat('3g')

	ret = {}
	ret['tfile'] = ROOT.TFile(fName)
	ret['rvs'] = []

	matrices = ['CorrelationMatrixS', 'CorrelationMatrixB']
	for matrix in matrices:
		rv = {}
		rv['cnv'] = ROOT.TCanvas(
			'%s_%s)'%(fName,matrix),
			'Correlations between MVA input variables (%s::%s)'%(fName,matrix)
		)
		
		rv['hist'] = ret['tfile'].Get(matrix)
		
		rv['cnv'].SetGrid();
		rv['cnv'].SetTicks();
		rv['cnv'].SetLeftMargin  ( 0.13 );
		rv['cnv'].SetBottomMargin( 0.13 );
		rv['cnv'].SetRightMargin ( 0.15 );
		rv['cnv'].SetTopMargin   ( 0.15 );
		
		rv['hist'].SetMarkerSize( 1.5 );
		rv['hist'].SetMarkerColor( 0 );
		
		rv['hist'].Draw('colz')
		rv['hist'].Draw('textsame')
		rv['cnv'].Update()
		ret['rvs'].append(rv)
	return ret

import sys
if __name__ == "__main__":
	if len(sys.argv) > 1:
		cnvss = list(map(getCorrelationPlots, sys.argv[1:]))
		raw_input('Press enter..')
	else:
		print 'No files given!'
