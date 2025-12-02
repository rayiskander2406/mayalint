"""
Comprehensive Validation Script for Academic Extension Checks
==============================================================================

This script tests ALL 15 new checks added in the Academic Extension.
Copy the MAYA_VALIDATION_SCRIPT into Maya's Script Editor and execute.

CHECKS TESTED:
  1. flippedNormals        - Detects inverted face normals
  2. overlappingVertices   - Finds vertices at same position
  3. polyCountLimit        - Flags high-poly meshes
  4. missingTextures       - Detects broken texture paths
  5. defaultMaterials      - Finds objects with lambert1
  6. sceneUnits            - Validates scene unit settings
  7. uvDistortion          - Detects stretched/compressed UVs
  8. texelDensity          - Checks UV texel consistency
  9. textureResolution     - Validates texture dimensions
 10. unusedNodes           - Finds orphaned nodes
 11. hiddenObjects         - Detects hidden geometry
 12. namingConvention      - Validates naming patterns
 13. hierarchyDepth        - Checks nesting depth
 14. concaveFaces          - Detects non-convex polygons
 15. intermediateObjects   - Finds construction history objects

==============================================================================
"""

MAYA_VALIDATION_SCRIPT = '''
##############################################################################
#  ACADEMIC EXTENSION - COMPREHENSIVE VALIDATION SCRIPT
#  Copy this entire script into Maya's Script Editor and execute
##############################################################################

import maya.cmds as cmds
import maya.api.OpenMaya as om
from collections import defaultdict
import traceback

# Try to import modelChecker
try:
    from modelChecker import modelChecker_commands as mc
    MODELCHECKER_AVAILABLE = True
except ImportError:
    print("ERROR: modelChecker not found in Python path!")
    print("Add the modelChecker parent directory to your PYTHONPATH")
    MODELCHECKER_AVAILABLE = False

##############################################################################
# HELPER FUNCTIONS
##############################################################################

def get_transform_uuids(exclude_cameras=True):
    """Get UUIDs for all transform nodes."""
    transforms = cmds.ls(type='transform', long=True) or []
    if exclude_cameras:
        default_cams = ['|front', '|persp', '|side', '|top']
        transforms = [t for t in transforms if t not in default_cams]
    uuids = []
    for t in transforms:
        uuid = cmds.ls(t, uuid=True)
        if uuid:
            uuids.append(uuid[0])
    return uuids

def get_mesh_selection_list():
    """Get MSelectionList of all mesh shapes."""
    meshes = cmds.ls(type='mesh', long=True) or []
    sel = om.MSelectionList()
    for mesh in meshes:
        try:
            sel.add(mesh)
        except:
            pass
    return sel

def create_test_scene():
    """Create a scene with various test objects."""
    cmds.file(new=True, force=True)
    print("Creating test scene...")

    created = {}

    # 1. Clean cube (should pass most checks)
    cube = cmds.polyCube(name='clean_cube')[0]
    cmds.delete(cube, constructionHistory=True)
    created['clean_cube'] = cube

    # 2. Hidden object
    hidden = cmds.polyCube(name='hidden_cube')[0]
    cmds.delete(hidden, constructionHistory=True)
    cmds.hide(hidden)
    created['hidden_cube'] = hidden

    # 3. Deep hierarchy
    parent = cmds.group(empty=True, name='level1')
    for i in range(2, 8):
        child = cmds.group(empty=True, name='level{}'.format(i), parent=parent)
        parent = child
    deep_cube = cmds.polyCube(name='deep_cube')[0]
    cmds.delete(deep_cube, constructionHistory=True)
    cmds.parent(deep_cube, parent)
    created['deep_cube'] = deep_cube

    # 4. Bad naming (trailing numbers)
    bad_name = cmds.polyCube(name='cube_001')[0]
    cmds.delete(bad_name, constructionHistory=True)
    created['bad_name'] = bad_name

    # 5. Object with intermediate (via lattice deformer)
    deformed = cmds.polyCube(name='deformed_cube')[0]
    cmds.lattice(deformed, divisions=(2, 2, 2))
    created['deformed_cube'] = deformed

    # 6. High poly object
    highpoly = cmds.polySphere(name='highpoly_sphere', subdivisionsX=50, subdivisionsY=50)[0]
    cmds.delete(highpoly, constructionHistory=True)
    created['highpoly_sphere'] = highpoly

    # 7. Object with default material (already has lambert1)
    default_mat = cmds.polyCube(name='default_material_cube')[0]
    cmds.delete(default_mat, constructionHistory=True)
    created['default_material_cube'] = default_mat

    # 8. Concave face (L-shaped polygon)
    # Create a plane and delete a corner vertex to make concave
    plane = cmds.polyPlane(name='concave_plane', sx=2, sy=2)[0]
    cmds.delete(plane, constructionHistory=True)
    # Merge some vertices to create a concave face
    cmds.polyMergeVertex(plane + '.vtx[0]', plane + '.vtx[1]', distance=0.1)
    created['concave_plane'] = plane

    print("  Created {} test objects".format(len(created)))
    return created

##############################################################################
# TEST FUNCTIONS
##############################################################################

def test_flipped_normals():
    """Test flippedNormals check."""
    try:
        sel = get_mesh_selection_list()
        result_type, result_data = mc.flippedNormals(None, sel)
        return True, len(result_data), "polygon"
    except Exception as e:
        return False, str(e), None

def test_overlapping_vertices():
    """Test overlappingVertices check."""
    try:
        sel = get_mesh_selection_list()
        result_type, result_data = mc.overlappingVertices(None, sel)
        count = sum(len(v) for v in result_data.values()) if isinstance(result_data, dict) else len(result_data)
        return True, count, "vertex"
    except Exception as e:
        return False, str(e), None

def test_poly_count_limit():
    """Test polyCountLimit check."""
    try:
        transforms = get_transform_uuids()
        result_type, result_data = mc.polyCountLimit(transforms, None)
        return True, len(result_data), "nodes"
    except Exception as e:
        return False, str(e), None

def test_missing_textures():
    """Test missingTextures check."""
    try:
        result_type, result_data = mc.missingTextures(None, None)
        return True, len(result_data), "nodes"
    except Exception as e:
        return False, str(e), None

def test_default_materials():
    """Test defaultMaterials check."""
    try:
        transforms = get_transform_uuids()
        result_type, result_data = mc.defaultMaterials(transforms, None)
        return True, len(result_data), "nodes"
    except Exception as e:
        return False, str(e), None

def test_scene_units():
    """Test sceneUnits check."""
    try:
        result_type, result_data = mc.sceneUnits(None, None)
        return True, len(result_data), "scene"
    except Exception as e:
        return False, str(e), None

def test_uv_distortion():
    """Test uvDistortion check."""
    try:
        sel = get_mesh_selection_list()
        result_type, result_data = mc.uvDistortion(None, sel)
        count = sum(len(v) for v in result_data.values()) if isinstance(result_data, dict) else len(result_data)
        return True, count, "polygon"
    except Exception as e:
        return False, str(e), None

def test_texel_density():
    """Test texelDensity check."""
    try:
        sel = get_mesh_selection_list()
        result_type, result_data = mc.texelDensity(None, sel)
        return True, len(result_data), "nodes"
    except Exception as e:
        return False, str(e), None

def test_texture_resolution():
    """Test textureResolution check."""
    try:
        result_type, result_data = mc.textureResolution(None, None)
        return True, len(result_data), "nodes"
    except Exception as e:
        return False, str(e), None

def test_unused_nodes():
    """Test unusedNodes check."""
    try:
        result_type, result_data = mc.unusedNodes(None, None)
        return True, len(result_data), "nodes"
    except Exception as e:
        return False, str(e), None

def test_hidden_objects():
    """Test hiddenObjects check."""
    try:
        transforms = get_transform_uuids()
        result_type, result_data = mc.hiddenObjects(transforms, None)
        return True, len(result_data), "nodes"
    except Exception as e:
        return False, str(e), None

def test_naming_convention():
    """Test namingConvention check."""
    try:
        transforms = get_transform_uuids()
        result_type, result_data = mc.namingConvention(transforms, None)
        return True, len(result_data), "nodes"
    except Exception as e:
        return False, str(e), None

def test_hierarchy_depth():
    """Test hierarchyDepth check."""
    try:
        transforms = get_transform_uuids()
        result_type, result_data = mc.hierarchyDepth(transforms, None)
        return True, len(result_data), "nodes"
    except Exception as e:
        return False, str(e), None

def test_concave_faces():
    """Test concaveFaces check."""
    try:
        sel = get_mesh_selection_list()
        result_type, result_data = mc.concaveFaces(None, sel)
        count = sum(len(v) for v in result_data.values()) if isinstance(result_data, dict) else len(result_data)
        return True, count, "polygon"
    except Exception as e:
        return False, str(e), None

def test_intermediate_objects():
    """Test intermediateObjects check."""
    try:
        transforms = get_transform_uuids()
        result_type, result_data = mc.intermediateObjects(transforms, None)
        return True, len(result_data), "nodes"
    except Exception as e:
        return False, str(e), None

##############################################################################
# MAIN VALIDATION
##############################################################################

def run_validation():
    """Run comprehensive validation of all 15 Academic Extension checks."""

    print("")
    print("=" * 70)
    print("  ACADEMIC EXTENSION - COMPREHENSIVE VALIDATION")
    print("=" * 70)
    print("")

    if not MODELCHECKER_AVAILABLE:
        print("ABORTED: modelChecker module not available")
        return False

    # Create test scene
    test_objects = create_test_scene()

    # Define all checks to test
    checks = [
        ("flippedNormals", test_flipped_normals),
        ("overlappingVertices", test_overlapping_vertices),
        ("polyCountLimit", test_poly_count_limit),
        ("missingTextures", test_missing_textures),
        ("defaultMaterials", test_default_materials),
        ("sceneUnits", test_scene_units),
        ("uvDistortion", test_uv_distortion),
        ("texelDensity", test_texel_density),
        ("textureResolution", test_texture_resolution),
        ("unusedNodes", test_unused_nodes),
        ("hiddenObjects", test_hidden_objects),
        ("namingConvention", test_naming_convention),
        ("hierarchyDepth", test_hierarchy_depth),
        ("concaveFaces", test_concave_faces),
        ("intermediateObjects", test_intermediate_objects),
    ]

    print("")
    print("Running {} checks...".format(len(checks)))
    print("-" * 70)

    results = []
    for name, test_func in checks:
        try:
            success, count_or_error, result_type = test_func()
            if success:
                results.append((name, "PASS", count_or_error, result_type))
                print("  [PASS] {:25s} - Found {} issues ({})".format(
                    name, count_or_error, result_type))
            else:
                results.append((name, "FAIL", count_or_error, None))
                print("  [FAIL] {:25s} - Error: {}".format(name, count_or_error))
        except Exception as e:
            results.append((name, "ERROR", str(e), None))
            print("  [ERROR] {:25s} - {}".format(name, str(e)))
            traceback.print_exc()

    # Summary
    print("")
    print("=" * 70)
    print("  VALIDATION SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, status, _, _ in results if status == "PASS")
    failed = sum(1 for _, status, _, _ in results if status == "FAIL")
    errors = sum(1 for _, status, _, _ in results if status == "ERROR")

    print("")
    print("  Total Checks: {}".format(len(checks)))
    print("  Passed:       {} ({:.0f}%)".format(passed, 100*passed/len(checks)))
    print("  Failed:       {}".format(failed))
    print("  Errors:       {}".format(errors))
    print("")

    if failed > 0 or errors > 0:
        print("  FAILED/ERROR CHECKS:")
        for name, status, msg, _ in results:
            if status in ("FAIL", "ERROR"):
                print("    - {}: {}".format(name, msg))
        print("")

    # Expected detections in test scene
    print("  EXPECTED DETECTIONS IN TEST SCENE:")
    print("    - hiddenObjects:        1 (hidden_cube)")
    print("    - hierarchyDepth:       1+ (deep_cube at level 7)")
    print("    - namingConvention:     1+ (cube_001 has trailing numbers)")
    print("    - intermediateObjects:  1 (deformed_cube has lattice)")
    print("    - polyCountLimit:       1 (highpoly_sphere)")
    print("    - defaultMaterials:     Most objects (using lambert1)")
    print("")

    if passed == len(checks):
        print("  SUCCESS: All {} checks executed without errors!".format(len(checks)))
    else:
        print("  WARNING: Some checks failed - review errors above")

    print("=" * 70)
    print("")

    return passed == len(checks)

# Run validation
if MODELCHECKER_AVAILABLE:
    run_validation()
'''


