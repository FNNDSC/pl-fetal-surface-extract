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
parser.add_argument('-s', '--side', default='auto', choices=SIDE_OPTIONS,
                    help='brain hemisphere side. "auto" => infer from file name')
parser.add_argument('-p', '--pattern', default='**/*.mnc',
                    help='pattern for file names to include')
parser.add_argument('--subsample', action='store_true',
                    help='Use -subsample option for spehre_mesh, use with narrow sulci')
parser.add_argument('--mincmorph-iterations', dest='mincmorph_iterations', type=int, default=5,
                    help='Number of mincmorph iterations. Mincmorph is a mask preprocessing step '
                         'which repairs disconnected voxels. A larger value may improve results '
                         'for messy masks, but at the cost of accuracy.')
parser.add_argument('--adapt_object_mesh', dest='adapt_object_mesh', type=str, default='1,50,1',
                    help='Parameters for adapt_object_mesh, which does mesh smoothing.')
parser.add_argument('--inflate_to_sphere_implicit', dest='inflate_to_sphere_implicit', type=str, default='200,200',
                    help='Parameters for inflate_to_sphere_implicit. Larger values are necessary '
                         'for larger brain size.')
parser.add_argument('-k', '--keep-mask', dest='keep_mask', action='store_true',
                    help='Copy input mask file to output directory')
parser.add_argument('--no-fail', dest='no_fail', action='store_true',
                    help='Exit normally even when failed to process a subject')
parser.add_argument('-V', '--version', action='version',
                    version=f'$(prog)s {__version__}')


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

    with ThreadPoolExecutor(max_workers=len(os.sched_getaffinity(0))) as pool:
        mapper = PathMapper.file_mapper(inputdir, outputdir, glob=options.pattern, suffix='._81920.obj')
        results = pool.map(lambda t: extract_surface(*t, params=params), mapper)

    if not options.no_fail:
        for _ in results:
            pass


if __name__ == '__main__':
    main()
