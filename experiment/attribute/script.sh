genomator ../sources/805_SNP_1000G_real_split1.vcf.gz GENOMATOR_A.vcf 1000 1 1
MARK_run.py ../sources/805_SNP_1000G_real_split1.vcf.gz MARK_A.vcf 1000 --window_leng=30
GAN_run.py ../sources/805_SNP_1000G_real_split1.vcf.gz GAN_A 1000 --dump_output_interval=300 --epochs=310 --base_layer_size=500
RBM_run.py ../sources/805_SNP_1000G_real_split1.vcf.gz RBM_A 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=500 --lr=0.01
CRBM_run.py ../sources/805_SNP_1000G_real_split1.vcf.gz CRBM_A 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=500 --fixnodes=300

genomator ../sources/805_SNP_1000G_real_split2.vcf.gz GENOMATOR_B.vcf 1000 1 1
MARK_run.py ../sources/805_SNP_1000G_real_split2.vcf.gz MARK_B.vcf 1000 --window_leng=30
GAN_run.py ../sources/805_SNP_1000G_real_split2.vcf.gz GAN_B 1000 --dump_output_interval=300 --epochs=310 --base_layer_size=500
RBM_run.py ../sources/805_SNP_1000G_real_split2.vcf.gz RBM_B 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=500 --lr=0.01
CRBM_run.py ../sources/805_SNP_1000G_real_split2.vcf.gz CRBM_B 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=500 --fixnodes=300

pickle_to_vcf.py GAN_A300.pickle ../sources/805_SNP_1000G_real_split1.vcf.gz GAN_A.vcf
pickle_to_vcf.py RBM_A1201.pickle ../sources/805_SNP_1000G_real_split1.vcf.gz RBM_A.vcf
pickle_to_vcf.py CRBM_A1201.pickle ../sources/805_SNP_1000G_real_split1.vcf.gz CRBM_A.vcf

pickle_to_vcf.py GAN_B300.pickle ../sources/805_SNP_1000G_real_split2.vcf.gz GAN_B.vcf
pickle_to_vcf.py RBM_B1201.pickle ../sources/805_SNP_1000G_real_split2.vcf.gz RBM_B.vcf
pickle_to_vcf.py CRBM_B1201.pickle ../sources/805_SNP_1000G_real_split2.vcf.gz CRBM_B.vcf

echo Attribute Inference Experiment > results.txt
echo GAN >> results.txt
attribute_inference_experiment.py ../sources/805_SNP_1000G_real_split1.vcf.gz ../sources/805_SNP_1000G_real_split2.vcf.gz GAN_A.vcf GAN_B.vcf >> results.txt 2>&1
echo GENOMATOR >> results.txt
attribute_inference_experiment.py ../sources/805_SNP_1000G_real_split1.vcf.gz ../sources/805_SNP_1000G_real_split2.vcf.gz GENOMATOR_A.vcf GENOMATOR_B.vcf >> results.txt 2>&1
echo MARK >> results.txt
attribute_inference_experiment.py ../sources/805_SNP_1000G_real_split1.vcf.gz ../sources/805_SNP_1000G_real_split2.vcf.gz MARK_A.vcf MARK_B.vcf >> results.txt 2>&1
echo RBM >> results.txt
attribute_inference_experiment.py ../sources/805_SNP_1000G_real_split1.vcf.gz ../sources/805_SNP_1000G_real_split2.vcf.gz RBM_A.vcf RBM_B.vcf >> results.txt 2>&1
echo CRBM >> results.txt
attribute_inference_experiment.py ../sources/805_SNP_1000G_real_split1.vcf.gz ../sources/805_SNP_1000G_real_split2.vcf.gz CRBM_A.vcf CRBM_B.vcf >> results.txt 2>&1
