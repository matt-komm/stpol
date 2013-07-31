#include "binnings.h"
#include "utils.hpp"
#include "plotutils.hpp"

plot_compare()
{
	TCanvas *ccomp = new TCanvas("compare","compare",800,600);
	TFile *f1 = new TFile("histos/pseudo_data.root");
	TFile *f2 = new TFile("histos/subtracted_pdata.root");
	
	TH1D *hsignal = (TH1D*)f1->Get(var_y+"__tchan");
	TH1D *hsubtract = (TH1D*)f2->Get(var_y+"__DATA");

	hsignal->Scale(1/hsignal->Integral());
	hsubtract->Scale(1/hsubtract->Integral());

	hsignal->SetLineColor(kRed+1);

	hsignal->SetStats(0);
	hsignal->SetTitle("");
	hsignal->GetXaxis()->SetTitle("Shape of "+varname);
	hsignal->GetYaxis()->SetTitle("Norm. to unit area");
	hsignal->SetMaximum(hsignal->GetMaximum()*1.3);

	hsignal->Draw("HIST");
	hsubtract->Draw("HIST SAME");

	TLegend *leg = new TLegend(0.45,0.76,0.85,0.88);
        leg->AddEntry(hsignal,"Reconstructed signal","l");
        leg->AddEntry(hsubtract,"Subtracted data","l");
        leg->SetTextSize(0.04);
        leg->SetFillColor(0);
	leg->Draw();

	ccomp->Print("plots/compare.pdf");
	ccomp->Print("plots/compare.png");
}

plot_unfolded()
{
	TCanvas *cunf = new TCanvas("unfolded","unfolded",800,600);
	TFile *f1 = new TFile("histos/unfolded.root");
	TFile *f2 = new TFile("histos/rebinned.root");
	TFile *feff = new TFile("histos/efficiency.root");

	TH1D *hunf = (TH1D*)f1->Get("unfolded");
	//TH1D *hgen_presel_rebin = (TH1D*)f2->Get(var_x+"_rebin");
	TH1D *hgen_presel_rebin = (TH1D*)feff->Get("hgen_presel_rebin");

	hgen_presel_rebin->Scale(hunf->Integral()/hgen_presel_rebin->Integral());

	// unfolded and generated in bins of generated divided by bin width
	TH1D *hunf_rebin_width = new TH1D(var_y+"_unf",var_y+"_unf",bin_x,list_x);
	TH1D *hgen_rebin_width = new TH1D(var_x+"_rebin_width",var_x+"_rebin_width",bin_x,list_x);
	
	for(Int_t i = 1; i <= bin_x; i++) {
		hunf_rebin_width->SetBinContent(i,hunf->GetBinContent(i)/(list_x[i]-list_x[i-1]));
		hunf_rebin_width->SetBinError(i,hunf->GetBinError(i));
		hgen_rebin_width->SetBinContent(i,hgen_presel_rebin->GetBinContent(i)/(list_x[i]-list_x[i-1]));
		hgen_rebin_width->SetBinError(i,hgen_presel_rebin->GetBinError(i));
	}

	// color
        hunf_rebin_width->SetLineColor(kRed+1);
        hgen_rebin_width->SetLineColor(kGreen+1);

	hgen_rebin_width->SetStats(0);
	hgen_rebin_width->SetTitle("");
	hgen_rebin_width->SetMaximum(hunf_rebin_width->GetMaximum()*1.1);
	hgen_rebin_width->SetMinimum(0);
	hgen_rebin_width->GetXaxis()->SetTitle(varname);
	hgen_rebin_width->GetYaxis()->SetTitle("Events");
	hgen_rebin_width->Draw("HIST,E");
	hunf_rebin_width->Draw("SAME E");
	
	TLegend *leg = new TLegend(0.25,0.8,0.45,0.88);
        leg->AddEntry(hunf_rebin_width,"Unfolded","l");
        leg->AddEntry(hgen_rebin_width,"Generated","l");
        leg->SetTextSize(0.04);
        leg->SetFillColor(0);
	leg->Draw();

	cunf->Print("plots/unfolded.pdf");
	cunf->Print("plots/unfolded.png");
}

