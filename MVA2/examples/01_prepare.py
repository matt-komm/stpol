from MVA2 import common

# different use options

#~ signals = ["T_t_ToLeptons", "Tbar_t_ToLeptons"]
#~ backgrounds = ["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"]
#~ common.prepare_files(signals, backgrounds, ofname="mypreparedfile.root", default_ratio = 0.5)

signals = {"T_t_ToLeptons": 0.5, "Tbar_t_ToLeptons": 0.4}
backgrounds = {"W1Jets_exclusive": 0.2, "W2Jets_exclusive": 0.2, "W3Jets_exclusive": 0.3, "W4Jets_exclusive": 0.2}
common.prepare_files(signals, backgrounds)


