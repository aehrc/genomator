
# calculating results for attribute_inference_experiment for genoamtor with perturbed parameor genoamtor with perturbed parameor genoamtor with perturbed parameor genoamtor with perturbed parameters
# into 'results2' files in attributes_perturbation directory

import glob
import os
import sys
from tqdm import tqdm

datasetfiles = glob.glob("./attribute_perturbation/*.pickle")
datasetfiles = [f for f in datasetfiles if 'split2' in f]
datasetfiles = sorted(datasetfiles)
datasetfiles = [d for d in datasetfiles if not os.path.isfile(f"./attribute_perturbation/results2_{d.split('/')[-1]}.txt")]

if len(sys.argv)>1:
    index = int(sys.argv[1])
    new_files = []
    while len(datasetfiles)!=0:
        new_files.append(datasetfiles[:30])
        datasetfiles = datasetfiles[30:]
    print(len(new_files))
    datasetfiles = new_files[index]

reffile1 = "./sources/65K_SNP_1000G_real_split1.vcf.gz.pickle"
reffile2 = "./sources/65K_SNP_1000G_real_split2.vcf.gz.pickle"

def run_system(a):
    print(a)
    os.system(a)

for file in tqdm(datasetfiles):
    filename = f"./attribute_perturbation/results2_{file.split('/')[-1]}.txt"
    run_system(f"echo {file.split('/')[-1]} >> {filename}")
    run_system(f"attribute_inference_experiment.py {reffile1} {reffile2} {file.replace('split2','split1')} {file} -1 -1 5 >> {filename}")

