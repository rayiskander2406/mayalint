"""
Tests for unusedNodes check.

================================================================================
OVERVIEW
================================================================================

The unusedNodes check detects materials and shading groups that are not assigned
to any geometry in the scene. Scene clutter from unused nodes indicates:
- Leftover materials from deleted objects
- Imported materials that were never used
- Duplicate materials from copy-paste operations
- Unprofessional scene organization
- Unnecessary file size increase

================================================================================
ALGORITHM
================================================================================

1. Get all shading engines (shadingEngine nodes) in the scene
2. For each shading engine, check if it has any geometry assigned using cmds.sets()
3. Identify shading engines with no assignments (excluding defaults)
4. Also check for orphaned materials not connected to any shading engine
5. Return list of unused node UUIDs

================================================================================
KNOWN LIMITATIONS
================================================================================

1. MATERIALS ONLY: Does not detect unused textures - use missingTextures check
   for texture-related issues.

2. NO UTILITY NODES: Does not detect unused utility nodes like samplerInfo,
   multiplyDivide, etc.

3. INTENTIONAL UNUSED: Some materials may be kept intentionally for reference
   or future use.

4. REFERENCED FILES: Materials in referenced files may appear unused if the
   geometry is in a different reference.

5. DEFAULT MATERIALS: Does not flag Maya's default materials (lambert1,
   initialShadingGroup, etc.) even if they appear unused.

================================================================================
TEST CASES
================================================================================

1. test_clean_scene - New scene should have no unused nodes
2. test_unused_material - Material not assigned to anything should FAIL
3. test_used_material - Material assigned to geometry should PASS
4. test_orphaned_material - Material disconnected from shading engine should FAIL
5. test_default_materials - lambert1 should never be flagged
6. test_default_shading_groups - initialShadingGroup should never be flagged
7. test_multiple_unused - Multiple unused materials should all be flagged
8. test_mixed_scene - Scene with both used and unused materials

================================================================================
RUNNING TESTS
================================================================================

Copy MAYA_TEST_SCRIPT into Maya's Script Editor and execute.

================================================================================
"""

