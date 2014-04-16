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
}

const titles = {
	:jet => ((nj, nt) -> ("%(nj)J(%(nt)T)")),
	:lepton => (lep -> {:mu=>"\$\\mu^\\pm\$", :ele=>"\$\\mu^\\pm\$"}[lep]),
}

title(nj::Integer, nt::Integer, lepton::Symbol) =
	string(titles[:lepton][lepton], ", ", titles[:jet](nj, nt))

export VARS, titles
