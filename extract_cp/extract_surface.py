import dataclasses
import json
import os
import shlex
import shutil
from pathlib import Path
from typing import Optional, Sequence, BinaryIO, TypedDict
from civet.extraction.hemisphere import Side, HemisphereMask, IrregularSurface
import subprocess as sp
from loguru import logger

import numpy as np
import numpy.typing as npt

from extract_cp.params import SideStr, SIDE_OPTIONS, Parameters
from extract_cp.qc import surfdisterr, smtherr
from extract_cp.predict_smth import predict_aom

_LOG_PREFIX = b'[' + os.path.basename(__file__).encode(encoding='utf-8') + b']'

BAD_SMTHERR = 2.0
BAD_DISTERR = 2.0


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
    smtherr_max: float


@dataclasses.dataclass(frozen=True)
class _ExtractSurface:
    """
    Defines the procedures for surface extraction. Every method is riddled with side effects...
    """
    mask: Path
    surface: Path
    side: Side
    params: Parameters
    output_sink: BinaryIO
    outcomes: list[StepOutcome] = dataclasses.field(default_factory=list)

    def run(self):
        """
        See README.md for explanation of this algorithm.
        """
        self._marching_cubes_until_disterr_ok()
        self._iterpolate_with_sphere()
        self._smooth_as_needed()
        self.conclude()

    def conclude(self):
        """
        Finishing touches
        """
        self._check_qc_bad()
        self.output_sink.flush()
        self._write_steps()

    def _check_qc_bad(self):
        """
        If any final QC measurement is worse than a threshold, create a ".bad" file.
        """
        last_outcome = self.outcomes[-1]
        if last_outcome['smtherr_max'] >= BAD_SMTHERR:
            self._smtherr_file.with_suffix('.bad').touch()
        if last_outcome['disterr_abs_max'] >= BAD_DISTERR:
            self._disterr_file.with_suffix('.bad').touch()

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
        self._message('marching-cubes with subsampling improvement: max(surfdisterr) ',
                      self._percent_change(disterr, second_disterr))

        if second_disterr > disterr:
            self._message('!!!WARNING!!! marching-cubes with subsampling produced a surface '
                          'with greater distance error, this is unexpected.')

        smth_first = first_outcome['smtherr_mean']
        smth_second = second_outcome['smtherr_mean']
        self._message('affected mean(smtherr): ', self._percent_change(smth_first, smth_second))

    def _iterpolate_with_sphere(self):
        """
        Perform sphere-to-sphere interpolation, resampling the surface to have standard connectivity
        (a consistent 81,920 triangles).

        This should happen *before* smoothing because the resampling somewhat smoothens the surface.
        """
        current_smth = self.outcomes[-1]['smtherr_mean']
        IrregularSurface(self.surface)\
            .interpolate_with_sphere(self.side, *self.params.inflate_to_sphere_implicit)\
            .save(self.surface, shell=self._logged_runner)
        inflate_params = map(str, self.params.inflate_to_sphere_implicit)
        step_name = 'sphere-to-sphere interpolation ::: ' \
                    f'inflate_to_sphere_implicit {" ".join(inflate_params)}'
        outcome = self._evaluate(step_name)
        new_smth = outcome['smtherr_mean']
        self._message('mean(smtherr): ', self._percent_change(current_smth, new_smth))

    def _smooth_as_needed(self):
        """
        Apply a predicted number of iterations of ``adapt_object_mesh``.
        """
        current_smth = self.outcomes[-1]['smtherr_mean']
        n_smooth = predict_aom(current_smth, self.params.target_smoothness, self.params.max_smooth_iterations)
        if n_smooth <= 0:
            self._message('smoothing not needed')
            return
        self._adapt_object_mesh(n_smooth)
        outcome = self._evaluate(f'adapt_object_mesh 0 {n_smooth} 0 0')
        new_smth = outcome['smtherr_mean']
        self._message('mean(smtherr): ', self._percent_change(current_smth, new_smth))

    def _adapt_object_mesh(self, n_smooth: int):
        IrregularSurface(self.surface)\
            .adapt_object_mesh(0, n_smooth, 0, 0)\
            .save(self.surface, shell=self._logged_runner)

    def _marching_cubes(self, subsample: bool):
        HemisphereMask(self.mask)\
            .just_sphere_mesh(self.side, subsample=subsample)\
            .save(self.surface, shell=self._logged_runner)

    def _evaluate(self, name: str) -> StepOutcome:
        """
        (Re)-calculate smtherr and disterr, writing both data to files and append
        a summary to ``self.outcomes``. This summary is also returned.
        """
        smtherr_data = self._load_smtherr()
        disterr_data = self._load_surfdisterr()
        outcome = StepOutcome(
            name=name,
            disterr_abs_max=float(np.abs(disterr_data).max()),
            smtherr_mean=float(smtherr_data.mean()),
            smtherr_max=float(smtherr_data.max())
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

    @staticmethod
    def _percent_change(a: float, b: float) -> str:
        percent = (b - a) / a
        plus = '+' if percent > 0 else ''
        return f'{a:.3f} -> {b:.3f} ({plus}{percent:.1%} change)'

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
