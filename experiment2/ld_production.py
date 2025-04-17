import glob
import os
datasetfiles = glob.glob("./attribute/*.pickle")
datasetfiles = [f for f in datasetfiles if 'split2' in f]
reffile = "./sources/65K_SNP_1000G_real_split1.vcf.gz.pickle"
datasetfiles += [reffile]

for file in datasetfiles:
    os.system(f"ld.py {file} {file}_ld.png" )

