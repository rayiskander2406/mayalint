from modelChecker.validation_check_base import ValidationCheckBase
from modelChecker import maya_utility

from maya import cmds

class UncenteredPivots(ValidationCheckBase):
    name = "uncentered_pivots"
    label = "Uncentered Pivots"
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        uncentered_pivots = []
        for node in runner.get_maya_nodes():
            node_name = maya_utility.get_name_from_uuid(node)
            if cmds.xform(node_name, q=1, ws=1, rp=1) != [0, 0, 0]:
                uncentered_pivots.append(node)
        return uncentered_pivots