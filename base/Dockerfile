FROM docker.io/fnndsc/microminc-builder:latest as builder

RUN microminc.sh \
    adapt_object_mesh \
    dilate_volume \
    minccalc \
    mincchamfer \
    mincdefrag \
    mincresample \
    mincreshape \
    param2xfm \
    sphere_mesh \
    surface_mask2 \
    transform_objects \
    inflate_to_sphere_implicit \
    inflate_to_sphere \
    create_tetra \
    print_n_polygons \
    subdivide_polygons \
    interpolate_sphere \
    depth_potential \
    vertstats_math \
    volume_object_evaluate \
    adapt_metric \
    depth_potential \
        /microminc

# perl libraries need to be copied manually
RUN cp -r /opt/CIVET/dist/perl /microminc/perl

# MNI data needs to be copied manually
RUN mkdir -vp /microminc/share  \
    && cp -rv "$MNI_DATAPATH/surface-extraction" "/microminc/share"

FROM ghcr.io/mamba-org/micromamba:1.5.1-bookworm-slim

USER root
RUN --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean \
    && apt-get update \
    && apt-get -y --no-install-recommends install perl

COPY --from=builder /microminc /opt/microminc
ENV PATH=/opt/conda/bin:/opt/microminc/bin:$PATH \
    LD_LIBRARY_PATH=/opt/microminc/lib:$LD_LIBRARY_PATH \
    MINC_FORCE_V2=1 MINC_COMPRESS=4 VOLUME_CACHE_THRESHOLD=-1 \
    MNI_DATAPATH=/opt/microminc/share \
    PERL5LIB=/opt/microminc/perl

USER mambauser
