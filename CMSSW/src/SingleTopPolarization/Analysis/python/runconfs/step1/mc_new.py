import sys

from PhysicsTools.PatAlgos.patTemplate_cfg import *
import SingleTopPolarization.Analysis.common.global_tags as global_tags
sys.argv += ["isMC=True", "globalTag="+global_tags.gt_mc]
from SingleTopPolarization.Analysis.pfbreco_stpol_tth_common_cfg import *
