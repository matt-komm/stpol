import sys

from PhysicsTools.PatAlgos.patTemplate_cfg import *
import SingleTopPolarization.Analysis.common.global_tags as global_tags
sys.argv += ["isMC=False", "globalTag="+global_tags.gt_data]
from UserCode.TTHPAT.pfbreco_stpol_tth_common_cfg import *
