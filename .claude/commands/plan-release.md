# Release Plan Command

Display the comprehensive release plan for the modelChecker Academic Extension.

## Usage
`/plan-release` - View full release plan
`/plan-release --phase 1|2|3` - View specific phase
`/plan-release --status completed|in_progress|not_started` - Filter by status

---

## Your Task

Read `.claude/release-plan.json` and display:

### 1. Project Overview

```
╔══════════════════════════════════════════════════════════════════════╗
║          modelChecker Academic Extension - Release Plan               ║
║                          Version 0.2.0                                ║
╚══════════════════════════════════════════════════════════════════════╝

Repository: https://github.com/rayiskander2406/modelChecker
Preview: https://modelchecker-preview-....vercel.app

Progress: X/15 checks (XX%)
├── Completed:   X
├── In Progress: X
└── Not Started: X
```

### 2. Implementation Workflow

Display the 7-step workflow from release-plan.json:

```
Standard Implementation Workflow:
┌─────────────────────────────────────────────────────────────────────┐
│ Step 1: Implementation    │ Create check function                   │
│ Step 2: Registration      │ Add to command list                     │
│ Step 3: Testing          │ Create test file (4+ cases)              │
│ Step 4: Integration      │ Verify compatibility                     │
│ Step 5: Documentation    │ Update CHECKS.md                         │
│ Step 6: UI Preview       │ Update & deploy to Vercel                │
│ Step 7: Finalization     │ Commit & push                            │
└─────────────────────────────────────────────────────────────────────┘
```

### 3. Phase Breakdown

For each phase, show:

```
═══════════════════════════════════════════════════════════════════════
PHASE 1: HIGH IMPACT (Critical Priority)
Catches most common student mistakes
═══════════════════════════════════════════════════════════════════════

Progress: X/6 checks

[✓] #1  flipped_normals      Flipped Normals           topology
        → Detect faces pointing wrong direction
        → Completed: 2025-12-02

[ ] #2  overlapping_vertices Overlapping Vertices      topology
        → Detect vertices at same position
        → Hint: Compare positions with MFnMesh.getPoints()

[ ] #3  poly_count_limit     Poly Count Limit          general
        → Verify polygon budget
        → Hint: Count faces using MFnMesh.numPolygons

...
```

Use these status icons:
- `[✓]` = completed
- `[~]` = in_progress
- `[ ]` = not_started

### 4. Quality Checklist Reference

```
Quality Checklist (for each check):
┌─────────────────────────────────────────────────────────────────────┐
│ Code        │ Patterns, docstring, edge cases, syntax              │
│ Testing     │ 4+ cases, pass/fail/edge/limitation                  │
│ Integration │ Signature, return format, registration               │
│ Docs        │ CHECKS.md, limitations, how-to-fix                   │
│ Preview     │ HTML updated, deployed, mobile-ready                 │
└─────────────────────────────────────────────────────────────────────┘
```

### 5. Future Roadmap

List items from `future_additions` array:
```
Future Additions (Post v1.0):
• Edge Loop Flow (animation)
• UV Island Padding (UVs)
• Real-World Scale (scene)
• Symmetry Validation (topology)
```

### 6. Quick Commands

```
Commands:
  /start <check_id>     Begin implementing a check
  /finish <check_id>    Complete and commit a check
  /dashboard            Visual progress view
  /update-preview       Deploy UI updates
```

---

## Filtering Options

### --phase X
Show only checks in the specified phase (1, 2, or 3)

### --status X
Show only checks with the specified status:
- `completed` - Done and committed
- `in_progress` - Currently being worked on
- `not_started` - Not yet begun

### --next
Show just the next recommended check to implement

---

## Notes

- Always read from `.claude/release-plan.json` for current state
- Calculate percentages dynamically
- Show algorithm hints for not_started checks
- Show completion dates for completed checks