plot_shape()
{	
	TCanvas *ceff = new TCanvas("ceff","efficiency",800,600);
	TFile *f = new TFile("histos/efficiency.root");
	TH1D *hgen_presel = (TH1D*)f->Get("hgen_presel");
	TH1D *hgen = (TH1D*)f->Get("hgen");
	TH1D *hrec = (TH1D*)f->Get("hrec");

	// Normalize
	hgen_presel->Scale(1/hgen_presel->Integral());
	hgen->Scale(1/hgen->Integral());
	hrec->Scale(1/hrec->Integral());
	
	// rebin
	hgen_presel->Rebin(2);
	hgen->Rebin(2);
	hrec->Rebin(2);

	// color
        hrec->SetLineColor(kRed+1);
        hgen->SetLineColor(kGreen+1);
        hgen_presel->SetLineColor(kBlue-1);

	hgen_presel->SetStats(0);
	hgen_presel->SetTitle("");
	hgen_presel->GetXaxis()->SetTitle("Shape of "+varname);
	hgen_presel->GetYaxis()->SetTitle("Norm. to unit area");
	hgen_presel->SetMaximum(hrec->GetMaximum()*1.1);
	hgen_presel->Draw("HIST");
	hgen->Draw("HIST SAME");
	hrec->Draw("HIST SAME");

	TLegend *leg = new TLegend(0.15,0.76,0.55,0.88);
        leg->AddEntry(hgen_presel,"Generated","l");
        leg->AddEntry(hgen,"Generated after cuts","l");
        leg->AddEntry(hrec,"Reconstructed","l");
        leg->SetTextSize(0.04);
        leg->SetFillColor(0);
	leg->Draw();
	
	ceff->Print("plots/shape.pdf");
	ceff->Print("plots/shape.png");
}

plot_asymmetry_pull()
{
	TCanvas *casy = new TCanvas("casy","asymmetry",800,600);
	TFile *f = new TFile("histos/unfolded.root");

	// Plot pull
	TH1D *hasy_pull = (TH1D*)f->Get("asymmetry_pull");
	
	hasy_pull->SetStats(0);
	hasy_pull->SetTitle("");
	hasy_pull->GetXaxis()->SetTitle("Asymmetry pull");
	hasy_pull->GetYaxis()->SetTitle("# PEs");
	
	adaptrange(hasy_pull);
	hasy_pull->SetMaximum(hasy_pull->GetMaximum()*1.3);
	hasy_pull->Draw("HIST");
	
	hasy_pull->Fit("gaus");
	hasy_pull->GetFunction("gaus")->SetLineColor(kBlue);
	TLegend *leg = new TLegend(0.6,0.76,0.85,0.88);
        leg->AddEntry(hasy_pull,"PEs","l");
        leg->AddEntry(hasy_pull->GetFunction("gaus"),"Gaussian fit","l");
        leg->SetTextSize(0.04);
        leg->SetFillColor(0);
	leg->Draw();
	
	Double_t mean = hasy_pull->GetMean();
	Double_t mean_err = hasy_pull->GetMeanError();
	Double_t rms = hasy_pull->GetRMS();
	Double_t rms_err = hasy_pull->GetRMSError();

	//TString info1 = TString::Format("Mean: %.4f#pm%.4f",mean,mean_err);
	//TString info2 = TString::Format("RMS:  %.4f#pm%.4f",rms,rms_err);
	TString info1 = TString::Format("Mean: %.4f",mean);
	TString info2 = TString::Format("RMS:  %.4f",rms);
	TLatex linfo1;
	linfo1.SetNDC();
	linfo1.DrawLatex(0.15,0.85,info1);
	TLatex linfo2;
	linfo2.SetNDC();
	linfo2.DrawLatex(0.15,0.82,info2);

	casy->Print("plots/asymmetry_pull.pdf");
	casy->Print("plots/asymmetry_pull.png");
}

