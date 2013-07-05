import re

def is_wjets(sample_name):
    return re.match("w[0-9]jets.*", sample_name.lower()) or sample_name.lower().startswith("wjets")

def is_ttbar(sample_name):
    return sample_name.lower().startswith("ttjets") or sample_name.lower().startswith("ttbar")

def is_signal(sample_name):
    return sample_name.lower() in ["t_t_toleptons", "tbar_t_toleptons", "t_t", "tbar_t"] or sample_name.lower().startswith() ["ttob"]
