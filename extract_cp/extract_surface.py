import os
from pathlib import Path
from typing import Optional, Literal, Sequence, BinaryIO
from civet.extraction.hemisphere import Side, HemisphereMask
import subprocess as sp
from loguru import logger

SIDE_OPTIONS = ('left', 'right', 'auto', 'none')
SideStr = Literal['left', 'right', 'auto', 'none']

__log_prefix = b'[' + os.path.basename(__file__).encode(encoding='utf-8') + b']$> '


def extract_surface(mask: Path, surface: Path, side: SideStr):
    log_path = surface.with_suffix('.extraction.log')
    try:
        chosen_side = __pick_side(mask, side)
        logger.info('Processing {} to {}, log: {}', mask, surface, log_path)
        with log_path.open('wb') as log:
            HemisphereMask(mask)\
                .smoothen_using_mincmorph()\
                .just_sphere_mesh(chosen_side, subsample=True)\
                .interpolate_with_sphere(chosen_side)\
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
