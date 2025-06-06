from modelChecker.validation_check_base import ValidationCheckBase
from modelChecker.constants import DataType
from modelChecker import maya_utility

from maya import cmds

class UnfrozenTransformsCheck(ValidationCheckBase):
    name = "unfrozen_transforms"
    label = "Unfrozen Transforms"
    category = "General"
    data_type = DataType.Node
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        unfrozen_transforms = []
        for node in runner.get_maya_nodes():
            node_name = maya_utility.get_name_from_uuid(node)
            translation = cmds.xform(node_name, query=True, worldSpace=True, translation=True)
            rotation = cmds.xform(node_name, q=True, worldSpace=True, rotation=True)
            scale = cmds.xform(node_name, q=True, worldSpace=True, scale=True)
            if translation != [0.0, 0.0, 0.0] or rotation != [0.0, 0.0, 0.0] or scale != [1.0, 1.0, 1.0]:
                unfrozen_transforms.append(node)
        return unfrozen_transforms