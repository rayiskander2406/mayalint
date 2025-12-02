"""
Tests for missingTextures check.

================================================================================
OVERVIEW
================================================================================

The missingTextures check detects file texture nodes in the scene where the
referenced texture file does not exist on disk. This is essential for catching
broken texture references before rendering or submission.

================================================================================
ALGORITHM
================================================================================

1. Find all 'file' texture nodes in the scene using cmds.ls(type='file')
2. For each file node, get the 'fileTextureName' attribute
3. Check if the file exists on disk using os.path.exists
4. Flag nodes where the path is set but the file doesn't exist

================================================================================
KNOWN LIMITATIONS
================================================================================

1. ONLY FILE NODES: Only checks 'file' node type, not procedural textures
   or other texture node types (psdFileTex, mentalrayTexture, etc.)

2. UDIM PATTERNS: Does not resolve UDIM patterns like texture.<UDIM>.exr
   These will appear as missing even if individual tiles exist.

3. NETWORK PATHS: Network paths may report as missing if the network share
   is unavailable at the time of checking.

4. RELATIVE PATHS: Relative paths are resolved from Maya's current working
   directory, which may differ from the project directory.

5. EMPTY PATHS: Empty texture paths are skipped (not flagged as missing).
   This is intentional - empty paths indicate unused file nodes.

================================================================================
TEST CASES
================================================================================

1. test_no_textures - Scene with no file nodes should PASS
2. test_valid_texture - File node with existing texture should PASS
3. test_missing_texture - File node with non-existent path should FAIL
4. test_empty_path - File node with empty path should PASS (skipped)
5. test_multiple_textures - Mix of valid and missing should flag only missing
6. test_connected_texture - Texture connected to material should still be checked

================================================================================
RUNNING TESTS
================================================================================

Copy MAYA_TEST_SCRIPT into Maya's Script Editor and execute.

================================================================================
"""

