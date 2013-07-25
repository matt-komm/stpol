from plots.common.make_systematics_histos import *    

if __name__=="__main__":
    cut_str = "n_jets==2 && n_tags==1 && top_mass>130 && top_mass<220 && rms_lj<0.025 && mt_mu>50"
    cut_str_antiiso = cut_str+" && mu_iso>0.3 && mu_iso<0.5 && deltaR_lj>0.3 && deltaR_bj>0.3"
    systematics = generate_systematics()
    var = "eta_lj"
    outdir = '/'.join([os.environ["STPOL_DIR"], "lqetafit", "histos"])
    make_systematics_histos(var, cut_str, cut_str_antiiso, systematics, outdir, plot_range=[15, 0, 5])
