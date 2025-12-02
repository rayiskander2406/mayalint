# Start Check Implementation Command

You are starting the implementation of a new check for the modelChecker Academic Extension.

## Arguments
The user should provide: `/start <check_id>`

Available check IDs (run `/plan-release` to see current status):
- Phase 1: flipped_normals, overlapping_vertices, poly_count_limit, missing_textures, default_materials, scene_units
- Phase 2: uv_distortion, texel_density, texture_resolution, unused_nodes, hidden_objects
- Phase 3: naming_convention, hierarchy_depth, concave_faces, intermediate_objects

---

## Complete Implementation Workflow

When starting a check, follow ALL 7 steps from the release plan:

### Step 1: Setup & Research

1. Read `.claude/release-plan.json` to get check details:
   - Verify the check_id exists and is `not_started`
   - Get the `algorithm_hint`, `why_matters`, and `category`
   - Update status to `in_progress` and set `started_at` timestamp

2. Read existing code to understand patterns:
   - `modelChecker/modelChecker_commands.py` - study similar functions
   - `modelChecker/modelChecker_list.py` - understand registration format
   - Identify the best template function to follow

3. Display implementation plan:
```
╔══════════════════════════════════════════════════════════════════════╗
║  Starting: [Check Name]                                               ║
║  Priority: X/15 | Phase: Y | Category: Z                             ║
╚══════════════════════════════════════════════════════════════════════╝

Algorithm Hint: [from release-plan.json]
Why It Matters: [from release-plan.json]

Implementation Checklist:
[ ] Step 1: Implementation - Create check function
[ ] Step 2: Registration - Add to command list
[ ] Step 3: Testing - Create test file with 4+ cases
[ ] Step 4: Integration Testing - Verify compatibility
[ ] Step 5: Documentation - Update CHECKS.md
[ ] Step 6: UI Preview - Update and deploy
[ ] Step 7: Finalization - Commit and push
```

---

### Step 2: Implementation

Create the check function in `modelChecker/modelChecker_commands.py`:

```python
def checkName(nodes_or_unused, SLMesh_or_unused):
    """Short description of what this check does.

    Detailed explanation of the algorithm and what issues it detects.

    Algorithm:
        1. Step one
        2. Step two
        3. Step three

    Args:
        nodes: List of node UUIDs to check (or _ if unused)
        SLMesh: MSelectionList containing mesh shapes (or _ if unused)

    Returns:
        tuple: (error_type, errors_dict)
            - error_type: "nodes", "vertex", "edge", "polygon", or "uv"
            - errors_dict: For "nodes" type: list of UUIDs
                          For others: dict mapping UUID -> list of component indices

    Known Limitations:
        - Limitation 1 with workaround
        - Limitation 2 with workaround

    Academic Use:
        Explanation of why this matters for student projects.
    """
    # Implementation following existing patterns
    errors = defaultdict(list)  # or [] for "nodes" type

    # ... check logic ...

    return ("error_type", errors)
```

**Requirements:**
- Follow existing code patterns EXACTLY
- Use `defaultdict(list)` for component errors, `[]` for node errors
- Handle empty input gracefully (return empty results, don't crash)
- Use Maya API (OpenMaya) for performance where possible

---

### Step 3: Registration

Add to `modelChecker/modelChecker_list.py`:

```python
"functionName": {
    'label': 'Human Readable Label',
    'category': 'category_name',  # naming, general, topology, UVs, materials, scene
},
```

**For new categories (materials, scene):**
The UI dynamically creates category sections, so new categories work automatically.

---

### Step 4: Testing

Create `tests/test_<check_id>.py` with this structure:

```python
"""
Tests for <checkName> check.

================================================================================
OVERVIEW
================================================================================
[Description of what this check does]

================================================================================
ALGORITHM
================================================================================
[How the check works]

================================================================================
KNOWN LIMITATIONS
================================================================================
[List limitations and why they exist]

================================================================================
TEST CASES
================================================================================
1. test_pass_case - Clean geometry should pass
2. test_fail_case - Problematic geometry should fail
3. test_edge_case - Edge cases handled gracefully
4. test_empty_selection - Empty input should not crash
5. test_limitation - Document known limitation behavior
"""

MAYA_TEST_SCRIPT = '''
# ... Maya test code ...
'''
```

**Minimum 4 test cases required:**
1. Pass case (clean geometry)
2. Fail case (problematic geometry)
3. Edge case handling
4. Limitation documentation

---

### Step 5: Integration Testing

Run these verification checks:

```bash
# 1. Python syntax check
python3 -m py_compile modelChecker/modelChecker_commands.py
python3 -m py_compile modelChecker/modelChecker_list.py

# 2. Verify function exists
grep -n "def functionName" modelChecker/modelChecker_commands.py

# 3. Verify registration
grep -n "functionName" modelChecker/modelChecker_list.py

# 4. Cross-reference check (use AST parsing)
```

**Verify:**
- [ ] Function signature matches: `(nodes, SLMesh)` or `(_, SLMesh)` or `(nodes, _)`
- [ ] Return format matches: `("type", errors)`
- [ ] Function name matches registration key EXACTLY (case-sensitive)
- [ ] Category is valid: naming, general, topology, UVs, materials, scene

---

### Step 6: Documentation

Update `CHECKS.md` with a new section:

```markdown
### Check Name

**Category:** category
**Function:** `functionName`
**Returns:** type (nodes/vertex/edge/polygon/uv)

#### Description
[What it detects and why it's a problem]

#### How It Works
[Algorithm explanation]

#### Known Limitations
| Limitation | Impact | Workaround |
|------------|--------|------------|
| ... | ... | ... |

#### When This Check Helps
- [Use case 1]
- [Use case 2]

#### How to Fix
[Maya instructions to fix detected issues]

#### Test Cases
| Test | Expected Result |
|------|-----------------|
| ... | ... |
```

---

### Step 7: UI Preview Update

1. Update `ui-preview/checks-overview.html`:
   - Find the check in `checksData` array
   - Change `status: 'planned'` to `status: 'implemented'`

2. Update `ui-preview/index.html`:
   - Move check from planned to implemented section (if applicable)

3. Deploy to Vercel:
```bash
cd ui-preview && vercel --yes --prod
```

4. Verify mobile responsiveness in browser

---

## Completion Notice

After ALL steps are done, display:

```
╔══════════════════════════════════════════════════════════════════════╗
║                    Implementation Complete!                           ║
╚══════════════════════════════════════════════════════════════════════╝

Check: [Check Name]
Status: Ready for /finish

Completed Steps:
✓ Step 1: Implementation - Function created
✓ Step 2: Registration - Added to command list
✓ Step 3: Testing - Test file with X test cases
✓ Step 4: Integration - All verifications passed
✓ Step 5: Documentation - CHECKS.md updated
✓ Step 6: UI Preview - Deployed to Vercel
○ Step 7: Finalization - Run /finish <check_id>

Files Modified:
- modelChecker/modelChecker_commands.py
- modelChecker/modelChecker_list.py
- CHECKS.md
- ui-preview/checks-overview.html

Files Created:
- tests/test_<check_id>.py

Next Step:
  /finish <check_id>
```

---

## Important Notes

- Use the TodoWrite tool to track progress through each step
- Complete ALL steps before running /finish
- If you encounter issues, document them and ask for clarification
- Each check should take the full workflow - no shortcuts!