def get_validation_script():
    """Return the Maya validation script for copy/paste."""
    return MAYA_VALIDATION_SCRIPT


if __name__ == "__main__":
    print("=" * 70)
    print("  ACADEMIC EXTENSION - COMPREHENSIVE VALIDATION SCRIPT")
    print("=" * 70)
    print()
    print("  This script tests ALL 15 new checks in a real Maya environment.")
    print()
    print("  TO RUN:")
    print("    1. Open Maya")
    print("    2. Ensure modelChecker is in your Python path")
    print("    3. Copy MAYA_VALIDATION_SCRIPT into Script Editor")
    print("    4. Execute (Ctrl+Enter)")
    print()
    print("  WHAT IT DOES:")
    print("    1. Creates a test scene with various problem objects")
    print("    2. Runs all 15 Academic Extension checks")
    print("    3. Reports pass/fail status for each check")
    print("    4. Shows expected detections vs actual results")
    print()
    print("  CHECKS TESTED:")
    checks = [
        "flippedNormals", "overlappingVertices", "polyCountLimit",
        "missingTextures", "defaultMaterials", "sceneUnits",
        "uvDistortion", "texelDensity", "textureResolution",
        "unusedNodes", "hiddenObjects", "namingConvention",
        "hierarchyDepth", "concaveFaces", "intermediateObjects"
    ]
    for i, check in enumerate(checks, 1):
        print("    {:2d}. {}".format(i, check))
    print()
    print("=" * 70)
