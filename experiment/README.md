# Experiment Scripts for Genomator Paper

This is the repository accompanying the publication of the Genomator paper, in this repository there is the experimental procedures that should reproduce the results featured in that paper.
To execute these procedures, the python package in directory "experiment_tools" should be installed in a python environment. this package installation should install a range of requisite python libraries, and these libraries should work particularly on a system which has a GPU (or otherwise GPU functionality can be disabled, as detailed in following sections) and a system capable of supporting pytorch and tensorflow system libraries.

In addition to python libraries a particular set of system utilities should be accessible via the script files. particularly:

 - bcftools (including utility 'bcftools' and 'bgzip' command utilities)
 - plink2
 - wget

The Genomator package should be installed with Tinicard library.

Once these system utilities and tools are installed (the python package 'experiment_tools' with pytorch and tensorflow system, and utilities bcftools&plink&wget) then a single script should be run:

    /experiment/RUNME.sh

### Running without GPU
In various scripts and python files the flag **--gpu=True** this should be changed to **--gpu=False** which should facilitate running on systems without GPU.

