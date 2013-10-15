TESTFILE=http://phys.hep.kbfi.ee/~joosep/test_100ev.root

all: step3py 

testfile:
	edmFileUtil test_edm.root || curl -k $(TESTFILE) -o test_edm.root && edmFileUtil test_edm.root

step3py: testfile
	python step3.py test_edm.root


.PHONY: testfile
.PHONY: step3py
