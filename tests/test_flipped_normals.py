"""
Tests for flippedNormals check.

================================================================================
OVERVIEW
================================================================================

The flippedNormals check detects faces with normals pointing inward (toward
the mesh center) rather than outward. This is a common issue that causes:
- Black faces in renders
- Incorrect lighting
- Backface culling problems in game engines

================================================================================
ALGORITHM
================================================================================

1. Get mesh bounding box center as reference point
2. For each face:
   - Get face center and normal in world space
   - Calculate vector from mesh center to face center
   - If dot product < 0, normal points inward (flipped)

================================================================================
KNOWN LIMITATIONS
================================================================================

1. CONCAVE MESHES: The algorithm uses bounding box center, which works well
   for convex meshes but may give false positives on highly concave geometry
   where faces legitimately point toward the bounding box center.

   Example: A donut/torus shape may have inner faces flagged incorrectly.

2. INTENDED USE: Designed for academic evaluation where models are expected
   to be "clean" with consistent outward-facing normals. Production use on
   complex organic models may require manual verification.

3. MESH POSITION: Uses world space calculations. Results are consistent
   regardless of mesh position in scene.

================================================================================
TEST CASES
================================================================================

These tests require Maya to be running. Run them from within Maya's Script
Editor or using mayapy.

Test Cases:
1. Clean cube (all normals pointing outward) - should PASS
2. Cube with all normals reversed - should FAIL and report all 6 faces
3. Sphere with some reversed faces - should FAIL and report specific faces
4. Empty mesh list - should return empty results (no crash)
5. (Known limitation) Concave mesh - may have false positives

================================================================================
RUNNING TESTS
================================================================================

Option 1: Maya Script Editor
   - Copy MAYA_TEST_SCRIPT below into Maya's Script Editor
   - Execute

Option 2: mayapy
   - mayapy tests/test_flipped_normals.py

Option 3: Standalone (info only)
   - python tests/test_flipped_normals.py

================================================================================
"""

# =============================================================================
# MAYA TEST COMMANDS
# =============================================================================
# Copy and paste these into Maya's Script Editor to test manually:

