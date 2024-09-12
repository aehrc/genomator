# Experiment Scripts for Genomator Paper

This is the repository accompanying the publication of the Genomator paper, in this repository there is the experimental procedures that should reproduce the results featured in that paper.
To execute these procedures, the python package in directory "experiment_tools" should be installed in a python environment. this package installation should install a range of requisite python libraries, and these libraries should work particularly on a system which has a GPU (or otherwise GPU functionality can be disabled, as detailed in following sections) and a system capable of supporting pytorch and tensorflow system libraries.

In addition to python libraries a particular set of system utilities should be accessible via the script files. particularly:

 - bcftools (including utility 'bcftools' and 'bgzip' command utilities)
 - plink2
 - wget

Once these system utilities and tools are installed (the python package 'experiment_tools' with pytorch and tensorflow system, and utilities bcftools&plink&wget) then a single script should be run:

    /experiment/run_me.sh

This script runs the */experiment/sources/script.py* file, which downloads and processes all source data, and then scans all subdirectories of */experiment/** for any and all files */script.sh* and runs them.
Each of these */script.sh* files contains the code to execute a respective experiment.
And the results for each experiment should be contained in those corresponding subdirectories.
we note that the `run_me.sh` script file will take a LONG time to compute, and alternatively to running that script any specific experiment can be run by executing the `script.sh` file in the desired experiment folder (assuming the `/experiment/sources/script.py` has successfully downloaded and formatted the input datasets to these experiments first)

### Running without GPU
In various scripts and python files in */experiment/* the flag **--gpu=True** this should be changed to **--gpu=False** which should facilitate running on systems without GPU.

# Running with the genomator binary
There are currently two ways to run these scripts with the genomator binary: using Code Ocean and using Docker.
More information is available in the [binary branch README](https://github.com/aehrc/genomator/blob/binary/README.md).

### Code Ocean
Navigate to [https://codeocean.com/capsule/1806639](https://codeocean.com/capsule/1806639) and select "Reproducible Run". This may require making an account for Code Ocean. Please also note that the runtime for all the tests can be in excess of 4 hours.

When the run is complete the resulting files will be in `results/` organised by test name.

### Docker
From the Code Ocean capsule (accessible at [https://codeocean.com/capsule/1806639](https://codeocean.com/capsule/1806639)), click on `Capsule` and then `Export...`. Opt to include the data. Extract the zip file and inspect `REPRODUCING.md` for detailed instructions on how to run the capsule in Docker.
The simple instructions are below.

To build the docker image:
```shell
cd environment && docker build . --tag genomator-tests; cd ..
```
To run the capsule:
```shell
docker run --platform linux/amd64 --rm --gpus all \
  --workdir /code \
  --volume "$PWD/data":/data \
  --volume "$PWD/code":/code \
  --volume "$PWD/results":/results \
  genomator-tests bash run
```
The completed test files will be stored in the `results/` directory, organised by test name.

# Experiment details

### 805
The 805 experiment contains experimental code to reproduce V-shaped PCAs associated with 805 SNP data, including calculating wasserstein distance on the PCA for each of the methods. in each of the subfolders 1-10 should be PNG images visualsing these PCA images, as well as various .txt files containing the wasserstein distances.
The information collating the wasserstein distances is collated by running the `/experiment/805/analyse_pca.sh` script

### attribute
the 'attribute' experiment contains the execution code to produce data associated with how accurate the synthetic data produced by each method matches against its source vs a similar dataset - to produce a measure of privacy. The results of this experiment are stored in the */results.txt* file

### ld
the 'ld' experiment produces pictures showing how well each method reproduces the LD structure on the AGBL4 gene, the LD scores between the first 2000 SNPs in the source AGBL4 dataset, and that reproduced in the output from each of the methods are produced as *.png* files in this directory.

### ld_error
the 'ld_error' experiment contains 4 subfolders for each of the genes considered in the paper, each sub-experiment computes 1000 synthetic genomes from each method and gene, and computes the square error in LD reproduction across a range of genome window sizes, output from these experiments is graphs in *.png* files.

### pharmacogenetic
the 'pharmacogenetic' experiment computes 1000 synthetic sets of chromosomes 10&16 with genomator. in this directory there is information about how to perform analysis with these data to extract relevent pharamacogenetic SNP analysis across ethnicities via PCA analysis.

### quadruplets
the 'quadruplets' experiment contains code to interrogate how many private vs fictitious SNP quadruplets are generated from each of the methods on the AGBL4 gene dataset. Output from this experiment is contained in a *.png* graph and in *results.txt* file.

### reverse
the 'reverse' experiment contains script to run genomator and use reverse genomator to detect the number of privacy-exposed instances. the results are generated and stored in the */results* subdirectory and therein a *.png* file shoud contain the experiment results graph.

### runtimes
the 'runtimes' experiment contains the experiment process of callilng each of the methods on iteratively larger portions of the dataset of the human genome, up till the full 22 chromosomes. output is a 'runtime_results.txt' file that should show how long each call took to succeed (or fail).
