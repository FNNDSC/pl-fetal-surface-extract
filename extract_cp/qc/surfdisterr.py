from pathlib import Path
import subprocess as sp
from tempfile import NamedTemporaryFile


def surfdisterr(surface: Path, mask: Path, output: Path):
    """
    Compute the distance from each vertex of the surface to the mask boundary,
    and write the output to a text file.
    """
    with NamedTemporaryFile() as temp:
        chamfer = temp.name
        create_chamfer(mask, chamfer)
        volume_object_evaluate(chamfer, surface, output)


def create_chamfer(mask, chamfer):
    cmd = ['chamfer.sh', '-c', '0.0', mask, chamfer]
    sp.run(cmd, check=True)


def volume_object_evaluate(chamfer, surface, result):
    cmd = ['volume_object_evaluate', '-linear', chamfer, surface, result]
    sp.run(cmd, check=True)
