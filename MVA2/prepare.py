import common

signal  = {"T_t_ToLeptons": 0.5, "Tbar_t_ToLeptons": 0.4}

WJets   = ['W1Jets_exclusive', 'W2Jets_exclusive', 'W3Jets_exclusive', 'W4Jets_exclusive']

top     = ['TTJets_FullLept', 'TTJets_MassiveBinDECAY', 'TTJets_SemiLept', 'T_s', 'Tbar_s', 'T_tW', 'Tbar_tW'] # T/Tbar_t ?
diboson = ['WW', 'WZ', 'ZZ']
GJets   = ['GJets1','GJets2']
other   = ['DYJets'] + GJets + diboson + top

QCD     = ['QCDMu', 'QCD_Pt_170_250_BCtoE', 'QCD_Pt_170_250_EMEnriched', 'QCD_Pt_20_30_BCtoE', 'QCD_Pt_20_30_EMEnriched', 'QCD_Pt_250_350_BCtoE', 'QCD_Pt_250_350_EMEnriched', 'QCD_Pt_30_80_BCtoE', 'QCD_Pt_30_80_EMEnriched', 'QCD_Pt_350_BCtoE', 'QCD_Pt_350_EMEnriched', 'QCD_Pt_80_170_BCtoE', 'QCD_Pt_80_170_EMEnriched']

import sys
if __name__ == "__main__":
	if len(sys.argv) < 2:
		print 'Argument needed: wjets, noqcd, withqcd'
		exit(1)
	
	if sys.argv[1] == 'wjets':
		print 'Prepping only WJets...'
		common.prepare_files(signal, WJets,           ofname='mvaprep_wjets.root')
	elif sys.argv[1] == 'noqcd':
		print 'Prepping all except QCD...'
		common.prepare_files(signal, WJets+other,     ofname='mvaprep_noqcd.root')
	elif sys.argv[1] == 'withqcd':
		print 'Prepping all with QCD...'
		common.prepare_files(signal, WJets+other+QCD, ofname='mvaprep_allqcd.root')
	else:
		print 'Bad argument %s (needs: wjets, noqcd, withqcd)'%sys.argv[1]
		exit(1)
