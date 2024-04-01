import glob
import os
datasetfiles = glob.glob("*.vcf")
reffiles = ["../sources/AGBL4.vcf.gz"]*len(datasetfiles)
input_files = sum(list(map(list,zip(datasetfiles,reffiles))),[])
os.system("rare_SNP_diagnosis8.py {} --degree=4 --trials=10000 > results.txt".format(" ".join(input_files)) )
