"""
Tests for namingConvention check.

================================================================================
OVERVIEW
================================================================================

The namingConvention check validates that scene objects follow proper naming
conventions. It detects:
1. Maya default names (pCube1, pSphere2, etc.)
2. Objects missing type-appropriate prefixes (geo_, grp_, jnt_, etc.)

Proper naming is essential for:
- Professional scene organization
- Easy asset identification in large scenes
- Team collaboration and handoffs
- Pipeline/script compatibility
- Grading and review of student work

================================================================================
ALGORITHM
================================================================================

1. For each transform node, get its short name (without DAG path)
2. Strip trailing numbers to get the base name
3. Check if base name matches any Maya default name patterns
4. Determine the object type (mesh, group, joint, locator, etc.)
5. Verify the name has an appropriate prefix for its type
6. Flag objects that use default names OR lack proper prefixes

================================================================================
VALID PREFIXES BY TYPE
================================================================================

| Type     | Valid Prefixes                              |
|----------|---------------------------------------------|
| mesh     | geo_, mesh_, msh_, GEO_, MESH_              |
| group    | grp_, group_, GRP_, GROUP_                  |
| joint    | jnt_, joint_, JNT_, JOINT_, bn_, bone_      |
| locator  | loc_, locator_, LOC_, LOCATOR_              |
| curve    | crv_, curve_, CRV_, CURVE_                  |
| control  | ctrl_, control_, CTRL_, CONTROL_, con_      |
| camera   | cam_, camera_, CAM_, CAMERA_                |
| light    | lgt_, light_, LGT_, LIGHT_                  |

================================================================================
KNOWN LIMITATIONS
================================================================================

1. PREFIX-BASED ONLY: Only validates prefix conventions, not suffix or
   other naming patterns used by some studios.

2. SEMANTIC VALIDITY: Does not check if names are meaningful. "geo_blah"
   would pass even though it's not descriptive.

3. STYLE CONSISTENCY: Does not enforce camelCase vs snake_case vs
   PascalCase within the name itself.

4. CUSTOM CONVENTIONS: Built-in patterns may not match all studio or
   school-specific conventions.

5. MATERIAL NAMES: Does not validate material or shader node naming.

================================================================================
TEST CASES
================================================================================

1. test_properly_named_mesh - geo_cube should PASS
2. test_default_name_mesh - pCube1 should FAIL
3. test_properly_named_group - grp_props should PASS
4. test_default_name_group - group1 should FAIL
5. test_properly_named_joint - jnt_spine should PASS
6. test_properly_named_locator - loc_target should PASS
7. test_mixed_scene - Mixed valid/invalid names
8. test_case_insensitive_prefix - GEO_ uppercase should PASS
9. test_empty_selection - Empty input should not crash

================================================================================
RUNNING TESTS
================================================================================

Copy MAYA_TEST_SCRIPT into Maya's Script Editor and execute.

================================================================================
"""

