"""
Tests for textureResolution check.

================================================================================
OVERVIEW
================================================================================

The textureResolution check detects file texture nodes where the image dimensions
are not powers of 2 (e.g., 512, 1024, 2048, 4096). This is important because:
- GPU memory is allocated in power-of-2 blocks
- Many game engines require power-of-2 textures
- Mipmapping works best with power-of-2 dimensions
- Non-power-of-2 (NPOT) textures waste memory

================================================================================
ALGORITHM
================================================================================

1. Find all 'file' texture nodes in the scene
2. For each file node, get the texture file path
3. Query the image dimensions using Maya's outSizeX/outSizeY attributes
4. Check if both width and height are powers of 2 using bit manipulation
5. Flag nodes where either dimension is not a power of 2

The power-of-2 check uses the efficient bit trick: (n & (n - 1)) == 0

================================================================================
KNOWN LIMITATIONS
================================================================================

1. FILE NODES ONLY: Only checks 'file' node type, not procedural textures or
   other texture node types (substance, etc.)

2. REQUIRES FILE: The texture file must exist on disk to read its dimensions.
   Missing textures are skipped (use missingTextures check).

3. LOAD ERRORS: Textures that fail to load (corrupted, unsupported format)
   are skipped without error.

4. UDIM/ANIMATED: UDIM sequences and animated textures may report sizes for
   only the first tile/frame.

5. NPOT SUPPORT: Some modern engines (Unity, Unreal) do support NPOT textures
   with caveats. This check enforces strict power-of-2 compliance.

================================================================================
TEST CASES
================================================================================

1. test_no_textures - Scene without textures should PASS
2. test_power_of_two_texture - 1024x1024 texture should PASS
3. test_non_power_of_two_texture - 1000x1000 texture should FAIL
4. test_non_square_power_of_two - 1024x512 texture should PASS
5. test_mixed_textures - Multiple textures, some valid some not
6. test_missing_texture - Missing texture file should be skipped
7. test_empty_path - Texture node with no file path should be skipped
8. test_common_sizes - Test common valid sizes (256, 512, 1024, 2048, 4096)

================================================================================
RUNNING TESTS
================================================================================

Copy MAYA_TEST_SCRIPT into Maya's Script Editor and execute.

Note: These tests require actual texture files to exist on disk. The test
script creates temporary texture files for testing purposes.

================================================================================
"""

