# General 
from .default_shader_check import DefaultShaderCheck
from .empty_groups_check import EmptyGroupsCheck
from .history_check import HistoryCheck
from .layers_check import LayersCheck
from .on_grid_check import OnGridCheck
from .parent_geometry_check import ParentGeometryCheck
from .uncentered_pivots import UncenteredPivots

# Naming
from .duplicated_name_check import DuplicatedNamesCheck
from .namespaces_check import NamespacesCheck
from .shape_names_check import ShapeNamesCheck
from .trailing_number_check import TrailingNumberCheck

# Topology
from .hard_edges_check import HardEdgesCheck
from .lamina_check import LaminaCheck
from .ngon_check import NgonCheck
from .none_manifold_eges_check import NoneManifoldEdgesCheck
from .open_edges_check import OpenEdgesCheck
from .poles_check import PolesCheck
from .triangle_check import TriangleCheck
from .zero_area_faces_check import ZeroAreaFacesCheck
from .zero_length_edges_check import ZeroLengthEdgesCheck

# UVs
from .cross_border_check import CrossBorderCheck
from .self_penetrating_uvs import SelfPenetratingUVsCheck
from .uv_range_check import UVRangeCheck

all_checks = [
    # General
    DefaultShaderCheck,
    EmptyGroupsCheck,
    HistoryCheck,
    LayersCheck,
    OnGridCheck,
    ParentGeometryCheck,
    UncenteredPivots,

    # Naming
    DuplicatedNamesCheck,
    NamespacesCheck,
    ShapeNamesCheck,
    TrailingNumberCheck,

    # Topology
    HardEdgesCheck,
    LaminaCheck,
    NgonCheck,
    NoneManifoldEdgesCheck,
    OpenEdgesCheck,
    PolesCheck,
    TriangleCheck,
    ZeroAreaFacesCheck,
    ZeroLengthEdgesCheck,

    # UVs
    CrossBorderCheck,
    SelfPenetratingUVsCheck,
    UVRangeCheck
]
