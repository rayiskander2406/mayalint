"""
Tests for sceneUnits check.

================================================================================
OVERVIEW
================================================================================

The sceneUnits check verifies that the scene's linear unit setting matches
the expected standard (default: centimeters). This is a scene-level check
that doesn't operate on individual objects.

Wrong units are a common cause of scale issues when exporting to game engines
or collaborating with others.

================================================================================
ALGORITHM
================================================================================

1. Query Maya's current linear unit using cmds.currentUnit(query=True, linear=True)
2. Compare against the expected unit (EXPECTED_LINEAR_UNIT constant)
3. Return a special marker if units don't match, empty list if correct

================================================================================
KNOWN LIMITATIONS
================================================================================

1. LINEAR ONLY: Only checks linear units, not angular or time units.
   Some workflows may also require specific angular units.

2. HARD-CODED DEFAULT: The expected unit (cm) is hard-coded.
   To change it, edit EXPECTED_LINEAR_UNIT in modelChecker_commands.py.

3. NO AUTO-FIX: The check doesn't offer to fix units because changing
   units would require scaling all existing geometry.

4. SCENE-LEVEL: This is a scene property, not per-object. The result
   applies to the entire scene.

================================================================================
TEST CASES
================================================================================

1. test_centimeters - Scene set to cm (default) should PASS
2. test_meters - Scene set to meters should FAIL
3. test_millimeters - Scene set to mm should FAIL
4. test_inches - Scene set to inches should FAIL
5. test_restore_units - Verify units can be changed back
6. test_configurable_expected - Test that constant can be modified

================================================================================
RUNNING TESTS
================================================================================

Copy MAYA_TEST_SCRIPT into Maya's Script Editor and execute.

================================================================================
"""

