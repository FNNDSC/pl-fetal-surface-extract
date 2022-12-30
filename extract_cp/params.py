from dataclasses import dataclass
from typing import Literal

SIDE_OPTIONS = ('left', 'right', 'auto', 'none')
SideStr = Literal['left', 'right', 'auto', 'none']


@dataclass(frozen=True)
class Parameters:
    """
    Magic constants which set how many iterations should be performed by
    internal subroutines. These values are primarily dependent on brain size.
    """
    side: SideStr
    mincmorph_iterations: int
    adapt_object_mesh: tuple[int, int, int, int]
    inflate_to_sphere_implicit: tuple[int, int]
    keep_mask: bool
    subsample: bool

    def __post_init__(self):
        if not len(self.adapt_object_mesh) == 4:
            raise ValueError('adapt_object_mesh takes 4 parameters')
        if not len(self.inflate_to_sphere_implicit) == 2:
            raise ValueError('inflate_to_sphere_implicit takes 2 parameters')

    @classmethod
    def new(
            cls,
            side: SideStr,
            mincmorph_iterations: int,
            adapt_object_mesh: str,
            inflate_to_sphere_implicit: str,
            keep_mask: bool,
            subsample: bool
    ) -> 'Parameters':
        return cls(
            side=side,
            mincmorph_iterations=mincmorph_iterations,
            adapt_object_mesh=_str2ints(adapt_object_mesh),
            inflate_to_sphere_implicit=_str2ints(inflate_to_sphere_implicit),
            keep_mask=keep_mask,
            subsample=subsample
        )

    @classmethod
    def from_obj(cls, options) -> 'Parameters':
        return cls.new(
            side=options.side,
            mincmorph_iterations=options.mincmorph_iterations,
            adapt_object_mesh=options.adapt_object_mesh,
            inflate_to_sphere_implicit=options.inflate_to_sphere_implicit,
            keep_mask=options.keep_mask,
            subsample=options.subsample
        )


def _str2ints(x: str) -> tuple:
    return tuple(map(int, x.split(',')))
