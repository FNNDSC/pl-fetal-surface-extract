import os
from tempfile import NamedTemporaryFile

import numpy as np
import subprocess as sp
import numpy.typing as npt
from bicpl import PolygonObj
from bicpl.math import difference_average


def smtherr(surface: os.PathLike) -> npt.NDArray[np.float32]:
    """
    Calculate the average change in mean curvature for every vertex and its neighbors.
    """
    data = depth_potential(surface, '-mean_curvature')
    obj = PolygonObj.from_file(surface)
    return np.fromiter(difference_average(obj.neighbor_graph(), data), dtype=np.float32)


def depth_potential(filename: str | os.PathLike, arg: str, command: str = 'depth_potential'):
    if not arg.startswith('-'):
        arg = '-' + arg
    with NamedTemporaryFile() as tmp:
        cmd = (command, arg, filename, tmp.name)
        sp.run(cmd, check=True)
        data = np.loadtxt(tmp.name, dtype=np.float32)
    return data
