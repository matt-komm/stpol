from subprocess import call
call("python ../filler.py -o filled_trees/ file:trained.root ../step3_latest/mu/iso/nominal/*.root", shell=True)
