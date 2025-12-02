#!/usr/bin/env python3
"""
Check Scaffold Generator

Generates boilerplate code for new mayaLint checks:
- Test file template
- Docstring template
- CHECKS.md entry template

Usage:
    python scripts/generate_scaffold.py <check_id>

Example:
    python scripts/generate_scaffold.py overlapping_vertices
"""

import json
import os
import sys
from datetime import datetime

RELEASE_PLAN_PATH = ".claude/release-plan.json"


def load_release_plan():
    """Load the release plan JSON."""
    with open(RELEASE_PLAN_PATH, 'r') as f:
        return json.load(f)


def find_check(release_plan, check_id):
    """Find a check by ID in the release plan."""
    for phase_key, phase in release_plan['phases'].items():
        for check in phase['checks']:
            if check['id'] == check_id:
                return check, phase_key, phase
    return None, None, None


def generate_docstring(check):
    """Generate the function docstring template."""
    return f'''    """{check['description']}

    {check.get('why_matters', 'Explain why this matters for academic evaluation.')}

    Algorithm:
        1. [Step one - describe what happens first]
        2. [Step two - describe the main processing]
        3. [Step three - describe how results are collected]

    Args:
        nodes: List of node UUIDs to check (use _ if not needed)
        SLMesh: MSelectionList containing mesh shapes (use _ if not needed)

    Returns:
        tuple: ("{check['category']}", errors)
            - For "nodes" type: list of UUIDs
            - For component types: dict mapping UUID -> list of indices

    Known Limitations:
        - [Limitation 1 - describe when this check may not work perfectly]
        - [Limitation 2 - describe edge cases]

    Academic Use:
        {check.get('why_matters', 'This check helps ensure professional quality work.')}
    """'''


def generate_function_template(check):
    """Generate the function implementation template."""
    func_name = check['function']
    category = check['category']

    # Determine return type based on category
    if category in ['naming', 'general', 'scene']:
        return_type = 'nodes'
        error_init = '[]'
        error_append = f'{func_name}.append(node)'
    else:
        return_type = 'polygon'  # or vertex, edge, uv
        error_init = 'defaultdict(list)'
        error_append = f'{func_name}[uuid].append(index)'

    hint = check.get('algorithm_hint', '# TODO: Implement algorithm')

    return f'''
def {func_name}(nodes, SLMesh):
{generate_docstring(check)}
    {func_name} = {error_init}

    # Algorithm hint: {hint}

    # TODO: Implement check logic here
    # For node-based checks:
    #   for node in nodes:
    #       nodeName = _getNodeName(node)
    #       if <condition>:
    #           {func_name}.append(node)
    #
    # For mesh component checks:
    #   selIt = om.MItSelectionList(SLMesh)
    #   while not selIt.isDone():
    #       # Process mesh...
    #       selIt.next()

    return "{return_type}", {func_name}
'''


