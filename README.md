# _ChRIS_ Plugin Template

This is a minimal template repository for _ChRIS_ plugin applications in Python.

## About _ChRIS_ Plugins

A _ChRIS_ plugin is a scientific data-processing software which can run anywhere all-the-same:
in the cloud via a [web app](https://github.com/FNNDSC/ChRIS_ui/), or on your own laptop
from the terminal. They are easy to build and easy to understand: most simply, a
_ChRIS_ plugin is a command-line program which processes data from an input directory
and creates data to an output directory with the usage
`commandname [options...] inputdir/ outputdir/`.

For more information, visit our website https://chrisproject.org

## How to Use This Template

Go to https://github.com/FNNDSC/python-chrisapp-template and click "Use this template".
The newly created repository is ready to use right away.

A script `bootstrap.sh` is provided to help fill in and rename values for your new project.
It is optional to use.

1. Edit the variables in `bootstrap.sh`
2. Run `./bootstrap.sh`
3. Follow the instructions it will print out

## Example Plugins

Here are some good, complete examples of _ChRIS_ plugins created from this template.

- https://github.com/FNNDSC/pl-nums2mask
- https://github.com/FNNDSC/pl-nii2mnc-u8
- https://github.com/FNNDSC/pl-dcm2niix

## What's Inside

| Path                       | Purpose                                                                                                                                                                                                  |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `app.py`                   | main script                                                                                                                                                                                              |
| `setup.py`                 | [Python project metadata and installation script](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#setup-py)                                                        |
| `requirements.txt`         | List of Python dependencies                                                                                                                                                                              |
| `Dockerfile`               | [Container image build recipe](https://docs.docker.com/engine/reference/builder/)                                                                                                                        |
| `.github/workflows/ci.yml` | "continuous integration" using [Github Actions](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions): automatic testing, building, and uploads to https://chrisstore.co |


<!-- BEGIN README TEMPLATE

# ChRIS Plugin Title

[![Version](https://img.shields.io/docker/v/fnndsc/pl-appname?sort=semver)](https://hub.docker.com/r/fnndsc/pl-appname)
[![MIT License](https://img.shields.io/github/license/fnndsc/pl-appname)](https://github.com/FNNDSC/pl-appname/blob/main/LICENSE)
[![ci](https://github.com/FNNDSC/pl-appname/actions/workflows/ci.yml/badge.svg)](https://github.com/FNNDSC/pl-appname/actions/workflows/ci.yml)

`pl-appname` is a [_ChRIS_](https://chrisproject.org/)
_ds_ plugin which takes in ...  as input files and
creates ... as output files.

## Abstract

...

## Installation

`pl-appname` is a _[ChRIS](https://chrisproject.org/) plugin_, meaning it can
run from either within _ChRIS_ or the command-line.

[![Get it from chrisstore.co](https://ipfs.babymri.org/ipfs/QmaQM9dUAYFjLVn3PpNTrpbKVavvSTxNLE5BocRCW1UoXG/light.png)](https://chrisstore.co/plugin/pl-appname)

## Local Usage

To get started with local command-line usage, use [Apptainer](https://apptainer.org/)
(a.k.a. Singularity) to run `pl-appname` as a container:

```shell
singularity exec docker://fnndsc/pl-appname commandname [--args values...] input/ output/
```

To print its available options, run:

```shell
singularity exec docker://fnndsc/pl-appname commandname --help
```

## Examples

`commandname` requires two positional arguments: a directory containing
input data, and a directory where to create output data.
First, create the input directory and move input data into it.

```shell
mkdir incoming/ outgoing/
mv some.dat other.dat incoming/
singularity exec docker://fnndsc/pl-appname:latest commandname [--args] incoming/ outgoing/
```

## Development

Instructions for developers.

### Building

Build a local container image:

```shell
docker build -t localhost/fnndsc/pl-appname .
```

### Get JSON Representation

Run [`chris_plugin_info`](https://github.com/FNNDSC/chris_plugin#usage)
to produce a JSON description of this plugin, which can be uploaded to a _ChRIS Store_.

```shell
docker run --rm localhost/fnndsc/pl-appname chris_plugin_info > chris_plugin_info.json
```

### Local Test Run

Mount the source code `app.py` into a container to test changes without rebuild.

```shell
docker run --rm -it --userns=host -u $(id -u):$(id -g) \
    -v $PWD/app.py:/usr/local/lib/python3.10/site-packages/app.py:ro \
    -v $PWD/in:/incoming:ro -v $PWD/out:/outgoing:rw -w /outgoing \
    localhost/fnndsc/pl-appname commandname /incoming /outgoing
```
END README TEMPLATE -->