#!/bin/env python

import argparse
from plots.common.sample import Sample
from plots.common.plot_defs import cutlist
from plots.common.utils import *
from plots.common.cuts import *

logger.setLevel(logging.ERROR)

cut={}
cut['ele']=str(cutlist['2j1t']*cutlist['final_ele']*Cuts.met)
cut['mu']=str(cutlist['2j1t']*cutlist['final_mu']*Cuts.mt_mu)
cut['ele_pre']=str(cutlist['2j1t']*cutlist['presel_ele']*Cuts.met)
cut['mu_pre']=str(cutlist['2j1t']*cutlist['presel_mu']*Cuts.mt_mu)

parser = argparse.ArgumentParser( description='Finds optimal BDT cut' )
parser.add_argument(
    "--indir", type=str, required=False, default=(os.environ["STPOL_DIR"] + "/step3_latest"),
    help="the input directory"
)

args = parser.parse_args()

lumi=19700

for proc in ['ele', 'mu']:
    physics_processes = PhysicsProcess.get_proc_dict(lepton_channel=proc)
    merge_cmds = PhysicsProcess.get_merge_dict(physics_processes) 
    flist = get_file_list({'signal': merge_cmds['tchan']}, args.indir + "/%s/mc/iso/nominal/Jul15/" % proc)
    weight_str = str(Weights.total(proc) *
                     Weights.wjets_madgraph_shape_weight() *
                     Weights.wjets_madgraph_flat_weight())
    samples={}
    for f in flist:
        samples[f] = Sample.fromFile(f)
    yld = 0;
    yld_pre = 0;
    for k,v in samples.items():
        yld+=v.getTree().Draw('cos_theta',weight_str+'*('+cut[proc]+')','goff BATCH')*v.lumiScaleFactor(lumi)
        yld_pre+=v.getTree().Draw('cos_theta',weight_str+'*('+cut[proc+'_pre']+')','goff BATCH')*v.lumiScaleFactor(lumi)
    print "Channel="+proc+": Yields -> final="+str(yld),'presel='+str(yld_pre),"eff="+str(yld/yld_pre)
