A = '''
for i in $(seq 1 60)
do
    vcf_trimmer.py ../sources/AGBL4.SMALLER.vcf.gz ./results/extract_{seed}.vcf {g} 400
    genomator ./results/extract_{seed}.vcf ./results/generated_{seed}.vcf 1 {ex} 1 --sample_group_size={s} --solver_name=cmsgen --exception_space=-{p} --cluster_information_file=results/privacy{seed}_cluster.txt --difference_samples=1000
    reverse_genomator ./results/extract_{seed}.vcf ./results/generated_{seed}.vcf {s} --upper_exception_space=-{p} --max_iterations=500 --output_file=results/privacy{seed}.txt --diversity_requirement={ex} --timeout=1800
    rare_SNP_diagnosis6.py ./results/extract_{seed}.vcf ./results/generated_{seed}.vcf results/privacy{seed}_cluster.txt results/privacy{seed}.txt results/privacy{ex}_{p}_analyse_{s}.txt --trials=5000 --combination_degree=4
    rm results/privacy{seed}_cluster.txt
    rm results/privacy{seed}.txt
    rm results/extract_{seed}.vcf
    rm results/generated_{seed}.vcf
done
'''
B = '''
for i in $(seq 1 30)
do
    vcf_trimmer.py ../sources/AGBL4.SMALLER.vcf.gz ./results/extract_{seed}.vcf {g} 400
    genomator ./results/extract_{seed}.vcf ./results/generated_{seed}.vcf {g} {ex} 1 --sample_group_size={s} --solver_name=cmsgen --exception_space=-{p} --cluster_information_file=results/privacy{seed}_cluster.txt --difference_samples=1000
    wasserstein_analyse.py ./results/extract_{seed}.vcf ./results/generated_{seed}.vcf >> ./results/wasserstein_{seed}_{g}_{ex}_{s}_{p}.txt
    rm results/extract_{seed}.vcf
    rm results/generated_{seed}.vcf
done
'''


from random import random
with open("experiment.sh","w") as ff:
    g=400
    ex=0
    s=100
    p=0.0
    for i in range(0,31):
        p = i*1.0/5
        seed = str(random())[2:]
        ff.write(A.format(g=g,ex=ex,s=s,p=p,seed=seed))
        seed = str(random())[2:]
        ff.write(B.format(g=g,ex=ex,s=s,p=p,seed=seed))
