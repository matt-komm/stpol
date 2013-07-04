echo "Setting up stpol env..."

# Extract directories
CURRENT_DIR=`pwd`
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CMSSW_DIR=$1
if [ -z "$CMSSW_DIR" ]; then CMSSW_DIR="CMSSW_5_3_11"; fi
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

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/scratch/mario/boost_1_53_0/lib

cd ${SCRIPT_DIR}/$CMSSW_DIR
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`

# Return to original directory
cd $CURRENT_DIR

