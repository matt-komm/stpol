#!/bin/bash

FLDIR=/home/joosep/singletop/stpol2/filelist_step2_latest
run_samples() {
    OUTDIR=$1
    SCRIPT=$2
    mkdir -p $OUTDIR
    $STPOL_DIR/analysis_step3/slurm_sub_step3.sh $FLDIR/iso/nominal/mc/T_t.txt $OUTDIR/T_t $SCRIPT
    $STPOL_DIR/analysis_step3/slurm_sub_step3.sh $FLDIR/iso/nominal/mc/Tbar_t.txt $OUTDIR/Tbar_t $SCRIPT
    $STPOL_DIR/analysis_step3/slurm_sub_step3.sh $FLDIR/iso/nominal/mc/T_t_ToLeptons.txt $OUTDIR/T_t_ToLeptons $SCRIPT
    $STPOL_DIR/analysis_step3/slurm_sub_step3.sh $FLDIR/iso/nominal/mc/Tbar_t_ToLeptons.txt $OUTDIR/Tbar_t_ToLeptons $SCRIPT
    $STPOL_DIR/analysis_step3/slurm_sub_step3.sh $FLDIR/iso/nominal/mc/TTJets_MassiveBinDECAY.txt $OUTDIR/TTJets_MassiveBinDECAY $SCRIPT
    $STPOL_DIR/analysis_step3/slurm_sub_step3.sh $FLDIR/iso/nominal/mc/TTJets_FullLept.txt $OUTDIR/TTJets_FullLept $SCRIPT
    $STPOL_DIR/analysis_step3/slurm_sub_step3.sh $FLDIR/iso/nominal/mc/TTJets_SemiLept.txt $OUTDIR/TTJets_SemiLept $SCRIPT
    $STPOL_DIR/analysis_step3/slurm_sub_step3.sh $FLDIR/iso/nominal/mc/W1Jets_exclusive.txt $OUTDIR/W1Jets_exclusive $SCRIPT
    $STPOL_DIR/analysis_step3/slurm_sub_step3.sh $FLDIR/iso/nominal/mc/W2Jets_exclusive.txt $OUTDIR/W2Jets_exclusive $SCRIPT
    $STPOL_DIR/analysis_step3/slurm_sub_step3.sh $FLDIR/iso/nominal/mc/W3Jets_exclusive.txt $OUTDIR/W3Jets_exclusive $SCRIPT
    $STPOL_DIR/analysis_step3/slurm_sub_step3.sh $FLDIR/iso/nominal/mc/W4Jets_exclusive.txt $OUTDIR/W4Jets_exclusive $SCRIPT
    $STPOL_DIR/analysis_step3/slurm_sub_step3.sh $FLDIR/iso/nominal/mc/WJets_inclusive.txt $OUTDIR/WJets_inclusive $SCRIPT
}

OUTDIR=$STPOL_DIR/out_b_effs/2J_nocut/mu
SCRIPT="$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/b_effs/step3_beffs_base.py --isMC --lep=mu --doNJets --nJ=2,2"
run_samples $OUTDIR "$SCRIPT"

OUTDIR=$STPOL_DIR/out_b_effs/2J_nocut/ele
SCRIPT="$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/b_effs/step3_beffs_base.py --isMC --lep=ele --doNJets --nJ=2,2"
run_samples $OUTDIR "$SCRIPT"

OUTDIR=$STPOL_DIR/out_b_effs/3J_nocut/mu
SCRIPT="$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/b_effs/step3_beffs_base.py --isMC --lep=mu --doNJets --nJ=3,10"
run_samples $OUTDIR "$SCRIPT"

OUTDIR=$STPOL_DIR/out_b_effs/3J_nocut/ele
SCRIPT="$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/b_effs/step3_beffs_base.py --isMC --lep=ele --doNJets --nJ=3,10"
run_samples $OUTDIR "$SCRIPT"

OUTDIR=$STPOL_DIR/out_b_effs/2J_mtw/mu
SCRIPT="$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/b_effs/step3_beffs_base.py --isMC --lep=mu --mtw --doNJets --nJ=2,2"
run_samples $OUTDIR "$SCRIPT"

OUTDIR=$STPOL_DIR/out_b_effs/2J_met/ele
SCRIPT="$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/b_effs/step3_beffs_base.py --isMC --lep=ele --met --doNJets --nJ=2,2"
run_samples $OUTDIR "$SCRIPT"

OUTDIR=$STPOL_DIR/out_b_effs/3J_mtw/mu
SCRIPT="$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/b_effs/step3_beffs_base.py --isMC --lep=mu --mtw --doNJets --nJ=3,10"
run_samples $OUTDIR "$SCRIPT"

OUTDIR=$STPOL_DIR/out_b_effs/3J_met/ele
SCRIPT="$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/b_effs/step3_beffs_base.py --isMC --lep=ele --met --doNJets --nJ=3,10"
run_samples $OUTDIR "$SCRIPT"


OUTDIR=$STPOL_DIR/out_b_effs/2J_mtw_mtop/mu
SCRIPT="$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/b_effs/step3_beffs_base.py --isMC --lep=mu --mtw --mtop --doNJets --nJ=2,2"
run_samples $OUTDIR "$SCRIPT"

OUTDIR=$STPOL_DIR/out_b_effs/2J_met_mtop/ele
SCRIPT="$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/b_effs/step3_beffs_base.py --isMC --lep=ele --met --mtop --doNJets --nJ=2,2"
run_samples $OUTDIR "$SCRIPT"

OUTDIR=$STPOL_DIR/out_b_effs/3J_mtw_mtop/mu
SCRIPT="$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/b_effs/step3_beffs_base.py --isMC --lep=mu --mtw --mtop --doNJets --nJ=3,10"
run_samples $OUTDIR "$SCRIPT"

OUTDIR=$STPOL_DIR/out_b_effs/3J_met_mtop/ele
SCRIPT="$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/b_effs/step3_beffs_base.py --isMC --lep=ele --met --mtop --doNJets --nJ=3,10"
run_samples $OUTDIR "$SCRIPT"

OUTDIR=$STPOL_DIR/out_b_effs/2J_mtw_mtop_etalj/mu
SCRIPT="$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/b_effs/step3_beffs_base.py --isMC --lep=mu --mtw --mtop --etalj --doNJets --nJ=2,2"
run_samples $OUTDIR "$SCRIPT"

OUTDIR=$STPOL_DIR/out_b_effs/2J_met_mtop_etalj/ele
SCRIPT="$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/b_effs/step3_beffs_base.py --isMC --lep=ele --met --mtop --etalj --doNJets --nJ=2,2"
run_samples $OUTDIR "$SCRIPT"

OUTDIR=$STPOL_DIR/out_b_effs/3J_mtw_mtop_etalj/mu
SCRIPT="$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/b_effs/step3_beffs_base.py --isMC --lep=mu --mtw --mtop --etalj --doNJets --nJ=3,10"
run_samples $OUTDIR "$SCRIPT"

OUTDIR=$STPOL_DIR/out_b_effs/3J_met_mtop_etalj/ele
SCRIPT="$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/b_effs/step3_beffs_base.py --isMC --lep=ele --met --mtop --etalj --doNJets --nJ=3,10"
run_samples $OUTDIR "$SCRIPT"
