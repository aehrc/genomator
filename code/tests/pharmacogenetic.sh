#!/bin/bash

set -exuo pipefail

vcfshark decompress /data/vcfshark/pharmacogenetic/ALL.chr10_and_16.cleaned.vcfshark ALL.chr10_and_16.cleaned.vcf
# Too large a job for Cloud Ocean, use a file generated elsewhere
# genomator ALL.chr10_and_16.cleaned.vcf GENOMATOR.vcf 1000 1 1
vcfshark decompress /data/vcfshark/pharmacogenetic/GENOMATOR.vcfshark GENOMATOR.vcf

#Input files: 
#   - ALL.chr10_and_16.cleaned.vcf
#   - GENOMATOR.vcf (generated from ALL.chr10_and_16.cleaned.vcf)
#   - pharmacogenetic.rsids (list of three pharmacogenetic SNPs of interest)
#   - pharmacogenetic.rsids.allele (list of three pharmacogenetic SNPs of interest with alternate allele)
    
#Step 1: Locate variants in LD and MAF
plink --indep 50 5 1.5 --maf 0.10 --out ALL.chr10_and_16.cleaned.vcf --vcf ALL.chr10_and_16.cleaned.vcf

#Step 2: Remove variants in LD with MAF < 0.10 (as calculated from step 1) and write out as plink format
plink2 --extract ALL.chr10_and_16.cleaned.vcf.prune.in --make-bed --out ALL.chr10_and_16.cleaned.vcf.pruned --vcf ALL.chr10_and_16.cleaned.vcf

#Step 3: Calculate eigenvectors, eigenvalues, and allele freq of reference dataset
plink2 --bfile ALL.chr10_and_16.cleaned.vcf.pruned --freq counts --out ALL.chr10_and_16.cleaned.vcf.pruned.pca --pca allele-wts

#Step 4: Project genomator synthetic genomes onto reference PC space
plink2 --out GENOMATOR.1KGProjected --read-freq ALL.chr10_and_16.cleaned.vcf.pruned.pca.acount --score ALL.chr10_and_16.cleaned.vcf.pruned.pca.eigenvec.allele 2 5 header-read no-mean-imputation variance-standardize --score-col-nums 6-15 --vcf GENOMATOR.vcf

##Note: Projected genomator PCs will be scaled a bit differently from the reference 1000 Genomes Project, and will require some manipulation to put both on the same scale (e.g., multiply/divide projected PCs by a multiple fo the square root of their eigenvalues). Also, projected genomator PCs will tend to be shrunk towards zero. 

#Step 5: Extract genotypes of pharmacogenetic variants of interest
plink2 --export A --export-allele /data/pharmacogenetic.rsids.allele --extract /data/pharmacogenetic.rsids --out GENOMATOR.pharmacogenetics --vcf GENOMATOR.vcf


## Move to R for visualisation - required files:
#   - ALL.chr10_and_16.cleaned.vcf.pruned.pca.eigenvec (from step 3)
#   - 20130606_g1k.ped (downloaded from 1000 Genomes Project - metadata on ancestry)
#   - GENOMATOR.1KGProjected.sscore (from step 4)
#   - ALL.chr10_and_16.cleaned.vcf.pruned.pca.eigenval (from step 3)
#   - GENOMATOR.pharmacogenetics.raw (from step 5)

RESULTS_DIR=$1
/code/bin/pharmacogenetic.r > "${RESULTS_DIR}/results.txt"
mv PCA.tiff "${RESULTS_DIR}/"
mv MAF.tiff "${RESULTS_DIR}/"
