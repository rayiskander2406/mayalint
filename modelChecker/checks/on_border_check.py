from collections import defaultdict

import maya.api.OpenMaya as om

from modelChecker.constants import NodeType
from modelChecker.validation_check_base import ValidationCheckBase

TOLERANCE = 0.00001

class OnBorderCheck(ValidationCheckBase):
    name = "on_border"
    label = "On Border"
    category = "UVs"
    node_type = NodeType.UV
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        on_border = defaultdict(list)
        for dag_path in runner.get_mesh_iterator():
            mesh = om.MFnMesh(dag_path)
            fn = om.MFnDependencyNode(dag_path.node())
            uuid = fn.uuid().asString()
            Us, Vs = mesh.getUVs()
            for i in range(len(Us)):
                if abs(int(Us[i]) - Us[i]) < TOLERANCE or abs(int(Vs[i]) - Vs[i]) < TOLERANCE:
                    on_border[uuid].append(i)
        return on_border