MAYA_TEST_SCRIPT = '''
import maya.cmds as cmds
from mayaLint import mayaLint_commands as mc

# =============================================================================
# TEST CASES
# =============================================================================

def test_clean_scene():
    """
    Test: New scene should have no unused nodes (only defaults).
    """
    cmds.file(new=True, force=True)

    result_type, result_data = mc.unusedNodes(None, None)

    if len(result_data) == 0:
        print("PASS: test_clean_scene - New scene has no unused nodes")
        return True
    else:
        print("FAIL: test_clean_scene - {} unused nodes in clean scene".format(len(result_data)))
        return False


def test_unused_material():
    """
    Test: Material created but not assigned should be flagged.
    """
    cmds.file(new=True, force=True)

    # Create a material but don't assign it to anything
    material = cmds.shadingNode('lambert', asShader=True, name='unused_lambert')
    shadingGroup = cmds.sets(renderable=True, noSurfaceShader=True,
                             empty=True, name=material + 'SG')
    cmds.connectAttr(material + '.outColor', shadingGroup + '.surfaceShader')

    result_type, result_data = mc.unusedNodes(None, None)

    if len(result_data) > 0:
        print("PASS: test_unused_material - Unused material flagged")
        return True
    else:
        print("FAIL: test_unused_material - Unused material not detected")
        return False


def test_used_material():
    """
    Test: Material assigned to geometry should NOT be flagged.
    """
    cmds.file(new=True, force=True)

    # Create geometry
    cube = cmds.polyCube(name='test_cube')[0]

    # Create and assign a material
    material = cmds.shadingNode('lambert', asShader=True, name='used_lambert')
    shadingGroup = cmds.sets(renderable=True, noSurfaceShader=True,
                             empty=True, name=material + 'SG')
    cmds.connectAttr(material + '.outColor', shadingGroup + '.surfaceShader')
    cmds.sets(cube, edit=True, forceElement=shadingGroup)

    result_type, result_data = mc.unusedNodes(None, None)

    if len(result_data) == 0:
        print("PASS: test_used_material - Used material not flagged")
        return True
    else:
        print("FAIL: test_used_material - Used material was incorrectly flagged")
        return False


def test_orphaned_material():
    """
    Test: Material not connected to any shading engine should be flagged.
    """
    cmds.file(new=True, force=True)

    # Create a material without connecting it to a shading engine
    material = cmds.shadingNode('blinn', asShader=True, name='orphaned_blinn')
    # Don't create or connect to a shading group

    result_type, result_data = mc.unusedNodes(None, None)

    if len(result_data) > 0:
        print("PASS: test_orphaned_material - Orphaned material flagged")
        return True
    else:
        print("FAIL: test_orphaned_material - Orphaned material not detected")
        return False


def test_default_materials():
    """
    Test: Default materials (lambert1) should never be flagged.
    """
    cmds.file(new=True, force=True)

    # lambert1 exists in every scene but may have no assignments
    # It should NOT be flagged

    result_type, result_data = mc.unusedNodes(None, None)

    # Check that lambert1's UUID is not in the results
    lambert1_uuid = cmds.ls('lambert1', uuid=True)
    if lambert1_uuid:
        if lambert1_uuid[0] not in result_data:
            print("PASS: test_default_materials - lambert1 not flagged")
            return True
        else:
            print("FAIL: test_default_materials - lambert1 was incorrectly flagged")
            return False
    else:
        print("SKIP: test_default_materials - lambert1 not found")
        return True


def test_default_shading_groups():
    """
    Test: Default shading groups should never be flagged.
    """
    cmds.file(new=True, force=True)

    # initialShadingGroup exists in every scene
    # It should NOT be flagged

    result_type, result_data = mc.unusedNodes(None, None)

    # Check that initialShadingGroup's UUID is not in the results
    isg_uuid = cmds.ls('initialShadingGroup', uuid=True)
    if isg_uuid:
        if isg_uuid[0] not in result_data:
            print("PASS: test_default_shading_groups - initialShadingGroup not flagged")
            return True
        else:
            print("FAIL: test_default_shading_groups - initialShadingGroup incorrectly flagged")
            return False
    else:
        print("SKIP: test_default_shading_groups - initialShadingGroup not found")
        return True


def test_multiple_unused():
    """
    Test: Multiple unused materials should all be flagged.
    """
    cmds.file(new=True, force=True)

    # Create multiple unused materials
    for i in range(3):
        material = cmds.shadingNode('phong', asShader=True, name='unused_phong_{}'.format(i))
        shadingGroup = cmds.sets(renderable=True, noSurfaceShader=True,
                                 empty=True, name=material + 'SG')
        cmds.connectAttr(material + '.outColor', shadingGroup + '.surfaceShader')

    result_type, result_data = mc.unusedNodes(None, None)

    # Should flag at least 3 unused shading groups
    if len(result_data) >= 3:
        print("PASS: test_multiple_unused - {} unused nodes flagged".format(len(result_data)))
        return True
    else:
        print("FAIL: test_multiple_unused - Expected 3+, got {}".format(len(result_data)))
        return False


def test_mixed_scene():
    """
    Test: Scene with both used and unused materials.
    """
    cmds.file(new=True, force=True)

    # Create geometry
    cube = cmds.polyCube(name='test_cube')[0]

    # Create and assign a used material
    usedMat = cmds.shadingNode('lambert', asShader=True, name='used_mat')
    usedSG = cmds.sets(renderable=True, noSurfaceShader=True,
                       empty=True, name=usedMat + 'SG')
    cmds.connectAttr(usedMat + '.outColor', usedSG + '.surfaceShader')
    cmds.sets(cube, edit=True, forceElement=usedSG)

    # Create an unused material
    unusedMat = cmds.shadingNode('blinn', asShader=True, name='unused_mat')
    unusedSG = cmds.sets(renderable=True, noSurfaceShader=True,
                         empty=True, name=unusedMat + 'SG')
    cmds.connectAttr(unusedMat + '.outColor', unusedSG + '.surfaceShader')

    result_type, result_data = mc.unusedNodes(None, None)

    # Should flag only the unused shading group
    unusedSG_uuid = cmds.ls(unusedSG, uuid=True)[0]
    usedSG_uuid = cmds.ls(usedSG, uuid=True)[0]

    if unusedSG_uuid in result_data and usedSG_uuid not in result_data:
        print("PASS: test_mixed_scene - Only unused material flagged")
        return True
    else:
        print("FAIL: test_mixed_scene - Incorrect flagging in mixed scene")
        return False


# =============================================================================
# RUN ALL TESTS
# =============================================================================

def run_all_tests():
    print("")
    print("=" * 70)
    print("  unusedNodes Test Suite")
    print("=" * 70)
    print("")

    results = []
    results.append(("Clean scene", test_clean_scene()))
    results.append(("Unused material", test_unused_material()))
    results.append(("Used material", test_used_material()))
    results.append(("Orphaned material", test_orphaned_material()))
    results.append(("Default materials", test_default_materials()))
    results.append(("Default shading groups", test_default_shading_groups()))
    results.append(("Multiple unused", test_multiple_unused()))
    results.append(("Mixed scene", test_mixed_scene()))

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
    print("  unusedNodes Test Suite")
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
    print("    Detects materials and shading groups not assigned to any geometry")
    print()
    print("  WHAT GETS FLAGGED:")
    print("    - Shading groups with no geometry assigned")
    print("    - Materials not connected to any shading group")
    print()
    print("  WHAT DOES NOT GET FLAGGED:")
    print("    - Default materials (lambert1, etc.)")
    print("    - Default shading groups (initialShadingGroup)")
    print("    - Materials properly assigned to geometry")
    print()
    print("  WHY THIS MATTERS:")
    print("    - Clean scenes demonstrate professional workflow")
    print("    - Unused nodes increase file size")
    print("    - Instructors check scene organization in grading")
    print()
    print("=" * 70)
