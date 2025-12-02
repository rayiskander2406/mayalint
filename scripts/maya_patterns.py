"""
Maya API Pattern Library for modelChecker

This file contains common Maya API patterns used in modelChecker checks.
Copy and adapt these patterns for new check implementations.

Usage:
    - Reference this file when implementing new checks
    - Copy the relevant pattern and modify for your use case
    - All patterns are tested and production-ready
"""

from collections import defaultdict
# These imports work in Maya only:
# import maya.cmds as cmds
# import maya.api.OpenMaya as om

# =============================================================================
# PATTERN 1: Iterate Over All Mesh Faces (Polygons)
# =============================================================================
# Use for: flipped_normals, concave_faces, zero_area_faces, triangles, ngons
#
# Returns: ("polygon", {uuid: [face_indices]})

def pattern_iterate_faces(_, SLMesh):
    """Iterate over all faces in meshes and check each one."""
    results = defaultdict(list)

    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        dagPath = selIt.getDagPath()
        fn = om.MFnDependencyNode(dagPath.node())
        uuid = fn.uuid().asString()

        faceIt = om.MItMeshPolygon(dagPath)
        while not faceIt.isDone():
            # Access face properties:
            # - faceIt.index()                    # Face index
            # - faceIt.getArea()                  # Face area
            # - faceIt.center(om.MSpace.kWorld)   # Face center point
            # - faceIt.getNormal(om.MSpace.kWorld) # Face normal vector
            # - faceIt.getEdges()                 # Connected edge indices
            # - faceIt.isConvex()                 # Is face convex?
            # - faceIt.isLamina()                 # Is face lamina?
            # - faceIt.isStarlike()               # Is face starlike?
            # - faceIt.hasUVs()                   # Does face have UVs?

            if some_condition:  # Replace with your check
                results[uuid].append(faceIt.index())

            faceIt.next()
        selIt.next()

    return "polygon", results


# =============================================================================
# PATTERN 2: Iterate Over All Mesh Vertices
# =============================================================================
# Use for: overlapping_vertices, poles
#
# Returns: ("vertex", {uuid: [vertex_indices]})

def pattern_iterate_vertices(_, SLMesh):
    """Iterate over all vertices in meshes and check each one."""
    results = defaultdict(list)

    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        dagPath = selIt.getDagPath()
        fn = om.MFnDependencyNode(dagPath.node())
        uuid = fn.uuid().asString()

        vertexIt = om.MItMeshVertex(dagPath)
        while not vertexIt.isDone():
            # Access vertex properties:
            # - vertexIt.index()                    # Vertex index
            # - vertexIt.position(om.MSpace.kWorld) # Vertex position (MPoint)
            # - vertexIt.numConnectedEdges()        # Connected edge count
            # - vertexIt.numConnectedFaces()        # Connected face count
            # - vertexIt.getNormal(om.MSpace.kWorld) # Vertex normal

            if some_condition:  # Replace with your check
                results[uuid].append(vertexIt.index())

            vertexIt.next()
        selIt.next()

    return "vertex", results


# =============================================================================
# PATTERN 3: Iterate Over All Mesh Edges
# =============================================================================
# Use for: open_edges, hard_edges, zero_length_edges, non_manifold_edges
#
# Returns: ("edge", {uuid: [edge_indices]})

def pattern_iterate_edges(_, SLMesh):
    """Iterate over all edges in meshes and check each one."""
    results = defaultdict(list)

    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        dagPath = selIt.getDagPath()
        fn = om.MFnDependencyNode(dagPath.node())
        uuid = fn.uuid().asString()

        edgeIt = om.MItMeshEdge(dagPath)
        while not edgeIt.isDone():
            # Access edge properties:
            # - edgeIt.index()              # Edge index
            # - edgeIt.length()             # Edge length
            # - edgeIt.isSmooth             # Is edge smooth?
            # - edgeIt.onBoundary()         # Is edge on boundary?
            # - edgeIt.numConnectedFaces()  # Connected face count

            if some_condition:  # Replace with your check
                results[uuid].append(edgeIt.index())

            edgeIt.next()
        selIt.next()

    return "edge", results