plot_asymmetry_bias()
{
	TCanvas *casy = new TCanvas("casy","asymmetry",800,600);
	TFile *f = new TFile("histos/unfolded.root");

	// Plot bias
	TH1D *hasy_bias = (TH1D*)f->Get("asymmetry_bias");
	
	hasy_bias->SetStats(0);
	hasy_bias->SetTitle("");
	hasy_bias->GetXaxis()->SetTitle("Asymmetry bias");
	hasy_bias->GetYaxis()->SetTitle("# PEs");
	
	adaptrange(hasy_bias);
	hasy_bias->SetMaximum(hasy_bias->GetMaximum()*1.3);
	hasy_bias->Draw("HIST");
	
	hasy_bias->Fit("gaus");
	hasy_bias->GetFunction("gaus")->SetLineColor(kBlue);
	TLegend *leg = new TLegend(0.6,0.76,0.85,0.88);
        leg->AddEntry(hasy_bias,"PEs","l");
        leg->AddEntry(hasy_bias->GetFunction("gaus"),"Gaussian fit","l");
        leg->SetTextSize(0.04);
        leg->SetFillColor(0);
	leg->Draw();
	
	Double_t mean = hasy_bias->GetMean();
	Double_t mean_err = hasy_bias->GetMeanError();
	Double_t rms = hasy_bias->GetRMS();
	Double_t rms_err = hasy_bias->GetRMSError();

	//TString info1 = TString::Format("Mean: %.4f#pm%.4f",mean,mean_err);
	//TString info2 = TString::Format("RMS:  %.4f#pm%.4f",rms,rms_err);
	TString info1 = TString::Format("Mean: %.4f",mean);
	TString info2 = TString::Format("RMS:  %.4f",rms);
	TLatex linfo1;
	linfo1.SetNDC();
	linfo1.DrawLatex(0.15,0.85,info1);
	TLatex linfo2;
	linfo2.SetNDC();
	linfo2.DrawLatex(0.15,0.82,info2);

	casy->Print("plots/asymmetry_bias.pdf");
	casy->Print("plots/asymmetry_bias.png");
}

plot_asymmetry()
{	
	TCanvas *casy = new TCanvas("casy","asymmetry",800,600);
	TFile *f = new TFile("histos/unfolded.root");

	// Plot pull
	TH1D *hasy = (TH1D*)f->Get("asymmetry");
	
	hasy->SetStats(0);
	hasy->SetTitle("");
	hasy->GetXaxis()->SetTitle("Asymmetry");
	hasy->GetYaxis()->SetTitle("# PEs");
	
	adaptrange(hasy);
	hasy->SetMaximum(hasy->GetMaximum()*1.3);
	hasy->Draw("HIST");
	
	hasy->Fit("gaus");
	hasy->GetFunction("gaus")->SetLineColor(kBlue);
	TLegend *leg = new TLegend(0.6,0.76,0.85,0.88);
        leg->AddEntry(hasy,"PEs","l");
        leg->AddEntry(hasy->GetFunction("gaus"),"Gaussian fit","l");
        leg->SetTextSize(0.04);
        leg->SetFillColor(0);
	leg->Draw();
	
	Double_t mean = hasy->GetMean();
	Double_t mean_err = hasy->GetMeanError();
	Double_t rms = hasy->GetRMS();
	Double_t rms_err = hasy->GetRMSError();

	//TString info1 = TString::Format("Mean: %.4f#pm%.4f",mean,mean_err);
	//TString info2 = TString::Format("RMS:  %.4f#pm%.4f",rms,rms_err);
	TString info1 = TString::Format("Mean: %.4f",mean);
	TString info2 = TString::Format("RMS:  %.4f",rms);
	TLatex linfo1;
	linfo1.SetNDC();
	linfo1.DrawLatex(0.15,0.85,info1);
	TLatex linfo2;
	linfo2.SetNDC();
	linfo2.DrawLatex(0.15,0.82,info2);

	casy->Print("plots/asymmetry.pdf");
	casy->Print("plots/asymmetry.png");
}

