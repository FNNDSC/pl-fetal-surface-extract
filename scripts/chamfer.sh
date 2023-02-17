#!/bin/bash -e
# the original chamfer map created in marching_cubes_fetus.pl
# Date: 21 Aug 2019
# Author: Jennings Zhang <jenni_zh@protonmail.com>

# &run( 'mincdefrag', $wm_mask, "${tmpdir}/wm_mask_defragged.mnc", 1, 6 );
# &run( 'mincchamfer', '-quiet', '-max_dist', '10.0',
#       "${tmpdir}/wm_mask_defragged.mnc", "${tmpdir}/chamfer_outside.mnc" );
# &run( 'minccalc', '-quiet', '-clobber', '-expression', '1-A[0]',
#       "${tmpdir}/wm_mask_defragged.mnc", "${tmpdir}/wm_mask_negated.mnc" );
# &run( 'mincchamfer', '-quiet', '-max_dist', '5.0',
#       "${tmpdir}/wm_mask_negated.mnc", "${tmpdir}/chamfer_inside.mnc" );
# unlink( "${tmpdir}/wm_mask_negated.mnc" );
# &run( 'minccalc', '-quiet', '-clob', '-expression', "10.0-A[0]+A[1]",
#       "${tmpdir}/chamfer_inside.mnc", "${tmpdir}/chamfer_outside.mnc",
#       "${tmpdir}/wm_chamfer.mnc" );
# unlink( "${tmpdir}/chamfer_outside.mnc" );
# unlink( "${tmpdir}/chamfer_inside.mnc" );

function show_help () {
  cat << EOF
usage: $0 wm.mnc chamfer.mnc

Creates a bidirectional radial distance map for the volume (wm.mnc) using mincchamfer.

options:
  -h        show this help message and exit
  -v        verbose output
  -k        keep temporary files
  -c        boundary value (default: 10)
  -i [1-6]  treats the input as painted labels instead of a binary mask.
            The chamfer is generated around the outer surface of the layer
            as specified by the given isovalue.
              1 = CSF
              2 = gray matter (cortical plate)
              3 = white matter (subplate zone)
              4 = intermediate zone
              5 = subventricular zone
              6 = ventricle
EOF
}

[[ $1 == *"-h"* ]] && show_help && exit 0

quiet="-quiet"
keep=0
label=1
iso=10

while getopts ":hvki:c:" opt; do
  case $opt in
  h   ) show_help && exit 0 ;;
  v   ) quiet="" ;;
  k   ) keep=1 ;;
  i   ) label=$OPTARG ;;
  c   ) iso=$OPTARG ;;
  \?  ) echo "Invalid option: -$OPTARG\nRun $0 -h for help."
    exit 1 ;;
  esac
done
shift $((OPTIND-1))
wm_mask=$1
output_chamfer=$2

if [ -z "$wm_mask" ] || [ -z "$output_chamfer" ]; then
  echo "Missing filenames, run $0 -h for help."
  exit 1
fi

tmpdir=$(mktemp -d -t chamfer-$(date +%Hh%M,%S)-XXXXXXXXX)

wm_mask_defragged=$tmpdir/wm_mask_defragged.mnc
negative_mask=$tmpdir/wm_mask_negated.mnc
outer_chamfer=$tmpdir/chamfer_outer.mnc
inner_chamfer=$tmpdir/chamfer_inner.mnc

# create a binary mask from painted labels
bin_mask=$tmpdir/wm_mask.mnc
if [ "$label" -gt "1" ]; then
  label="$((label-1)).5"  # label = label - 0.5
  [ "$quiet" = "" ] && set -x
  minccalc $quiet -byte -clob -expression "A[0]>$label" $wm_mask $bin_mask
  { set +x; } 2> /dev/null
else
  # number range must be compatible with mincchamer
  mincreshape $quiet -image_range 0 255 $wm_mask $bin_mask
fi
wm_mask=$bin_mask

if [ "$quiet" = "" ]; then
  set -x # print commands before running them
  mincdefrag $wm_mask $wm_mask_defragged 0 6
  mincdefrag $wm_mask_defragged $wm_mask_defragged 1 6
else
  mincdefrag $wm_mask $wm_mask_defragged 0 6 > /dev/null
  mincdefrag $wm_mask_defragged $wm_mask_defragged 1 6 > /dev/null
fi
mincchamfer $quiet -max_dist 10.0 $wm_mask_defragged $outer_chamfer
minccalc $quiet -clob -expression "A[0]<0.5" $wm_mask_defragged $negative_mask
mincchamfer $quiet -max_dist 5.0 $negative_mask $inner_chamfer
minccalc $quiet -clob -expression "$iso-A[0]+A[1]" \
         $inner_chamfer $outer_chamfer $output_chamfer

# output volume will be of type image: unsigned byte 0 to 255
# seems incorrect, I think it should be float, but it works
# mincreshape $quiet -clobber -signed -float $output_chamfer $float_chamfer

{ set +x; } 2> /dev/null

if [ "$keep" = "0" ]; then
  rm -r $tmpdir
  [ "$quiet" = "" ] && echo "Removed $tmpdir" || true
else
  echo "-k flag specified, intermediate files are in $tmpdir"
  echo "Run rm -r /tmp/chamfer-* to clean up tempoary tiles."
fi
