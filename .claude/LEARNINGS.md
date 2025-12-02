# Critical Learnings & Accelerators

## Key Insight: 80% of Each Check is Boilerplate

After implementing the first check, we discovered that ~80% of the work is repetitive:
- Same docstring structure
- Same test file structure
- Same CHECKS.md format
- Same UI preview updates
- Same git workflow

**Solution: Automate the boilerplate, focus human effort on the 20% (algorithm logic)**

---

## Accelerator #1: Template Generator Script

### Problem
Manually creating test files, docstrings, and documentation entries is slow and error-prone.

### Solution
Create a Python script that generates scaffolds from release-plan.json:

```python
# scripts/generate_check_scaffold.py
# Input: check_id
# Output:
#   - Test file template with all sections
#   - Docstring template to paste into function
#   - CHECKS.md entry template
#   - UI preview data entry
```

**Impact: Save 30-40 minutes per check**

---

## Accelerator #2: Batch Similar Checks

### Problem
Implementing checks one-by-one ignores natural groupings.

### Solution
Group checks by Maya API pattern:

| Pattern | Checks | Shared Code |
|---------|--------|-------------|
| **MItMeshPolygon** | flipped_normals, concave_faces | Face iteration |
| **MItMeshVertex** | overlapping_vertices | Vertex iteration |
| **Node attributes** | hidden_objects, intermediate_objects | Attribute queries |
| **File nodes** | missing_textures, texture_resolution | File texture scanning |
| **Shading** | default_materials, unused_nodes | Shading network traversal |

**Implementation Strategy:**
```
Instead of: Check 1 → Check 2 → Check 3 → ...
Do:         [Topology batch] → [Materials batch] → [Scene batch]
```

**Impact: 40% faster through code reuse within batches**

---

## Accelerator #3: Automated Integration Verification

### Problem
Manual verification steps in /finish are tedious and can be forgotten.

### Solution
Create a verification script:

```python
# scripts/verify_check.py <check_id>
# Automatically:
#   1. Syntax check all Python files
#   2. Verify function exists with correct signature
#   3. Verify registration exists
#   4. Cross-reference all commands have functions
#   5. Check test file exists with minimum test cases
#   6. Verify CHECKS.md entry exists
#   7. Output pass/fail report
```

**Impact: Verification drops from 5 minutes to 10 seconds**

---

## Accelerator #4: UI Preview Auto-Sync

### Problem
Manually updating HTML files after each check is tedious and error-prone.

### Solution
Generate UI data from release-plan.json:

```javascript
// ui-preview/data.js - Auto-generated from release-plan.json
export const checksData = [/* generated */];
export const statistics = {/* generated */};
```

```bash
# scripts/sync_preview.py
# Reads release-plan.json
# Updates checksData in HTML files
# Deploys to Vercel
```

**Impact: UI updates become one command instead of manual editing**

---

## Accelerator #5: Maya API Pattern Library

### Problem
Each check requires figuring out the Maya API approach from scratch.

### Solution
Create a reference library of common patterns:

```python
# Reference: Common Maya API Patterns

# Pattern: Iterate all faces
selIt = om.MItSelectionList(SLMesh)
while not selIt.isDone():
    faceIt = om.MItMeshPolygon(selIt.getDagPath())
    while not faceIt.isDone():
        # ... process face ...
        faceIt.next()
    selIt.next()

# Pattern: Get all vertices
mesh = om.MFnMesh(dagPath)
points = mesh.getPoints(om.MSpace.kWorld)

# Pattern: Check shading connections
shadingEngines = cmds.listConnections(shape, type='shadingEngine')

# Pattern: Query file textures
fileNodes = cmds.ls(type='file')
for node in fileNodes:
    path = cmds.getAttr(node + '.fileTextureName')
```

**Impact: Algorithm implementation drops from 30 minutes to 10 minutes**

---

## Accelerator #6: Parallel Check Implementation

### Problem
Sequential implementation doesn't utilize available bandwidth.

### Solution
For independent checks, implement in parallel:

```
Session 1: /start overlapping_vertices
Session 2: /start missing_textures
Session 3: /start hidden_objects

# All three use different Maya API patterns
# No conflicts, can be developed simultaneously
```

**Impact: 3x throughput for independent checks**

---

## Accelerator #7: Pre-built Test Geometries

### Problem
Each test requires creating Maya geometry from scratch.

### Solution
Create a test scene library:

```
tests/fixtures/
├── clean_cube.ma          # Normal cube (passes all checks)
├── reversed_normals.ma    # Cube with flipped normals
├── overlapping_verts.ma   # Mesh with coincident vertices
├── missing_uvs.ma         # Mesh without UVs
├── complex_scene.ma       # Full scene with multiple issues
```

**Impact: Test writing drops from 15 minutes to 5 minutes**

---

## Implementation Priority

### Quick Wins (Implement First)
1. **Template Generator** - Immediate 30min/check savings
2. **Verification Script** - Catches errors early
3. **Maya Pattern Library** - Speeds up algorithm writing

### Medium Effort, High Impact
4. **Batch Similar Checks** - 40% overall speedup
5. **UI Auto-Sync** - Eliminates manual HTML editing

### Nice to Have
6. **Parallel Implementation** - If multiple people contributing
7. **Test Fixtures** - Useful but not critical

---

## Projected Impact

| Metric | Before | After Accelerators |
|--------|--------|-------------------|
| Time per check | ~60 min | ~20 min |
| Error rate | ~15% | ~3% |
| Consistency | Variable | Uniform |
| Total project time | ~15 hours | ~5 hours |

---

## Recommended Next Steps

1. **Now:** Create the template generator script
2. **Now:** Create the Maya API pattern library
3. **Then:** Batch implement Phase 1 topology checks together
4. **Then:** Batch implement Phase 1 materials checks together
5. **Ongoing:** Use verification script before every /finish
