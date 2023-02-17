import dataclasses
import json
import os
import shlex
import shutil
from pathlib import Path
from typing import Optional, Sequence, BinaryIO, TypedDict
from civet.extraction.hemisphere import Side, HemisphereMask
import subprocess as sp
from loguru import logger

import numpy as np
import numpy.typing as npt

from extract_cp.params import SideStr, SIDE_OPTIONS, Parameters
from extract_cp.qc import surfdisterr, smtherr

_LOG_PREFIX = b'[' + os.path.basename(__file__).encode(encoding='utf-8') + b']'


def extract_surface(mask: Path, surface: Path, params: Parameters):
    log_path = surface.with_suffix('.extraction.log')
    chosen_side = __pick_side(mask, params.side)
    try:
        logger.info('Surface extraction {} to {} ({}), log: {}', mask, surface, chosen_side, log_path)
        with log_path.open('wb') as log:
            _ExtractSurface(
                mask=mask,
                surface=surface,
                side=chosen_side,
                params=params,
                output_sink=log
            ).run()
        if params.keep_mask:
            shutil.copy(mask, surface.with_name(mask.name))
        logger.info('Completed {}', surface)
    except Exception as e:
        logger.exception('Failed to process {}', mask)
        raise e


class StepOutcome(TypedDict):
    name: str
    disterr_abs_max: float
    smtherr_mean: float


@dataclasses.dataclass(frozen=True)
class _ExtractSurface:
    mask: Path
    surface: Path
    side: Side
    params: Parameters
    output_sink: BinaryIO
    outcomes: list[StepOutcome] = dataclasses.field(default_factory=list)

    def run(self):
        self._marching_cubes_until_disterr_ok()
        self.conclude()

    def conclude(self):
        """
        Finishing touches
        """
        self.output_sink.flush()
        self._write_steps()

    def _marching_cubes_until_disterr_ok(self):
        """
        Runs marching-cubes (``sphere_mesh``), saving the surface.
        The created surface has an inconsistent number of triangles.
        If maximum absolute distance error exceeds threshold, then
        retry marching-cubes with subsampling.
        """
        self._message('marching-cubes first attempt')
        self._marching_cubes(subsample=False)
        first_outcome = self._evaluate('marching-cubes (sphere_mesh)')
        disterr = first_outcome['disterr_abs_max']
        if disterr <= self.params.distance_threshold:
            self._message(f'max(surfdisterr)={disterr:.3f} is ok')
            return

        self._message(f'max(surfdisterr)={disterr:.3f} is bad')
        self._message('marching-cubes second attempt **with subsampling**')
        self._marching_cubes(subsample=True)

        second_outcome = self._evaluate('marching-cubes (sphere_mesh) WITH SUBSAMPLING')
        second_disterr = second_outcome['disterr_abs_max']
        percent_change = (second_disterr - disterr) / disterr * 100
        self._message('marching-cubes with subsampling improvement: '
                      f'max(surfdisterr) {disterr:.3f} -> {second_disterr:.3f} '
                      f'({percent_change:.1g}% change)')

        if second_disterr > disterr:
            self._message('!!!WARNING!!! marching-cubes with subsampling produced a surface '
                          'with greater distance error, this is unexpected.')

        smth_first = first_outcome['smtherr_mean']
        smth_second = second_outcome['smtherr_mean']
        smth_percent_change = (smth_second - smth_first) / smth_first * 100
        self._message(f'affected mean(smtherr): {smth_first:.3f} -> {smth_second:.3f} '
                      f'({smth_percent_change:.1g}% change)')

    def _marching_cubes(self, subsample: bool):
        HemisphereMask(self.mask)\
            .just_sphere_mesh(self.side, subsample=subsample)\
            .save(self.surface, shell=self._logged_runner)

    def _evaluate(self, name: str) -> StepOutcome:
        """
        (Re)-calculate smtherr and disterr, writing both data to files and append
        a summary to ``self.outcomes``. This summary is also returned.
        """
        outcome = StepOutcome(
            name=name,
            smtherr_mean=self._smtherr_mean(),
            disterr_abs_max=self._disterr_abs_max()
        )
        self.outcomes.append(outcome)
        return outcome

    def _write_surfdisterr(self):
        surfdisterr(self.surface, self.mask, self._disterr_file)

    def _load_smtherr(self) -> npt.NDArray[np.float32]:
        data = smtherr(self.surface)
        np.savetxt(self._smtherr_file, data)
        return data

    def _load_surfdisterr(self) -> npt.NDArray[np.float32]:
        self._write_surfdisterr()
        return np.loadtxt(self._disterr_file, dtype=np.float32)

    def _disterr_abs_max(self) -> float:
        data = self._load_surfdisterr()
        return float(np.abs(data).max())

    def _smtherr_mean(self) -> float:
        data = self._load_smtherr()
        return float(data.mean())

    def _write_steps(self):
        with self._outcomes_file.open('w') as f:
            json.dump(self.outcomes, f, indent=2)

    @property
    def _disterr_file(self) -> Path:
        return self.surface.with_suffix('.disterr.txt')

    @property
    def _smtherr_file(self) -> Path:
        return self.surface.with_suffix('.smtherr.txt')

    @property
    def _outcomes_file(self) -> Path:
        return self.surface.with_suffix('.extraction.steps.json')

    @property
    def _logged_runner(self):
        def run_with_log(cmd: Sequence[str | os.PathLike]) -> None:
            self.output_sink.write(_LOG_PREFIX)
            self.output_sink.write(b' COMMAND $>')
            cmdstr = shlex.join(map(str, cmd))
            self.output_sink.write(cmdstr.encode('utf-8'))
            self.output_sink.write(b'\n')
            self.output_sink.flush()
            sp.run(cmd, stderr=self.output_sink, stdout=self.output_sink, check=True)

        return run_with_log

    def _message(self, *args):
        self.output_sink.write(_LOG_PREFIX)
        self.output_sink.write(b' MESSAGE  >>>  ')
        for msg in map(str, args):
            self.output_sink.write(msg.encode('utf-8'))
        self.output_sink.write(b'  <<<\n')


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