def generate_test_file(check, phase):
    """Generate the complete test file."""
    check_id = check['id']
    func_name = check['function']
    check_name = check['name']
    description = check['description']
    why_matters = check.get('why_matters', 'Important for academic evaluation')
    hint = check.get('algorithm_hint', 'See implementation')

    return f'''"""
Tests for {func_name} check.

================================================================================
OVERVIEW
================================================================================

The {func_name} check {description.lower()}

Why It Matters:
{why_matters}

================================================================================
ALGORITHM
================================================================================

{hint}

================================================================================
KNOWN LIMITATIONS
================================================================================

1. [Document any known limitations here]
2. [Describe edge cases that may not work perfectly]

================================================================================
TEST CASES
================================================================================

1. test_pass_case - Clean geometry should pass
2. test_fail_case - Problematic geometry should be detected
3. test_edge_case - Edge cases handled gracefully
4. test_empty_selection - Empty input should not crash
5. test_limitation - Document known limitation behavior

================================================================================
RUNNING TESTS
================================================================================

Option 1: Maya Script Editor
   - Copy MAYA_TEST_SCRIPT below into Maya's Script Editor
   - Execute

Option 2: mayapy
   - mayapy tests/test_{check_id}.py

================================================================================
"""

MAYA_TEST_SCRIPT = \'\'\'
import maya.cmds as cmds
import maya.api.OpenMaya as om
from mayaLint import mayaLint_commands as mc

# -----------------------------------------------------------------------------
# Test 1: Pass Case (should PASS - no issues detected)
# -----------------------------------------------------------------------------
def test_pass_case():
    """Test that clean geometry passes the check."""
    cmds.file(new=True, force=True)

    # Create clean test geometry
    obj = cmds.polyCube(name='test_clean')[0]

    # Get shape and create selection list
    shape = cmds.listRelatives(obj, shapes=True)[0]
    selList = om.MSelectionList()
    selList.add(shape)

    # Get node UUIDs
    nodes = [cmds.ls(obj, uuid=True)[0]]

    result_type, result_data = mc.{func_name}(nodes, selList)

    if len(result_data) == 0:
        print("TEST 1 PASSED: Clean geometry has no issues")
        return True
    else:
        print("TEST 1 FAILED: Clean geometry incorrectly flagged")
        print("  Found:", result_data)
        return False

# -----------------------------------------------------------------------------
# Test 2: Fail Case (should FAIL - issues detected)
# -----------------------------------------------------------------------------
def test_fail_case():
    """Test that problematic geometry is detected."""
    cmds.file(new=True, force=True)

    # Create problematic test geometry
    obj = cmds.polyCube(name='test_problem')[0]

    # TODO: Modify geometry to trigger the check
    # Example: cmds.polyNormal(obj, normalMode=0)  # for flipped normals

    # Get shape and create selection list
    shape = cmds.listRelatives(obj, shapes=True)[0]
    selList = om.MSelectionList()
    selList.add(shape)

    nodes = [cmds.ls(obj, uuid=True)[0]]

    result_type, result_data = mc.{func_name}(nodes, selList)

    if len(result_data) > 0:
        print("TEST 2 PASSED: Problematic geometry detected")
        return True
    else:
        print("TEST 2 FAILED: Problem was not detected")
        return False

# -----------------------------------------------------------------------------
# Test 3: Edge Case
# -----------------------------------------------------------------------------
def test_edge_case():
    """Test edge case handling."""
    cmds.file(new=True, force=True)

    # Create edge case geometry (e.g., single vertex, empty mesh, etc.)
    obj = cmds.polyCube(name='test_edge')[0]

    # TODO: Create specific edge case

    shape = cmds.listRelatives(obj, shapes=True)[0]
    selList = om.MSelectionList()
    selList.add(shape)

    nodes = [cmds.ls(obj, uuid=True)[0]]

    try:
        result_type, result_data = mc.{func_name}(nodes, selList)
        print("TEST 3 PASSED: Edge case handled without error")
        return True
    except Exception as e:
        print("TEST 3 FAILED: Edge case caused exception:", str(e))
        return False

# -----------------------------------------------------------------------------
# Test 4: Empty Selection (should not crash)
# -----------------------------------------------------------------------------
def test_empty_selection():
    """Test that empty selection is handled gracefully."""
    cmds.file(new=True, force=True)

    selList = om.MSelectionList()
    nodes = []

    try:
        result_type, result_data = mc.{func_name}(nodes, selList)
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
# Test 5: Known Limitation (documents expected behavior)
# -----------------------------------------------------------------------------
def test_limitation():
    """
    Document known limitation behavior.

    This test creates geometry that may trigger false positives/negatives
    due to known limitations. This is expected behavior, not a bug.
    """
    cmds.file(new=True, force=True)

    # TODO: Create geometry that demonstrates a known limitation
    obj = cmds.polyCube(name='test_limitation')[0]

    shape = cmds.listRelatives(obj, shapes=True)[0]
    selList = om.MSelectionList()
    selList.add(shape)

    nodes = [cmds.ls(obj, uuid=True)[0]]

    result_type, result_data = mc.{func_name}(nodes, selList)

    print("TEST 5 (LIMITATION): Check completed")
    print("  NOTE: This documents expected behavior for edge cases")
    print("  Results:", len(result_data), "items flagged")
    return True

# -----------------------------------------------------------------------------
# Run All Tests
# -----------------------------------------------------------------------------
def run_all_tests():
    print("")
    print("=" * 70)
    print("  {func_name} Test Suite")
    print("=" * 70)
    print("")

    results = []
    results.append(("Pass Case", test_pass_case()))
    results.append(("Fail Case", test_fail_case()))
    results.append(("Edge Case", test_edge_case()))
    results.append(("Empty Selection", test_empty_selection()))
    results.append(("Limitation", test_limitation()))

    print("")
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print("  [{{}}] {{}}".format(status, name))
    print("")
    print("  Total: {{}}/{{}}" .format(passed, total))
    print("=" * 70)

run_all_tests()
\'\'\'


def get_test_script():
    """Return the Maya test script for copy/paste."""
    return MAYA_TEST_SCRIPT


if __name__ == "__main__":
    print("=" * 70)
    print("  {func_name} Test Suite")
    print("=" * 70)
    print()
    print("  These tests require Maya to run.")
    print()
    print("  To execute tests:")
    print("  1. Open Maya")
    print("  2. Ensure mayaLint is in your Python path")
    print("  3. Copy MAYA_TEST_SCRIPT into Script Editor")
    print("  4. Execute")
    print()
    print("=" * 70)
'''