MAYA_TEST_SCRIPT = '''
import maya.cmds as cmds
from modelChecker import modelChecker_commands as mc

# Store original expected unit to restore after tests
ORIGINAL_EXPECTED = mc.EXPECTED_LINEAR_UNIT

def get_current_unit():
    """Helper to get current linear unit."""
    return cmds.currentUnit(query=True, linear=True)

def set_unit(unit):
    """Helper to set linear unit."""
    cmds.currentUnit(linear=unit)

# =============================================================================
# TEST CASES
# =============================================================================

def test_centimeters():
    """
    Test: Scene set to centimeters (Maya default) should PASS.
    """
    # Reset expected to default
    mc.EXPECTED_LINEAR_UNIT = 'cm'

    # Set scene to centimeters
    set_unit('cm')

    result_type, result_data = mc.sceneUnits(None, None)

    if len(result_data) == 0:
        print("PASS: test_centimeters - Scene in cm matches expected cm")
        return True
    else:
        print("FAIL: test_centimeters - Scene in cm incorrectly flagged")
        print("      Current unit: {}, Expected: {}".format(get_current_unit(), mc.EXPECTED_LINEAR_UNIT))
        return False


def test_meters():
    """
    Test: Scene set to meters should FAIL (when expecting cm).
    """
    mc.EXPECTED_LINEAR_UNIT = 'cm'

    # Set scene to meters
    set_unit('m')

    result_type, result_data = mc.sceneUnits(None, None)

    if len(result_data) == 1 and 'SCENE_UNITS_MISMATCH' in result_data[0]:
        print("PASS: test_meters - Scene in meters correctly flagged")
        return True
    else:
        print("FAIL: test_meters - Scene in meters not flagged")
        return False


def test_millimeters():
    """
    Test: Scene set to millimeters should FAIL (when expecting cm).
    """
    mc.EXPECTED_LINEAR_UNIT = 'cm'

    # Set scene to millimeters
    set_unit('mm')

    result_type, result_data = mc.sceneUnits(None, None)

    if len(result_data) == 1 and 'SCENE_UNITS_MISMATCH' in result_data[0]:
        print("PASS: test_millimeters - Scene in mm correctly flagged")
        return True
    else:
        print("FAIL: test_millimeters - Scene in mm not flagged")
        return False


def test_inches():
    """
    Test: Scene set to inches should FAIL (when expecting cm).
    """
    mc.EXPECTED_LINEAR_UNIT = 'cm'

    # Set scene to inches
    set_unit('in')

    result_type, result_data = mc.sceneUnits(None, None)

    if len(result_data) == 1 and 'SCENE_UNITS_MISMATCH' in result_data[0]:
        print("PASS: test_inches - Scene in inches correctly flagged")
        return True
    else:
        print("FAIL: test_inches - Scene in inches not flagged")
        return False


def test_feet():
    """
    Test: Scene set to feet should FAIL (when expecting cm).
    """
    mc.EXPECTED_LINEAR_UNIT = 'cm'

    # Set scene to feet
    set_unit('ft')

    result_type, result_data = mc.sceneUnits(None, None)

    if len(result_data) == 1 and 'SCENE_UNITS_MISMATCH' in result_data[0]:
        print("PASS: test_feet - Scene in feet correctly flagged")
        return True
    else:
        print("FAIL: test_feet - Scene in feet not flagged")
        return False


def test_configurable_expected():
    """
    Test: Verify the expected unit can be configured.
    If we expect meters, then meters should PASS and cm should FAIL.
    """
    # Change expected to meters
    mc.EXPECTED_LINEAR_UNIT = 'm'

    # Set scene to meters - should pass now
    set_unit('m')
    result_type, result_data = mc.sceneUnits(None, None)
    meters_pass = len(result_data) == 0

    # Set scene to cm - should fail now
    set_unit('cm')
    result_type, result_data = mc.sceneUnits(None, None)
    cm_fail = len(result_data) == 1

    if meters_pass and cm_fail:
        print("PASS: test_configurable_expected - Expected unit is configurable")
        return True
    else:
        print("FAIL: test_configurable_expected - Configuration not working")
        print("      Meters pass: {}, CM fail: {}".format(meters_pass, cm_fail))
        return False


def test_mismatch_message_format():
    """
    Test: Verify the mismatch message contains useful information.
    """
    mc.EXPECTED_LINEAR_UNIT = 'cm'
    set_unit('m')

    result_type, result_data = mc.sceneUnits(None, None)

    if len(result_data) == 1:
        message = result_data[0]
        has_current = 'm' in message
        has_expected = 'cm' in message

        if has_current and has_expected:
            print("PASS: test_mismatch_message_format - Message contains unit info")
            print("      Message: {}".format(message))
            return True
        else:
            print("FAIL: test_mismatch_message_format - Message missing unit info")
            print("      Message: {}".format(message))
            return False
    else:
        print("FAIL: test_mismatch_message_format - No mismatch detected")
        return False


# =============================================================================
# RUN ALL TESTS
# =============================================================================

def run_all_tests():
    print("")
    print("=" * 70)
    print("  sceneUnits Test Suite")
    print("=" * 70)
    print("")
    print("  Current scene unit: {}".format(get_current_unit()))
    print("  Expected unit: {}".format(mc.EXPECTED_LINEAR_UNIT))
    print("")

    # Store original unit to restore
    original_unit = get_current_unit()

    results = []
    results.append(("Centimeters (default)", test_centimeters()))
    results.append(("Meters", test_meters()))
    results.append(("Millimeters", test_millimeters()))
    results.append(("Inches", test_inches()))
    results.append(("Feet", test_feet()))
    results.append(("Configurable expected", test_configurable_expected()))
    results.append(("Mismatch message format", test_mismatch_message_format()))

    # Restore original unit and expected value
    set_unit(original_unit)
    mc.EXPECTED_LINEAR_UNIT = ORIGINAL_EXPECTED

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
    print("  Scene unit restored to: {}".format(get_current_unit()))
    print("  Expected unit restored to: {}".format(mc.EXPECTED_LINEAR_UNIT))
    print("=" * 70)

    return passed == total

run_all_tests()
'''


def get_test_script():
    """Return the Maya test script for copy/paste."""
    return MAYA_TEST_SCRIPT


if __name__ == "__main__":
    print("=" * 70)
    print("  sceneUnits Test Suite")
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
    print("    Verifies scene linear units match expected value (default: cm)")
    print()
    print("  DEFAULT EXPECTED UNIT: centimeters (cm)")
    print()
    print("  TO CUSTOMIZE EXPECTED UNIT:")
    print("    Edit EXPECTED_LINEAR_UNIT in modelChecker_commands.py")
    print("    Common values: cm, m, mm, in, ft")
    print()
    print("  COMMON UNIT STANDARDS:")
    print("    - Maya default: centimeters")
    print("    - Unity: meters (1 unit = 1 meter)")
    print("    - Unreal: centimeters (1 unit = 1 cm)")
    print("    - Blender: meters")
    print()
    print("=" * 70)
