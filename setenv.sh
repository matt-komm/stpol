#STPOL environment script
#Author: Joosep Pata <joosep.pata@cern.ch>
#Usage: source setenv.sh

echo "Setting up stpol env..."
#Note: as much as possible DON'T add references to your privately installed libraries,
#instead try to make some scripts to install them into the working directory of the user
#--JP

# Extract directories
CURRENT_DIR=`pwd`
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CMSSW_VERSION=CMSSW_5_3_11
export CMSSW_VERSION
#if [ -z "$CMSSW_VERSION" ]; then CMSSW_VERSION="CMSSW_5_3_11"; fi
#echo "Current:" $CURRENT_DIR
#echo "Script:" $SCRIPT_DIR

# Set up CMSSW env
export STPOL_DIR=$SCRIPT_DIR
export local_dbs_instance=cms_dbs_ph_analysis_02
export local_dbs_url=https://cmsdbsprod.cern.ch:8443/cms_dbs_ph_analysis_02_writer/servlet/DBSServlet

# Add plotfw to python library path
#PYTHONPATH=$PYTHONPATH:${SCRIPT_DIR}/newplots
#PYTHONPATH=$PYTHONPATH:`readlink -f runconfs`:$STPOL_DIR/:$STPOL_DIR/plots/:$STPOL_DIR/local/lib/python2.6/site-packages/
PYTHONPATH=$PYTHONPATH:$STPOL_DIR/:$STPOL_DIR/plots/:$STPOL_DIR/local/lib/python2.6/site-packages/

#Add QCD estimation stuff
PYTHONPATH=$PYTHONPATH:$STPOL_DIR/qcd_estimation/
PYTHONPATH=$PYTHONPATH:$STPOL_DIR/theta/utils2/

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$STPOL_DIR/local/lib
export LD_RUN_PATH=$LD_RUN_PATH:$STPOL_DIR/local/lib
export PATH=$PATH:$STPOL_DIR/local/bin

if [[ "`hostname`" == *hep.kbfi.ee ]] || [[ "`hostname`" == comp* ]]
then
    echo "Detected that we're on hep.kbfi.ee, sourcing CMS-specific stuff"
    echo ${SCRIPT_DIR}/$CMSSW_VERSION 
    cd ${SCRIPT_DIR}/$CMSSW_VERSION
    source /cvmfs/cms.cern.ch/cmsset_default.sh
    eval `scramv1 runtime -sh`
else
    echo "Detected that we're not on hep.kbfi.ee, environment may be broken!"
    PYTHONPATH=$STPOL_DIR/$CMSSW_VERSION/python/:$PYTHONPATH
    $STPOL_DIR/util/prepare_paths.sh
fi

# Return to original directory
cd $CURRENT_DIR
export PYTHONPATH
