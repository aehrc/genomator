# hash:sha256:09451799ab0e3b230e766e156967f5b3e9208b0020c36947f704608f22a4e50e
FROM registry.codeocean.com/codeocean/ubuntu:20.04-cuda11.7.0-cudnn8

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get purge -y --autoremove software-properties-common \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential=12.8ubuntu1.1 \
        cmake=3.16.3-1ubuntu1.20.04.1 \
        gcc=4:9.3.0-1ubuntu2 \
        libbz2-dev=1.0.8-2 \
        libcurl4-gnutls-dev=7.68.0-1ubuntu2.22 \
        libdeflate-dev=1.5-3 \
        liblzma-dev=5.2.4-1ubuntu1.1 \
        libncurses5-dev=6.2-0ubuntu2.1 \
        libncursesw5-dev=6.2-0ubuntu2.1 \
        make=4.2.1-1.2 \
        python3.11=3.11.9-1+focal1 \
        python3.11-venv=3.11.9-1+focal1 \
        wget=1.20.3-1ubuntu2 \
        zlib1g=1:1.2.11.dfsg-2ubuntu1.5 \
        zlib1g-dev=1:1.2.11.dfsg-2ubuntu1.5 \
        zlibc=0.9k-4.3 \
    && rm -rf /var/lib/apt/lists/*

COPY postInstall /
RUN /postInstall
