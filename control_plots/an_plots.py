from plots.syst_band import PlotDef, data_mc_plot, logger
from plots.common.cuts import Cuts

logger.setLevel("INFO")
from plots.common.cross_sections import lumis
from plots.common.tdrstyle import tdrstyle

from plots.fit_scale_factors import fitpars_process
from plots.qcd_scale_factors import load_qcd_sf, qcd_cut_SF
from plots.vars import varnames

from plots.common.histogram import calc_int_err

import os

channels_pretty = {"mu":"Muon", "ele":"Electron"}

#Determined from the QCD fit
qcd_mt_fit_sfs = dict()
qcd_mt_fit_sfs['mu'] = load_qcd_sf('mu', 50)
qcd_mt_fit_sfs['ele'] = load_qcd_sf('ele', 45)

#Determined as the ratio of the integral of anti-iso data after full selection / full selection minus MVA
#See qcd_scale_factors.ipynb for determination
qcd_loose_to_MVA_sfs = qcd_cut_SF['mva']['loose']

fit_sfs = dict()
fit_sfs['mu'] = [x[1] for x in fitpars_process['final_2j1t_mva']['mu']]
fit_sfs['ele'] = [x[1] for x in fitpars_process['final_2j1t_mva']['ele']]

def scale_factors(channel, cut, apply_signal_cut=True, mt_cut=False):
    tchan = fit_sfs[channel][0]
    top = fit_sfs[channel][1]
    wzjets = fit_sfs[channel][2]
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
        (['tchan'], tchan, -1),
        (['TTJets', 'tWchan', 'schan'], top, -1),
        (['qcd'], qcd, -1),
        (['WJets', 'diboson', 'DYJets'], wzjets, -1)
    ]
    return ret

def channel_to_an(channel):
    return channel[0:2]
def pd(var, cut, channel, hpath="hists/Aug27/", **kwargs):
    return PlotDef(
        infile=hpath+"/hists_merged__%s__%s_%s.root" % (cut, var, channel),
        lumi=lumis["Aug4_0eb863_full"]["iso"][channel],
        var=var,
        channel_pretty=channels_pretty[channel],
        systematics='.*',
        systematics_shapeonly=not "baseline" in cutname,
        lb_comments=', all syst.'+kwargs.pop("lb_comments", ""),
        save_name="out/plots/an/%s/%s_%s_%s.pdf" % (
            kwargs.pop("subdir_AN", ""),
            kwargs.pop("cutname_AN", cut), kwargs.pop("varname_AN", var), channel_to_an(channel)
        ),
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

    def rbf(varname):
        """
        Rebin factor
        """
        return 4

    def lgp(varname):
        if varname in ["cos_theta"]:
            return "top-left"
        else:
            return "top-right"

    def lb_comments(cutname, channel):
        spl = cutname.split("_")
        if len(spl) == 2:
            jet, cuttype = spl
            wp = None
        elif len(spl)==3:
            jet, cuttype, wp = spl
        ret = ""
        if cuttype=="mva" and wp=="loose":
            ret += ", BDT>%.2f" % (Cuts.mva_wps['bdt'][channel]['loose'])
        elif cuttype=="cutbased":
            ret += ", cut-based"
        return ret

    def save_yields(hists, ofn):
        hmc, hdata = hists
        if not os.path.exists(os.path.dirname(ofn)):
            os.makedirs(os.path.dirname(ofn))
        of = open(ofn, "w+")
        for k, v in sorted(
                hmc.items() +
                [
                    ("MC", reduce(lambda x,y: x+y, hmc.values())),
                    ("data", hdata)
                ], key=lambda x: x[0]):
            i, e = calc_int_err(v)
            of.write("%s | %.2f | %.2f\n" % (k, i, e))
        of.close()

    failed = []
    for cutname in [
        "2j1t_cutbased_final", "2j1t_mva_loose", "2j1t_baseline",
        "3j1t_baseline", "3j2t_baseline", "2j0t_baseline", "3j0t_baseline"]:

        if not "2j1t" in cutname:
            subdir="control"
        else:
            subdir = ""
        if "baseline" in cutname:
            cutname_AN = cutname.split("_")[0]
        else:
            cutname_AN = cutname

        for channel in ["mu", "ele"]:
            def plot(varname, **kwargs):
                h = pd(varname, cutname, channel,
                    rebin=rbf(varname), legend_pos=lgp(varname), lb_comments=lb_comments(cutname, channel),
                    subdir_AN=subdir, cutname_AN=cutname_AN,
                    **kwargs
                )
                if "baseline" in cutname and "eta_lj" in varname:
                    def _new_minmax():
                        return (-0.2, 0.2)
                    h.get_ratio_minmax = _new_minmax
                canv, hists = data_mc_plot(h)
                save_canv(canv, h.save_name)
                canv.Close()

                if varname=="cos_theta" and ("cutbased_final" in cutname or "mva_loose" in cutname):
                    save_yields(hists, "out/yields/%s_%s.txt" % (cutname, channel))

            plot("abs_eta_lj", varname_AN="etaLj")
            plot("cos_theta", varname_AN="cosTheta")


            try:
                plot("bdt_discr", log=True, min_bin=100, varname_AN="BDT")
            except Exception as e:

                failed.append((cutname, channel, "bdt_discr", str(e)))
                pass

            try:
                plot("top_mass_sr", var_name=varnames["top_mass"], varname_AN="topMass")
            except Exception as e:
                failed.append((cutname, channel, "top_mass_sr", str(e)))
                pass

    for f in failed:
        print "FAILED:", f