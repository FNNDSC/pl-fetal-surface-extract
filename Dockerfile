FROM docker.io/fnndsc/pl-fetal-surface-extract:base-2

LABEL org.opencontainers.image.authors="Jennings Zhang <Jennings.Zhang@childrens.harvard.edu>" \
      org.opencontainers.image.title="pl-fetal-surface-extract" \
      org.opencontainers.image.description="Fetal brain MRI surface extraction using CIVET marching-cubes"

RUN \
    --mount=type=cache,sharing=private,target=/home/mambauser/.mamba/pkgs,uid=57439,gid=57439 \
    --mount=type=cache,sharing=private,target=/opt/conda/pkgs,uid=57439,gid=57439 \
    micromamba install -y -n base -c conda-forge python=3.11.5 numpy=1.26.0

ARG SRCDIR=/home/mambauser/pl-fetal-surface-extract
ARG MAMBA_DOCKERFILE_ACTIVATE=1
WORKDIR ${SRCDIR}

COPY --chown=57439:57439 requirements.txt .
RUN --mount=type=cache,sharing=private,target=/home/mambauser/.cache/pip,uid=57439,gid=57439 \
    pip install -r requirements.txt

COPY --chown=mambauser:mambauser . .
ARG extras_require=none
RUN pip install ".[${extras_require}]" \
    && cd / && rm -rf ${SRCDIR}
WORKDIR /

CMD ["extract_cp"]
