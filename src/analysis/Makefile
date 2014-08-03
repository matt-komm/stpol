include ../analysis/Makefile.options

INDIR=../../results/hists/Aug1/bdt_scan/hists/
OUTDIR=../../results/hists/Aug1/merged

clean:
	rm -Rf $(OUTDIR)


test:
	julia evloop2.jl test.txt infile.json 0 10000 /hdfs/local/joosep/stpol/skims/step3_v2/Jul4_newsyst_newvars_metshift/iso/nominal/T_t_ToLeptons/837/output.root

merge:
	python regroup.py $(INDIR)/preselection/2j_1t/mu/bdt_sig_bg.root $(OUTDIR)/preselection/2j_1t/mu/merged/bdt_sig_bg.root mu 2j1t fit
	python regroup.py $(INDIR)/preselection/3j_2t/mu/bdt_sig_bg.root $(OUTDIR)/preselection/3j_2t/mu/merged/bdt_sig_bg.root mu 3j2t fit
	
	python regroup.py $(INDIR)/preselection/2j_1t/ele/bdt_sig_bg.root $(OUTDIR)/preselection/2j_1t/ele/merged/bdt_sig_bg.root ele 2j1t fit
	python regroup.py $(INDIR)/preselection/3j_2t/ele/bdt_sig_bg.root $(OUTDIR)/preselection/3j_2t/ele/merged/bdt_sig_bg.root ele 3j2t fit

	@for lep in mu ele; do \
	  for var in $(INDIR)/preselection/2j_1t/$$lep/*.root; do \
	    fn=`basename $$var` ; \
	    python regroup.py $$var $(OUTDIR)/preselection/2j_1t/$$lep/$$fn $$lep 2j1t plot ; \
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



merge2:
	mkdir -p $(OUTDIR)/0.60000/mu
	mkdir -p $(OUTDIR)/0.60000/ele
	cp $(INDIR)/0.60000/mu/tmatrix*.root $(OUTDIR)/0.60000/mu/
	cp $(INDIR)/0.60000/ele/tmatrix*.root $(OUTDIR)/0.60000/ele/
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

.PHONY: test
