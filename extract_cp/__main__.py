#!/usr/bin/env python
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
from chris_plugin import chris_plugin, PathMapper

from extract_cp import DISPLAY_TITLE, __version__
from extract_cp.params import SIDE_OPTIONS, Parameters
from extract_cp.extract_surface import extract_surface


parser = ArgumentParser(description='Fetal brain MRI CP inner surface extraction',
                        formatter_class=ArgumentDefaultsHelpFormatter)
# -------------------- Input and Output Options --------------------
parser.add_argument('-s', '--side', default='auto', choices=SIDE_OPTIONS,
                    help='brain hemisphere side. "auto" => infer from file name')
parser.add_argument('-p', '--pattern', default='**/*.mnc',
                    help='pattern for file names to include')
parser.add_argument('-J', '--threads', type=int, default=0,
                    help='number of threads to use (pass 0 to use number of visible CPU cores)')
parser.add_argument('-k', '--keep-mask', dest='keep_mask', action='store_true',
                    help='Copy input mask file to output directory')
parser.add_argument('--no-fail', dest='no_fail', action='store_true',
                    help='Exit normally even when failed to process a subject')
parser.add_argument('-V', '--version', action='version',
                    version=f'%(prog)s {__version__}')
# --------------------   Algorithm Parameters   --------------------
parser.add_argument('--inflate_to_sphere_implicit', dest='inflate_to_sphere_implicit', type=str, default='500,500',
                    help='Parameters for inflate_to_sphere_implicit. Larger values are necessary '
                         'for larger brain size.')
parser.add_argument('--distance-threshold', dest='distance_threshold', default=1.0, type=float,
                    help='Maximum distance error to allow without using subsampling')
parser.add_argument('--target-smoothness', dest='target_smoothness', type=float, default=0.2,
                    help='Target mean smoothness error for how many iterations of adapt_object_mesh to perform.')
parser.add_argument('--max-smooth-iterations', dest='max_smooth_iterations', type=int, default=200,
                    help='Maximum allowed number of smoothing iterations using adapt_object_mesh.')


@chris_plugin(
    parser=parser,
    title='Fetal CP Surface Extraction',
    category='Surface Extraction',
    min_memory_limit='100Mi',
    min_cpu_limit='1000m',
    min_gpu_limit=0
)
def main(options: Namespace, inputdir: Path, outputdir: Path):
    params = Parameters.from_obj(options)
    print(DISPLAY_TITLE, file=sys.stderr, flush=True)
    print(params, file=sys.stderr, flush=True)

    proc = len(os.sched_getaffinity(0)) if options.threads <= 0 else options.threads
    with ThreadPoolExecutor(max_workers=proc) as pool:
        mapper = PathMapper.file_mapper(inputdir, outputdir, glob=options.pattern, suffix='._81920.obj')
        results = pool.map(lambda t: extract_surface(*t, params=params), mapper)

    if not options.no_fail:
        for _ in results:
            pass


if __name__ == '__main__':
    main()
