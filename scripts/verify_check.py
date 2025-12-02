#!/usr/bin/env python3
"""
Check Verification Script

Automatically verifies that a check is properly implemented:
1. Syntax check all Python files
2. Verify function exists with correct name
3. Verify registration exists
4. Cross-reference all commands have functions
5. Check test file exists
6. Verify CHECKS.md entry exists

Usage:
    python scripts/verify_check.py <check_id>
    python scripts/verify_check.py --all

Example:
    python scripts/verify_check.py flipped_normals
"""

import ast
import json
import os
import re
import subprocess
import sys

RELEASE_PLAN_PATH = ".claude/release-plan.json"
COMMANDS_FILE = "mayaLint/mayaLint_commands.py"
LIST_FILE = "mayaLint/mayaLint_list.py"
CHECKS_MD = "CHECKS.md"
TESTS_DIR = "tests"


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def ok(msg):
    print(f"  {Colors.GREEN}✓{Colors.END} {msg}")


def fail(msg):
    print(f"  {Colors.RED}✗{Colors.END} {msg}")


def warn(msg):
    print(f"  {Colors.YELLOW}!{Colors.END} {msg}")


def info(msg):
    print(f"  {Colors.BLUE}ℹ{Colors.END} {msg}")


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


def check_syntax(filepath):
    """Check Python syntax."""
    try:
        result = subprocess.run(
            ['python3', '-m', 'py_compile', filepath],
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stderr
    except Exception as e:
        return False, str(e)


def get_functions_in_file(filepath):
    """Get all function names defined in a Python file."""
    with open(filepath, 'r') as f:
        try:
            tree = ast.parse(f.read())
            return [node.name for node in ast.walk(tree)
                    if isinstance(node, ast.FunctionDef)]
        except SyntaxError:
            return []


def get_registered_commands(filepath):
    """Get all command keys from the list file."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Use regex to find all quoted keys in the dict
    pattern = r'^\s*["\'](\w+)["\']:\s*\{'
    matches = re.findall(pattern, content, re.MULTILINE)
    return matches


def check_function_exists(func_name):
    """Check if function exists in commands file."""
    functions = get_functions_in_file(COMMANDS_FILE)
    return func_name in functions


def check_registration_exists(func_name):
    """Check if function is registered in list file."""
    commands = get_registered_commands(LIST_FILE)
    return func_name in commands


def check_test_file_exists(check_id):
    """Check if test file exists."""
    test_path = os.path.join(TESTS_DIR, f"test_{check_id}.py")
    return os.path.exists(test_path)


def check_documentation_exists(func_name):
    """Check if documentation exists in CHECKS.md."""
    if not os.path.exists(CHECKS_MD):
        return False

    with open(CHECKS_MD, 'r') as f:
        content = f.read()

    # Look for function name in documentation
    return func_name in content or func_name.replace('_', ' ').title() in content


def count_test_cases(check_id):
    """Count test cases in test file."""
    test_path = os.path.join(TESTS_DIR, f"test_{check_id}.py")
    if not os.path.exists(test_path):
        return 0

    with open(test_path, 'r') as f:
        content = f.read()

    # Count def test_ functions
    return len(re.findall(r'def test_\w+', content))


def verify_check(check_id, verbose=True):
    """Verify a single check implementation."""
    release_plan = load_release_plan()
    check, phase_key, phase = find_check(release_plan, check_id)

    if not check:
        if verbose:
            fail(f"Check '{check_id}' not found in release plan")
        return False, []

    func_name = check['function']
    issues = []

    if verbose:
        print(f"\n{'='*60}")
        print(f"  Verifying: {check['name']}")
        print(f"  Function:  {func_name}")
        print(f"  Category:  {check['category']}")
        print(f"  Status:    {check['status']}")
        print(f"{'='*60}\n")

    # 1. Syntax check
    if verbose:
        print("Syntax Checks:")

    syntax_ok, error = check_syntax(COMMANDS_FILE)
    if syntax_ok:
        if verbose:
            ok(f"{COMMANDS_FILE} - syntax valid")
    else:
        if verbose:
            fail(f"{COMMANDS_FILE} - syntax error: {error}")
        issues.append("Commands file has syntax errors")

    syntax_ok, error = check_syntax(LIST_FILE)
    if syntax_ok:
        if verbose:
            ok(f"{LIST_FILE} - syntax valid")
    else:
        if verbose:
            fail(f"{LIST_FILE} - syntax error: {error}")
        issues.append("List file has syntax errors")

    # 2. Function exists
    if verbose:
        print("\nFunction Check:")

    if check_function_exists(func_name):
        if verbose:
            ok(f"Function '{func_name}' exists in commands file")
    else:
        if verbose:
            fail(f"Function '{func_name}' NOT FOUND in commands file")
        issues.append(f"Function '{func_name}' not implemented")

    # 3. Registration exists
    if verbose:
        print("\nRegistration Check:")

    if check_registration_exists(func_name):
        if verbose:
            ok(f"Function '{func_name}' is registered in list file")
    else:
        if verbose:
            fail(f"Function '{func_name}' NOT REGISTERED in list file")
        issues.append(f"Function '{func_name}' not registered")

    # 4. Cross-reference
    if verbose:
        print("\nCross-Reference Check:")

    functions = get_functions_in_file(COMMANDS_FILE)
    commands = get_registered_commands(LIST_FILE)

    # Filter out private functions
    public_functions = [f for f in functions if not f.startswith('_')]

    missing_funcs = [c for c in commands if c not in public_functions]
    missing_regs = [f for f in public_functions if f not in commands
                    and f not in ['pattern_', 'helper_']]

    if not missing_funcs:
        if verbose:
            ok(f"All {len(commands)} registered commands have functions")
    else:
        if verbose:
            fail(f"Missing functions: {missing_funcs}")
        issues.append(f"Missing function implementations: {missing_funcs}")

    # 5. Test file
    if verbose:
        print("\nTest File Check:")

    if check_test_file_exists(check_id):
        test_count = count_test_cases(check_id)
        if test_count >= 4:
            if verbose:
                ok(f"Test file exists with {test_count} test cases")
        else:
            if verbose:
                warn(f"Test file exists but only has {test_count} test cases (need 4+)")
            issues.append(f"Test file needs more test cases ({test_count}/4)")
    else:
        if verbose:
            fail(f"Test file 'tests/test_{check_id}.py' not found")
        issues.append("Test file not created")

    # 6. Documentation
    if verbose:
        print("\nDocumentation Check:")

    if check_documentation_exists(func_name):
        if verbose:
            ok(f"Documentation found in CHECKS.md")
    else:
        if verbose:
            warn(f"Documentation not found in CHECKS.md")
        issues.append("Documentation not added to CHECKS.md")

    # Summary
    if verbose:
        print(f"\n{'='*60}")
        if not issues:
            print(f"  {Colors.GREEN}{Colors.BOLD}ALL CHECKS PASSED{Colors.END}")
            print(f"  Ready for: /finish {check_id}")
        else:
            print(f"  {Colors.RED}{Colors.BOLD}ISSUES FOUND ({len(issues)}){Colors.END}")
            for issue in issues:
                print(f"    • {issue}")
        print(f"{'='*60}\n")

    return len(issues) == 0, issues


def verify_all():
    """Verify all checks in release plan."""
    release_plan = load_release_plan()

    results = {
        'completed': [],
        'in_progress': [],
        'not_started': [],
        'issues': []
    }

    print(f"\n{'='*60}")
    print(f"  Verifying All Checks")
    print(f"{'='*60}\n")

    for phase_key, phase in release_plan['phases'].items():
        print(f"\n{phase['name'].upper()}:")

        for check in phase['checks']:
            check_id = check['id']
            status = check['status']

            if status == 'not_started':
                print(f"  [ ] {check_id} - not started")
                results['not_started'].append(check_id)
            else:
                passed, issues = verify_check(check_id, verbose=False)

                if passed:
                    icon = "✓" if status == 'completed' else "~"
                    print(f"  [{icon}] {check_id} - {status}")
                    results[status].append(check_id)
                else:
                    print(f"  [✗] {check_id} - has issues: {issues}")
                    results['issues'].append((check_id, issues))

    # Summary
    print(f"\n{'='*60}")
    print(f"  Summary")
    print(f"{'='*60}")
    print(f"  Completed:    {len(results['completed'])}")
    print(f"  In Progress:  {len(results['in_progress'])}")
    print(f"  Not Started:  {len(results['not_started'])}")
    print(f"  With Issues:  {len(results['issues'])}")

    if results['issues']:
        print(f"\n  Checks with issues:")
        for check_id, issues in results['issues']:
            print(f"    • {check_id}: {', '.join(issues)}")

    print(f"{'='*60}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/verify_check.py <check_id>")
        print("       python scripts/verify_check.py --all")
        sys.exit(1)

    if sys.argv[1] == '--all':
        verify_all()
    else:
        verify_check(sys.argv[1])


if __name__ == "__main__":
    main()
