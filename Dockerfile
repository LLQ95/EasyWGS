# EasyWGS main analysis environment (container image).
#
# The image provides the conda environment with the core WGS tools. The EasyWGS
# scripts and your data are mounted at run time, so updating the repository does
# not require rebuilding the image. Large reference databases (CheckM2, GUNC,
# Bakta, eggNOG, FCS-GX) are never baked into the image; mount them read-only and
# point the DBROOT / CHECKM2_DB / BAKTA_DB / EGGNOG_DB / GUNC_DB variables at
# them. The dedicated checkm2/gunc/bakta/eggnog/longread environments are not in
# this default image; build them with 00_install/install_env.sh on the cluster.
#
# Build:
#   docker build -t easywgs:latest -f Dockerfile .
# Run (mount the repository and a database directory):
#   docker run --rm -it -v "$PWD":/EasyWGS -v "$HOME/easywgs_db":/opt/db:ro \
#     -w /EasyWGS -e DBROOT=/opt/db easywgs:latest bash
#
# A prebuilt image is published to ghcr.io by .github/workflows/container.yml.

FROM mambaorg/micromamba:1.5-jammy

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        coreutils \
        gzip \
        procps \
        time \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=$MAMBA_USER:$MAMBA_USER install/environment.yml /tmp/environment.yml

USER $MAMBA_USER
RUN micromamba create -y -f /tmp/environment.yml \
    && micromamba clean --all --yes \
    && rm -f /tmp/environment.yml

# Put the named easywgs environment first on PATH.
ENV PATH=/opt/conda/envs/easywgs/bin:$PATH \
    EASYWGS_ENV=easywgs \
    DBROOT=/opt/db

WORKDIR /EasyWGS

# Metadata (the version label is refreshed at build time, see container.yml).
LABEL org.opencontainers.image.title="EasyWGS" \
      org.opencontainers.image.description="Reproducible whole-genome sequencing workflow for bacterial isolates" \
      org.opencontainers.image.url="https://github.com/LLQ95/EasyWGS" \
      org.opencontainers.image.source="https://github.com/LLQ95/EasyWGS" \
      org.opencontainers.image.licenses="MIT"

CMD ["bash"]
