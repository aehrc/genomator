import pandas as pd
import random
from genomator import parse_VCF_to_genome_strings, parse_genome_strings_to_VCF, generate_genomes

genotype_file="geno.vcf"
phenotype_file="pheno_new2.csv"
genotype_output_file="new_genomes.vcf"
phenotype_output_file="new_phenotypes.csv"

# loading abBMD phenotype
with open(phenotype_file,"r") as f:
    data = pd.read_csv(f)
data['abBMD'] = data['abBMD'].apply(int)
data['SW16'] = data['SW16'].apply(int)
del data['id']
s = data.to_numpy().tolist()
s = [bytes(b) for b in s]

# loading genomes VCF and concatenate genotypes with abBMD phenotype
genomes,ploidy = parse_VCF_to_genome_strings(genotype_file)


# do genomator
s1 = [genomes[i]+s[i] for i in range(len(s)) if s[i][0]==0]
s2 = [genomes[i]+s[i] for i in range(len(s)) if s[i][0]==1]
s1 = generate_genomes(s1, 13, None, int(len(s1)*1.0), 0, 0, solver_name='minicard', biasing=False, difference_samples=50000, looseness=0.00, freq_multiplier=100)
s2 = generate_genomes(s2, 13, None, int(len(s2)*1.0), 0, 0, solver_name='minicard', biasing=False, difference_samples=50000, looseness=0.00, freq_multiplier=100)
s = s1+s2


# extract new genomes
new_genomes = [ss[:len(genomes[0])] for ss in s]
new_phenomes = [list(ss[len(genomes[0]):]) for ss in s]

# output new genomes
parse_genome_strings_to_VCF(new_genomes, genotype_file, genotype_output_file, ploidy, False)

# postprocess new phenomes
new_phenomes = [['GENERATEDSAMPLE{}'.format(i),ss[0],ss[1]] for i,ss in enumerate(new_phenomes)]
new_phenomes = pd.DataFrame(new_phenomes)
new_phenomes = new_phenomes.rename(columns={0:'id',1:'abBMD',2:"SW16"})

# output new phenomes
new_phenomes.to_csv(phenotype_output_file,index=False)
