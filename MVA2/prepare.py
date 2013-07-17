import common

import sys
if __name__ == "__main__":
	if len(sys.argv) < 2:
		print 'Argument needed: wjets, noqcd, withqcd'
		exit(1)
	
	if sys.argv[1] == 'wjets':
		print 'Prepping only WJets...'
		common.prepare_files(common.samples.signal, common.samples.WJets,           ofname='mvaprep_wjets.root')
	elif sys.argv[1] == 'noqcd':
		print 'Prepping all except QCD...'
		common.prepare_files(common.samples.signal, common.samples.WJets+common.samples.other,     ofname='mvaprep_noqcd.root')
	elif sys.argv[1] == 'withqcd':
		print 'Prepping all with QCD...'
		common.prepare_files(common.samples.signal, common.samples.WJets+common.samples.other+common.samples.QCD, ofname='mvaprep_allqcd.root')
	else:
		print 'Bad argument %s (needs: wjets, noqcd, withqcd)'%sys.argv[1]
		exit(1)
