all: fit fit_C fit_abs_ljet_eta

fit: fit_ele fit_mu
fit_C: fit_mu_C fit_ele_C
fit_abs_ljet_eta: fit_mu_abs_ljet_eta fit_ele_abs_ljet_eta

HISTDIR=../analysis/output/bdt_scan/hists/preselection/

fit_ele:
	./runtheta.sh bgfit.py results/bdt/ele.json $(HISTDIR)/2j_1t/ele/merged/bdt_sig_bg.root $(HISTDIR)/3j_2t/ele/merged/bdt_sig_bg.root

fit_mu:
	./runtheta.sh bgfit.py results/bdt/mu.json $(HISTDIR)/2j_1t/mu/merged/bdt_sig_bg.root $(HISTDIR)/3j_2t/mu/merged/bdt_sig_bg.root

fit_ele_C:
	./runtheta.sh bgfit.py results/C/ele.json $(HISTDIR)/2j_1t/ele/merged/C.root $(HISTDIR)/3j_2t/ele/merged/C.root

fit_mu_C:
	./runtheta.sh bgfit.py results/C/mu.json $(HISTDIR)/2j_1t/mu/merged/C.root $(HISTDIR)/3j_2t/mu/merged/C.root

fit_ele_abs_ljet_eta:
	./runtheta.sh bgfit.py results/abs_ljet_eta/ele.json $(HISTDIR)/2j_1t/ele/merged/abs_ljet_eta.root $(HISTDIR)/3j_2t/ele/merged/abs_ljet_eta.root

fit_mu_abs_ljet_eta:
	./runtheta.sh bgfit.py results/abs_ljet_eta/mu.json $(HISTDIR)/2j_1t/mu/merged/abs_ljet_eta.root $(HISTDIR)/3j_2t/mu/merged/abs_ljet_eta.root

