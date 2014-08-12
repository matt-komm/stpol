const VARS = {
	:C=>"C variable",
	:shat=>"\$ \\hat{S} \$\ [GeV]",
	:ht=>"\$ H_t \$\ [GeV]",
	:ljet_eta=>"\$ \\eta_{j'} \$",
	:abs_ljet_eta=>"\$|\\eta_{j'}|\$",
	:abs_bjet_eta=>"\$|\\eta_{b}|\$",
	:bjet_eta=>"\$ \\eta_{b} \$",
	:(abs(ljet_eta))=>"\$\|\\eta_{j'}\|\$",
	:bdt_sig_bg=>"\$BDT_{W,t\\bar{t}}\$\ output",
	:top_mass=>"\$ M_{bl\\nu} \$ [GeV]",
	:lepton_pt=>"\$ p_{t,l} \$ [GeV]",
	:lepton_iso=>"\$ I_{rel,l} \$",
	:ljet_pt=>"\$ p_{t,j'} \$ [GeV]",
	:bjet_pt=>"\$ p_{t,b} \$ [GeV]",
	:mtw=>"\$ M_{l,\\nu} \$ [GeV]",
	:met=>"MET",
	:cos_theta_lj=>"\$ \\cos{\\ \\theta^*} \$",
	:cos_theta_bl=>"\$ \\cos{\\ \\theta}_{\\eta-bl} \$",
	:cos_theta_lj_gen=>"generated \$ \\cos{\\ \\theta^*} \$",
	:cos_theta_bl_gen=>"generated \$ \\cos{\\ \\theta}_{\\eta-bl} \$",
	:ljet_rms=>"\$ RMS_{j'} \$",
	:ljet_dr=>"\$\\Delta R_{j',l}\$",
	:bjet_dr=>"\$\\Delta R_{b,l}\$",
	:n_good_vertices=>"\$N_{vertices}\$",
	:bdt_qcd=>"\$BDT_{QCD}\$\ output",
	:nu_soltype => "\$p_{\\nu, z}\$ quadratic solution type",
	:met_phi => "\$ \\Phi_{MET} \$",
	:lepton_eta => "\$ \\eta_{l} \$",
	:abs_lepton_eta => "\$| \\eta_{l} |\$",
    :differential_cos_theta => "\$\\frac{\\mathrm{d}\\sigma}{\\sigma\\ \\\mathrm{d}\\cos\\ \\theta^*}\$"
}

const SAMPLENAMES = {
	:ttjets => "\$ t \\bar{t} \$",
	:tchan => "t-channel",
	:wjets_heavy => "W+jets (bc)",
	:wjets_light => "W+jets (udsg)",
	:wjets => "W+jets",
	:wzjets => "W, DY, \$\\gamma\$-jets"
}

const SAMPLENAMES_MERGED = {
	:tchan => "t-channel",
	:wzjets => "W, DY, \$\\gamma\$-jets",
	:ttjets => "\$ t \\bar{t} \$, tW, s",
	:data => "Data"
}

const titles = {
	:jet => ((nj, nt) -> ("%(nj)J(%(nt)T)")),
	:lepton => (lep -> {:mu=>"\$\\mu^\\pm\$", :ele=>"\$\\mu^\\pm\$"}[lep]),
}

title(nj::Integer, nt::Integer, lepton::Symbol) =
	string(titles[:lepton][lepton], ", ", titles[:jet](nj, nt))

export VARS, titles, SAMPLENAMES, SAMPLENAMES_MERGED
