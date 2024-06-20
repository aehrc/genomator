from tqdm import tqdm
import pandas as pd

def generate_vcf_file(data, output_file="geno.vcf"):
    vcf_header='''##fileformat=VCFv4.2
##FILTER=<ID=PASS,Description="All filters passed">
##fileDate=20230223
##source=PLINKv1.90
##contig=<ID=1,length=249240544>
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
'''
    vcf_header_top = "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	"
    vcf_line = "1	{}	{}	A	G	.	.	.	GT	"
    f = open(output_file,"w")
    f.write(vcf_header)
    f.write(vcf_header_top + "\t".join(data['id'].to_list())+"\n")
    transform = lambda x:'0/0' if x==0 else '0/1' if x==1 else '1/1'
    for i,variant in enumerate(data.keys()):
        if variant=='id' or variant=='discard':
            continue
        f.write(vcf_line.format(i,variant)+"\t".join(data[variant].apply(transform))+"\n")
    f.close()


print("loading CSV data....")
with open("geno.txt","r") as f:
    geno_data = pd.read_csv(f, delimiter=" ")
print("converting id column to str")
geno_data = geno_data.astype({'id':'str'})
print("rounding genotypes")
geno_data = geno_data.round()
print("loading phenotypes")
with open("pheno_new.csv","r") as f:
    pheno_data = pd.read_csv(f)
print("considering only abBMD phenotype")
pheno_data = pheno_data[['id','abBMD',"SW16"]]
pheno_data = pheno_data.dropna()
print("processing phenotype entries to linke to genotypes")
pheno_ids = pheno_data.id.to_list()
print("filtering genotypes and sorting by id")
geno_data = geno_data[geno_data.id.apply(lambda x:x in pheno_ids)].sort_values('id')
geno_ids = geno_data.id.to_list()
pheno_data = pheno_data[pheno_data.id.apply(lambda x:x in geno_ids)].sort_values('id')
print("generating VCF")
generate_vcf_file(geno_data)
print("generating pheno refined CSV")
pheno_data.to_csv("pheno_new2.csv",index=False)
