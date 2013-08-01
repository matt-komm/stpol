from subprocess import call
#~ call("python ../filler.py -o filled_trees/ trained_WJets.root ../step3_latest/mu/iso/nominal/*.root", shell=True)
#~ call("python ../filler.py -o filled_trees/ trained_WJets_ttbar.root filled_trees/*.root", shell=True)
call("python ../filler.py -o filled_trees_mu/ trained_all_mu.root ../step3_latest/mu/mc/iso/nominal/Jul15/*.root", shell=True)
call("python ../filler.py -o filled_trees_mu/ trained_all_mu.root ../step3_latest/mu/data/iso/Jul15/*.root", shell=True)
