#!/usr/bin/env python
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
from chris_plugin import chris_plugin, PathMapper

from extract_cp import DISPLAY_TITLE, __version__
from extract_cp.extract_surface import SIDE_OPTIONS, extract_surface


parser = ArgumentParser(description='Fetal brain MRI CP inner surface extraction',
                        formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('-s', '--side', default='auto', choices=SIDE_OPTIONS,
                    help='brain hemisphere side. "auto" => infer from file name')
parser.add_argument('-p', '--pattern', default='**/*.mnc',
                    help='pattern for file names to include')
parser.add_argument('--no-fail', dest='no_fail', type=bool, default=False,
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
    print(DISPLAY_TITLE, file=sys.stderr, flush=True)

    with ThreadPoolExecutor(max_workers=len(os.sched_getaffinity(0))) as pool:
        mapper = PathMapper.file_mapper(inputdir, outputdir, glob=options.pattern, suffix='.obj')
        results = pool.map(lambda t: extract_surface(*t, side=options.side), mapper)

    if not options.no_fail:
        for _ in results:
            pass


if __name__ == '__main__':
    main()