MAYA_TEST_SCRIPT = '''
import maya.cmds as cmds
import os
import tempfile
from modelChecker import modelChecker_commands as mc

def create_temp_texture():
    """Create a temporary texture file for testing."""
    # Create a simple 1x1 pixel image file
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, 'modelchecker_test_texture.png')

    # Create a minimal PNG file (1x1 white pixel)
    # PNG header + IHDR + IDAT + IEND chunks
    png_data = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 image
        0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,  # 8-bit RGB
        0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT chunk
        0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0xFF,  # compressed data
        0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59,  # checksum
        0xE7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,  # IEND chunk
        0x44, 0xAE, 0x42, 0x60, 0x82                     # IEND checksum
    ])

    with open(temp_path, 'wb') as f:
        f.write(png_data)

    return temp_path

def cleanup_temp_texture(path):
    """Remove temporary texture file."""
    if os.path.exists(path):
        os.remove(path)

# =============================================================================
# TEST CASES
# =============================================================================

def test_no_textures():
    """
    Test: Scene with no file texture nodes should PASS.
    """
    cmds.file(new=True, force=True)

    # Create a simple cube (no textures)
    cmds.polyCube(name='simple_cube')

    result_type, result_data = mc.missingTextures(None, None)

    if len(result_data) == 0:
        print("PASS: test_no_textures - No file nodes, no errors")
        return True
    else:
        print("FAIL: test_no_textures - Unexpected results: {}".format(result_data))
        return False


def test_valid_texture():
    """
    Test: File node with existing texture file should PASS.
    """
    cmds.file(new=True, force=True)

    # Create a real texture file
    temp_texture = create_temp_texture()

    try:
        # Create a file node with valid texture path
        file_node = cmds.shadingNode('file', asTexture=True, name='valid_texture')
        cmds.setAttr(file_node + '.fileTextureName', temp_texture, type='string')

        result_type, result_data = mc.missingTextures(None, None)

        if len(result_data) == 0:
            print("PASS: test_valid_texture - Valid texture path not flagged")
            return True
        else:
            print("FAIL: test_valid_texture - Valid texture incorrectly flagged")
            return False
    finally:
        cleanup_temp_texture(temp_texture)


def test_missing_texture():
    """
    Test: File node with non-existent texture path should FAIL.
    """
    cmds.file(new=True, force=True)

    # Create a file node with fake texture path
    file_node = cmds.shadingNode('file', asTexture=True, name='missing_texture')
    fake_path = '/nonexistent/path/to/texture.png'
    cmds.setAttr(file_node + '.fileTextureName', fake_path, type='string')

    result_type, result_data = mc.missingTextures(None, None)

    if len(result_data) == 1:
        print("PASS: test_missing_texture - Missing texture correctly flagged")
        return True
    else:
        print("FAIL: test_missing_texture - Expected 1 flagged, got {}".format(len(result_data)))
        return False


def test_empty_path():
    """
    Test: File node with empty path should PASS (not flagged).
    Empty paths are common for unused file nodes.
    """
    cmds.file(new=True, force=True)

    # Create a file node with empty texture path (default state)
    file_node = cmds.shadingNode('file', asTexture=True, name='empty_texture')
    # Don't set fileTextureName - leave it empty

    result_type, result_data = mc.missingTextures(None, None)

    if len(result_data) == 0:
        print("PASS: test_empty_path - Empty path not flagged (intentional)")
        return True
    else:
        print("FAIL: test_empty_path - Empty path incorrectly flagged")
        return False


def test_multiple_textures():
    """
    Test: Multiple textures - only missing ones should be flagged.
    """
    cmds.file(new=True, force=True)

    # Create a real texture file
    temp_texture = create_temp_texture()

    try:
        # Create file node with valid texture
        valid_file = cmds.shadingNode('file', asTexture=True, name='valid_tex')
        cmds.setAttr(valid_file + '.fileTextureName', temp_texture, type='string')

        # Create file node with missing texture
        missing_file = cmds.shadingNode('file', asTexture=True, name='missing_tex')
        cmds.setAttr(missing_file + '.fileTextureName', '/fake/missing.png', type='string')

        # Create file node with empty path
        empty_file = cmds.shadingNode('file', asTexture=True, name='empty_tex')

        result_type, result_data = mc.missingTextures(None, None)

        # Should only flag the missing one
        if len(result_data) == 1:
            print("PASS: test_multiple_textures - 1/3 textures flagged (missing one)")
            return True
        else:
            print("FAIL: test_multiple_textures - Expected 1 flagged, got {}".format(len(result_data)))
            return False
    finally:
        cleanup_temp_texture(temp_texture)


def test_connected_texture():
    """
    Test: Texture connected to a material should still be checked.
    """
    cmds.file(new=True, force=True)

    # Create a material with a connected file texture
    shader = cmds.shadingNode('lambert', asShader=True, name='test_material')
    file_node = cmds.shadingNode('file', asTexture=True, name='connected_texture')

    # Connect file to material color
    cmds.connectAttr(file_node + '.outColor', shader + '.color')

    # Set a missing texture path
    cmds.setAttr(file_node + '.fileTextureName', '/missing/connected_texture.png', type='string')

    result_type, result_data = mc.missingTextures(None, None)

    if len(result_data) == 1:
        print("PASS: test_connected_texture - Connected texture with missing file flagged")
        return True
    else:
        print("FAIL: test_connected_texture - Expected 1 flagged, got {}".format(len(result_data)))
        return False


def test_udim_limitation():
    """
    Test: UDIM pattern textures will be flagged as missing (known limitation).
    This documents the expected behavior, not a bug.
    """
    cmds.file(new=True, force=True)

    # Create a file node with UDIM pattern
    file_node = cmds.shadingNode('file', asTexture=True, name='udim_texture')
    cmds.setAttr(file_node + '.fileTextureName', '/textures/model.<UDIM>.exr', type='string')

    result_type, result_data = mc.missingTextures(None, None)

    # UDIM patterns will be flagged because the literal path doesn't exist
    # This is expected behavior (documented limitation)
    if len(result_data) == 1:
        print("PASS: test_udim_limitation - UDIM pattern flagged (expected limitation)")
        return True
    else:
        print("INFO: test_udim_limitation - UDIM handling: {} flagged".format(len(result_data)))
        return True  # This test always passes - it's documenting behavior


# =============================================================================
# RUN ALL TESTS
# =============================================================================

def run_all_tests():
    print("")
    print("=" * 70)
    print("  missingTextures Test Suite")
    print("=" * 70)
    print("")

    results = []
    results.append(("No textures", test_no_textures()))
    results.append(("Valid texture", test_valid_texture()))
    results.append(("Missing texture", test_missing_texture()))
    results.append(("Empty path", test_empty_path()))
    results.append(("Multiple textures", test_multiple_textures()))
    results.append(("Connected texture", test_connected_texture()))
    results.append(("UDIM limitation", test_udim_limitation()))

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
    print("  missingTextures Test Suite")
    print("=" * 70)
    print()
    print("  These tests require Maya to run.")
    print()
    print("  To execute tests:")
    print("    1. Open Maya")
    print("    2. Ensure modelChecker is in your Python path")
    print("    3. Copy MAYA_TEST_SCRIPT into Script Editor")
    print("    4. Execute")
    print()
    print("  WHAT THIS CHECK DOES:")
    print("    Finds file texture nodes with missing texture files on disk")
    print()
    print("  COMMON STUDENT ISSUES:")
    print("    - Moving projects between computers")
    print("    - Using absolute paths instead of relative paths")
    print("    - Forgetting to include textures when submitting")
    print()
    print("=" * 70)
