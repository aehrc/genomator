
def genomator_run(f,i,z,postpend=""):
    f.write(f"genomator ../sources/805_SNP_1000G_real_split_haplotypes1.vcf.gz GENOMATOR_A_{i}_{z}.vcf 1000 0 0 --sample_group_size={i} --exception_space=-{z}\n")
    f.write(f"genomator ../sources/805_SNP_1000G_real_split_haplotypes2.vcf.gz GENOMATOR_B_{i}_{z}.vcf 1000 0 0 --sample_group_size={i} --exception_space=-{z}\n")
    f.write(f"bgzip GENOMATOR_A_{i}_{z}.vcf -f\n")
    f.write(f"bgzip GENOMATOR_B_{i}_{z}.vcf -f\n")
    f.write(f"tabix GENOMATOR_A_{i}_{z}.vcf.gz\n")
    f.write(f"tabix GENOMATOR_B_{i}_{z}.vcf.gz\n")
    f.write(f"echo GENOMATOR{postpend}_{i}_{z} >> results.txt\n")
    f.write(f"attribute_inference_experiment.py ../sources/805_SNP_1000G_real_split_haplotypes1.vcf.gz ../sources/805_SNP_1000G_real_split_haplotypes2.vcf.gz GENOMATOR_A_{i}_{z}.vcf.gz GENOMATOR_B_{i}_{z}.vcf.gz --silent=True >> results.txt\n")

def mark_run(f,i):
    f.write(f"MARK_run.py ../sources/805_SNP_1000G_real_split_haplotypes1.vcf.gz MARK_A_{i}.vcf 1000 --window_leng={i}\n")
    f.write(f"MARK_run.py ../sources/805_SNP_1000G_real_split_haplotypes2.vcf.gz MARK_B_{i}.vcf 1000 --window_leng={i}\n")
    f.write(f"bgzip MARK_A_{i}.vcf -f\n")
    f.write(f"bgzip MARK_B_{i}.vcf -f\n")
    f.write(f"tabix MARK_A_{i}.vcf.gz\n")
    f.write(f"tabix MARK_B_{i}.vcf.gz\n")
    f.write(f"echo MARK_{i} >> results.txt\n")
    f.write(f"attribute_inference_experiment.py ../sources/805_SNP_1000G_real_split_haplotypes1.vcf.gz ../sources/805_SNP_1000G_real_split_haplotypes2.vcf.gz MARK_A_{i}.vcf.gz MARK_B_{i}.vcf.gz --silent=True >> results.txt\n")

def rbm_run(f,nh,lr):
    f.write(f"RBM_run.py ../sources/805_SNP_1000G_real_split_haplotypes1.vcf.gz RBM_A_{nh}_{lr} 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh={nh} --lr={lr}\n")
    f.write(f"RBM_run.py ../sources/805_SNP_1000G_real_split_haplotypes2.vcf.gz RBM_B_{nh}_{lr} 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh={nh} --lr={lr}\n")
    f.write(f"pickle_to_vcf.py RBM_A_{nh}_{lr}1201.pickle ../sources/805_SNP_1000G_real_split_haplotypes1.vcf.gz RBM_A_{nh}_{lr}.vcf --ploidy=1\n")
    f.write(f"pickle_to_vcf.py RBM_B_{nh}_{lr}1201.pickle ../sources/805_SNP_1000G_real_split_haplotypes2.vcf.gz RBM_B_{nh}_{lr}.vcf --ploidy=1\n")
    f.write(f"bgzip RBM_A_{nh}_{lr}.vcf -f\n")
    f.write(f"bgzip RBM_B_{nh}_{lr}.vcf -f\n")
    f.write(f"tabix RBM_A_{nh}_{lr}.vcf.gz\n")
    f.write(f"tabix RBM_B_{nh}_{lr}.vcf.gz\n")
    f.write(f"echo RBM_{nh}_{lr} >> results.txt\n")
    f.write(f"attribute_inference_experiment.py ../sources/805_SNP_1000G_real_split_haplotypes1.vcf.gz ../sources/805_SNP_1000G_real_split_haplotypes2.vcf.gz RBM_A_{nh}_{lr}.vcf.gz RBM_B_{nh}_{lr}.vcf.gz --silent=True >> results.txt\n")

