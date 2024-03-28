genomator ../../sources/805_SNP_1000G_real.vcf GENOMATOR.vcf 1000 1 1
MARK_run.py ../../sources/805_SNP_1000G_real.vcf MARK.vcf 1000 --window_leng=30
GAN_run.py ../../sources/805_SNP_1000G_real.vcf GAN 1000 --dump_output_interval=300 --epochs=310
RBM_run.py ../../sources/805_SNP_1000G_real.vcf RBM 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250
CRBM_run.py ../../sources/805_SNP_1000G_real.vcf CRBM 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250

pickle_to_vcf.py GAN300.pickle ../../sources/805_SNP_1000G_real.vcf GAN.vcf
pickle_to_vcf.py RBM1201.pickle ../../sources/805_SNP_1000G_real.vcf RBM.vcf
pickle_to_vcf.py CRBM1201.pickle ../../sources/805_SNP_1000G_real.vcf CRBM.vcf

pca_plot_genomes_vcf2.py ../../sources/805_SNP_1000G_real.vcf GENOMATOR.vcf GENOMATOR.png
pca_plot_genomes_vcf2.py ../../sources/805_SNP_1000G_real.vcf MARK.vcf MARK.png
pca_plot_genomes_vcf2.py ../../sources/805_SNP_1000G_real.vcf GAN.vcf GAN.png
pca_plot_genomes_vcf2.py ../../sources/805_SNP_1000G_real.vcf RBM.vcf RBM.png
pca_plot_genomes_vcf2.py ../../sources/805_SNP_1000G_real.vcf CRBM.vcf CRBM.png

wasserstein_analyse.py ../../sources/805_SNP_1000G_real.vcf GAN.vcf > GAN_results.txt 2>&1
wasserstein_analyse.py ../../sources/805_SNP_1000G_real.vcf GENOMATOR.vcf > GENOMATOR_results.txt 2>&1
wasserstein_analyse.py ../../sources/805_SNP_1000G_real.vcf MARK.vcf > MARK_results.txt 2>&1
wasserstein_analyse.py ../../sources/805_SNP_1000G_real.vcf RBM.vcf > RBM_results.txt 2>&1
wasserstein_analyse.py ../../sources/805_SNP_1000G_real.vcf CRBM.vcf > CRBM_results.txt 2>&1

wasserstein_analyse_pca.py ../../sources/805_SNP_1000G_real.vcf GAN.vcf > GAN_results_pca.txt 2>&1
wasserstein_analyse_pca.py ../../sources/805_SNP_1000G_real.vcf GENOMATOR.vcf > GENOMATOR_results_pca.txt 2>&1
wasserstein_analyse_pca.py ../../sources/805_SNP_1000G_real.vcf MARK.vcf > MARK_results_pca.txt 2>&1
wasserstein_analyse_pca.py ../../sources/805_SNP_1000G_real.vcf RBM.vcf > RBM_results_pca.txt 2>&1
wasserstein_analyse_pca.py ../../sources/805_SNP_1000G_real.vcf CRBM.vcf > CRBM_results_pca.txt 2>&1
