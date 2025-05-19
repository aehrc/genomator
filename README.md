# Genomator

This is the repository accompanying the publication of the Genomator paper, in this repository there is the software and experimental procedures that should reproduce the results featured in that paper.

## Directories
A breakdown of these directories is given below:

### /Genomator

The core software for the Genomator tool itself, which is to be installed in an appropriate python environment for execution on any data source (in VCF) to generate new synthetic data (see included details and documentation)
READMEs and documentation for the tool and its install and use are provided therein.

### /experiment

Python scripts and tools to reproduce the results of the paper, the tools need to be installed into an appropriate python environment.
All data used in the experiments are from the 65K dataset used by Yelman et al. downloaded from URL (https://gitlab.inria.fr/ml_genetics/public/artificial_genomes/-/tree/master/1000G_real_genomes)
and all preprocessing is conducted by scripts in /experiment/experiment/source_gen.py and subsequently ingested by experiment code.

### /tinicard

A cardinality SAT solver and python wrapper built, which is compatible with Genomator.

## Licensing
- The main codebase (in `/genomator`) is licensed under the CSIRO Non-Commercial License (based on BSD 3-Clause Clear).
- The optional module in `/tinicard` is based on a GPLv2+ codebase and is therefore licensed under the GNU GPLv2+.
- The optional module is not required for basic functionality.

Also IMPORTANT note: the optional `/tinicard` module is not required for the main codebase to be operational, as it is a separate SAT solving software with a python wrapper to provide an API for interfacing with various python scripts.
The main codebase will only attempt to import and use the API functions associated with this SAT solver if command line parameter `--solver_name=tinicard` is specified, and if not, will default to using the Minicard SAT solver through the PySAT python library.