def crbm_run(f,nh):
    f.write(f"CRBM_run.py ../sources/805_SNP_1000G_real_split_haplotypes1.vcf.gz CRBM_A_{nh} 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh={nh}\n")
    f.write(f"CRBM_run.py ../sources/805_SNP_1000G_real_split_haplotypes2.vcf.gz CRBM_B_{nh} 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh={nh}\n")
    f.write(f"pickle_to_vcf.py CRBM_A_{nh}1201.pickle ../sources/805_SNP_1000G_real_split_haplotypes1.vcf.gz CRBM_A_{nh}.vcf --ploidy=1\n")
    f.write(f"pickle_to_vcf.py CRBM_B_{nh}1201.pickle ../sources/805_SNP_1000G_real_split_haplotypes2.vcf.gz CRBM_B_{nh}.vcf --ploidy=1\n")
    f.write(f"bgzip CRBM_A_{nh}.vcf -f\n")
    f.write(f"bgzip CRBM_B_{nh}.vcf -f\n")
    f.write(f"tabix CRBM_A_{nh}.vcf.gz\n")
    f.write(f"tabix CRBM_B_{nh}.vcf.gz\n")
    f.write(f"echo CRBM_{nh} >> results.txt\n")
    f.write(f"attribute_inference_experiment.py ../sources/805_SNP_1000G_real_split_haplotypes1.vcf.gz ../sources/805_SNP_1000G_real_split_haplotypes2.vcf.gz CRBM_A_{nh}.vcf.gz CRBM_B_{nh}.vcf.gz --silent=True >> results.txt\n")

def gan_run(f,m):
    f.write(f"GAN_run_orig.py ../sources/805_SNP_1000G_real_split_haplotypes1.vcf.gz GAN_A_{m} 1000 --dump_output_interval=20000 --epochs=20010 --layer_multiplier={m}\n")
    f.write(f"GAN_run_orig.py ../sources/805_SNP_1000G_real_split_haplotypes2.vcf.gz GAN_B_{m} 1000 --dump_output_interval=20000 --epochs=20010 --layer_multiplier={m}\n")
    f.write(f"pickle_to_vcf.py GAN_A_{m}20000.pickle ../sources/805_SNP_1000G_real_split_haplotypes1.vcf.gz GAN_A_{m}.vcf --ploidy=1\n")
    f.write(f"pickle_to_vcf.py GAN_B_{m}20000.pickle ../sources/805_SNP_1000G_real_split_haplotypes2.vcf.gz GAN_B_{m}.vcf --ploidy=1\n")
    f.write(f"bgzip GAN_A_{m}.vcf -f\n")
    f.write(f"bgzip GAN_B_{m}.vcf -f\n")
    f.write(f"tabix GAN_A_{m}.vcf.gz\n")
    f.write(f"tabix GAN_B_{m}.vcf.gz\n")
    f.write(f"echo GAN_{m} >> results.txt\n")
    f.write(f"attribute_inference_experiment.py ../sources/805_SNP_1000G_real_split_haplotypes1.vcf.gz ../sources/805_SNP_1000G_real_split_haplotypes2.vcf.gz GAN_A_{m}.vcf.gz GAN_B_{m}.vcf.gz --silent=True >> results.txt\n")


with open("experiment_script.sh","w") as f:
    f.write("rm results.txt\n")
    i_range = list(range(10,50,5))+list(range(50,100,10))+list(range(100,200,20))+list(range(200,401,40))
    for i,z in [(i,(i-10)//5) for i in i_range]:
        postpend=''
        if z==0:
            postpend="-DEFAULT"
        if z==1:
            postpend="-P"
        genomator_run(f,i,z,postpend)
    for i in range(2,51,2):
        mark_run(f,i)
    for nh in range(100,2100,100):
        for lr in [0.01,0.005]:
            rbm_run(f,nh,lr)
    for nh in range(100,2100,100):
        crbm_run(f,nh)
    for m in [i*0.1 for i in range(1,50,3)]:
        gan_run(f,m)

