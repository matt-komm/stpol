#STPOL environment script
#Author: Joosep Pata <joosep.pata@cern.ch>
#Usage: source setenv.sh

echo "Setting up stpol env..."

CURRENT_DIR=`pwd`
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export STPOL_DIR=$SCRIPT_DIR
echo STPOL_DIR=$STPOL_DIR

cd $SCRIPT_DIR/CMSSW
echo "pwd="`pwd`
echo "calling cmsenv..."
eval `scram runtime -sh`

cd $CURRENT_DIR

#Note: as much as possible DON'T add references to your privately installed libraries,
#instead try to make some scripts to install them into the working directory of the user
#--JP
#
## Extract directories
#SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#CMSSW_VERSION=CMSSW_5_3_11
#export CMSSW_VERSION
#
## Set up CMSSW env
#export STPOL_DIR=$SCRIPT_DIR
#export local_dbs_instance=cms_dbs_ph_analysis_02
#export local_dbs_url=https://cmsdbsprod.cern.ch:8443/cms_dbs_ph_analysis_02_writer/servlet/DBSServlet
#
## Add plotfw to python library path
##FIXME: is this really necessary?
#PYTHONPATH=$PYTHONPATH:$STPOL_DIR/:$STPOL_DIR/plots/:$STPOL_DIR/mvatools:$STPOL_DIR/local/lib/python2.6/site-packages/:$STPOL_DIR/local/lib/python2.7/site-packages/
#
##Add QCD estimation stuff
##FIXME: this is probably not really necessary, and should actually be considered harmful
#PYTHONPATH=$PYTHONPATH:$STPOL_DIR/qcd_estimation/
#PYTHONPATH=$PYTHONPATH:$STPOL_DIR/local/theta/utils2/
#PYTHONPATH=$PYTHONPATH:$STPOL_DIR/final_fit/
#PYTHONPATH=$PYTHONPATH:$STPOL_DIR/src/
#
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$STPOL_DIR/local/lib:$STPOL_DIR/local/hdf5-1.8.9-linux-x86_64-shared/lib
#
##Only for OSX
#export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:$STPOL_DIR/local/lib
#
##export LD_RUN_PATH=$LD_RUN_PATH:$STPOL_DIR/local/lib
#export PATH=$PATH:$STPOL_DIR/local/bin
#
#if [[ "`hostname`" == *hep.kbfi.ee ]] || [[ "`hostname`" == comp* ]]
#then
#    echo "Detected that we're on hep.kbfi.ee, sourcing CMS-specific stuff"
#    echo ${SCRIPT_DIR}/$CMSSW_VERSION 
#    cd ${SCRIPT_DIR}/$CMSSW_VERSION
#    source /cvmfs/cms.cern.ch/cmsset_default.sh
#    scramv1 runtime -sh > /dev/null && eval `scramv1 runtime -sh` || echo "ERROR: CMSSW was not properly set up in "pwd", try running ./setup.sh and reading README.md. Some things may nevertheless work."
#else
#    echo "Detected that we're not on hep.kbfi.ee, environment may be broken!"
#    PYTHONPATH=$STPOL_DIR/$CMSSW_VERSION/python/:$PYTHONPATH
#    $STPOL_DIR/util/prepare_paths.sh
#fi
#
## Return to original directory
#cd $CURRENT_DIR
#export PYTHONPATH
