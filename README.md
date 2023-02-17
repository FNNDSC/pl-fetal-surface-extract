# Fetal CP Surface Extraction

[![Version](https://img.shields.io/docker/v/fnndsc/pl-fetal-cp-surface-extract?sort=semver)](https://hub.docker.com/r/fnndsc/pl-fetal-cp-surface-extract)
[![MIT License](https://img.shields.io/github/license/fnndsc/pl-fetal-cp-surface-extract)](https://github.com/FNNDSC/pl-fetal-cp-surface-extract/blob/main/LICENSE)
[![ci](https://github.com/FNNDSC/pl-fetal-cp-surface-extract/actions/workflows/ci.yml/badge.svg)](https://github.com/FNNDSC/pl-fetal-cp-surface-extract/actions/workflows/ci.yml)

Fetal brain cortical plate surface extraction using CIVET marching-cubes (`sphere_mesh`).

![Figure](docs/fig.png)

## Abstract

`pl-fetal-cp-surface-extract` consumes binary volumetric `.mnc` brain masks to produce
surfaces as `.obj` files with standard connectivity (81,920 triangles). This program is
suitable for targeting the **inner cortical plate** surface (gray-white matter boundary)
of high-quality human fetal brain MRI segmentation for subjects between 23-35 gestational
weeks of age.

## Background

Polygonal surface mesh representations of brain hemispheres are useful for measuring cortical
thickness, image registration, and quantitative regional analysis.

## Marching Cubes

We have evaluated two implementations of marching-cubes:

- [scikit-image](https://github.com/FNNDSC/pl-fetal-cp-surface-extract)
- [CIVET](https://github.com/FNNDSC/ep-sphere_mesh)

We found that CIVET's implementation of the marching-cubes algorithm, `sphere_mesh`, is
[more accurate](docs/compare_civet_skimage.md)
than scikit-image's implementation, which requires FWHM blurring of the volume.
Moreover, `sphere_mesh` guarantees a spherical topology.

## Surface Extraction Algorithm

1. Preprocess mask using `mincmorph` to fill in disconnected voxels (improve mask quality)
2. Marching-cubes -> spherical topology surface mesh with unknown number of triangles
3. Calculate distance error
4. _If_ maximum distance error is too large, _then_ redo marching-cubes with subsampling
5. Sphere-to-sphere interpolation -> resample mesh to standard connectivity of 81,920 triangles, preserving morphology
6. Calculate smoothness error
7. Run `adapt_object_mesh` to achieve desired smoothness. Number of iterations is predicted by a regression model

### Estimation of: How much smoothing?

We developed a model which predicts the number of `adapt_object_mesh` smoothing iterations necessary, given a desired smoothness error threshold.
The model was created from the experiment described here:

- https://github.com/FNNDSC/voxelation-error-datalad/blob/90fd86aa2e1a280cbda6a210c802236e34b76457/README.md
- https://github.com/FNNDSC/voxelation-error-datalad/blob/90fd86aa2e1a280cbda6a210c802236e34b76457/5_notebook/taubin_vs_mean_smtherr.ipynb

## Pipeline

1. https://github.com/FNNDSC/ep-premc-mincmorph
2. https://github.com/FNNDSC/pl-nums2mask
3. https://github.com/FNNDSC/pl-subdiv-minc TODO
4. pl-fetal-cp-surface-extract
5. pl-extracted-surface-asp TODO

<!--
While the upstream
[marching_cube.pl](https://github.com/aces/surface-extraction/blob/master/scripts/marching_cubes.pl.in)
script uses ASP (`surface_fit`) post-processing to fully converge the surface to the volume boundary,
without the extra step the accuracy is nonetheless sufficient.
-->

## Installation

`pl-fetal-cp-surface-extract` is a _[ChRIS](https://chrisproject.org/) plugin_, meaning it can
run from either within _ChRIS_ or the command-line.

[![Get it from chrisstore.co](https://raw.githubusercontent.com/FNNDSC/ChRIS_store_ui/963938c241636e4c3dc4753ee1327f56cb82d8b5/src/assets/public/badges/light.svg)](https://chrisstore.co/plugin/pl-fetal-cp-surface-extract)

## Usage

`extract_cp` reads mask files from an input directory and creates
the resulting surface files in an output directory.

### Input

Input files should be MINC `.mnc` files representing a mask of the white matter (WM)
for a single brain hemisphere (either left or right). WM should be indicated by a
value of `1`, background value should be `0`.

If the input directory contains multiple masks, they will all be processed
individually and in parallel.

### Options

#### `--inflate_to_sphere_implicit`

Arguments to pass to `inflate_to_sphere_implicit`. The default value `(200, 200)`
should work for fetal brains. While it shouldn't be necessary, increasing the
values shouldn't do any harm, and would help compensate for larger brain sizes.

#### `--keep-mask`

Copy input mask file to output directory.

`--keep-mask` is a workaround for using `pl-fetal-cp-surface-extract` as part of a
_ChRIS_ pipeline. It eliminates the need for an extra _ts_ plugin step.

## Local Usage

To get started with local command-line usage, use [Apptainer](https://apptainer.org/)
to run `pl-fetal-cp-surface-extract` as a container:

```shell
apptainer exec docker://fnndsc/pl-fetal-cp-surface-extract extract_cp input/ output/
```

To print its available options, run:

```shell
apptainer exec docker://fnndsc/pl-fetal-cp-surface-extract extract_cp --help
```

## Suggested Software

### Before `pl-fetal-cp-surface-extract`

- [`pl-nums2mask`](https://chrisstore.co/plugin/pl-nums2mask): create input masks

### After `pl-fetal-cp-surface-extract`

- [`pl-surfdisterr`](https://chrisstore.co/plugin/pl-surfdisterr): QC
- [`pl-smoothness-error`](https://chrisstore.co/plugin/pl-smoothness-error): QC

## Development

Instructions for developers.

### Building

Build a local container image:

```shell
docker build -t localhost/fnndsc/pl-fetal-cp-surface-extract .
```

### Get JSON Representation

Run [`chris_plugin_info`](https://github.com/FNNDSC/chris_plugin#usage)
to produce a JSON description of this plugin, which can be uploaded to a _ChRIS Store_.

```shell
docker run --rm localhost/fnndsc/pl-fetal-cp-surface-extract chris_plugin_info > chris_plugin_info.json
```

### Local Test Run

Mount the source code `extract_cp.py` into a container to test changes without rebuild.

```shell
docker run --rm -it --userns=host -u $(id -u):$(id -g) \
    -v $PWD/extract_cp:/opt/conda/lib/python3.10/site-packages/extract_cp:ro \
    -v $PWD/in:/incoming:ro -v $PWD/out:/outgoing:rw -w /outgoing \
    localhost/fnndsc/pl-fetal-cp-surface-extract extract_cp /incoming /outgoing
```