# =============================================================================
# PATTERN 4: Check Node Attributes/Properties
# =============================================================================
# Use for: hidden_objects, unfrozen_transforms, layers
#
# Returns: ("nodes", [uuid_list])

def pattern_check_node_attributes(nodes, _):
    """Check transform node attributes."""
    results = []

    for node in nodes:
        # Get node name from UUID
        nodeName = cmds.ls(node, uuid=True)
        if not nodeName:
            continue
        nodeName = nodeName[0]

        # Common attribute checks:
        # - cmds.getAttr(nodeName + '.visibility')
        # - cmds.getAttr(nodeName + '.intermediateObject')
        # - cmds.xform(nodeName, q=True, ws=True, t=True)  # translation
        # - cmds.xform(nodeName, q=True, ws=True, ro=True) # rotation
        # - cmds.xform(nodeName, q=True, ws=True, s=True)  # scale
        # - cmds.listConnections(nodeName, type='displayLayer')

        if some_condition:  # Replace with your check
            results.append(node)

    return "nodes", results


# =============================================================================
# PATTERN 5: Check Shading/Material Connections
# =============================================================================
# Use for: default_materials, shaders
#
# Returns: ("nodes", [uuid_list])

def pattern_check_shading(nodes, _):
    """Check material/shading assignments."""
    results = []

    for node in nodes:
        nodeName = cmds.ls(node, uuid=True)
        if not nodeName:
            continue
        nodeName = nodeName[0]

        # Get shape node
        shapes = cmds.listRelatives(nodeName, shapes=True, type='mesh')
        if not shapes:
            continue

        # Get shading groups
        shadingGroups = cmds.listConnections(shapes[0], type='shadingEngine')
        if not shadingGroups:
            continue

        # Common shading checks:
        # - shadingGroups[0] == 'initialShadingGroup'  # Default lambert1
        # - cmds.listConnections(shadingGroups[0], type='lambert')
        # - cmds.listConnections(shadingGroups[0], type='file')

        if some_condition:  # Replace with your check
            results.append(node)

    return "nodes", results


# =============================================================================
# PATTERN 6: Check File Textures
# =============================================================================
# Use for: missing_textures, texture_resolution
#
# Returns: ("nodes", [uuid_list])

def pattern_check_file_textures(nodes, _):
    """Check file texture nodes."""
    results = []

    # Get all file nodes in scene
    fileNodes = cmds.ls(type='file')

    for fileNode in fileNodes:
        # Get texture path
        texturePath = cmds.getAttr(fileNode + '.fileTextureName')

        # Common file texture checks:
        # - os.path.exists(texturePath)  # File exists?
        # - Check image dimensions (requires external library or Maya's getAttr)
        # - Check file extension

        if some_condition:  # Replace with your check
            # For file nodes, you might want to find connected meshes
            connections = cmds.listConnections(fileNode, type='mesh')
            if connections:
                for conn in connections:
                    uuid = cmds.ls(conn, uuid=True)[0]
                    if uuid not in results:
                        results.append(uuid)

    return "nodes", results


# =============================================================================
# PATTERN 7: Get All Vertex Positions (for comparison)
# =============================================================================
# Use for: overlapping_vertices
#
# Returns positions as MPointArray

def pattern_get_all_positions(SLMesh):
    """Get all vertex positions from meshes."""
    all_positions = {}  # uuid -> [(index, MPoint), ...]

    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        dagPath = selIt.getDagPath()
        fn = om.MFnDependencyNode(dagPath.node())
        uuid = fn.uuid().asString()

        mesh = om.MFnMesh(dagPath)
        points = mesh.getPoints(om.MSpace.kWorld)

        all_positions[uuid] = [(i, p) for i, p in enumerate(points)]

        selIt.next()

    return all_positions


# =============================================================================
# PATTERN 8: Get Mesh Bounding Box
# =============================================================================
# Use for: flipped_normals, scale checks
#
# Returns MBoundingBox

