from .ngon_check import NgonCheck
from .triangle_check import TriangleCheck
from .trailing_number_check import TrailingNumberCheck
from .uv_range_check import UVRangeCheck
from .poles_check import PolesCheck
from .self_penetrating_uvs import SelfPenetratingUVsCheck
from .default_shader_check import DefaultShaderCheck
from .uncentered_pivots import UncenteredPivots
from .duplicated_name_check import DuplicatedNamesCheck

all_checks = [
    NgonCheck,
    TrailingNumberCheck,
    TriangleCheck,
    UVRangeCheck,
    PolesCheck,
    SelfPenetratingUVsCheck,
    DefaultShaderCheck,
    UncenteredPivots,
    DuplicatedNamesCheck
]