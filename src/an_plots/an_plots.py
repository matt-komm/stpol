import logging
logger = logging.getLogger(__name__)

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)

from plots.syst_band import PlotDef, data_mc_plot
from plots.common.cuts import Cuts
from plots.common.cross_sections import lumis
from plots.common.tdrstyle import tdrstyle

from plots.fit_scale_factors import fitpars_process
from plots.qcd_scale_factors import load_qcd_sf, qcd_cut_SF
from plots.vars import varnames

from plots.common.histogram import calc_int_err

import os, copy, math
import numpy as np

channels_pretty = {"mu":"Muon", "ele":"Electron"}

#Determined from the QCD fit
qcd_mt_fit_sfs = dict()
qcd_mt_fit_sfs['mu'] = load_qcd_sf('mu', 50, do_uncertainty=True)
qcd_mt_fit_sfs['ele'] = load_qcd_sf('ele', 45, do_uncertainty=True)

#Determined as the ratio of the integral of anti-iso data after full selection / full selection minus MVA
#See qcd_scale_factors.ipynb for determination
qcd_loose_to_MVA_sfs = qcd_cut_SF['mva']['loose']

fit_sfs = dict()
fit_sfs['mu'] = [x[1:] for x in fitpars_process['final_2j1t_mva']['mu']]
fit_sfs['ele'] = [x[1:] for x in fitpars_process['final_2j1t_mva']['ele']]


# FIXME: load from file
# final_fit/results/ele__mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj.txt
# final_fit/results/mu__mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj.txt
Rab = 0.358255 #tchan top
Rac = -0.425863 #tchan wzjets
Rbc = -0.989548 #top wzjets
corr_mat = [
    #tchan  #ttbar  #tw     #s      #qcd    #w      #dy     #diboson
    [1,     Rab,    Rab,    Rab,    Rab,    Rac,    Rac,    Rac], #tchan
    [0,     1,      1,      1,      1,      Rbc,    Rbc,    Rbc], #ttbar
    [0,     0,      1,      1,      1,      Rbc,    Rbc,    Rbc], #tw
    [0,     0,      0,      1,      1,      Rbc,    Rbc,    Rbc], #s
    [0,     0,      0,      0,      1,      Rbc,    Rbc,    Rbc], #qcd
    [0,     0,      0,      0,      0,      1,      1,      1  ], #w
    [0,     0,      0,      0,      0,      0,      1,      1  ], #dy
    [0,     0,      0,      0,      0,      0,      0,      1  ], #diboson
]
diag  = np.diag(corr_mat)
corr_mat = np.triu(corr_mat).T + np.triu(corr_mat)
corr_mat[np.diag_indices(8)] = diag


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
        qcd_sf, qcd_err = qcd_mt_fit_sfs[channel]
    else:
        qcd_sf, qcd_err = load_qcd_sf(channel, mt_cut, do_uncertainty=True)
    qcd = qcd * qcd_sf

    # Calculate the total error in the QCD scale factor from the error in
    # the MET fit (qcd_err) and the BDT fit (top_err) assuming uncorrelate
    # errors.
    rel_qcd_err = qcd_err / qcd_sf
    rel_top_err = top_err / top

    tot_rel_qcd_err = math.sqrt(sum([x**2 for x in [rel_top_err, rel_qcd_err]]))
    tot_qcd_err = tot_rel_qcd_err * qcd

    ret = [
        (['tchan'], tchan, tchan_err),
        (['TTJets', 'tWchan', 'schan'], top, top_err),
        (['qcd'], qcd, tot_qcd_err),
        (['WJets', 'diboson', 'DYJets'], wzjets, wzjets_err)
    ]
    return ret

