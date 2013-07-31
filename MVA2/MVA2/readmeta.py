import sys
import ROOT
import common

if len(sys.argv) < 2:
	print 'Files not given!'
	exit(1)

for fName in sys.argv[1:]:
	print 'Metadata for `{0}`'.format(fName)
	try:
		meta = common.readTObject('meta', ROOT.TFile(fName))
		print meta
	except AttributeError:
		print 'Bad root file!'
