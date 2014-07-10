all: fit fit_C fit_abs_ljet_eta fit_separate

fit: fit_ele fit_mu
fit_C: fit_mu_C fit_ele_C
fit_abs_ljet_eta: fit_mu_abs_ljet_eta fit_ele_abs_ljet_eta fit_mu_2j1t_abs_ljet_eta fit_ele_2j1t_abs_ljet_eta

fit_separate: fit_mu_2j1t fit_ele_2j1t fit_mu_3j2t fit_ele_3j2t

HISTDIR=../../results/hists/Jun13/preselection
OUTDIR=results/csvt/qcd__mva_nominal

# HISTDIR=../../results/hists/csvt_only/preselection
# OUTDIR=results/csvt/qcd__metmtw_nominal
#
# HISTDIR=../../results/hists/apr16/csvt_qcd_metmtw/preselection/
# OUTDIR=results/csvt/qcd__metmtw_nominal

#HISTDIR=../../results/hists/remade_tchpt_2/preselection/
#OUTDIR=results/tchpt/qcd__metmtw_nominal

fit_ele_2j1t:
	./runtheta.sh bgfit.py $(OUTDIR)/bdt_2j_1t/ele $(HISTDIR)/2j_1t/ele/merged/bdt_sig_bg.root

fit_mu_2j1t:
	./runtheta.sh bgfit.py $(OUTDIR)/bdt_2j_1t/mu $(HISTDIR)/2j_1t/mu/merged/bdt_sig_bg.root

fit_mu_2j1t_abs_ljet_eta:
	./runtheta.sh bgfit.py $(OUTDIR)/abs_ljet_eta_2j_1t/mu $(HISTDIR)/2j_1t/mu/merged/abs_ljet_eta.root

fit_ele_2j1t_abs_ljet_eta:
	./runtheta.sh bgfit.py $(OUTDIR)/abs_ljet_eta_2j_1t/ele $(HISTDIR)/2j_1t/ele/merged/abs_ljet_eta.root

fit_ele_3j2t:
	./runtheta.sh bgfit.py $(OUTDIR)/bdt_3j_2t/ele $(HISTDIR)/3j_2t/ele/merged/bdt_sig_bg.root

fit_mu_3j2t:
	./runtheta.sh bgfit.py $(OUTDIR)/bdt_3j_2t/mu $(HISTDIR)/3j_2t/mu/merged/bdt_sig_bg.root

fit_ele:
	./runtheta.sh bgfit.py $(OUTDIR)/bdt/ele $(HISTDIR)/2j_1t/ele/merged/bdt_sig_bg.root $(HISTDIR)/3j_2t/ele/merged/bdt_sig_bg.root

#fit_ele:
#	./runtheta.sh bgfit.py $(OUTDIR)/bdt/ele $(HISTDIR)/2j_1t/ele/merged/bdt_sig_bg.root $(HISTDIR)/3j_2t/ele/merged/bdt_sig_bg.root $(HISTDIR)/2j_0t/ele/merged/bdt_sig_bg.root

fit_mu:
	./runtheta.sh bgfit.py $(OUTDIR)/bdt/mu $(HISTDIR)/2j_1t/mu/merged/bdt_sig_bg.root $(HISTDIR)/3j_2t/mu/merged/bdt_sig_bg.root $(HISTDIR)/2j_0t/mu/merged/bdt_sig_bg.root

#fit_mu:
#	./runtheta.sh bgfit.py $(OUTDIR)/bdt/mu $(HISTDIR)/2j_1t/mu/merged/bdt_sig_bg.root $(HISTDIR)/3j_2t/mu/merged/bdt_sig_bg.root $(HISTDIR)/2j_0t/mu/merged/bdt_sig_bg.root


fit_ele_C:
	./runtheta.sh bgfit.py $(OUTDIR)/C/ele $(HISTDIR)/2j_1t/ele/merged/C.root $(HISTDIR)/3j_2t/ele/merged/C.root

fit_mu_C:
	./runtheta.sh bgfit.py $(OUTDIR)/C/mu $(HISTDIR)/2j_1t/mu/merged/C.root $(HISTDIR)/3j_2t/mu/merged/C.root

fit_ele_abs_ljet_eta:
	./runtheta.sh bgfit.py $(OUTDIR)/abs_ljet_eta/ele $(HISTDIR)/2j_1t/ele/merged/abs_ljet_eta.root $(HISTDIR)/3j_2t/ele/merged/abs_ljet_eta.root

fit_mu_abs_ljet_eta:
	./runtheta.sh bgfit.py $(OUTDIR)/abs_ljet_eta/mu $(HISTDIR)/2j_1t/mu/merged/abs_ljet_eta.root $(HISTDIR)/3j_2t/mu/merged/abs_ljet_eta.root

fit_wjets:
	./runtheta.sh wjets_fit.py $(OUTDIR)/2j0t_cos_theta_lj/mu $(HISTDIR)/2j_0t/mu/cos_theta_lj.root
	./runtheta.sh wjets_fit.py $(OUTDIR)/2j0t_cos_theta_lj/ele $(HISTDIR)/2j_0t/ele/cos_theta_lj.root
	./runtheta.sh wjets_fit.py $(OUTDIR)/2j0t_cos_theta_lj/combined $(HISTDIR)/2j_0t/mu/cos_theta_lj.root $(HISTDIR)/2j_0t/ele/cos_theta_lj.root

copies:
	./copy_cfgs.sh fitconfigs/bdt/mu/nominal.cfg
	rm -Rf fitconfigs/bdt/ele	
	cp -R fitconfigs/bdt/mu fitconfigs/bdt/ele
	sed -i '' 's/mu/ele/g' fitconfigs/bdt/ele/*.cfg

fit_all:
	find fitconfigs/bdt -name "*.cfg" -exec ./runtheta.sh bgfit.py {} \;