MAYA_TEST_SCRIPT = '''
import maya.cmds as cmds
import maya.api.OpenMaya as om
from mayaLint import mayaLint_commands as mc

def get_transform_nodes():
    """Helper to get all transform nodes as UUIDs."""
    transforms = cmds.ls(type='transform', long=True) or []
    # Filter out default cameras
    default_cams = ['|front', '|persp', '|side', '|top']
    transforms = [t for t in transforms if t not in default_cams]
    uuids = []
    for t in transforms:
        uuid = cmds.ls(t, uuid=True)
        if uuid:
            uuids.append(uuid[0])
    return uuids

# =============================================================================
# TEST CASES
# =============================================================================

def test_properly_named_mesh():
    """
    Test: Mesh with proper geo_ prefix should PASS.
    """
    cmds.file(new=True, force=True)

    # Create a properly named cube
    cube = cmds.polyCube(name='geo_mainBuilding')[0]

    nodes = get_transform_nodes()
    result_type, result_data = mc.namingConvention(nodes, None)

    if len(result_data) == 0:
        print("PASS: test_properly_named_mesh - geo_ prefix accepted")
        return True
    else:
        print("FAIL: test_properly_named_mesh - geo_ prefix incorrectly flagged")
        return False


def test_default_name_mesh():
    """
    Test: Mesh with Maya default name should FAIL.
    """
    cmds.file(new=True, force=True)

    # Create cube with default name
    cube = cmds.polyCube()[0]  # Creates "pCube1"

    nodes = get_transform_nodes()
    result_type, result_data = mc.namingConvention(nodes, None)

    if len(result_data) > 0:
        print("PASS: test_default_name_mesh - Default pCube name flagged")
        return True
    else:
        print("FAIL: test_default_name_mesh - Default name not detected")
        return False


def test_properly_named_group():
    """
    Test: Group with proper grp_ prefix should PASS.
    """
    cmds.file(new=True, force=True)

    # Create a properly named group with a child
    cube = cmds.polyCube(name='geo_box')[0]
    grp = cmds.group(cube, name='grp_props')

    nodes = get_transform_nodes()
    result_type, result_data = mc.namingConvention(nodes, None)

    # Check that the group is not in results
    grpUUID = cmds.ls(grp, uuid=True)[0]
    if grpUUID not in result_data:
        print("PASS: test_properly_named_group - grp_ prefix accepted")
        return True
    else:
        print("FAIL: test_properly_named_group - grp_ prefix incorrectly flagged")
        return False


def test_default_name_group():
    """
    Test: Group with Maya default name should FAIL.
    """
    cmds.file(new=True, force=True)

    # Create cube and group with default name
    cube = cmds.polyCube(name='geo_box')[0]
    grp = cmds.group(cube)  # Creates "group1"

    nodes = get_transform_nodes()
    result_type, result_data = mc.namingConvention(nodes, None)

    # Check that the group is in results
    grpUUID = cmds.ls(grp, uuid=True)[0]
    if grpUUID in result_data:
        print("PASS: test_default_name_group - Default group name flagged")
        return True
    else:
        print("FAIL: test_default_name_group - Default group name not detected")
        return False


def test_properly_named_joint():
    """
    Test: Joint with proper jnt_ prefix should PASS.
    """
    cmds.file(new=True, force=True)

    # Create a properly named joint
    joint = cmds.joint(name='jnt_spine01')

    nodes = get_transform_nodes()
    result_type, result_data = mc.namingConvention(nodes, None)

    # Get joint UUID
    jointUUID = cmds.ls(joint, uuid=True)[0]
    if jointUUID not in result_data:
        print("PASS: test_properly_named_joint - jnt_ prefix accepted")
        return True
    else:
        print("FAIL: test_properly_named_joint - jnt_ prefix incorrectly flagged")
        return False


def test_properly_named_locator():
    """
    Test: Locator with proper loc_ prefix should PASS.
    """
    cmds.file(new=True, force=True)

    # Create a properly named locator
    loc = cmds.spaceLocator(name='loc_aimTarget')[0]

    nodes = get_transform_nodes()
    result_type, result_data = mc.namingConvention(nodes, None)

    locUUID = cmds.ls(loc, uuid=True)[0]
    if locUUID not in result_data:
        print("PASS: test_properly_named_locator - loc_ prefix accepted")
        return True
    else:
        print("FAIL: test_properly_named_locator - loc_ prefix incorrectly flagged")
        return False


def test_mixed_scene():
    """
    Test: Scene with both valid and invalid names.
    """
    cmds.file(new=True, force=True)

    # Create valid names
    validCube = cmds.polyCube(name='geo_house')[0]
    validGrp = cmds.group(validCube, name='grp_buildings')

    # Create invalid names
    invalidCube = cmds.polyCube()[0]  # pCube1
    invalidSphere = cmds.polySphere()[0]  # pSphere1

    nodes = get_transform_nodes()
    result_type, result_data = mc.namingConvention(nodes, None)

    validCubeUUID = cmds.ls(validCube, uuid=True)[0]
    validGrpUUID = cmds.ls(validGrp, uuid=True)[0]
    invalidCubeUUID = cmds.ls(invalidCube, uuid=True)[0]
    invalidSphereUUID = cmds.ls(invalidSphere, uuid=True)[0]

    valid_passed = (validCubeUUID not in result_data and
                    validGrpUUID not in result_data)
    invalid_flagged = (invalidCubeUUID in result_data and
                       invalidSphereUUID in result_data)

    if valid_passed and invalid_flagged:
        print("PASS: test_mixed_scene - Correctly identified valid/invalid names")
        return True
    else:
        print("FAIL: test_mixed_scene - Incorrect flagging in mixed scene")
        return False


def test_case_insensitive_prefix():
    """
    Test: Uppercase prefixes (GEO_, GRP_) should also PASS.
    """
    cmds.file(new=True, force=True)

    # Create with uppercase prefix
    cube = cmds.polyCube(name='GEO_building')[0]
    grp = cmds.group(cube, name='GRP_assets')

    nodes = get_transform_nodes()
    result_type, result_data = mc.namingConvention(nodes, None)

    cubeUUID = cmds.ls(cube, uuid=True)[0]
    grpUUID = cmds.ls(grp, uuid=True)[0]

    if cubeUUID not in result_data and grpUUID not in result_data:
        print("PASS: test_case_insensitive_prefix - Uppercase prefixes accepted")
        return True
    else:
        print("FAIL: test_case_insensitive_prefix - Uppercase prefixes incorrectly flagged")
        return False


def test_empty_selection():
    """
    Test: Empty input should not crash.
    """
    cmds.file(new=True, force=True)

    try:
        result_type, result_data = mc.namingConvention([], None)
        if len(result_data) == 0:
            print("PASS: test_empty_selection - Empty input handled gracefully")
            return True
        else:
            print("FAIL: test_empty_selection - Unexpected results from empty input")
            return False
    except Exception as e:
        print("FAIL: test_empty_selection - Exception: {}".format(str(e)))
        return False


# =============================================================================
# RUN ALL TESTS
# =============================================================================

def run_all_tests():
    print("")
    print("=" * 70)
    print("  namingConvention Test Suite")
    print("=" * 70)
    print("")

    results = []
    results.append(("Properly named mesh", test_properly_named_mesh()))
    results.append(("Default name mesh", test_default_name_mesh()))
    results.append(("Properly named group", test_properly_named_group()))
    results.append(("Default name group", test_default_name_group()))
    results.append(("Properly named joint", test_properly_named_joint()))
    results.append(("Properly named locator", test_properly_named_locator()))
    results.append(("Mixed scene", test_mixed_scene()))
    results.append(("Uppercase prefixes", test_case_insensitive_prefix()))
    results.append(("Empty selection", test_empty_selection()))

    print("")
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print("  [{}] {}".format(status, name))
    print("")
    print("  Total: {}/{} tests passed".format(passed, total))
    print("=" * 70)

    return passed == total

run_all_tests()
'''


