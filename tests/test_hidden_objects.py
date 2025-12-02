"""
Tests for hiddenObjects check.

================================================================================
OVERVIEW
================================================================================

The hiddenObjects check detects transform nodes with mesh shapes that have their
visibility turned off, either directly or via display layers. Hidden objects can:
- Unexpectedly appear in renders
- Cause file size bloat
- Create confusion when collaborating
- Be missing in game engine exports
- Indicate unprofessional scene organization

================================================================================
ALGORITHM
================================================================================

1. For each transform node, check if it has a mesh shape child
2. Check the 'visibility' attribute directly on the transform
3. Check if the object is in a display layer with visibility off
4. Flag objects that are hidden by either method
5. Skip non-mesh objects (cameras, lights, locators, etc.)

================================================================================
KNOWN LIMITATIONS
================================================================================

1. RENDER LAYERS: Does not detect objects hidden via render layer overrides.

2. ANIMATED VISIBILITY: Does not detect visibility that is animated to 0
   at the current frame.

3. REFERENCE GEOMETRY: May flag intentionally hidden reference geometry
   used for modeling reference.

4. LOD/TEMPLATE: Does not check lodVisibility or template display status.

5. PARENT VISIBILITY: Only checks direct visibility, not inherited visibility
   from parent nodes.

================================================================================
TEST CASES
================================================================================

1. test_visible_object - Visible mesh should PASS
2. test_hidden_object - Hidden mesh should FAIL
3. test_display_layer_hidden - Object in hidden layer should FAIL
4. test_camera - Camera should not be checked (not a mesh)
5. test_light - Light should not be checked (not a mesh)
6. test_multiple_hidden - Multiple hidden objects should all be flagged
7. test_mixed_scene - Scene with visible and hidden objects
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
    """Helper to get all transform nodes with meshes as UUIDs."""
    transforms = cmds.ls(type='transform', long=True) or []
    uuids = []
    for t in transforms:
        shapes = cmds.listRelatives(t, shapes=True, fullPath=True) or []
        if any(cmds.nodeType(s) == 'mesh' for s in shapes):
            uuid = cmds.ls(t, uuid=True)
            if uuid:
                uuids.append(uuid[0])
    return uuids

# =============================================================================
# TEST CASES
# =============================================================================

def test_visible_object():
    """
    Test: Visible mesh should not be flagged.
    """
    cmds.file(new=True, force=True)

    # Create a visible cube
    cube = cmds.polyCube(name='visible_cube')[0]

    nodes = get_transform_nodes()
    result_type, result_data = mc.hiddenObjects(nodes, None)

    if len(result_data) == 0:
        print("PASS: test_visible_object - Visible object not flagged")
        return True
    else:
        print("FAIL: test_visible_object - Visible object incorrectly flagged")
        return False


def test_hidden_object():
    """
    Test: Hidden mesh (visibility=False) should be flagged.
    """
    cmds.file(new=True, force=True)

    # Create a cube and hide it
    cube = cmds.polyCube(name='hidden_cube')[0]
    cmds.setAttr(cube + '.visibility', False)

    nodes = get_transform_nodes()
    result_type, result_data = mc.hiddenObjects(nodes, None)

    if len(result_data) > 0:
        print("PASS: test_hidden_object - Hidden object flagged")
        return True
    else:
        print("FAIL: test_hidden_object - Hidden object not detected")
        return False


def test_display_layer_hidden():
    """
    Test: Object in hidden display layer should be flagged.
    """
    cmds.file(new=True, force=True)

    # Create a cube
    cube = cmds.polyCube(name='layer_hidden_cube')[0]

    # Create a display layer and add the cube
    layer = cmds.createDisplayLayer(name='hiddenLayer', empty=True)
    cmds.editDisplayLayerMembers(layer, cube)

    # Hide the layer
    cmds.setAttr(layer + '.visibility', False)

    nodes = get_transform_nodes()
    result_type, result_data = mc.hiddenObjects(nodes, None)

    if len(result_data) > 0:
        print("PASS: test_display_layer_hidden - Layer-hidden object flagged")
        return True
    else:
        print("FAIL: test_display_layer_hidden - Layer-hidden object not detected")
        return False


def test_camera():
    """
    Test: Camera should not be checked (not a mesh).
    """
    cmds.file(new=True, force=True)

    # Create a camera and hide it
    camera = cmds.camera(name='test_camera')[0]
    cmds.setAttr(camera + '.visibility', False)

    nodes = get_transform_nodes()
    result_type, result_data = mc.hiddenObjects(nodes, None)

    # Camera shouldn't be in results since it's not a mesh
    if len(result_data) == 0:
        print("PASS: test_camera - Hidden camera not flagged (correct)")
        return True
    else:
        print("FAIL: test_camera - Camera incorrectly flagged")
        return False


def test_light():
    """
    Test: Light should not be checked (not a mesh).
    """
    cmds.file(new=True, force=True)

    # Create a light and hide it
    light = cmds.pointLight(name='test_light')
    lightTransform = cmds.listRelatives(light, parent=True)[0]
    cmds.setAttr(lightTransform + '.visibility', False)

    nodes = get_transform_nodes()
    result_type, result_data = mc.hiddenObjects(nodes, None)

    # Light shouldn't be flagged since it's not a mesh
    if len(result_data) == 0:
        print("PASS: test_light - Hidden light not flagged (correct)")
        return True
    else:
        print("FAIL: test_light - Light incorrectly flagged")
        return False


def test_multiple_hidden():
    """
    Test: Multiple hidden objects should all be flagged.
    """
    cmds.file(new=True, force=True)

    # Create multiple hidden cubes
    for i in range(3):
        cube = cmds.polyCube(name='hidden_cube_{}'.format(i))[0]
        cmds.setAttr(cube + '.visibility', False)

    nodes = get_transform_nodes()
    result_type, result_data = mc.hiddenObjects(nodes, None)

    if len(result_data) >= 3:
        print("PASS: test_multiple_hidden - {} hidden objects flagged".format(len(result_data)))
        return True
    else:
        print("FAIL: test_multiple_hidden - Expected 3, got {}".format(len(result_data)))
        return False


def test_mixed_scene():
    """
    Test: Scene with both visible and hidden objects.
    """
    cmds.file(new=True, force=True)

    # Create visible cube
    visibleCube = cmds.polyCube(name='visible_cube')[0]

    # Create hidden cube
    hiddenCube = cmds.polyCube(name='hidden_cube')[0]
    cmds.setAttr(hiddenCube + '.visibility', False)

    nodes = get_transform_nodes()
    result_type, result_data = mc.hiddenObjects(nodes, None)

    # Get UUIDs for verification
    hiddenUUID = cmds.ls(hiddenCube, uuid=True)[0]
    visibleUUID = cmds.ls(visibleCube, uuid=True)[0]

    if hiddenUUID in result_data and visibleUUID not in result_data:
        print("PASS: test_mixed_scene - Only hidden object flagged")
        return True
    else:
        print("FAIL: test_mixed_scene - Incorrect flagging in mixed scene")
        return False


def test_empty_selection():
    """
    Test: Empty input should not crash.
    """
    cmds.file(new=True, force=True)

    try:
        result_type, result_data = mc.hiddenObjects([], None)
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
    print("  hiddenObjects Test Suite")
    print("=" * 70)
    print("")

    results = []
    results.append(("Visible object", test_visible_object()))
    results.append(("Hidden object", test_hidden_object()))
    results.append(("Display layer hidden", test_display_layer_hidden()))
    results.append(("Camera (non-mesh)", test_camera()))
    results.append(("Light (non-mesh)", test_light()))
    results.append(("Multiple hidden", test_multiple_hidden()))
    results.append(("Mixed scene", test_mixed_scene()))
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
    print("  hiddenObjects Test Suite")
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
    print("    Detects mesh objects with visibility turned off")
    print("    - Direct visibility attribute = False")
    print("    - In a display layer with visibility off")
    print()
    print("  WHAT DOES NOT GET FLAGGED:")
    print("    - Cameras (not mesh objects)")
    print("    - Lights (not mesh objects)")
    print("    - Locators (not mesh objects)")
    print("    - Visible mesh objects")
    print()
    print("  WHY THIS MATTERS:")
    print("    - Hidden objects can appear unexpectedly in renders")
    print("    - File size bloat from forgotten geometry")
    print("    - Clean scenes for professional submissions")
    print()
    print("=" * 70)
