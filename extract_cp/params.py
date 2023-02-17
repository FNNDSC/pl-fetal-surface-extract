from dataclasses import dataclass
from typing import Literal

SIDE_OPTIONS = ('left', 'right', 'auto', 'none')
SideStr = Literal['left', 'right', 'auto', 'none']


@dataclass(frozen=True)
class Parameters:
    """
    Provides typing for the expected values of a `argparse.Namespace`.
    """
    side: SideStr
    inflate_to_sphere_implicit: tuple[int, int]
    distance_threshold: float
    target_smoothness: float
    max_smooth_iterations: int
    keep_mask: bool

    def __post_init__(self):
        if not len(self.inflate_to_sphere_implicit) == 2:
            raise ValueError('inflate_to_sphere_implicit takes 2 parameters')

    @classmethod
    def from_obj(cls, options) -> 'Parameters':
        return cls(
            side=options.side,
            inflate_to_sphere_implicit=_str2ints(options.inflate_to_sphere_implicit),
            distance_threshold=options.distance_threshold,
            target_smoothness=options.target_smoothness,
            max_smooth_iterations=options.max_smooth_iterations,
            keep_mask=options.keep_mask,
        )


def _str2ints(x: str) -> tuple:
    return tuple(map(int, x.split(',')))