plot_staterror()
{
	TCanvas *cstaterr = new TCanvas("cstaterr","error",800,600);
	TFile *f = new TFile("histos/unfolded.root");
	TH1D *herror = (TH1D*)f->Get("staterr");
	
	
	herror->SetStats(0);
	herror->SetTitle("");
	herror->GetXaxis()->SetTitle("Asymmetry stat. uncertainty");
	herror->GetYaxis()->SetTitle("# PEs");
	
	adaptrange(herror);
	herror->SetMaximum(herror->GetMaximum()*1.3);
	herror->Draw("HIST");
	
	herror->Fit("gaus");
	herror->GetFunction("gaus")->SetLineColor(kBlue);
	TLegend *leg = new TLegend(0.6,0.76,0.85,0.88);
        leg->AddEntry(herror,"PEs","l");
        leg->AddEntry(herror->GetFunction("gaus"),"Gaussian fit","l");
        leg->SetTextSize(0.04);
        leg->SetFillColor(0);
	leg->Draw();
	
	Double_t mean = herror->GetMean();
	Double_t mean_err = herror->GetMeanError();
	Double_t rms = herror->GetRMS();
	Double_t rms_err = herror->GetRMSError();

	//TString info1 = TString::Format("Mean: %.4f#pm%.4f",mean,mean_err);
	//TString info2 = TString::Format("RMS:  %.4f#pm%.4f",rms,rms_err);
	TString info1 = TString::Format("Mean: %.4f",mean);
	TString info2 = TString::Format("RMS:  %.4f",rms);
	TLatex linfo1;
	linfo1.SetNDC();
	linfo1.DrawLatex(0.15,0.85,info1);
	TLatex linfo2;
	linfo2.SetNDC();
	linfo2.DrawLatex(0.15,0.82,info2);

	cstaterr->Print("plots/asymmetry_staterror.pdf");
	cstaterr->Print("plots/asymmetry_staterror.png");
}

plot_error()
{
	TCanvas *cerror = new TCanvas("cerror","Error matrix",800,600);
	TFile *f = new TFile("histos/unfolded.root");
	TH2D *herror = (TH2D*)f->Get("error");

	herror->SetStats(0);
	herror->Draw("COLZ");
	//herror->Draw("COLZ TEXT");
	cerror->Print("plots/error.pdf");
	cerror->Print("plots/error.png");
}

plot_correlation()
{
	TCanvas *ccorr = new TCanvas("ccorr","Correlation matrix",800,600);
	TFile *f = new TFile("histos/unfolded.root");
	TH2D *hcorr = (TH2D*)f->Get("correlation");

	hcorr->SetStats(0);
	hcorr->Draw("COLZ");
	ccorr->Print("plots/correlation.pdf");
	ccorr->Print("plots/correlation.png");
}

plot_efficiency()
{
	TCanvas *ceff= new TCanvas("ceff","Efficiency",800,600);
	TFile *feff = new TFile("histos/efficiency.root");
	TH1D *heff = (TH1D*)feff->Get("efficiency");
	heff->SetStats(0);
	heff->SetTitle("");
	heff->GetXaxis()->SetTitle("Selection efficiency");
	heff->GetYaxis()->SetTitle("Percentage");

	heff->Draw("HIST E");
	ceff->Print("plots/efficiency.pdf");
	ceff->Print("plots/efficiency.png");
}


plot_matrix()
{
	TCanvas *cmat = new TCanvas("cmat","matrix",800,600);
	TFile *f = new TFile("histos/rebinned.root");
	TH2D *hmat = (TH2D*)f->Get("matrix");

	Int_t nbinsx = hmat->GetNbinsX();
	Int_t nbinsy = hmat->GetNbinsY();
	Double_t *n_x = new Double_t[nbinsx+1];
	Double_t *n_y = new Double_t[nbinsy+1];

	// plot in bins
	for(Int_t i=0;i<=nbinsx;i++) n_x[i] = i;
	for(Int_t i=0;i<=nbinsy;i++) n_y[i] = i;
	
	TH2D *hnew = new TH2D("migmatrix","migmatrix",nbinsx,n_x,nbinsy,n_y);
	

	for(Int_t i=1;i<=nbinsx;i++) {
		TString label = "";
		label += i;
		hnew->GetXaxis()->SetBinLabel(i,label);
	}
	for(Int_t j=1;j<=nbinsy;j++) {
		TString label = "";
		label += j;
		hnew->GetYaxis()->SetBinLabel(j,label);
	}

	for(Int_t i=1;i<=nbinsx;i++) {
		for(Int_t j=1;j<=nbinsy;j++) {
			hnew->SetBinContent(i,j,hmat->GetBinContent(i,j));
		}
	}

	
	hnew->SetTitle("");
	hnew->SetStats(0);
	hnew->GetXaxis()->SetTitle("Bins of generated "+varname);
	hnew->GetYaxis()->SetTitle("Bins of reconstructed "+varname);

	hnew->Draw("COLZ");

	cmat->Print("plots/matrix.pdf");
	cmat->Print("plots/matrix.png");
}