def get_test_script():
    """Return the Maya test script for copy/paste."""
    return MAYA_TEST_SCRIPT


if __name__ == "__main__":
    print("=" * 70)
    print("  namingConvention Test Suite")
    print("=" * 70)
    print()
    print("  These tests require Maya to run.")
    print()
    print("  To execute tests:")
    print("    1. Open Maya")
    print("    2. Ensure mayaLint is in your Python path")
    print("    3. Copy MAYA_TEST_SCRIPT into Script Editor")
    print("    4. Execute")
    print()
    print("  WHAT THIS CHECK DOES:")
    print("    Validates object naming conventions:")
    print("    - Detects Maya default names (pCube1, pSphere2, etc.)")
    print("    - Checks for proper type prefixes (geo_, grp_, jnt_, etc.)")
    print()
    print("  VALID PREFIXES:")
    print("    Mesh:    geo_, mesh_, msh_")
    print("    Group:   grp_, group_")
    print("    Joint:   jnt_, joint_, bn_, bone_")
    print("    Locator: loc_, locator_")
    print("    Curve:   crv_, curve_")
    print("    Camera:  cam_, camera_")
    print("    Light:   lgt_, light_")
    print()
    print("  WHY THIS MATTERS:")
    print("    - Professional scene organization")
    print("    - Easy asset identification")
    print("    - Pipeline/script compatibility")
    print("    - Team collaboration")
    print()
    print("=" * 70)
