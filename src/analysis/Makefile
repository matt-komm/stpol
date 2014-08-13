include ../analysis/Makefile.options

INDIR=../../results/hists/Aug12/bdt_scan/hists/
OUTDIR=../../results/hists/Aug12/merged

clean:
	rm -Rf $(OUTDIR)


test:
	julia evloop2.jl test.txt infile.json 0 10000 /hdfs/local/joosep/stpol/skims/step3_v2/Jul4_newsyst_newvars_metshift/iso/nominal/T_t_ToLeptons/837/output.root

merge:
	@for lep in mu ele; do \
	  for var in $(INDIR)/preselection/2j_1t/$$lep/*.root; do \
	    fn=`basename $$var` ; \
	    python regroup.py $$var $(OUTDIR)/preselection/2j_1t/$$lep/merged/$$fn $$lep 2j1t fit ; \
	  done ; \
	  for var in $(INDIR)/preselection/3j_2t/$$lep/*.root; do \
	    fn=`basename $$var` ; \
	    python regroup.py $$var $(OUTDIR)/preselection/3j_2t/$$lep/merged/$$fn $$lep 3j2t fit ; \
	  done ; \
	done

	python regroup.py $(INDIR)/preselection/2j_1t/mu/bdt_sig_bg.root $(OUTDIR)/preselection/2j_1t/mu/merged/bdt_sig_bg__nopdf.root mu 2j1t fit
	python regroup.py $(INDIR)/preselection/3j_2t/mu/bdt_sig_bg.root $(OUTDIR)/preselection/3j_2t/mu/merged/bdt_sig_bg__nopdf.root mu 3j2t fit
	python regroup.py $(INDIR)/preselection/2j_1t/ele/bdt_sig_bg.root $(OUTDIR)/preselection/2j_1t/ele/merged/bdt_sig_bg__nopdf.root ele 2j1t fit
	python regroup.py $(INDIR)/preselection/3j_2t/ele/bdt_sig_bg.root $(OUTDIR)/preselection/3j_2t/ele/merged/bdt_sig_bg__nopdf.root ele 3j2t fit
	

	hadd -f $(OUTDIR)/preselection/2j_1t/mu/merged/bdt_sig_bg.root $(OUTDIR)/preselection/2j_1t/mu/merged/bdt_sig_bg__nopdf.root ../../results/hists/pdf_histos_merged_05_08/mu_bdt_sig_bg_2j1t_pdf.root
	hadd -f $(OUTDIR)/preselection/3j_2t/mu/merged/bdt_sig_bg.root $(OUTDIR)/preselection/3j_2t/mu/merged/bdt_sig_bg__nopdf.root ../../results/hists/pdf_histos_merged_05_08/mu_bdt_sig_bg_3j2t_pdf.root
	hadd -f $(OUTDIR)/preselection/2j_1t/ele/merged/bdt_sig_bg.root $(OUTDIR)/preselection/2j_1t/ele/merged/bdt_sig_bg__nopdf.root ../../results/hists/pdf_histos_merged_05_08/ele_bdt_sig_bg_2j1t_pdf.root
	hadd -f $(OUTDIR)/preselection/3j_2t/ele/merged/bdt_sig_bg.root $(OUTDIR)/preselection/3j_2t/ele/merged/bdt_sig_bg__nopdf.root ../../results/hists/pdf_histos_merged_05_08/ele_bdt_sig_bg_3j2t_pdf.root
	

	@for lep in mu ele; do \
	  for var in $(INDIR)/preselection/2j_1t/$$lep/*.root; do \
	    fn=`basename $$var` ; \
	    python regroup.py $$var $(OUTDIR)/preselection/2j_1t/$$lep/$$fn $$lep 2j1t plot ; \
	  done ; \
	  for var in $(INDIR)/preselection/3j_1t/$$lep/*.root; do \
	    fn=`basename $$var` ; \
	    python regroup.py $$var $(OUTDIR)/preselection/3j_1t/$$lep/$$fn $$lep 3j1t plot ; \
	  done ; \
	  for var in $(INDIR)/preselection/3j_2t/$$lep/*.root; do \
	    fn=`basename $$var` ; \
	    python regroup.py $$var $(OUTDIR)/preselection/3j_2t/$$lep/$$fn $$lep 3j2t plot ; \
	  done ; \
	  for var in $(INDIR)/preselection/2j_0t/$$lep/*.root; do \
	    fn=`basename $$var` ; \
	    python regroup.py $$var $(OUTDIR)/preselection/2j_0t/$$lep/$$fn $$lep 2j0t plot ; \
	  done ; \
	done
	
	@for lep in mu ele; do \
	  for var in $(INDIR)/preqcd/2j_1t/$$lep/*.root; do \
	    fn=`basename $$var` ; \
	    python regroup.py $$var $(OUTDIR)/preqcd/2j_1t/$$lep/$$fn $$lep 2j1t plot ; \
	  done ; \
	  for var in $(INDIR)/preqcd/3j_1t/$$lep/*.root; do \
	    fn=`basename $$var` ; \
	    python regroup.py $$var $(OUTDIR)/preqcd/3j_1t/$$lep/$$fn $$lep 3j1t plot ; \
	  done ; \
	  for var in $(INDIR)/preqcd/3j_2t/$$lep/*.root; do \
	    fn=`basename $$var` ; \
	    python regroup.py $$var $(OUTDIR)/preqcd/3j_2t/$$lep/$$fn $$lep 3j2t plot ; \
	  done ; \
	  for var in $(INDIR)/preqcd/2j_0t/$$lep/*.root; do \
	    fn=`basename $$var` ; \
	    python regroup.py $$var $(OUTDIR)/preqcd/2j_0t/$$lep/$$fn $$lep 2j0t plot ; \
	  done ; \
	done



merge2:
	mkdir -p $(OUTDIR)/0.60000/mu
	mkdir -p $(OUTDIR)/0.60000/ele
	cp $(INDIR)/0.60000/mu/tmatrix*.root $(OUTDIR)/0.60000/mu/
	cp $(INDIR)/0.60000/ele/tmatrix*.root $(OUTDIR)/0.60000/ele/
	python regroup.py $(INDIR)/0.60000/mu/cos_theta_lj.root $(OUTDIR)/0.60000/mu/merged/cos_theta_lj__nopdf.root mu  2j1t fit
	python regroup.py $(INDIR)/0.60000/ele/cos_theta_lj.root $(OUTDIR)/0.60000/ele/merged/cos_theta_lj__nopdf.root ele 2j1t fit
	
	hadd -f $(OUTDIR)/0.60000/mu/merged/cos_theta_lj.root $(OUTDIR)/0.60000/mu/merged/cos_theta_lj__nopdf.root ../../results/hists/pdf_histos_merged_05_08/mu_cos_theta_2j1t_pdf.root
	hadd -f $(OUTDIR)/0.60000/ele/merged/cos_theta_lj.root $(OUTDIR)/0.60000/ele/merged/cos_theta_lj__nopdf.root ../../results/hists/pdf_histos_merged_05_08/mu_cos_theta_3j2t_pdf.root
	
	python regroup.py $(INDIR)/0.60000/mu/cos_theta_lj.root $(OUTDIR)/0.60000/mu/cos_theta_lj.root mu  2j1t plot
	python regroup.py $(INDIR)/0.60000/ele/cos_theta_lj.root $(OUTDIR)/0.60000/ele/cos_theta_lj.root ele 2j1t plot
	
	python regroup.py $(INDIR)/0.60000/mu/cos_theta_lj.root $(OUTDIR)/0.60000/mu/merged/cos_theta_lj.root mu  2j1t fit
	python regroup.py $(INDIR)/0.60000/ele/cos_theta_lj.root $(OUTDIR)/0.60000/ele/merged/cos_theta_lj.root ele 2j1t fit
	
	python regroup.py $(INDIR)/0.60000/mu/cos_theta_lj.root $(OUTDIR)/0.60000/mu/cos_theta_lj.root mu  2j1t plot
	python regroup.py $(INDIR)/0.60000/ele/cos_theta_lj.root $(OUTDIR)/0.60000/ele/cos_theta_lj.root ele 2j1t plot
	
	python regroup.py $(INDIR)/2j_0t/0.60000/mu/cos_theta_lj.root $(OUTDIR)/2j_0t/0.60000/mu/cos_theta_lj.root mu  2j0t plot
	python regroup.py $(INDIR)/2j_0t/0.60000/ele/cos_theta_lj.root $(OUTDIR)/2j_0t/0.60000/ele/cos_theta_lj.root ele 2j0t plot
	
	python regroup.py $(INDIR)/3j_1t/0.60000/mu/cos_theta_lj.root $(OUTDIR)/3j_1t/0.60000/mu/cos_theta_lj.root mu  3j1t plot
	python regroup.py $(INDIR)/3j_1t/0.60000/ele/cos_theta_lj.root $(OUTDIR)/3j_1t/0.60000/ele/cos_theta_lj.root ele 3j1t plot
	
	python regroup.py $(INDIR)/3j_2t/0.60000/mu/cos_theta_lj.root $(OUTDIR)/3j_2t/0.60000/mu/cos_theta_lj.root mu  3j2t plot
	python regroup.py $(INDIR)/3j_2t/0.60000/ele/cos_theta_lj.root $(OUTDIR)/3j_2t/0.60000/ele/cos_theta_lj.root ele 3j2t plot
	mkdir -p $(OUTDIR)/0.60000/combined/merged
	hadd -f $(OUTDIR)/0.60000/combined/merged/cos_theta_lj.root $(OUTDIR)/0.60000/mu/merged/cos_theta_lj.root $(OUTDIR)/0.60000/ele/merged/cos_theta_lj.root
	hadd -f $(OUTDIR)/0.60000/combined/cos_theta_lj.root $(OUTDIR)/0.60000/mu/cos_theta_lj.root $(OUTDIR)/0.60000/ele/cos_theta_lj.root
	hadd -f $(OUTDIR)/0.60000/combined/tmatrix_nocharge__gen_ele.root $(OUTDIR)/0.60000/mu/tmatrix_nocharge__gen_ele.root $(OUTDIR)/0.60000/ele/tmatrix_nocharge__gen_ele.root
	hadd -f $(OUTDIR)/0.60000/combined/tmatrix_nocharge__gen_mu.root $(OUTDIR)/0.60000/mu/tmatrix_nocharge__gen_mu.root $(OUTDIR)/0.60000/ele/tmatrix_nocharge__gen_mu.root
	hadd -f $(OUTDIR)/0.60000/combined/tmatrix_nocharge__gen_tau.root $(OUTDIR)/0.60000/mu/tmatrix_nocharge__gen_tau.root $(OUTDIR)/0.60000/ele/tmatrix_nocharge__gen_tau.root
	
	mkdir -p $(OUTDIR)/0.40000/mu
	mkdir -p $(OUTDIR)/0.40000/ele
	cp $(INDIR)/0.40000/mu/tmatrix*.root $(OUTDIR)/0.40000/mu/
	cp $(INDIR)/0.40000/ele/tmatrix*.root $(OUTDIR)/0.40000/ele/
	python regroup.py $(INDIR)/0.40000/mu/cos_theta_lj.root $(OUTDIR)/0.40000/mu/merged/cos_theta_lj__nopdf.root mu  2j1t fit
	python regroup.py $(INDIR)/0.40000/ele/cos_theta_lj.root $(OUTDIR)/0.40000/ele/merged/cos_theta_lj__nopdf.root ele 2j1t fit
	
	hadd -f $(OUTDIR)/0.40000/mu/merged/cos_theta_lj.root $(OUTDIR)/0.40000/mu/merged/cos_theta_lj__nopdf.root ../../results/hists/pdf_histos_merged_05_08/mu_cos_theta_2j1t_pdf.root
	hadd -f $(OUTDIR)/0.40000/ele/merged/cos_theta_lj.root $(OUTDIR)/0.40000/ele/merged/cos_theta_lj__nopdf.root ../../results/hists/pdf_histos_merged_05_08/mu_cos_theta_3j2t_pdf.root
	
	python regroup.py $(INDIR)/0.40000/mu/cos_theta_lj.root $(OUTDIR)/0.40000/mu/cos_theta_lj.root mu  2j1t plot
	python regroup.py $(INDIR)/0.40000/ele/cos_theta_lj.root $(OUTDIR)/0.40000/ele/cos_theta_lj.root ele 2j1t plot
	
	python regroup.py $(INDIR)/0.40000/mu/cos_theta_lj.root $(OUTDIR)/0.40000/mu/merged/cos_theta_lj.root mu  2j1t fit
	python regroup.py $(INDIR)/0.40000/ele/cos_theta_lj.root $(OUTDIR)/0.40000/ele/merged/cos_theta_lj.root ele 2j1t fit
	
	python regroup.py $(INDIR)/0.40000/mu/cos_theta_lj.root $(OUTDIR)/0.40000/mu/cos_theta_lj.root mu  2j1t plot
	python regroup.py $(INDIR)/0.40000/ele/cos_theta_lj.root $(OUTDIR)/0.40000/ele/cos_theta_lj.root ele 2j1t plot
	
	python regroup.py $(INDIR)/2j_0t/0.40000/mu/cos_theta_lj.root $(OUTDIR)/2j_0t/0.40000/mu/cos_theta_lj.root mu  2j0t plot
	python regroup.py $(INDIR)/2j_0t/0.40000/ele/cos_theta_lj.root $(OUTDIR)/2j_0t/0.40000/ele/cos_theta_lj.root ele 2j0t plot
	
	python regroup.py $(INDIR)/3j_1t/0.40000/mu/cos_theta_lj.root $(OUTDIR)/3j_1t/0.40000/mu/cos_theta_lj.root mu  3j1t plot
	python regroup.py $(INDIR)/3j_1t/0.40000/ele/cos_theta_lj.root $(OUTDIR)/3j_1t/0.40000/ele/cos_theta_lj.root ele 3j1t plot
	
	python regroup.py $(INDIR)/3j_2t/0.40000/mu/cos_theta_lj.root $(OUTDIR)/3j_2t/0.40000/mu/cos_theta_lj.root mu  3j2t plot
	python regroup.py $(INDIR)/3j_2t/0.40000/ele/cos_theta_lj.root $(OUTDIR)/3j_2t/0.40000/ele/cos_theta_lj.root ele 3j2t plot
	mkdir -p $(OUTDIR)/0.40000/combined/merged
	hadd -f $(OUTDIR)/0.40000/combined/merged/cos_theta_lj.root $(OUTDIR)/0.40000/mu/merged/cos_theta_lj.root $(OUTDIR)/0.40000/ele/merged/cos_theta_lj.root
	hadd -f $(OUTDIR)/0.40000/combined/cos_theta_lj.root $(OUTDIR)/0.40000/mu/cos_theta_lj.root $(OUTDIR)/0.40000/ele/cos_theta_lj.root
	hadd -f $(OUTDIR)/0.40000/combined/tmatrix_nocharge__gen_ele.root $(OUTDIR)/0.40000/mu/tmatrix_nocharge__gen_ele.root $(OUTDIR)/0.40000/ele/tmatrix_nocharge__gen_ele.root
	hadd -f $(OUTDIR)/0.40000/combined/tmatrix_nocharge__gen_mu.root $(OUTDIR)/0.40000/mu/tmatrix_nocharge__gen_mu.root $(OUTDIR)/0.40000/ele/tmatrix_nocharge__gen_mu.root
	hadd -f $(OUTDIR)/0.40000/combined/tmatrix_nocharge__gen_tau.root $(OUTDIR)/0.40000/mu/tmatrix_nocharge__gen_tau.root $(OUTDIR)/0.40000/ele/tmatrix_nocharge__gen_tau.root
	
	mkdir -p $(OUTDIR)/0.20000/mu
	mkdir -p $(OUTDIR)/0.20000/ele
	cp $(INDIR)/0.20000/mu/tmatrix*.root $(OUTDIR)/0.20000/mu/
	cp $(INDIR)/0.20000/ele/tmatrix*.root $(OUTDIR)/0.20000/ele/
	python regroup.py $(INDIR)/0.20000/mu/cos_theta_lj.root $(OUTDIR)/0.20000/mu/merged/cos_theta_lj__nopdf.root mu  2j1t fit
	python regroup.py $(INDIR)/0.20000/ele/cos_theta_lj.root $(OUTDIR)/0.20000/ele/merged/cos_theta_lj__nopdf.root ele 2j1t fit
	
	hadd -f $(OUTDIR)/0.20000/mu/merged/cos_theta_lj.root $(OUTDIR)/0.20000/mu/merged/cos_theta_lj__nopdf.root ../../results/hists/pdf_histos_merged_05_08/mu_cos_theta_2j1t_pdf.root
	hadd -f $(OUTDIR)/0.20000/ele/merged/cos_theta_lj.root $(OUTDIR)/0.20000/ele/merged/cos_theta_lj__nopdf.root ../../results/hists/pdf_histos_merged_05_08/mu_cos_theta_3j2t_pdf.root
	
	python regroup.py $(INDIR)/0.20000/mu/cos_theta_lj.root $(OUTDIR)/0.20000/mu/cos_theta_lj.root mu  2j1t plot
	python regroup.py $(INDIR)/0.20000/ele/cos_theta_lj.root $(OUTDIR)/0.20000/ele/cos_theta_lj.root ele 2j1t plot
	
	python regroup.py $(INDIR)/0.20000/mu/cos_theta_lj.root $(OUTDIR)/0.20000/mu/merged/cos_theta_lj.root mu  2j1t fit
	python regroup.py $(INDIR)/0.20000/ele/cos_theta_lj.root $(OUTDIR)/0.20000/ele/merged/cos_theta_lj.root ele 2j1t fit
	
	python regroup.py $(INDIR)/0.20000/mu/cos_theta_lj.root $(OUTDIR)/0.20000/mu/cos_theta_lj.root mu  2j1t plot
	python regroup.py $(INDIR)/0.20000/ele/cos_theta_lj.root $(OUTDIR)/0.20000/ele/cos_theta_lj.root ele 2j1t plot
	
	python regroup.py $(INDIR)/2j_0t/0.20000/mu/cos_theta_lj.root $(OUTDIR)/2j_0t/0.20000/mu/cos_theta_lj.root mu  2j0t plot
	python regroup.py $(INDIR)/2j_0t/0.20000/ele/cos_theta_lj.root $(OUTDIR)/2j_0t/0.20000/ele/cos_theta_lj.root ele 2j0t plot
	
	python regroup.py $(INDIR)/3j_1t/0.20000/mu/cos_theta_lj.root $(OUTDIR)/3j_1t/0.20000/mu/cos_theta_lj.root mu  3j1t plot
	python regroup.py $(INDIR)/3j_1t/0.20000/ele/cos_theta_lj.root $(OUTDIR)/3j_1t/0.20000/ele/cos_theta_lj.root ele 3j1t plot
	
	python regroup.py $(INDIR)/3j_2t/0.20000/mu/cos_theta_lj.root $(OUTDIR)/3j_2t/0.20000/mu/cos_theta_lj.root mu  3j2t plot
	python regroup.py $(INDIR)/3j_2t/0.20000/ele/cos_theta_lj.root $(OUTDIR)/3j_2t/0.20000/ele/cos_theta_lj.root ele 3j2t plot
	mkdir -p $(OUTDIR)/0.20000/combined/merged
	hadd -f $(OUTDIR)/0.20000/combined/merged/cos_theta_lj.root $(OUTDIR)/0.20000/mu/merged/cos_theta_lj.root $(OUTDIR)/0.20000/ele/merged/cos_theta_lj.root
	hadd -f $(OUTDIR)/0.20000/combined/cos_theta_lj.root $(OUTDIR)/0.20000/mu/cos_theta_lj.root $(OUTDIR)/0.20000/ele/cos_theta_lj.root
	hadd -f $(OUTDIR)/0.20000/combined/tmatrix_nocharge__gen_ele.root $(OUTDIR)/0.20000/mu/tmatrix_nocharge__gen_ele.root $(OUTDIR)/0.20000/ele/tmatrix_nocharge__gen_ele.root
	hadd -f $(OUTDIR)/0.20000/combined/tmatrix_nocharge__gen_mu.root $(OUTDIR)/0.20000/mu/tmatrix_nocharge__gen_mu.root $(OUTDIR)/0.20000/ele/tmatrix_nocharge__gen_mu.root
	hadd -f $(OUTDIR)/0.20000/combined/tmatrix_nocharge__gen_tau.root $(OUTDIR)/0.20000/mu/tmatrix_nocharge__gen_tau.root $(OUTDIR)/0.20000/ele/tmatrix_nocharge__gen_tau.root

merge3:
	mkdir -p $(OUTDIR)/etajprime_topmass_default/mu
	mkdir -p $(OUTDIR)/etajprime_topmass_default/ele
	cp $(INDIR)/etajprime_topmass_default/mu/tmatrix*.root $(OUTDIR)/etajprime_topmass_default/mu/
	cp $(INDIR)/etajprime_topmass_default/ele/tmatrix*.root $(OUTDIR)/etajprime_topmass_default/ele/
	python regroup.py $(INDIR)/etajprime_topmass_default/mu/cos_theta_lj.root $(OUTDIR)/etajprime_topmass_default/mu/merged/cos_theta_lj.root mu  2j1t fit
	python regroup.py $(INDIR)/etajprime_topmass_default/ele/cos_theta_lj.root $(OUTDIR)/etajprime_topmass_default/ele/merged/cos_theta_lj.root ele 2j1t fit
	
	python regroup.py $(INDIR)/etajprime_topmass_default/mu/cos_theta_lj.root $(OUTDIR)/etajprime_topmass_default/mu/cos_theta_lj.root mu  2j1t plot
	python regroup.py $(INDIR)/etajprime_topmass_default/ele/cos_theta_lj.root $(OUTDIR)/etajprime_topmass_default/ele/cos_theta_lj.root ele 2j1t plot
	
	python regroup.py $(INDIR)/etajprime_topmass_default/mu/cos_theta_lj.root $(OUTDIR)/etajprime_topmass_default/mu/merged/cos_theta_lj.root mu  2j1t fit
	python regroup.py $(INDIR)/etajprime_topmass_default/ele/cos_theta_lj.root $(OUTDIR)/etajprime_topmass_default/ele/merged/cos_theta_lj.root ele 2j1t fit
	
	python regroup.py $(INDIR)/etajprime_topmass_default/mu/cos_theta_lj.root $(OUTDIR)/etajprime_topmass_default/mu/cos_theta_lj.root mu  2j1t plot
	python regroup.py $(INDIR)/etajprime_topmass_default/ele/cos_theta_lj.root $(OUTDIR)/etajprime_topmass_default/ele/cos_theta_lj.root ele 2j1t plot

.PHONY: test