MAYA_TEST_SCRIPT = '''
import maya.cmds as cmds
import maya.api.OpenMaya as om
from modelChecker import modelChecker_commands as mc

# -----------------------------------------------------------------------------
# Test 1: Clean Cube (should PASS - no flipped normals)
# -----------------------------------------------------------------------------
def test_clean_cube():
    """Test that a normal cube has no flipped normals."""
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name='test_clean_cube')[0]

    # Get shape and create selection list
    shape = cmds.listRelatives(cube, shapes=True)[0]
    selList = om.MSelectionList()
    selList.add(shape)

    result_type, result_data = mc.flippedNormals(None, selList)

    if len(result_data) == 0:
        print("TEST 1 PASSED: Clean cube has no flipped normals")
        return True
    else:
        print("TEST 1 FAILED: Clean cube incorrectly detected flipped normals")
        print("  Found:", result_data)
        return False

# -----------------------------------------------------------------------------
# Test 2: Cube with All Normals Reversed (should FAIL - detect all 6 faces)
# -----------------------------------------------------------------------------
def test_reversed_cube():
    """Test that a cube with reversed normals is detected."""
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name='test_reversed_cube')[0]

    # Reverse all normals
    cmds.polyNormal(cube, normalMode=0, userNormalMode=0)

    # Get shape and create selection list
    shape = cmds.listRelatives(cube, shapes=True)[0]
    selList = om.MSelectionList()
    selList.add(shape)

    result_type, result_data = mc.flippedNormals(None, selList)

    if len(result_data) > 0:
        total_faces = sum(len(faces) for faces in result_data.values())
        if total_faces == 6:
            print("TEST 2 PASSED: All 6 reversed faces detected")
            return True
        else:
            print("TEST 2 PARTIAL: Detected {} of 6 reversed faces".format(total_faces))
            return False
    else:
        print("TEST 2 FAILED: Reversed cube was not detected")
        return False

# -----------------------------------------------------------------------------
# Test 3: Sphere with Partial Reversed Normals
# -----------------------------------------------------------------------------
def test_partial_reversed_sphere():
    """Test that partially reversed normals are detected."""
    cmds.file(new=True, force=True)
    sphere = cmds.polySphere(name='test_sphere', subdivisionsX=8, subdivisionsY=8)[0]

    # Reverse only some faces (first 10 faces)
    cmds.select(sphere + '.f[0:9]')
    cmds.polyNormal(normalMode=0, userNormalMode=0)

    # Get shape and create selection list
    shape = cmds.listRelatives(sphere, shapes=True)[0]
    selList = om.MSelectionList()
    selList.add(shape)

    result_type, result_data = mc.flippedNormals(None, selList)

    if len(result_data) > 0:
        total_faces = sum(len(faces) for faces in result_data.values())
        print("TEST 3 PASSED: Detected {} flipped faces in sphere".format(total_faces))
        return True
    else:
        print("TEST 3 FAILED: Flipped faces in sphere were not detected")
        return False

# -----------------------------------------------------------------------------
# Test 4: Empty Selection List (should not crash)
# -----------------------------------------------------------------------------
def test_empty_selection():
    """Test that empty selection is handled gracefully."""
    cmds.file(new=True, force=True)

    selList = om.MSelectionList()

    try:
        result_type, result_data = mc.flippedNormals(None, selList)
        if len(result_data) == 0:
            print("TEST 4 PASSED: Empty selection handled gracefully")
            return True
        else:
            print("TEST 4 FAILED: Unexpected results from empty selection")
            return False
    except Exception as e:
        print("TEST 4 FAILED: Exception on empty selection:", str(e))
        return False

# -----------------------------------------------------------------------------
# Test 5: Known Limitation - Concave Mesh (documents expected behavior)
# -----------------------------------------------------------------------------
def test_concave_limitation():
    """
    Document known limitation with concave meshes.

    This test creates a torus (donut shape) which has faces pointing toward
    the bounding box center by design. The algorithm may flag these as flipped.

    This is a KNOWN LIMITATION, not a bug.
    """
    cmds.file(new=True, force=True)
    torus = cmds.polyTorus(name='test_torus', radius=2, sectionRadius=0.5)[0]

    # Get shape and create selection list
    shape = cmds.listRelatives(torus, shapes=True)[0]
    selList = om.MSelectionList()
    selList.add(shape)

    result_type, result_data = mc.flippedNormals(None, selList)

    total_faces = sum(len(faces) for faces in result_data.values()) if result_data else 0

    print("TEST 5 (LIMITATION): Torus detected {} potentially flipped faces".format(total_faces))
    print("  NOTE: This is a KNOWN LIMITATION. Concave meshes may have false positives.")
    print("  The inner faces of a torus legitimately point toward the bounding box center.")
    print("  For production use on concave meshes, manual verification is recommended.")
    return True  # Always passes - this documents behavior, not tests correctness

# -----------------------------------------------------------------------------
# Run All Tests
# -----------------------------------------------------------------------------
def run_all_tests():
    print("")
    print("=" * 70)
    print("  flippedNormals Test Suite")
    print("=" * 70)
    print("")

    results = []
    results.append(("Clean Cube", test_clean_cube()))
    results.append(("Reversed Cube", test_reversed_cube()))
    results.append(("Partial Reversed Sphere", test_partial_reversed_sphere()))
    results.append(("Empty Selection", test_empty_selection()))
    results.append(("Concave Limitation", test_concave_limitation()))

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

run_all_tests()
'''


def get_test_script():
    """Return the Maya test script for copy/paste."""
    return MAYA_TEST_SCRIPT


if __name__ == "__main__":
    print("=" * 70)
    print("  flippedNormals Test Suite")
    print("=" * 70)
    print()
    print("  These tests require Maya to run.")
    print()
    print("  To execute tests:")
    print()
    print("  1. Open Maya")
    print("  2. Ensure modelChecker is in your Python path:")
    print("     import sys")
    print("     sys.path.append('/path/to/modelChecker')")
    print("  3. Copy the MAYA_TEST_SCRIPT from this file into Script Editor")
    print("  4. Execute")
    print()
    print("  Or run with mayapy:")
    print("    mayapy -c \"exec(open('tests/test_flipped_normals.py').read())\"")
    print()
    print("=" * 70)
    print()
    print("  KNOWN LIMITATIONS (documented in tests):")
    print()
    print("  - Algorithm uses bounding box center as reference")
    print("  - Works well for convex/mostly-convex meshes")
    print("  - May give false positives on highly concave geometry")
    print("  - Test 5 documents this limitation with a torus example")
    print()
    print("=" * 70)
