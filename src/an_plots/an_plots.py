from plots.syst_band import PlotDef, data_mc_plot, logger
from plots.common.cuts import Cuts

logger.setLevel("INFO")
from plots.common.cross_sections import lumis
from plots.common.tdrstyle import tdrstyle

from plots.fit_scale_factors import fitpars_process
from plots.qcd_scale_factors import load_qcd_sf, qcd_cut_SF
from plots.vars import varnames

from plots.common.histogram import calc_int_err

import os, copy, math

channels_pretty = {"mu":"Muon", "ele":"Electron"}

#Determined from the QCD fit
qcd_mt_fit_sfs = dict()
qcd_mt_fit_sfs['mu'] = load_qcd_sf('mu', 50)
qcd_mt_fit_sfs['ele'] = load_qcd_sf('ele', 45)

#Determined as the ratio of the integral of anti-iso data after full selection / full selection minus MVA
#See qcd_scale_factors.ipynb for determination
qcd_loose_to_MVA_sfs = qcd_cut_SF['mva']['loose']

fit_sfs = dict()
fit_sfs['mu'] = [x[1:] for x in fitpars_process['final_2j1t_mva']['mu']]
fit_sfs['ele'] = [x[1:] for x in fitpars_process['final_2j1t_mva']['ele']]

def scale_factors(channel, cut, apply_signal_cut=True, mt_cut=False):
    tchan, tchan_err = fit_sfs[channel][0]
    top, top_err = fit_sfs[channel][1]
    wzjets, wzjets_err = fit_sfs[channel][2]
    if "2j1t" not in cut:
        tchan = 1
        top = 1
        wzjets = 1

    qcd = top
    if apply_signal_cut:
        if "mva_loose" in cut:
            qcd = qcd * qcd_cut_SF['mva']['loose'][channel]
        elif "cutbased_final" in cut:
            qcd = qcd * qcd_cut_SF['cutbased']['final'][channel]
    if mt_cut is False:
        qcd = qcd * qcd_mt_fit_sfs[channel]
    else:
        qcd = qcd * load_qcd_sf(channel, mt_cut)
                             
    ret = [
        (['tchan'], tchan, tchan_err),
        (['TTJets', 'tWchan', 'schan'], top, top_err),
        (['qcd'], qcd, top_err),
        (['WJets', 'diboson', 'DYJets'], wzjets, wzjets_err)
    ]
    return ret

def pd(var, cut, channel, hpath="hists/Aug27/", **kwargs):
    return PlotDef(
        infile=hpath+"/hists_merged__%s__%s_%s.root" % (cut, var, channel),
        lumi=lumis["Aug4_0eb863_full"]["iso"][channel],
        var=var,
        channel_pretty=channels_pretty[channel],
        systematics='.*',
        systematic_shapeonly=not 'mva' in cut,
        lb_comments=kwargs.pop("lb_comments", ""),
        process_scale_factor = scale_factors(channel, cut),
        **kwargs
    )

def save_canv(canv, path):
    import os

    #selection.tex
    if "2j1t_mva_loose_cosTheta" in path:
        path = path.replace("2j1t_mva_loose_cosTheta", "control/final_cosTheta_mva_loose_fit")
    elif "2j1t_cutbased_final_cosTheta" in path:
        path = path.replace("2j1t_cutbased_final_cosTheta", "control/final_cosTheta_fit")
    elif "baseline_bdt_discr" in path:
        path = path.replace("baseline_bdt_discr", "BDT/mva_bdt")
    elif "baseline_cosTheta" in path:
        import pdb; pdb.set_trace()
        p = os.path.dirname(path)
        b = os.path.basename(path)
        p += "control/" + b.split("_")[0] + ""
        path = path.replace("baseline_bdt_discr", "control/mva_bdt")
    dname = os.path.dirname(path)
    if not os.path.exists(dname):
        os.makedirs(dname)
    canv.SaveAs(path)

