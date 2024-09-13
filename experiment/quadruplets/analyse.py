import glob
import os
datasetfiles = glob.glob("*.vcf")
reffiles = ["../sources/AGBL4.vcf.gz"]*len(datasetfiles)
input_files = sum(list(map(list,zip(datasetfiles,reffiles))),[])
os.system("rare_SNP_diagnosis8.py {} --degree=4 --trials=100000 --output_image_file=quadruplets_analysis.png > results1.txt".format(" ".join(input_files)) )
os.system("rare_SNP_diagnosis8.py {} --degree=7 --trials=10000 --output_image_file=septuplets_analysis.png > results2.txt".format(" ".join(input_files)) )
