void adaptrange(TH1* histo)
{
	Double_t newmin = histo->GetXaxis()->GetBinLowEdge(histo->FindFirstBinAbove(0));
	Double_t newmax = histo->GetXaxis()->GetBinUpEdge(histo->FindLastBinAbove(0));

	histo->GetXaxis()->SetRangeUser(newmin, newmax);
}
