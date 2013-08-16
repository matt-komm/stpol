import re
import os
import logging
logger = logging.getLogger("sample_types")
logger.setLevel(logging.WARNING)
class SampleInfo:
    def __init__(self, **kwargs):
        self.props = []
        for k, v in kwargs.items():
            setattr(self, k, v)

    def has(self, prop, ret=False):
        pat = re.compile(prop)
        matches = [p for p in self.props if pat.match(p)]
        if not ret:
            return len(matches)>0
        else:
            return matches
    @staticmethod
    def from_line(line):
        elems = line.split()
        name = elems[0]
        props = elems[1:]

        return SampleInfo(
            name=name,
            props=props,
            subprocess=elems[2],
            process=elems[3]
        )

def is_wjets_mg(sample_name):
    if re.match("w[0-9]jets_exclusive.*", sample_name.lower()):
    	return True
    else:
    	return False

def is_wjets(sample_name):
    return is_wjets_mg(sample_name) or sample_name.lower().startswith("wjets")

def is_ttbar(sample_name):
    return sample_name.lower().startswith("ttjets") or sample_name.lower().startswith("ttbar")

def is_signal(sample_name):
    return sample_name.lower() in ["t_t_toleptons", "tbar_t_toleptons", "t_t", "tbar_t"] or sample_name.lower().startswith("ttob") or sample_name.lower().startswith("t_t") or sample_name.lower().startswith("tbar_t")

def is_mc(name):
    return not ("SingleMu" in name or "SingleEle" in name or "data" in name)

def sample_info(sample_name):
    si = None
    if is_wjets(sample_name):
        si = SampleInfo(process="wjets")
    elif is_ttbar(sample_name):
        si = SampleInfo(process="ttbar")
    elif is_signal(sample_name):
        si = SampleInfo(process="tchan")
    if not hasattr(si, "process"):
        raise ValueError("Couldn't parse sample info: %s => %s" % (sample_name, si))
    return si

sample_infos = {}
fi = open(os.path.join(os.environ["STPOL_DIR"], "datasets", "sample_descs.txt"))
for li in fi.readlines():
    if len(li)==0:
        continue
    try:
        si = SampleInfo.from_line(li)
    except:
        logger.info("Skipping line: '%s'" % li)
    sample_infos[si.name] = si
