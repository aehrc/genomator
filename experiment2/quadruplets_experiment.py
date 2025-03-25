import glob
import os
datasetfiles = glob.glob("./attribute/*.pickle")
datasetfiles = [f for f in datasetfiles if 'split2' in f]
reffiles = ["./sources/65K_SNP_1000G_real_split2.vcf.gz.pickle"]*len(datasetfiles)
input_files = sum(list(map(list,zip(datasetfiles,reffiles))),[])
#os.system("rare_SNP_diagnosis8.py {} --degree=4 --trials=100000 --output_image_file=quadruplets_analysis.png > results1.txt".format(" ".join(input_files)) )
os.system("rare_SNP_diagnosis8.py {} --degree=4 --trials=10000 --output_image_file=quadruplets_analysis.png > results1.txt".format(" ".join(input_files)) )

