# Finish Check Implementation Command

You are completing and finalizing a check implementation for the modelChecker Academic Extension.

## Arguments
The user should provide: `/finish <check_id>`

---

## Pre-Flight Verification

Before finalizing, verify ALL 7 steps from `/start` were completed.

### Step 1: Validate State

Read `.claude/release-plan.json` and verify:
- Check exists and status is `in_progress`
- `started_at` timestamp is set
- If status is `not_started`, inform user to run `/start <check_id>` first
- If status is `completed`, inform user this check is already done

---

## Complete Quality Checklist

### Code Quality Review

```
╔══════════════════════════════════════════════════════════════════════╗
║  Code Quality Checklist: [Check Name]                                 ║
╚══════════════════════════════════════════════════════════════════════╝
```

**Verify in modelChecker_commands.py:**
- [ ] Function exists with correct name
- [ ] Function signature is `(nodes, SLMesh)` or variant with `_`
- [ ] Comprehensive docstring with:
  - [ ] Description
  - [ ] Algorithm section
  - [ ] Args section
  - [ ] Returns section
  - [ ] Known Limitations section
  - [ ] Academic Use section
- [ ] Returns correct format: `("type", errors)`
- [ ] Uses `defaultdict(list)` or `[]` appropriately
- [ ] Handles empty input without crashing
- [ ] No syntax errors

**Verify in modelChecker_list.py:**
- [ ] Registration entry exists
- [ ] Key matches function name EXACTLY
- [ ] Label is descriptive
- [ ] Category is valid

---

### Testing Review

```
╔══════════════════════════════════════════════════════════════════════╗
║  Testing Checklist                                                    ║
╚══════════════════════════════════════════════════════════════════════╝
```

**Verify tests/test_<check_id>.py:**
- [ ] File exists
- [ ] Header documentation present
- [ ] Minimum 4 test cases:
  - [ ] Pass case (clean geometry passes)
  - [ ] Fail case (problematic geometry detected)
  - [ ] Edge case (unusual input handled)
  - [ ] Limitation test (documents known behavior)
- [ ] MAYA_TEST_SCRIPT included for manual testing
- [ ] Instructions for running tests

---

### Integration Verification

Run these commands and verify output:

```bash
# 1. Syntax check
python3 -m py_compile modelChecker/modelChecker_commands.py
python3 -m py_compile modelChecker/modelChecker_list.py

# 2. Function exists
grep -n "def <functionName>" modelChecker/modelChecker_commands.py

# 3. Registration exists
grep -n "<functionName>" modelChecker/modelChecker_list.py

# 4. All checks have functions (cross-reference)
```

**Display results:**
```
Integration Verification:
✓ Syntax check passed
✓ Function found at line XXX
✓ Registration found at line XXX
✓ Cross-reference: XX/XX commands have functions
```

---

### Documentation Review

**Verify CHECKS.md:**
- [ ] New section added for this check
- [ ] Description explains what it detects
- [ ] "How It Works" explains algorithm
- [ ] "Known Limitations" table present
- [ ] "When This Check Helps" section
- [ ] "How to Fix" Maya instructions
- [ ] Test cases table

---

### UI Preview Review

**Verify ui-preview/checks-overview.html:**
- [ ] Check status changed from 'planned' to 'implemented'

**Verify ui-preview/index.html:**
- [ ] Check appears as implemented (if applicable)

**Verify deployment:**
- [ ] Latest version deployed to Vercel
- [ ] Mobile responsive (check on phone or dev tools)

---

## Final Review Summary

Display comprehensive review:

```
╔══════════════════════════════════════════════════════════════════════╗
║                    Final Review: [Check Name]                         ║
╚══════════════════════════════════════════════════════════════════════╝

Code Quality:
  ✓ Function implemented correctly
  ✓ Docstring complete with all sections
  ✓ Error handling present
  ✓ Syntax valid

Testing:
  ✓ Test file created
  ✓ 5 test cases present
  ✓ Maya test script included

Integration:
  ✓ Function registered
  ✓ Names match exactly
  ✓ Return format correct

Documentation:
  ✓ CHECKS.md updated
  ✓ Limitations documented
  ✓ Fix instructions provided

UI Preview:
  ✓ Status updated to implemented
  ✓ Deployed to Vercel
  ✓ Mobile responsive

Overall: READY TO COMMIT
```

---

## If Issues Found

If ANY check fails, display:

```
╔══════════════════════════════════════════════════════════════════════╗
║                    Issues Found - Cannot Finalize                     ║
╚══════════════════════════════════════════════════════════════════════╝

The following issues must be fixed before committing:

1. [Issue description]
   Fix: [How to fix it]

2. [Issue description]
   Fix: [How to fix it]

Run /finish <check_id> again after fixing these issues.
```

**DO NOT proceed with git operations if any issues are found.**

---

## Git Operations (Only if all checks pass)

### 1. Stage Files

```bash
git add modelChecker/modelChecker_commands.py
git add modelChecker/modelChecker_list.py
git add tests/test_<check_id>.py
git add CHECKS.md
git add .claude/release-plan.json
```

### 2. Create Commit

```bash
git commit -m "$(cat <<'EOF'
feat(checks): add <check_name> check (#X/15)

Implement <functionName>() to detect <what it detects>.

Changes:
- Add check function in modelChecker_commands.py
- Register check in modelChecker_list.py under '<category>'
- Add tests in tests/test_<check_id>.py (X test cases)
- Update CHECKS.md with full documentation
- Update UI preview (deployed to Vercel)

Part of Academic Extension - Phase Y, Priority X/15

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 3. Push to Remote

```bash
git push origin main
```

---

## Update Release Plan

After successful commit:

1. Update `.claude/release-plan.json`:
   - Set check status to `completed`
   - Set `completed_at` to current ISO timestamp
   - Add `files_modified` and `files_created` arrays
   - Update `statistics.completed` (increment)
   - Update `statistics.not_started` (decrement)

2. Save the updated JSON

---

## Completion Summary

```
╔══════════════════════════════════════════════════════════════════════╗
║                    Check Completed Successfully!                      ║
╚══════════════════════════════════════════════════════════════════════╝

[Check Name] has been:
  ✓ Code reviewed and verified
  ✓ Tests verified (X test cases)
  ✓ Integration confirmed
  ✓ Documentation complete
  ✓ UI preview updated
  ✓ Committed to git
  ✓ Pushed to remote
  ✓ Release plan updated

═══════════════════════════════════════════════════════════════════════

Progress Update:
  Phase Y: X/Z checks complete
  Overall: X/15 checks complete (XX%)

═══════════════════════════════════════════════════════════════════════

Next Recommended Check:
  /start <next_check_id>
  [Next Check Name] - [Brief description]

Other Commands:
  /dashboard    - View progress visualization
  /plan-release - View full release plan
```

---

## Important Notes

- NEVER commit if any verification fails
- NEVER skip any checklist item
- ALWAYS update the release plan after commit
- If git push fails, investigate and resolve before marking complete
- The commit message should accurately reflect all changes
