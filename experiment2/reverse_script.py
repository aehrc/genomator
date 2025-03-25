from source_gen import *

A = '''
for i in $(seq 1 60)
do
    vcf_trimmer.py ../sources/65K_SNP_1000G_real{rotate}.vcf.gz ./extract_{seed}.vcf {g} 400
    genomator ./extract_{seed}.vcf ./generated_{seed}.vcf 1 {ex} 1 --sample_group_size={s} --solver_name=cmsgen --exception_space=-{p} --cluster_information_file=./privacy{seed}_cluster.txt --difference_samples=1000
    reverse_genomator ./extract_{seed}.vcf ./generated_{seed}.vcf {s} --upper_exception_space=-{p} --max_iterations=500 --output_file=./privacy{seed}.txt --diversity_requirement={ex} --timeout=1800
    rare_SNP_diagnosis6.py ./extract_{seed}.vcf ./generated_{seed}.vcf ./privacy{seed}_cluster.txt ./privacy{seed}.txt ./privacy{ex}_{p}_analyse_{s}.txt --trials=5000 --combination_degree=4
    rm ./privacy{seed}_cluster.txt
    rm ./privacy{seed}.txt
    rm ./extract_{seed}.vcf
    rm ./generated_{seed}.vcf
done
'''
B = '''
for i in $(seq 1 30)
do
    vcf_trimmer.py ../sources/65K_SNP_1000G_real{rotate}.vcf.gz ./extract_{seed}.vcf {g} 400
    genomator ./extract_{seed}.vcf ./generated_{seed}.vcf {g} {ex} 1 --sample_group_size={s} --solver_name=cmsgen --exception_space=-{p} --cluster_information_file=./privacy{seed}_cluster.txt --difference_samples=1000
    wasserstein_analyse.py ./extract_{seed}.vcf ./generated_{seed}.vcf >> ./wasserstein_{seed}_{g}_{ex}_{s}_{p}.txt
    rm ./extract_{seed}.vcf
    rm ./generated_{seed}.vcf
done
'''



import os
os.chdir("reverse")
from random import random
with open("run_all.sh","w") as f:
    for i in range(0,31):
        filename1 = f"reverse_experiment_{i}A.sh"
        filename2 = f"reverse_experiment_{i}B.sh"
        g=400
        ex=0
        s=100
        p = i*1.0/5
        with open(filename1,"w") as ff:
            ff.write(virga_header_nerfed)
            seed = str(random())[2:]
            ff.write(A.format(g=g,ex=ex,s=s,p=p,seed=seed,rotate='ABC'[i%3]))
        with open(filename2,"w") as ff:
            ff.write(virga_header_nerfed)
            seed = str(random())[2:]
            ff.write(B.format(g=g,ex=ex,s=s,p=p,seed=seed,rotate='ABC'[i%3]))
        f.write(f"sbatch {filename1}\n")
        f.write(f"sbatch {filename2}\n")




