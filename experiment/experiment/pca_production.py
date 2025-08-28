
# produces PCAs of synthetic 65k snp data from the methods

import glob
import os
from tqdm import tqdm
import sys
datasetfiles = glob.glob("./attribute_larger/*.pickle")
datasetfiles = [f for f in datasetfiles if 'split1' in f]
if len(sys.argv)>1:
    datasetfiles = [f for f in datasetfiles if sys.argv[1] in f]
reffile = "./sources/65K_SNP_1000G_real_split2.vcf.gz.pickle"

refined_datasetfiles = []
for file in datasetfiles:
    if not os.path.isfile(f"{file}.png"):
        refined_datasetfiles.append(file)
for file in tqdm(refined_datasetfiles):
    os.system(f"pca_plot_genomes_vcf2.py {reffile} {file} {file}.png" )