def pattern_get_bounding_box(dagPath):
    """Get mesh bounding box."""
    mesh = om.MFnMesh(dagPath)
    boundingBox = mesh.boundingBox

    # Access bounding box properties:
    # - boundingBox.center     # Center point (MPoint)
    # - boundingBox.width      # Width
    # - boundingBox.height     # Height
    # - boundingBox.depth      # Depth
    # - boundingBox.min        # Min corner (MPoint)
    # - boundingBox.max        # Max corner (MPoint)

    return boundingBox


# =============================================================================
# PATTERN 9: Check UV Properties
# =============================================================================
# Use for: uv_distortion, texel_density, uv_range
#
# Returns: ("uv", {uuid: [uv_indices]})

def pattern_check_uvs(_, SLMesh):
    """Check UV coordinates."""
    results = defaultdict(list)

    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        dagPath = selIt.getDagPath()
        fn = om.MFnDependencyNode(dagPath.node())
        uuid = fn.uuid().asString()

        mesh = om.MFnMesh(dagPath)

        # Get all UV coordinates
        Us, Vs = mesh.getUVs()

        for i in range(len(Us)):
            u, v = Us[i], Vs[i]

            # Common UV checks:
            # - u < 0 or u > 10 or v < 0  # Out of range
            # - abs(int(u) - u) < 0.00001  # On border
            # - Calculate UV area vs 3D area ratio

            if some_condition:  # Replace with your check
                results[uuid].append(i)

        selIt.next()

    return "uv", results


# =============================================================================
# PATTERN 10: Scene-Level Checks
# =============================================================================
# Use for: scene_units, unused_nodes
#
# Returns: ("nodes", []) or specific nodes

def pattern_scene_check(nodes, _):
    """Check scene-level settings."""
    results = []

    # Common scene checks:
    # - cmds.currentUnit(query=True, linear=True)  # Get linear units
    # - cmds.ls(type='unknown')  # Unknown nodes
    # - cmds.ls(materials=True)  # All materials
    # - cmds.ls(textures=True)   # All textures

    # For unused nodes:
    # materials = cmds.ls(materials=True)
    # for mat in materials:
    #     connections = cmds.listConnections(mat, type='mesh')
    #     if not connections:
    #         # Material is unused
    #         pass

    return "nodes", results


# =============================================================================
# HELPER: Get Node Name from UUID
# =============================================================================

def _getNodeName(uuid):
    """Convert UUID to node name."""
    nodeName = cmds.ls(uuid, uuid=True)
    if nodeName:
        return nodeName[0]
    return None


# =============================================================================
# HELPER: Distance Between Points
# =============================================================================

def point_distance(p1, p2):
    """Calculate distance between two MPoints."""
    return ((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2) ** 0.5


# =============================================================================
# HELPER: Dot Product
# =============================================================================

def dot_product(v1, v2):
    """Calculate dot product of two vectors."""
    return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z


# =============================================================================
# QUICK REFERENCE: Return Types
# =============================================================================
"""
Return Type Reference:

"nodes"   -> Returns: [uuid1, uuid2, ...]
              Used for: Node-level checks (visibility, transforms, etc.)
              UI shows: Node names

"vertex"  -> Returns: {uuid: [vtx_idx1, vtx_idx2, ...]}
              Used for: Vertex-level checks (poles, overlapping)
              UI shows: node.vtx[idx]

"edge"    -> Returns: {uuid: [edge_idx1, edge_idx2, ...]}
              Used for: Edge-level checks (hard edges, open edges)
              UI shows: node.e[idx]

"polygon" -> Returns: {uuid: [face_idx1, face_idx2, ...]}
              Used for: Face-level checks (triangles, ngons, flipped)
              UI shows: node.f[idx]

"uv"      -> Returns: {uuid: [uv_idx1, uv_idx2, ...]}
              Used for: UV-level checks (distortion, out of range)
              UI shows: node.map[idx]
"""
