import MVA2.common

#~ MVA2.common.prepare_files(MVA2.common.samples.signal, MVA2.common.samples.ttbar + MVA2.common.samples.WJets, ofname = "prepared_WJets_ttbar.root", lept = "mu", default_ratio = 0.1)
#~ MVA2.common.prepare_files(MVA2.common.samples.signal, MVA2.common.samples.WJets, ofname = "prepared_WJets.root", lept = "mu", default_ratio = 0.1)
#~ MVA2.common.prepare_files(MVA2.common.samples.signal, MVA2.common.samples.WJets + MVA2.common.samples.other, ofname = "prepared_all_mu.root", lept = "mu", default_ratio = 0.1)
MVA2.common.prepare_files(MVA2.common.samples.signal, MVA2.common.samples.WJets + MVA2.common.samples.other, ofname = "prepared_all_el.root", lept = "ele", default_ratio = 0.1)