plot_lcurve()
{

	TGraph *lcurve = (TGraph*)f->Get("Graph");

	lcurve->SetTitle("L-curve scan");
	lcurve->Draw("AL");
	//lcurve->GetXaxis()->SetTitle("#chi^{2}");
	//lcurve->GetYaxis()->SetTitle("curvature");
	c1->Print("plots/lcurve.pdf");
	c1->Print("plots/lcurve.png");
}

plot_pseudo()
{
	//gStyle->SetOptStat("mr");
	gStyle->SetOptStat("");

	TFile *f = new TFile("histos/unfolded.root");

	// pull
	TCanvas *c1 = new TCanvas("cpull","pull",800,600);
	c1->Divide(4,2);
	c1->cd();
	for(Int_t i = 1; i <= bin_x; i++) {
		TString pulname = "pull_";
		TString pultitle = "Pull in bin ";
		pulname += i;
		pultitle +=i;
		TH1D *hpull = (TH1D*)f->Get(pulname);
		adaptrange(hpull);
		c1->cd(i);
		hpull->SetMaximum(hpull->GetMaximum()*1.15);
		hpull->SetTitle("");
		hpull->GetXaxis()->SetTitle(pultitle);
		hpull->Draw("HIST E");

		Double_t mean = hpull->GetMean();
		Double_t mean_err = hpull->GetMeanError();
		Double_t rms = hpull->GetRMS();
		Double_t rms_err = hpull->GetRMSError();

		TString info1 = TString::Format("Mean: %.4f#pm%.4f",mean,mean_err);
		TString info2 = TString::Format("RMS:  %.4f#pm%.4f",rms,rms_err);
		TLatex linfo1;
		linfo1.SetNDC();
		linfo1.DrawLatex(0.15,0.85,info1);
		TLatex linfo2;
		linfo2.SetNDC();
		linfo2.DrawLatex(0.15,0.82,info2);

	}
	c1->Print("plots/pull.pdf");
	c1->Print("plots/pull.png");
	
	// reldiff
	TCanvas *c2 = new TCanvas("crel","relative difference",800,600);
	c2->Divide(4,2);
	c2->cd();
	for(Int_t i = 1; i <= bin_x; i++) {
		TString relname = "reldiff_";
		TString reltitle = "Rel. difference in bin ";
		relname += i;
		reltitle += i;
		TH1D *hrel = (TH1D*)f->Get(relname);
		adaptrange(hrel);
		c2->cd(i);
		hrel->SetMaximum(hrel->GetMaximum()*1.15);
		hrel->SetTitle("");
		hrel->GetXaxis()->SetTitle(reltitle);
		hrel->Draw("HIST E");
	
		Double_t mean = hrel->GetMean();
		Double_t mean_err = hrel->GetMeanError();
		Double_t rms = hrel->GetRMS();
		Double_t rms_err = hrel->GetRMSError();

		TString info1 = TString::Format("Mean: %.4f#pm%.4f",mean,mean_err);
		TString info2 = TString::Format("RMS:  %.4f#pm%.4f",rms,rms_err);
		TLatex linfo1;
		linfo1.SetNDC();
		linfo1.DrawLatex(0.15,0.85,info1);
		TLatex linfo2;
		linfo2.SetNDC();
		linfo2.DrawLatex(0.15,0.82,info2);
	}
	c2->Print("plots/reldiff.pdf");
	c2->Print("plots/reldiff.png");
}

plothistos()
{
	plot_unfolded();
	plot_asymmetry();
	plot_asymmetry_bias();
	plot_asymmetry_pull();
	plot_staterror();
	plot_shape();
	plot_pseudo();
	plot_matrix();
	plot_correlation();
	plot_error();
	plot_efficiency();
	//plot_compare();
}
