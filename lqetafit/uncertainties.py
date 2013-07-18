# model uncertainties
# lognormal
##model.add_lognormal_uncertainty('lumi', math.log(1.022), '*')
#model.add_lognormal_uncertainty('ttbar', math.log(1.1), 'ttbar')
#model.add_lognormal_uncertainty('wjets', math.log(2.0), 'wjets')
#model.add_lognormal_uncertainty('wjets', math.log(1.3), 'wjets') # test
#model.add_lognormal_uncertainty('zjets', math.log(1.3), 'zjets')
#model.add_lognormal_uncertainty('qcd', math.log(1.03), 'qcd')

# gaussian
##add_normal_uncertainty(model, 'qcd', 0.5, 'qcd')
#add_normal_uncertainty(model, 'qcd', 0.1, 'qcd')
#add_normal_uncertainty(model, 'ttbar', 0.1, 'ttbar')
#add_normal_uncertainty(model, 'schan', 0.1, 'schan')
#add_normal_uncertainty(model, 'twchan', 0.15, 'twchan')
#add_normal_uncertainty(model, 'wjets', 0.3, 'wjets')
#add_normal_uncertainty(model, 'zjets', 0.3, 'zjets')
#add_normal_uncertainty(model, 'diboson', 0.3, 'diboson')

# added top wzjets
# gaussian uncertainties
##add_normal_uncertainty(model, 'qcd', 0.5, 'qcd')
add_normal_uncertainty(model, 'qcd', 0.1, 'qcd')
add_normal_uncertainty(model, 'top', 0.1, 'top')
##add_normal_uncertainty(model, 'wzjets', inf, 'wzjets')
add_normal_uncertainty(model, 'wzjets', 0.3, 'wzjets')

#
##add_normal_uncertainty(model, 'wjets_heavy', inf, 'wjets_heavy')
##add_normal_uncertainty(model, 'wjets_light', 0.3, 'wjets_light')
#add_normal_uncertainty(model, 'wjets_heavy', inf, 'wjets_light')
#add_normal_uncertainty(model, 'wjets_light', 0.5, 'wjets_light')
#add_normal_uncertainty(model, 'zjets', 0.3, 'zjets')

#print sorted(model.processes)

