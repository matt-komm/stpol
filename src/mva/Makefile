
all: train_csvm train_csvt

train_csvm:
	python train.py input/csvm stpol_csvm

train_csvt:
	python train.py input/csvt stpol_csvt

addvars: train_csvm train_csvt
