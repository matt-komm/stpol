void maketest()
{
	TFile *fo = new TFile("trees/fake.root","RECREATE");
	//TH2D *m = new TH2D("m","matrix",5,-1,1,10,-1,1);

	TTree *t = new TTree("SKITA","test");
	
	// TRandom3 without 0 has default seed 
	TRandom3 rng(1337);
	cout << "seed: " << rng.GetSeed() << endl;

	Double_t weight = 1.0;
	Double_t var_gen = 0;
	Double_t var_rec = 0;
	
	t->Branch("weight", &weight);
	t->Branch("fake", &var_rec);
	t->Branch("MC_fake", &var_gen);

	for(Int_t i=0; i<100000; i++) {
		Double_t rnd = rng.Gaus(0,0.3);
		// generated
		var_gen = rng.Uniform(-1,1);
		
		// reconstructed
		var_rec = var_gen+rnd;

		//m->Fill(var_gen,var_rec);
		//cout << var_gen << " " << var_rec << endl;
		t->Fill();
	}

	//m->Draw("COLZ");

	t->Write();
	fo->Close();
}
