import logging
logger = logging.getLogger("data_mc")


def data_mc_plot(samples, plot_def):
    logger.info('Plot in progress %s' % pd)

    if not (plot_def["enabled"]):
        continue

    var = plot_def['var']


    if not isinstance(var, basestring):
        if proc == 'ele':
            var = var[0]
        else:
            var = var[1]

    cut = None
    if proc == 'ele':
        cut = plot_def['elecut']
    elif proc == 'mu':
        cut = plot_def['mucut']

    cut_str = str(cut)
    weight_str = str(Weights.total(proc) *
        Weights.wjets_madgraph_shape_weight() *
        Weights.wjets_madgraph_flat_weight())

    plot_range = plot_def['range']

    hists_mc = dict()
    hists_data = dict()
    for name, sample in samples.items():
        logger.debug("Starting to plot %s" % name)
        if sample.isMC:
            hist = sample.drawHistogram(var, cut_str, weight=weight_str, plot_range=plot_range)
            hist.Scale(sample.lumiScaleFactor(lumi))
            hists_mc[sample.name] = hist
            Styling.mc_style(hists_mc[sample.name], sample.name)

            if "fitpars" in plot_def.keys():
                rescale_to_fit(sample.name, hist, plot_def["fitpars"])
        elif "antiiso" in name and plot_def['estQcd']:

            #FIXME: it'd be nice to move the isolation cut to plots/common/cuts.py for generality :) -JP
            cv='mu_iso'
            lb=0.3
            if proc == 'ele':
                cv='el_iso'
                lb=0.1
            qcd_cut = cut*Cuts.deltaR(0.5)*Cut(cv+'>'+str(lb)+' & '+cv+'<0.5')


            #FIXME: It would be nice to factorise this part a bit (separate method?) or make it more clear :) -JP
            region = '2j1t'
            if plot_def['estQcd'] == '2j0t': region='2j0t'
            if plot_def['estQcd'] == '3j1t': region='3j1t'
            qcd_loose_cut = cutlist[region]*cutlist['presel_'+proc]*Cuts.deltaR(0.5)*Cut(cv+'>'+str(lb)+' & '+cv+'<0.5')
            logger.debug('QCD loose cut: %s' % str(qcd_loose_cut))
            hist_qcd = sample.drawHistogram(var, str(qcd_cut), weight="1.0", plot_range=plot_range)
            hist_qcd_loose = sample.drawHistogram(var, str(qcd_loose_cut), weight="1.0", plot_range=plot_range)
            hist_qcd.Scale(qcdScale[proc][plot_def['estQcd']])
            if hist_qcd_loose.Integral():
                hist_qcd_loose.Scale(hist_qcd.Integral()/hist_qcd_loose.Integral())
            sampn = "QCD"+sample.name

            #Rescale the QCD histogram to the eta_lj fit
            if "fitpars" in plot_def.keys():
                rescale_to_fit(sampn, hist_qcd_loose, plot_def["fitpars"])

            hists_mc[sampn] = hist_qcd_loose
            hists_mc[sampn].SetTitle('QCD')
            Styling.mc_style(hists_mc[sampn], 'QCD')

        #Real ordinary data in the isolated region
        elif not "antiiso" in name:
            hist_data = sample.drawHistogram(var, cut_str, weight="1.0", plot_range=plot_range)
            hist_data.SetTitle('Data')
            Styling.data_style(hist_data)
            hists_data[name] = hist_data


    if len(hists_data.values())==0:
        raise Exception("Couldn't draw the data histogram")

    #Combine the subsamples to physical processes
    hist_data = sum(hists_data.values())
    merge_cmds['QCD']=["QCD"+merge_cmds['data'][0]]
    order=['QCD']+PhysicsProcess.desired_plot_order
    if plot_defs[pd]['log']:
        order = PhysicsProcess.desired_plot_order_log+['QCD']
    merged_hists = merge_hists(hists_mc, merge_cmds, order=order)


    #Get the pretty names for the processes from the PhysicsProces.pretty_name variable
    for procname, hist in merged_hists.items():
        try:
            hist.SetTitle(physics_processes[procname].pretty_name)
        except KeyError: #QCD does not have a defined PhysicsProcess but that's fine because we take it separately
            pass
