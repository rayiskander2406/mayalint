from modelChecker.validation_check_base import ValidationCheckBase
from modelChecker import maya_utility

from maya import cmds

class LayersCheck(ValidationCheckBase):
    name = "layers"
    label = "Layers"
    category = "General"
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        layers = []
        for node in runner.get_maya_nodes():
            node_name = maya_utility.get_name_from_uuid(node)
            layer = cmds.listConnections(node_name, type="displayLayer")
            if layer:
                layers.append(node)
        return layers
    
    
    