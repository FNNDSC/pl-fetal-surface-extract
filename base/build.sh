#!/bin/bash -ex

exec docker buildx build --push \
    --platform linux/amd64,linux/arm64,linux/ppc64le \
    --build-arg http_proxy=$http_proxy \
    -t docker.io/fnndsc/pl-fetal-surface-extract:base-2 .
