from modelChecker.validation_check_base import ValidationCheckBase
from modelChecker import maya_utility, usd_utility
from modelChecker.constants import NodeType

from pxr import UsdGeom, Usd

from maya import cmds

TOLERENCE = 0.0001

class OnGridCheck(ValidationCheckBase):
    name = "on_grid"
    label = "On Grid"
    category = "General"
    description = f"Root nodes that are further than {TOLERENCE} from the grid will fail."
    node_type = NodeType.NODE
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        output = []
        
        for uuid in runner.get_maya_root_nodes():
            node_name = maya_utility.get_name_from_uuid(uuid)
            bounding_box = cmds.exactWorldBoundingBox(node_name)
            min_y = bounding_box[1]
            if abs(min_y) > TOLERENCE:
                output.append(uuid)
        
        return output
    
    
    def usd_run(self, runner):
        output = []
        for node in runner.get_usd_root_nodes():
            try:
                proxy_path, prim = usd_utility.get_stage_and_prim(node)
                stage = usd_utility.get_stage_from_proxy(proxy_path)
                prim = stage.GetPrimAtPath(prim)
                
                bbox_cache = UsdGeom.BBoxCache(
                    time=Usd.TimeCode.Default(), 
                    includedPurposes=[UsdGeom.Tokens.default_]
                )

                for child in Usd.PrimRange(prim):
                    bbox = bbox_cache.ComputeWorldBound(child)
                    min_y = bbox.GetRange().GetMin()[1]
                    
                    if abs(min_y) > TOLERENCE:
                        output.append(node)
                        break  
                    
            except Exception as e:
                print(f"Error processing node {node}: {e}")
                continue

        return output