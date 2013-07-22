signal = 'tchan'

current_syst = ''
#systematics = ['unclusen','en','res']
#systematics = ['mass','scale','unclusen','en']
# res up not working
systematics = ['en','unclusen', 'mass','top_scale','tchan_scale','matching']

def add_normal_uncertainty(model, u_name, rel_uncertainty, procname, obsname='*'):
    found_match = False
    par_name = u_name
    if par_name not in model.distribution.get_parameters():
        model.distribution.set_distribution(par_name, 'gauss', mean = 1.0, width = rel_uncertainty, range = [0.0, float("inf")])
    else:
        raise RuntimeError, "parameter name already used"
    for o in model.get_observables():
        if obsname != '*' and o!=obsname: continue
        for p in model.get_processes(o):
            if procname != '*' and procname != p: continue
            model.get_coeff(o,p).add_factor('id', parameter = par_name)
            found_match = True
    if not found_match: raise RuntimeError, 'did not find obname, procname = %s, %s' % (obsname, procname)

def norm_shape(model, process, syst):
    for o in model.observables:
        for p in model.get_processes(o):
            if not process in p: continue
            hf = model.get_histogram_function(o, p)
        nom = hf.get_nominal_histo().get_value_sum()
        hplus = hf.get_plus_histo(syst)
        hminus = hf.get_minus_histo(syst)
        hplus = hplus.scale(nom / hplus.get_value_sum())
        hminus = hminus.scale(nom / hminus.get_value_sum())
        #print nom
        #print hplus.get_value_sum()
        #print hminus.get_value_sum()
        hf.set_syst_histos(syst, hplus, hminus)

def histofilter(s):
    if s.count('__') == 3:
        chan, proc, syst, dir = s.split('__')
        if not current_syst == syst:
            return False
    return True

def get_model():
    model = build_model_from_rootfile('histos/lqeta.root', include_mc_uncertainties = False, histogram_filter = histofilter)
    # FIXME Using pseudo data
    #model = build_model_from_rootfile('histos/pseudo_data.root', include_mc_uncertainties = False, histogram_filter = histofilter)
    model.fill_histogram_zerobins()
    model.set_signal_processes(signal)
    return model


for syst in systematics:
    current_syst = syst
    print 'Checking systematics for', current_syst

    model = get_model()

    #print 'Processes:', sorted(model.processes)
    execfile('uncertainties.py')

    # only consider shape, normalize up/down histo to nominal
    if current_syst == 'mass': norm_shape(model, 'top','mass')
    #if current_syst == 'scale': norm_shape(model, 'ttbar','scale')

    fit_dist = copy.deepcopy(model.distribution)
    pars = model.get_parameters('')
    #print 'Model parameters:', pars
    # set all other systematics to zero
    #for p in pars:
    #    if p in systematics: continue
    #    #fit_dist.set_distribution_parameters(p, width=0.0)

    model.distribution = get_fixed_dist(model.distribution)
    options = Options()

    shifts = []
    #for p in systematics:
    p = current_syst
    orig_dist = copy.deepcopy(model.distribution)
    for new_mean in (-1.0, 1.0):
        print '=== shift %s to %f ===' % (p, new_mean)
        if new_mean == 1.0:
            shift = 'up'
        else:
            shift = 'down'
        model.distribution.set_distribution_parameters(p, mean = new_mean, range = (new_mean, new_mean))
        res = mle(model, input = 'toys-asimov:1.0', n = 1, nuisance_constraint = fit_dist, options = options)
        fitresults = {}
        for process in res[signal]:
            if '__' in process: continue
            fitresults[process] = [res[signal][process][0][0], res[signal][process][0][1]]
        f = open('results/syst_'+p+'_'+shift+'.txt','w')
        for key in sorted(fitresults.keys()):
            if key == current_syst: continue
            line = '%s %f %f\n' % (key, fitresults[key][0], fitresults[key][1])
            f.write(line)
            print line,
        f.close()
        model.distribution = orig_dist

