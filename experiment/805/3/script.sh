genomator ../../sources/805_SNP_1000G_real_haplotypes.vcf.gz GENOMATOR.vcf 1000 1 1
stochastic_sanity_checker.py ../../sources/805_SNP_1000G_real_haplotypes.vcf.gz GENOMATOR.vcf
MARK_run.py ../../sources/805_SNP_1000G_real_haplotypes.vcf.gz MARK.vcf 1000 --window_leng=10
GAN_run_orig.py ../../sources/805_SNP_1000G_real_haplotypes.vcf.gz GAN 1000 --dump_output_interval=20000 --epochs=20010
RBM_run.py ../../sources/805_SNP_1000G_real_haplotypes.vcf.gz RBM 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250
CRBM_run.py ../../sources/805_SNP_1000G_real_haplotypes.vcf.gz CRBM 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250

pickle_to_vcf.py GAN20000.pickle ../../sources/805_SNP_1000G_real_haplotypes.vcf.gz GAN.vcf --ploidy=1
pickle_to_vcf.py RBM1201.pickle ../../sources/805_SNP_1000G_real_haplotypes.vcf.gz RBM.vcf --ploidy=1
pickle_to_vcf.py CRBM1201.pickle ../../sources/805_SNP_1000G_real_haplotypes.vcf.gz CRBM.vcf --ploidy=1

pca_plot_genomes_vcf2.py ../../sources/805_SNP_1000G_real_haplotypes.vcf.gz GENOMATOR.vcf GENOMATOR.png
pca_plot_genomes_vcf2.py ../../sources/805_SNP_1000G_real_haplotypes.vcf.gz MARK.vcf MARK.png
pca_plot_genomes_vcf2.py ../../sources/805_SNP_1000G_real_haplotypes.vcf.gz GAN.vcf GAN.png
pca_plot_genomes_vcf2.py ../../sources/805_SNP_1000G_real_haplotypes.vcf.gz RBM.vcf RBM.png
pca_plot_genomes_vcf2.py ../../sources/805_SNP_1000G_real_haplotypes.vcf.gz CRBM.vcf CRBM.png

wasserstein_analyse_pca.py ../../sources/805_SNP_1000G_real_haplotypes.vcf.gz GAN.vcf > GAN_results_pca.txt 2>&1
wasserstein_analyse_pca.py ../../sources/805_SNP_1000G_real_haplotypes.vcf.gz GENOMATOR.vcf > GENOMATOR_results_pca.txt 2>&1
wasserstein_analyse_pca.py ../../sources/805_SNP_1000G_real_haplotypes.vcf.gz MARK.vcf > MARK_results_pca.txt 2>&1
wasserstein_analyse_pca.py ../../sources/805_SNP_1000G_real_haplotypes.vcf.gz RBM.vcf > RBM_results_pca.txt 2>&1
wasserstein_analyse_pca.py ../../sources/805_SNP_1000G_real_haplotypes.vcf.gz CRBM.vcf > CRBM_results_pca.txt 2>&1