def generate_checks_md_entry(check, phase):
    """Generate the CHECKS.md documentation entry."""
    func_name = check['function']
    check_name = check['name']
    category = check['category']
    description = check['description']
    why_matters = check.get('why_matters', 'Important for academic evaluation')
    hint = check.get('algorithm_hint', 'See implementation')

    return f'''
### {check_name}

**Category:** {category}
**Function:** `{func_name}`
**Returns:** [nodes/vertex/edge/polygon/uv]

#### Description

{description}

#### How It Works

{hint}

#### Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| [Limitation 1] | [What happens] | [How to work around it] |

#### When This Check Helps

- {why_matters}
- [Additional use case]

#### When to Ignore Results

- [Situation where false positives are expected]

#### How to Fix

In Maya:
1. Select the flagged [nodes/components]
2. [Specific fix instructions]
3. Re-run the check to verify

#### Test Cases

| Test | Expected Result |
|------|-----------------|
| Clean geometry | PASS |
| Problematic geometry | FAIL (issues detected) |
| Edge case | Handled gracefully |
| Empty selection | PASS (no crash) |
'''


def generate_registration_entry(check):
    """Generate the mayaLint_list.py entry."""
    func_name = check['function']
    label = check['name']
    category = check['category']

    return f'''    "{func_name}": {{
        'label': '{label}',
        'category': '{category}',
    }},'''


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_scaffold.py <check_id>")
        print("\nAvailable check IDs:")
        release_plan = load_release_plan()
        for phase_key, phase in release_plan['phases'].items():
            print(f"\n  {phase['name']}:")
            for check in phase['checks']:
                status_icon = "✓" if check['status'] == 'completed' else " "
                print(f"    [{status_icon}] {check['id']}")
        sys.exit(1)

    check_id = sys.argv[1]
    release_plan = load_release_plan()
    check, phase_key, phase = find_check(release_plan, check_id)

    if not check:
        print(f"Error: Check '{check_id}' not found in release plan")
        sys.exit(1)

    if check['status'] == 'completed':
        print(f"Warning: Check '{check_id}' is already completed")

    print(f"\n{'='*70}")
    print(f"  Generating scaffold for: {check['name']}")
    print(f"  Phase: {phase['name']} | Category: {check['category']}")
    print(f"{'='*70}\n")

    # Generate outputs
    print("=" * 70)
    print("1. FUNCTION TEMPLATE (paste into mayaLint_commands.py)")
    print("=" * 70)
    print(generate_function_template(check))

    print("\n" + "=" * 70)
    print("2. REGISTRATION (paste into mayaLint_list.py)")
    print("=" * 70)
    print(generate_registration_entry(check))

    print("\n" + "=" * 70)
    print("3. TEST FILE (will be created at tests/test_{}.py)".format(check_id))
    print("=" * 70)

    # Create test file
    test_dir = "tests"
    os.makedirs(test_dir, exist_ok=True)
    test_path = os.path.join(test_dir, f"test_{check_id}.py")

    if os.path.exists(test_path):
        print(f"  Test file already exists: {test_path}")
    else:
        with open(test_path, 'w') as f:
            f.write(generate_test_file(check, phase))
        print(f"  Created: {test_path}")

    print("\n" + "=" * 70)
    print("4. CHECKS.MD ENTRY (paste into CHECKS.md)")
    print("=" * 70)
    print(generate_checks_md_entry(check, phase))

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("""
1. Copy the FUNCTION TEMPLATE into mayaLint_commands.py
2. Implement the TODO sections in the function
3. Copy the REGISTRATION entry into mayaLint_list.py
4. Update the generated test file with specific test logic
5. Copy the CHECKS.MD ENTRY into CHECKS.md
6. Run /finish {} to verify and commit
""".format(check_id))


if __name__ == "__main__":
    main()
