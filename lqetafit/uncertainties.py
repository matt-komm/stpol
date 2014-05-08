# model uncertainties
# lognormal
##model.add_lognormal_uncertainty('lumi', math.log(1.022), '*')
#model.add_lognormal_uncertainty('ttbar', math.log(1.1), 'ttbar')
#model.add_lognormal_uncertainty('wjets', math.log(2.0), 'wjets')
#model.add_lognormal_uncertainty('wjets', math.log(1.3), 'wjets') # test
#model.add_lognormal_uncertainty('zjets', math.log(1.3), 'zjets')
#model.add_lognormal_uncertainty('qcd', math.log(1.03), 'qcd')

# FIXME test
#model.add_lognormal_uncertainty('top', math.log(1.1), 'top')
#model.add_lognormal_uncertainty('wzjets', math.log(1.5), 'wzjets')
#model.add_lognormal_uncertainty('qcd', math.log(1.1), 'qcd')

# gaussian
##add_normal_uncertainty(model, 'qcd', 0.5, 'qcd')
#add_normal_uncertainty(model, 'qcd', 0.1, 'qcd')
#add_normal_uncertainty(model, 'ttbar', 0.1, 'ttbar')
#add_normal_uncertainty(model, 'schan', 0.1, 'schan')
#add_normal_uncertainty(model, 'twchan', 0.15, 'twchan')
#add_normal_uncertainty(model, 'wjets', 0.3, 'wjets')
#add_normal_uncertainty(model, 'zjets', 0.3, 'zjets')
#add_normal_uncertainty(model, 'diboson', 0.3, 'diboson')

# FIXME
# added top wzjets
# gaussian uncertainties
##add_normal_uncertainty(model, 'qcd', 0.5, 'qcd')
#add_normal_uncertainty(model, 'qcd', 0.1, 'qcd')
#add_normal_uncertainty(model, 'top', 0.3, 'top')
#add_normal_uncertainty(model, 'wzjets', inf, 'wzjets')
#add_normal_uncertainty(model, 'wzjets', 0.5, 'wzjets')

# added other wzjets
# gaussian uncertainties
add_normal_uncertainty(model, 'other', 0.2, 'other')
#add_normal_uncertainty(model, 'other', 1.0, 'other')
add_normal_uncertainty(model, 'wzjets', inf, 'wzjets')

