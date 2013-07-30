#!/bin/env python

from plots.common.sample import *
from plots.common.utils import *
import sys

logger.setLevel(logging.INFO)

if len(sys.argv) < 3:
    print "Usage: ./checkStep3.py step3_1 step3_2"
    sys.exit(1)

flist=[]
flist2=[]

proc='ele'
physics_processes = PhysicsProcess.get_proc_dict(lepton_channel=proc)
merge_cmds = PhysicsProcess.get_merge_dict(physics_processes)

flist += get_file_list(
        merge_cmds,
        sys.argv[1] + "/%s/mc/iso/nominal/Jul15/" % proc
)
flist += get_file_list(
        merge_cmds,
        sys.argv[1] + "/%s/data/iso/Jul15/" % proc
)
flist += get_file_list(
        {'data':merge_cmds['data']},
        sys.argv[1] + "/%s/data/antiiso/Jul15/" % proc
)

flist2 += get_file_list(
        merge_cmds,
        sys.argv[2] + "/%s/mc/iso/nominal/Jul15/" % proc
)
flist2 += get_file_list(
        merge_cmds,
        sys.argv[2] + "/%s/data/iso/Jul15/" % proc
)
flist2 += get_file_list(
        {'data':merge_cmds['data']},
        sys.argv[2] + "/%s/data/antiiso/Jul15/" % proc
)

proc = 'mu'
physics_processes = PhysicsProcess.get_proc_dict(lepton_channel=proc)
merge_cmds = PhysicsProcess.get_merge_dict(physics_processes)

flist += get_file_list(
        merge_cmds,
        sys.argv[1] + "/%s/mc/iso/nominal/Jul15/" % proc
)
flist += get_file_list(
        merge_cmds,
        sys.argv[1] + "/%s/data/iso/Jul15/" % proc
)
flist += get_file_list(
        {'data':merge_cmds['data']},
        sys.argv[1] + "/%s/data/antiiso/Jul15/" % proc
)

flist2 += get_file_list(
        merge_cmds,
        sys.argv[2] + "/%s/mc/iso/nominal/Jul15/" % proc
)
flist2 += get_file_list(
        merge_cmds,
        sys.argv[2] + "/%s/data/iso/Jul15/" % proc
)
flist2 += get_file_list(
        {'data':merge_cmds['data']},
        sys.argv[2] + "/%s/data/antiiso/Jul15/" % proc
)
flist.sort()
flist2.sort()

for f1,f2 in zip(flist,flist2):
    s1 = Sample.fromFile(f1)
    s2 = Sample.fromFile(f2)
    if s1.getEventCount() != s2.getEventCount() or s1.getEntries('n_jets == 3') != s2.getEntries('n_jets == 3'):
        print "CRAP:",f1,s1.getEventCount(),s1.getEntries('n_jets == 3'),f2,s2.getEventCount(),s2.getEntries('n_jets == 3')
