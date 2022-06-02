# Fetal CP Surface Extraction

[![Version](https://img.shields.io/docker/v/fnndsc/pl-fetal-cp-surface-extract?sort=semver)](https://hub.docker.com/r/fnndsc/pl-fetal-cp-surface-extract)
[![MIT License](https://img.shields.io/github/license/fnndsc/pl-fetal-cp-surface-extract)](https://github.com/FNNDSC/pl-fetal-cp-surface-extract/blob/main/LICENSE)
[![ci](https://github.com/FNNDSC/pl-fetal-cp-surface-extract/actions/workflows/ci.yml/badge.svg)](https://github.com/FNNDSC/pl-fetal-cp-surface-extract/actions/workflows/ci.yml)

Fetal brain cortical plate surface extraction using CIVET marching-cubes (`sphere_mesh`).

**TODO add a figure here of screenshots.**

## Abstract

`pl-fetal-cp-surface-extract` consumes binary volumetric `.mnc` brain masks to produce
surfaces as `.obj` files. This program is suitable for targeting the **inner cortical plate**
surface (gray-white matter boundary) of high-quality human fetal brain MRI segmentation
for subjects between 23-35 gestational weeks of age.

## Installation

`pl-fetal-cp-surface-extract` is a _[ChRIS](https://chrisproject.org/) plugin_, meaning it can
run from either within _ChRIS_ or the command-line.

[![Get it from chrisstore.co](https://ipfs.babymri.org/ipfs/QmaQM9dUAYFjLVn3PpNTrpbKVavvSTxNLE5BocRCW1UoXG/light.png)](https://chrisstore.co/plugin/pl-fetal-cp-surface-extract)

## Usage

`extract_cp` reads mask files from an input directory and creates
the resulting surface files in an output directory.

### Input

Input files should be MINC `.mnc` files representing a mask of the white matter (WM)
for a single brain hemisphere (either left or right). WM should be indicated by a
value of `1`, background value should be `0`.

If the input directory contains multiple masks, they will all be processed
individually and in parallel.

## Local Usage

To get started with local command-line usage, use [Apptainer](https://apptainer.org/)
(a.k.a. Singularity) to run `pl-fetal-cp-surface-extract` as a container:

```shell
singularity exec docker://fnndsc/pl-fetal-cp-surface-extract extract_cp input/ output/
```

To print its available options, run:

```shell
singularity exec docker://fnndsc/pl-fetal-cp-surface-extract extract_cp --help
```

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
    -v $PWD/extract_cp.py:/usr/local/lib/python3.10/site-packages/extract_cp.py:ro \
    -v $PWD/in:/incoming:ro -v $PWD/out:/outgoing:rw -w /outgoing \
    localhost/fnndsc/pl-fetal-cp-surface-extract extract_cp /incoming /outgoing
```
