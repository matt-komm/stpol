import MVA2.common

signals = {
	"T_t_ToLeptons": 0.5, 
	"Tbar_t_ToLeptons": 0.5,
}

backgrounds = {
	"W1Jets_exclusive": 0.5, 
	"W2Jets_exclusive": 0.5, 
	"W3Jets_exclusive": 0.5, 
	"W4Jets_exclusive": 0.5,
}


MVA2.common.prepare_files(signals, backgrounds, lept = "mu")


