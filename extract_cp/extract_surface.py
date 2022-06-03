import os
from pathlib import Path
from typing import Optional, Sequence, BinaryIO
from civet.extraction.hemisphere import Side, HemisphereMask
import subprocess as sp
from loguru import logger

from extract_cp.params import SideStr, SIDE_OPTIONS, Parameters

__log_prefix = b'[' + os.path.basename(__file__).encode(encoding='utf-8') + b']$> '


def extract_surface(mask: Path, surface: Path, params: Parameters):
    log_path = surface.with_suffix('.extraction.log')
    try:
        chosen_side = __pick_side(mask, params.side)
        logger.info('Processing {} to {}, log: {}', mask, surface, log_path)
        with log_path.open('wb') as log:
            HemisphereMask(mask)\
                .smoothen_using_mincmorph(iterations=params.mincmorph_iterations)\
                .just_sphere_mesh(chosen_side, subsample=True)\
                .adapt_object_mesh(*params.adapt_object_mesh)\
                .interpolate_with_sphere(chosen_side, *params.inflate_to_sphere_implicit)\
                .save(surface, shell=__curry_log(log))
        logger.info('Completed {}', surface)
    except Exception as e:
        logger.exception('Failed to process {}', mask)
        raise e


def __pick_side(mask: Path, side: SideStr) -> Optional[Side]:
    if side == 'left':
        return Side.LEFT
    if side == 'right':
        return Side.RIGHT
    if side == 'auto':
        path = str(mask).lower()
        if 'left' in path:
            return Side.LEFT
        if 'right' in path:
            return Side.RIGHT
        raise ValueError(f'Substring "left" nor "right" found in: {path}')
    if side == 'none':
        return None
    raise ValueError(f'side must be one of: {SIDE_OPTIONS}')


def __curry_log(log: BinaryIO):
    def run_with_log(cmd: Sequence[str | os.PathLike]) -> None:
        log.write(__log_prefix)
        log.write(str(cmd).encode('utf-8'))
        log.write(b'\n')
        log.flush()
        sp.run(cmd, stderr=log, stdout=log, check=True)
    return run_with_log
