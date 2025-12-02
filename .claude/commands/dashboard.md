# Dashboard Command

You are displaying a visual dashboard for the modelChecker academic extension project.

## Your Task

Read `.claude/release-plan.json` and create a visually appealing ASCII dashboard showing:

### 1. Header
```
╔══════════════════════════════════════════════════════════════╗
║          modelChecker Academic Extension - Dashboard          ║
║                        Version X.X.X                          ║
╚══════════════════════════════════════════════════════════════╝
```

### 2. Overall Progress Bar
```
Overall Progress: [████████░░░░░░░░░░░░] 40% (6/15 checks)
```

### 3. Phase Progress (horizontal bars for each phase)
```
Phase 1 - High Impact:        [██████████] 100% (6/6)
Phase 2 - Professional:       [████░░░░░░]  40% (2/5)
Phase 3 - Polish:             [░░░░░░░░░░]   0% (0/4)
```

### 4. Status Summary Box
```
┌─────────────────────────────────┐
│  Completed:     6  ████████    │
│  In Progress:   1  █           │
│  Not Started:   8  ████████    │
└─────────────────────────────────┘
```

### 5. Current Focus
Show which check(s) are currently `in_progress` with details:
- Check name
- Phase
- Priority
- Description

### 6. Next Up
Show the next 2-3 `not_started` checks in priority order

### 7. Category Coverage
```
Categories:
  naming    [███░░] 2 existing + 1 new
  general   [████░] 3 existing + 3 new
  topology  [█████] 5 existing + 3 new
  UVs       [███░░] 3 existing + 2 new
  materials [░░░░░] 0 existing + 3 new (NEW!)
  scene     [░░░░░] 0 existing + 2 new (NEW!)
```

### 8. Quick Commands
```
Quick Commands:
  /start <id>     - Begin a check
  /finish <id>    - Complete a check
  /plan-release   - View full plan
```

## Guidelines
- Use ASCII box-drawing characters for visual appeal
- Calculate all percentages dynamically from the JSON
- Make it scannable at a glance
- Use consistent spacing and alignment