if __name__=="__main__":
    tdrstyle()

    def save_yields(hists, ofn, scale_factors):
        hmc, hdata = hists
        if not os.path.exists(os.path.dirname(ofn)):
            os.makedirs(os.path.dirname(ofn))
        of = open(ofn, "w+")
        items = hmc.items() + [
            ("MC", reduce(lambda x,y: x+y, hmc.values())),
            ("data", hdata)
        ]
        
        #Get the uncertainties that remain after the BDT fit
        errs_fit = dict()
        for k, v in hmc.items():
            unc_fit = 0
            if k.lower() in ["dyjets", "diboson", "wjets"]:
                unc_fit = scale_factors["wzjets"][1]
            elif k.lower() in ["ttjets", "twchan", "schan"]:
                unc_fit = scale_factors["topqcd"][1]
            elif k.lower() in ["tchan"]:
                unc_fit = scale_factors["tchan"][1]

            errs_fit[k] = unc_fit * v.Integral()

        #Assume that the fit results are uncorrelated for total MC
        errs_fit["MC"] = math.sqrt(sum([x**2 for x in errs_fit.values()]))
        errs_fit["qcd"] = hmc["qcd"].Integral()

        for k, v in sorted(items, key=lambda x: x[0]):
            i, e = calc_int_err(v)

            fit_unc = errs_fit.get(k, 0)

            #Total error is statistical (Poisson) + fit error (indep.)
            tot_err = math.sqrt(e**2 + fit_unc**2)

            of.write("%s | %.2f | %.2f | %.2f\n" % (k, i, e, tot_err))
        of.close()

    def plot(varname, cutname, **kwargs):
        for channel in ["mu", "ele"]:
            _kwargs = copy.deepcopy(kwargs)
            do_save_yields = _kwargs.pop("save_yields", False)
            lb_comments = _kwargs.pop("lb_comments", "")
            lb_comments = lb_comments.format(bdt_cut=Cuts.mva_wps['bdt'][channel]['loose'])
            save_name = _kwargs.pop("save_name", outdir + '/{cutname}_{varname}.pdf')
            save_name = save_name.format(channel=channel, varname=varname, cutname=cutname)
            _kwargs["save_name"] = save_name
            h = pd(varname, cutname, channel,
                lb_comments = lb_comments,
                #rebin=rbf(varname), legend_pos=lgp(varname), lb_comments=lb_comments(cutname, channel),
                #subdir_AN=subdir, cutname_AN=cutname_AN,
                **_kwargs
            )
            canv, hists = data_mc_plot(h)
            save_canv(canv, h.save_name)
            canv.Close()
            if do_save_yields:
                save_yields(
                    hists,
                    "results/yields/{0}_{1}.txt".format(cutname, channel),
                    {"tchan": h.process_scale_factor[0][1:],
                    "topqcd": h.process_scale_factor[1][1:],
                    "wzjets": h.process_scale_factor[2][1:]}
                )

    outdir = "out/plots/an/"
    plot("cos_theta", "2j1t_mva_loose", rebin=4, legend_pos='top-left',
        lb_comments=', 2J1T BDT > {bdt_cut:.2f}',
        save_name=outdir + '/control/2j1t_cosTheta_mva_{channel}.pdf',
        save_yields=True
    )
    plot("cos_theta", "2j1t_cutbased_final", rebin=4, legend_pos='top-left',
        lb_comments=', 2J1T cut-based',
        save_name=outdir + '/control/2j1t_cosTheta_cutbased_{channel}.pdf',
        save_yields=True
    )


    # plot("cos_theta", "2j0t_baseline", rebin=4, legend_pos='top-left', lb_comments=', 2J0T', max_bin_mult=2.5, save_name=outdir + '/control/2j0t_cosTheta_{channel}.pdf')
    # plot("cos_theta", "3j0t_baseline", rebin=4, legend_pos='top-left', lb_comments=', 3J0T', max_bin_mult=2.5, save_name=outdir + '/control/3j0t_cosTheta_{channel}.pdf')
    # plot("cos_theta", "3j1t_baseline", rebin=4, legend_pos='top-left', lb_comments=', 3J1T', max_bin_mult=2.5, save_name=outdir + '/control/3j1t_cosTheta_{channel}.pdf')
    # plot("cos_theta", "3j2t_baseline", rebin=4, legend_pos='top-left', lb_comments=', 3J2T', max_bin_mult=2.5, save_name=outdir + '/control/3j2t_cosTheta_{channel}.pdf')

    # plot("bdt_discr", "2j0t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 2J0T', log=True, save_name=outdir + '/BDT/2j0t_mva_bdt_{channel}.pdf', min_bin=100)
    # plot("bdt_discr", "3j0t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 3J0T', log=True, save_name=outdir + '/BDT/3j0t_mva_bdt_{channel}.pdf', min_bin=100)
    # plot("bdt_discr", "3j1t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 3J1T', log=True, save_name=outdir + '/BDT/3j1t_mva_bdt_{channel}.pdf', min_bin=10)
    # plot("bdt_discr", "3j2t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 3J2T', log=True, save_name=outdir + '/BDT/3j2t_mva_bdt_{channel}.pdf')

    # plot("abs_eta_lj", "2j0t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 2J0T', save_name=outdir + '/control/2j0t_etaLj_{channel}.pdf')
    # plot("abs_eta_lj", "3j0t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 3J0T', save_name=outdir + '/control/3j0t_etaLj_{channel}.pdf')
    # plot("abs_eta_lj", "3j1t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 3J1T', save_name=outdir + '/control/3j1t_etaLj_{channel}.pdf')
    # plot("abs_eta_lj", "3j2t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 3J2T', save_name=outdir + '/control/3j2t_etaLj_{channel}.pdf')

    # plot("top_mass_sr", "2j0t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 2J0T', save_name=outdir + '/control/2j0t_topMass_{channel}.pdf')
    # plot("top_mass_sr", "3j0t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 3J0T', save_name=outdir + '/control/3j0t_topMass_{channel}.pdf')
    # plot("top_mass_sr", "3j1t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 3J1T', save_name=outdir + '/control/3j1t_topMass_{channel}.pdf')
    # plot("top_mass_sr", "3j2t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 3J2T', save_name=outdir + '/control/3j2t_topMass_{channel}.pdf')