def pd(var, cut, channel, hpath="results/hists/hists_4ee08d9ca6e666ba2e8d42ada075061c58368c56/", **kwargs):
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

    #Fully correlated errors
    #corr_mat = np.eye(8)

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

            def ratio(x):
                """
                Calculates the relative uncertainty of the scale factor of a
                process

                Args:
                    x - process name185GB
                """
                return scale_factors[x][1] / scale_factors[x][0]
            if k.lower() in ["dyjets", "diboson", "wjets"]:
                unc_fit = ratio("wzjets")
            elif k.lower() in ["ttjets", "twchan", "schan"]:
                unc_fit = ratio("top")
            elif k.lower() in ["qcd"]:
                unc_fit = ratio("qcd")
            elif k.lower() in ["tchan"]:
                unc_fit = ratio("tchan")
            errs_fit[k.lower()] = unc_fit * v.Integral()
            logger.debug("Fit uncertainty forforfor {0}={1:.2f}".format(k, unc_fit))

        err_vec = np.array([
            errs_fit["tchan"], errs_fit["ttjets"], errs_fit["twchan"],
            errs_fit["schan"], errs_fit["qcd"], errs_fit["wjets"],
            errs_fit["dyjets"], errs_fit["diboson"]
        ])

        #Naive error
        #errs_fit["mc"] = math.sqrt(sum([x**2 for x in errs_fit.values()]))

        #Calculate the error using the covariance matrix
        errs_fit["mc"] = math.sqrt(np.dot(err_vec, np.dot(corr_mat, err_vec.T)))

        for k, v in sorted(items, key=lambda x: x[0]):
            k = k.lower()
            i, e = calc_int_err(v)

            fit_unc = errs_fit.get(k, 0)

            #Total error is statistical (Poisson) + fit error (indep.)
            tot_err = math.sqrt(e**2 + fit_unc**2)

            of.write("%s | %.2f | %.2f \n" % (k, i, tot_err))
        of.close()

    def plot(varname, cutname, **kwargs):
        for channel in ["mu", "ele"]:
            _kwargs = copy.deepcopy(kwargs)
            do_save_yields = _kwargs.pop("save_yields", False)
            lb_comments = _kwargs.pop("lb_comments", "")
            lb_comments = lb_comments.format(bdt_cut=Cuts.mva_wps['bdt'][channel]['loose'])
            save_name = _kwargs.pop("save_name", outdir + '/{cutname}_{varname}.pdf')
            
            #Inconsistency between code and AN/PAS
            channel_an = channel
            if channel=="ele":
                channel_an = "el"
            
            save_name = save_name.format(channel=channel_an, varname=varname, cutname=cutname)
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
                    "top": h.process_scale_factor[1][1:],
                    "qcd": h.process_scale_factor[2][1:],
                    "wzjets": h.process_scale_factor[3][1:]}
                )

    outdir = "out/plots/an/"
    plot("cos_theta", "2j1t_mva_loose", rebin=4, legend_pos='top-left',
        lb_comments=', 2J1T BDT > {bdt_cut:.2f}',
        save_name=outdir + '/control/final_cosTheta_mva_loose_fit_{channel}.pdf',
        save_yields=True
    )
    plot("cos_theta", "2j1t_cutbased_final", rebin=4, legend_pos='top-left',
        lb_comments=', 2J1T cut-based',
        save_name=outdir + '/control/final_cosTheta_fit_{channel}.pdf',
        save_yields=True
    )

    plot("cos_theta", "2j0t_baseline", rebin=4, legend_pos='top-left', lb_comments=', 2J0T', max_bin_mult=2.5, save_name=outdir + '/control/2j0t_cosTheta_{channel}.pdf')
    plot("cos_theta", "3j0t_baseline", rebin=4, legend_pos='top-left', lb_comments=', 3J0T', max_bin_mult=2.5, save_name=outdir + '/control/3j0t_cosTheta_{channel}.pdf')
    plot("cos_theta", "3j1t_baseline", rebin=4, legend_pos='top-left', lb_comments=', 3J1T', max_bin_mult=2.5, save_name=outdir + '/control/3j1t_cosTheta_{channel}.pdf')
    plot("cos_theta", "3j2t_baseline", rebin=4, legend_pos='top-left', lb_comments=', 3J2T', max_bin_mult=2.5, save_name=outdir + '/control/3j2t_cosTheta_{channel}.pdf')

    plot("bdt_discr", "2j0t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 2J0T', log=True, save_name=outdir + '/BDT/2j0t_BDT_{channel}.pdf', min_bin=100)
    plot("bdt_discr", "2j1t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 2J1T', log=True, save_name=outdir + '/BDT/mva_bdt_{channel}.pdf', min_bin=100)
    plot("bdt_discr_zoom_loose", "2j1t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 2J1T', save_name=outdir + '/BDT/mva_bdt_zoom_{channel}.pdf')
    plot("bdt_discr", "3j0t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 3J0T', log=True, save_name=outdir + '/BDT/3j0t_BDT_{channel}.pdf', min_bin=100)
    plot("bdt_discr", "3j1t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 3J1T', log=True, save_name=outdir + '/BDT/3j1t_BDT_{channel}.pdf', min_bin=10)
    plot("bdt_discr", "3j2t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 3J2T', log=True, save_name=outdir + '/BDT/3j2t_BDT_{channel}.pdf')

    plot("abs_eta_lj", "2j0t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 2J0T', save_name=outdir + '/control/2j0t_etaLj_{channel}.pdf')
    plot("abs_eta_lj", "3j0t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 3J0T', save_name=outdir + '/control/3j0t_etaLj_{channel}.pdf')
    plot("abs_eta_lj", "3j1t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 3J1T', save_name=outdir + '/control/3j1t_etaLj_{channel}.pdf')
    plot("abs_eta_lj", "3j2t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 3J2T', save_name=outdir + '/control/3j2t_etaLj_{channel}.pdf')

    plot("top_mass_sr", "2j0t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 2J0T', save_name=outdir + '/control/2j0t_topMass_{channel}.pdf')
    plot("top_mass_sr", "3j0t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 3J0T', save_name=outdir + '/control/3j0t_topMass_{channel}.pdf')
    plot("top_mass_sr", "3j1t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 3J1T', save_name=outdir + '/control/3j1t_topMass_{channel}.pdf')
    plot("top_mass_sr", "3j2t_baseline", rebin=4, legend_pos='top-right', lb_comments=', 3J2T', save_name=outdir + '/control/3j2t_topMass_{channel}.pdf')
