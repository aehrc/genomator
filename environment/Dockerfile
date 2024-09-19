# hash:sha256:02c2c9313ce2e57c55bdc47ee775dbbeb801e053680ed6887572535dbce320b9
FROM registry.codeocean.com/codeocean/ubuntu:20.04-cuda11.7.0-cudnn8

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys \
        AE89DB0EE10E60C01100A8F2A1489FE2AB99A21A \
        E298A3A825C0D65DFD57CBB651716619E084DAB9 \
    && apt-get update \
    && apt-get install -y --no-install-recommends software-properties-common \
    && add-apt-repository -y 'deb [arch=amd64] https://r2u.stat.illinois.edu/ubuntu focal main' \
    && add-apt-repository -y 'deb https://cloud.r-project.org/bin/linux/ubuntu focal-cran40/' \
    && add-apt-repository -y ppa:c2d4u.team/c2d4u4.0+ \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get purge -y --autoremove software-properties-common \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential=12.8ubuntu1.1 \
        cmake=3.16.3-1ubuntu1.20.04.1 \
        gcc=4:9.3.0-1ubuntu2 \
        gfortran=4:9.3.0-1ubuntu2 \
        libblas-dev=3.9.0-1build1 \
        libbz2-dev=1.0.8-2 \
        libcurl4-gnutls-dev=7.68.0-1ubuntu2.24 \
        libdeflate-dev=1.5-3 \
        libgit2-dev=0.28.4+dfsg.1-2ubuntu0.1 \
        liblapack-dev=3.9.0-1build1 \
        liblzma-dev=5.2.4-1ubuntu1.1 \
        libncurses5-dev=6.2-0ubuntu2.1 \
        libncursesw5-dev=6.2-0ubuntu2.1 \
        libssl-dev=1.1.1f-1ubuntu2.23 \
        libxml2-dev=2.9.10+dfsg-5ubuntu0.20.04.7 \
        make=4.2.1-1.2 \
        pkg-config=0.29.1-0ubuntu4 \
        plink2=2.00~a3-200217+dfsg-1 \
        python3.11=3.11.10-1+focal1 \
        python3.11-venv=3.11.10-1+focal1 \
        r-base-core=4.4.1-1.2004.0 \
        r-cran-data.table=1.15.0-1cran1.2004.0 \
        r-cran-ggpubr=0.6.0-1.ca2004.1 \
        r-cran-janitor=2.2.0-1.ca2004.1 \
        r-cran-knitr=1.48-1.ca2004.1 \
        r-cran-tidyverse=2.0.0-1.ca2004.1 \
        time=1.7-25.1build1 \
        unzip=6.0-25ubuntu1.2 \
        wget=1.20.3-1ubuntu2.1 \
        zlib1g=1:1.2.11.dfsg-2ubuntu1.5 \
        zlib1g-dev=1:1.2.11.dfsg-2ubuntu1.5 \
        zlibc=0.9k-4.3 \
    && rm -rf /var/lib/apt/lists/*

COPY postInstall /
RUN /postInstall