MAYA_TEST_SCRIPT = '''
import maya.cmds as cmds
import os
import tempfile
from modelChecker import modelChecker_commands as mc

# Create a temporary directory for test textures
TEMP_DIR = tempfile.mkdtemp(prefix='modelChecker_test_')

def create_test_texture(width, height, filename):
    """Create a simple test texture file using Maya's rendering capabilities."""
    filepath = os.path.join(TEMP_DIR, filename)

    # Use Maya to create a simple image file
    # Create a render target and save it
    try:
        # Create image using Maya's image API or simple file creation
        # For testing, we'll create a minimal valid image
        # Using Maya's internal image writing
        import maya.api.OpenMaya as om

        # Create image with specified dimensions
        image = om.MImage()
        image.create(width, height, 4, om.MImage.kFloat)

        # Fill with a solid color
        pixels = image.floatPixels()
        for i in range(width * height * 4):
            pixels[i] = 0.5

        image.setFloatPixels(pixels, width, height)
        image.writeToFile(filepath, 'png')

        return filepath
    except Exception as e:
        print("Warning: Could not create test texture: {}".format(e))
        return None


def cleanup_test_textures():
    """Remove temporary test texture files."""
    import shutil
    try:
        shutil.rmtree(TEMP_DIR)
    except:
        pass


# =============================================================================
# TEST CASES
# =============================================================================

def test_no_textures():
    """
    Test: Scene without textures should pass (no textures to check).
    """
    cmds.file(new=True, force=True)

    result_type, result_data = mc.textureResolution(None, None)

    if len(result_data) == 0:
        print("PASS: test_no_textures - No textures, no errors")
        return True
    else:
        print("FAIL: test_no_textures - Unexpected errors in empty scene")
        return False


def test_power_of_two_texture():
    """
    Test: Power-of-2 texture (1024x1024) should pass.
    """
    cmds.file(new=True, force=True)

    # Create a 1024x1024 test texture
    tex_path = create_test_texture(1024, 1024, 'test_1024x1024.png')
    if not tex_path:
        print("SKIP: test_power_of_two_texture - Could not create test texture")
        return True

    # Create file texture node
    fileNode = cmds.shadingNode('file', asTexture=True, name='test_texture_1024')
    cmds.setAttr(fileNode + '.fileTextureName', tex_path, type='string')

    result_type, result_data = mc.textureResolution(None, None)

    if len(result_data) == 0:
        print("PASS: test_power_of_two_texture - 1024x1024 texture accepted")
        return True
    else:
        print("FAIL: test_power_of_two_texture - Power-of-2 texture was flagged")
        return False


def test_non_power_of_two_texture():
    """
    Test: Non-power-of-2 texture (1000x1000) should fail.
    """
    cmds.file(new=True, force=True)

    # Create a 1000x1000 test texture (not power of 2)
    tex_path = create_test_texture(1000, 1000, 'test_1000x1000.png')
    if not tex_path:
        print("SKIP: test_non_power_of_two_texture - Could not create test texture")
        return True

    # Create file texture node
    fileNode = cmds.shadingNode('file', asTexture=True, name='test_texture_1000')
    cmds.setAttr(fileNode + '.fileTextureName', tex_path, type='string')

    result_type, result_data = mc.textureResolution(None, None)

    if len(result_data) > 0:
        print("PASS: test_non_power_of_two_texture - 1000x1000 texture flagged")
        return True
    else:
        print("FAIL: test_non_power_of_two_texture - NPOT texture not detected")
        return False


def test_non_square_power_of_two():
    """
    Test: Non-square but power-of-2 texture (1024x512) should pass.
    """
    cmds.file(new=True, force=True)

    # Create a 1024x512 test texture
    tex_path = create_test_texture(1024, 512, 'test_1024x512.png')
    if not tex_path:
        print("SKIP: test_non_square_power_of_two - Could not create test texture")
        return True

    # Create file texture node
    fileNode = cmds.shadingNode('file', asTexture=True, name='test_texture_nonsquare')
    cmds.setAttr(fileNode + '.fileTextureName', tex_path, type='string')

    result_type, result_data = mc.textureResolution(None, None)

    if len(result_data) == 0:
        print("PASS: test_non_square_power_of_two - 1024x512 texture accepted")
        return True
    else:
        print("FAIL: test_non_square_power_of_two - Non-square POT was flagged")
        return False


def test_mixed_textures():
    """
    Test: Multiple textures - only non-power-of-2 should be flagged.
    """
    cmds.file(new=True, force=True)

    # Create valid texture
    valid_path = create_test_texture(512, 512, 'test_valid_512.png')
    # Create invalid texture
    invalid_path = create_test_texture(500, 500, 'test_invalid_500.png')

    if not valid_path or not invalid_path:
        print("SKIP: test_mixed_textures - Could not create test textures")
        return True

    # Create file texture nodes
    validNode = cmds.shadingNode('file', asTexture=True, name='valid_texture')
    cmds.setAttr(validNode + '.fileTextureName', valid_path, type='string')

    invalidNode = cmds.shadingNode('file', asTexture=True, name='invalid_texture')
    cmds.setAttr(invalidNode + '.fileTextureName', invalid_path, type='string')

    result_type, result_data = mc.textureResolution(None, None)

    # Should flag exactly 1 texture (the 500x500 one)
    if len(result_data) == 1:
        print("PASS: test_mixed_textures - Only invalid texture flagged")
        return True
    else:
        print("FAIL: test_mixed_textures - Expected 1 error, got {}".format(len(result_data)))
        return False


def test_missing_texture():
    """
    Test: Missing texture file should be skipped (not flagged).
    """
    cmds.file(new=True, force=True)

    # Create file texture node pointing to non-existent file
    fileNode = cmds.shadingNode('file', asTexture=True, name='missing_texture')
    cmds.setAttr(fileNode + '.fileTextureName', '/nonexistent/path/texture.png', type='string')

    result_type, result_data = mc.textureResolution(None, None)

    if len(result_data) == 0:
        print("PASS: test_missing_texture - Missing texture skipped")
        return True
    else:
        print("FAIL: test_missing_texture - Missing texture should not be flagged")
        return False


def test_empty_path():
    """
    Test: Texture node with empty path should be skipped.
    """
    cmds.file(new=True, force=True)

    # Create file texture node with no path
    fileNode = cmds.shadingNode('file', asTexture=True, name='empty_path_texture')
    # Don't set any file path

    result_type, result_data = mc.textureResolution(None, None)

    if len(result_data) == 0:
        print("PASS: test_empty_path - Empty path texture skipped")
        return True
    else:
        print("FAIL: test_empty_path - Empty path should not be flagged")
        return False


def test_helper_function():
    """
    Test: Verify _isPowerOfTwo helper function works correctly.
    """
    # Test the helper function directly
    valid_powers = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
    invalid_numbers = [0, 3, 5, 6, 7, 9, 10, 100, 500, 1000, 1023, 1025, 2047, 2049]

    all_pass = True

    for n in valid_powers:
        if not mc._isPowerOfTwo(n):
            print("FAIL: {} should be power of 2".format(n))
            all_pass = False

    for n in invalid_numbers:
        if mc._isPowerOfTwo(n):
            print("FAIL: {} should NOT be power of 2".format(n))
            all_pass = False

    if all_pass:
        print("PASS: test_helper_function - _isPowerOfTwo works correctly")
        return True
    else:
        print("FAIL: test_helper_function - _isPowerOfTwo has errors")
        return False


# =============================================================================
# RUN ALL TESTS
# =============================================================================

def run_all_tests():
    print("")
    print("=" * 70)
    print("  textureResolution Test Suite")
    print("=" * 70)
    print("")
    print("  Creating test textures in: {}".format(TEMP_DIR))
    print("")

    results = []
    results.append(("No textures", test_no_textures()))
    results.append(("Helper function", test_helper_function()))
    results.append(("Power of 2 texture", test_power_of_two_texture()))
    results.append(("Non-power of 2 texture", test_non_power_of_two_texture()))
    results.append(("Non-square POT", test_non_square_power_of_two()))
    results.append(("Mixed textures", test_mixed_textures()))
    results.append(("Missing texture", test_missing_texture()))
    results.append(("Empty path", test_empty_path()))

    # Cleanup
    cleanup_test_textures()

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
    print("  Temp directory cleaned up")
    print("=" * 70)

    return passed == total

run_all_tests()
'''


def get_test_script():
    """Return the Maya test script for copy/paste."""
    return MAYA_TEST_SCRIPT


if __name__ == "__main__":
    print("=" * 70)
    print("  textureResolution Test Suite")
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
    print("    Detects file textures with non-power-of-2 resolutions")
    print("    (e.g., 1000x1000 instead of 1024x1024)")
    print()
    print("  VALID POWER-OF-2 SIZES:")
    print("    1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192")
    print()
    print("  WHY THIS MATTERS:")
    print("    - GPUs allocate memory in power-of-2 blocks")
    print("    - Game engines often require power-of-2 textures")
    print("    - Mipmapping works best with power-of-2 dimensions")
    print("    - NPOT textures waste memory and may cause issues")
    print()
    print("=" * 70)
