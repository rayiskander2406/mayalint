"""
Tests for hierarchyDepth check.

================================================================================
OVERVIEW
================================================================================

The hierarchyDepth check detects objects that are nested too deeply in the
Maya scene hierarchy. Excessive depth indicates poor scene organization and
can cause:
- Difficulty navigating the Outliner
- Confusion when working on teams
- Performance issues with very deep hierarchies
- Complications when exporting to game engines
- Unprofessional scene structure

================================================================================
ALGORITHM
================================================================================

1. For each transform node, get its full DAG path
2. Count the number of '|' separators to determine depth
3. Compare against HIERARCHY_DEPTH_MAX threshold (default: 5)
4. Flag objects that exceed the maximum allowed depth

Depth examples:
- "|geo_cube" = depth 1 (root level)
- "|grp_main|geo_cube" = depth 2
- "|grp1|grp2|grp3|grp4|grp5|geo" = depth 6 (exceeds default threshold)

================================================================================
KNOWN LIMITATIONS
================================================================================

1. INTENTIONAL NESTING: Does not consider whether deep nesting is intentional
   (e.g., complex character rigs may require deep hierarchies).

2. REFERENCED OBJECTS: Referenced objects may have additional depth from their
   source file that cannot be easily flattened.

3. GLOBAL THRESHOLD: The depth threshold is global, not context-aware. Some
   parts of a scene (like rigs) may legitimately need more depth.

4. CONSTRAINT TARGETS: Does not distinguish between group hierarchies and
   constraint target relationships.

================================================================================
TEST CASES
================================================================================

1. test_shallow_hierarchy - Objects at depth <= 5 should PASS
2. test_deep_hierarchy - Objects at depth > 5 should FAIL
3. test_exact_threshold - Objects at exactly depth 5 should PASS
4. test_one_over_threshold - Objects at depth 6 should FAIL
5. test_root_level - Root level objects (depth 1) should PASS
6. test_mixed_depths - Scene with various depths
7. test_very_deep - Very deeply nested objects should FAIL
8. test_empty_selection - Empty input should not crash

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

def create_nested_groups(depth, name_base='grp'):
    """Create nested groups to specified depth. Returns the deepest child."""
    parent = None
    for i in range(depth):
        grp = cmds.group(empty=True, name='{}_{}'.format(name_base, i+1))
        if parent:
            cmds.parent(grp, parent)
        parent = grp
    return parent

# =============================================================================
# TEST CASES
# =============================================================================

def test_shallow_hierarchy():
    """
    Test: Objects at depth <= 5 should PASS.
    """
    cmds.file(new=True, force=True)

    # Create a 3-level hierarchy (depth 3)
    grp1 = cmds.group(empty=True, name='grp_level1')
    grp2 = cmds.group(empty=True, name='grp_level2', parent=grp1)
    cube = cmds.polyCube(name='geo_cube')[0]
    cmds.parent(cube, grp2)
    # Path: |grp_level1|grp_level2|geo_cube = depth 3

    nodes = get_transform_nodes()
    result_type, result_data = mc.hierarchyDepth(nodes, None)

    cubeUUID = cmds.ls(cube, uuid=True)[0]
    if cubeUUID not in result_data:
        print("PASS: test_shallow_hierarchy - Depth 3 not flagged")
        return True
    else:
        print("FAIL: test_shallow_hierarchy - Depth 3 incorrectly flagged")
        return False


def test_deep_hierarchy():
    """
    Test: Objects at depth > 5 should FAIL.
    """
    cmds.file(new=True, force=True)

    # Create a 7-level hierarchy (depth 7)
    parent = None
    for i in range(6):
        grp = cmds.group(empty=True, name='grp_level{}'.format(i+1))
        if parent:
            cmds.parent(grp, parent)
        parent = grp

    cube = cmds.polyCube(name='geo_cube')[0]
    cmds.parent(cube, parent)
    # Path: |grp_level1|grp_level2|...|grp_level6|geo_cube = depth 7

    nodes = get_transform_nodes()
    result_type, result_data = mc.hierarchyDepth(nodes, None)

    cubeUUID = cmds.ls(cube, uuid=True)[0]
    if cubeUUID in result_data:
        print("PASS: test_deep_hierarchy - Depth 7 flagged correctly")
        return True
    else:
        print("FAIL: test_deep_hierarchy - Depth 7 not detected")
        return False


def test_exact_threshold():
    """
    Test: Objects at exactly depth 5 should PASS.
    """
    cmds.file(new=True, force=True)

    # Create exactly 4 levels of groups (depth 5 for child)
    parent = None
    for i in range(4):
        grp = cmds.group(empty=True, name='grp_level{}'.format(i+1))
        if parent:
            cmds.parent(grp, parent)
        parent = grp

    cube = cmds.polyCube(name='geo_cube')[0]
    cmds.parent(cube, parent)
    # Path: |grp_level1|grp_level2|grp_level3|grp_level4|geo_cube = depth 5

    nodes = get_transform_nodes()
    result_type, result_data = mc.hierarchyDepth(nodes, None)

    cubeUUID = cmds.ls(cube, uuid=True)[0]
    if cubeUUID not in result_data:
        print("PASS: test_exact_threshold - Depth 5 not flagged (at threshold)")
        return True
    else:
        print("FAIL: test_exact_threshold - Depth 5 incorrectly flagged")
        return False


def test_one_over_threshold():
    """
    Test: Objects at depth 6 (one over threshold) should FAIL.
    """
    cmds.file(new=True, force=True)

    # Create exactly 5 levels of groups (depth 6 for child)
    parent = None
    for i in range(5):
        grp = cmds.group(empty=True, name='grp_level{}'.format(i+1))
        if parent:
            cmds.parent(grp, parent)
        parent = grp

    cube = cmds.polyCube(name='geo_cube')[0]
    cmds.parent(cube, parent)
    # Path: |grp1|grp2|grp3|grp4|grp5|geo_cube = depth 6

    nodes = get_transform_nodes()
    result_type, result_data = mc.hierarchyDepth(nodes, None)

    cubeUUID = cmds.ls(cube, uuid=True)[0]
    if cubeUUID in result_data:
        print("PASS: test_one_over_threshold - Depth 6 flagged")
        return True
    else:
        print("FAIL: test_one_over_threshold - Depth 6 not detected")
        return False


def test_root_level():
    """
    Test: Root level objects (depth 1) should PASS.
    """
    cmds.file(new=True, force=True)

    # Create a cube at root level
    cube = cmds.polyCube(name='geo_cube')[0]
    # Path: |geo_cube = depth 1

    nodes = get_transform_nodes()
    result_type, result_data = mc.hierarchyDepth(nodes, None)

    cubeUUID = cmds.ls(cube, uuid=True)[0]
    if cubeUUID not in result_data:
        print("PASS: test_root_level - Root level object not flagged")
        return True
    else:
        print("FAIL: test_root_level - Root level object incorrectly flagged")
        return False


def test_mixed_depths():
    """
    Test: Scene with various depths - only deep ones flagged.
    """
    cmds.file(new=True, force=True)

    # Create shallow object (depth 2)
    grpShallow = cmds.group(empty=True, name='grp_shallow')
    cubeShallow = cmds.polyCube(name='geo_shallow')[0]
    cmds.parent(cubeShallow, grpShallow)

    # Create deep object (depth 7)
    parent = None
    for i in range(6):
        grp = cmds.group(empty=True, name='grp_deep{}'.format(i+1))
        if parent:
            cmds.parent(grp, parent)
        parent = grp
    cubeDeep = cmds.polyCube(name='geo_deep')[0]
    cmds.parent(cubeDeep, parent)

    nodes = get_transform_nodes()
    result_type, result_data = mc.hierarchyDepth(nodes, None)

    shallowUUID = cmds.ls(cubeShallow, uuid=True)[0]
    deepUUID = cmds.ls(cubeDeep, uuid=True)[0]

    shallow_ok = shallowUUID not in result_data
    deep_flagged = deepUUID in result_data

    if shallow_ok and deep_flagged:
        print("PASS: test_mixed_depths - Only deep objects flagged")
        return True
    else:
        print("FAIL: test_mixed_depths - Incorrect flagging (shallow_ok={}, deep_flagged={})".format(
            shallow_ok, deep_flagged))
        return False


def test_very_deep():
    """
    Test: Very deeply nested objects should FAIL.
    """
    cmds.file(new=True, force=True)

    # Create a 10-level hierarchy
    parent = None
    for i in range(9):
        grp = cmds.group(empty=True, name='grp_{}'.format(i+1))
        if parent:
            cmds.parent(grp, parent)
        parent = grp

    cube = cmds.polyCube(name='geo_cube')[0]
    cmds.parent(cube, parent)
    # Path: |grp1|grp2|...|grp9|geo_cube = depth 10

    nodes = get_transform_nodes()
    result_type, result_data = mc.hierarchyDepth(nodes, None)

    cubeUUID = cmds.ls(cube, uuid=True)[0]
    if cubeUUID in result_data:
        print("PASS: test_very_deep - Depth 10 flagged")
        return True
    else:
        print("FAIL: test_very_deep - Depth 10 not detected")
        return False


def test_empty_selection():
    """
    Test: Empty input should not crash.
    """
    cmds.file(new=True, force=True)

    try:
        result_type, result_data = mc.hierarchyDepth([], None)
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
    print("  hierarchyDepth Test Suite")
    print("=" * 70)
    print("")

    results = []
    results.append(("Shallow hierarchy (depth 3)", test_shallow_hierarchy()))
    results.append(("Deep hierarchy (depth 7)", test_deep_hierarchy()))
    results.append(("Exact threshold (depth 5)", test_exact_threshold()))
    results.append(("One over threshold (depth 6)", test_one_over_threshold()))
    results.append(("Root level (depth 1)", test_root_level()))
    results.append(("Mixed depths", test_mixed_depths()))
    results.append(("Very deep (depth 10)", test_very_deep()))
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
    print("  hierarchyDepth Test Suite")
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
    print("    Detects objects nested too deeply in the hierarchy")
    print("    - Default threshold: 5 levels deep")
    print("    - Counts '|' separators in DAG path")
    print()
    print("  DEPTH EXAMPLES:")
    print("    |geo_cube = depth 1 (root)")
    print("    |grp|geo_cube = depth 2")
    print("    |grp1|grp2|grp3|grp4|grp5|geo = depth 6 (FAILS)")
    print()
    print("  WHY THIS MATTERS:")
    print("    - Difficult to navigate Outliner")
    print("    - Team collaboration issues")
    print("    - Export complications")
    print("    - Unprofessional scene structure")
    print()
    print("=" * 70)
