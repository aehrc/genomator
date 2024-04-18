genomator ../sources/AGBL4.vcf.gz GENOMATOR.vcf 1000 1 1
stochastic_sanity_checker.py ../sources/AGBL4.vcf.gz GENOMATOR.vcf
MARK_run.py ../sources/AGBL4.vcf.gz MARK.vcf 1000 --window_leng=30
GAN_run.py ../sources/AGBL4.vcf.gz GAN 1000 --dump_output_interval=300 --epochs=310
RBM_run.py ../sources/AGBL4.vcf.gz RBM 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250
CRBM_run.py ../sources/AGBL4.vcf.gz CRBM 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250

pickle_to_vcf.py GAN300.pickle ../sources/AGBL4.vcf.gz GAN.vcf
pickle_to_vcf.py RBM1201.pickle ../sources/AGBL4.vcf.gz RBM.vcf
pickle_to_vcf.py CRBM1201.pickle ../sources/AGBL4.vcf.gz CRBM.vcf

ld.py ../sources/AGBL4.vcf.gz AGBL4_dataset_ld_REF.png --begin=0 --end=1000
ld.py GENOMATOR.vcf AGBL4_dataset_ld_GENOMATOR.png --begin=0 --end=1000
ld.py MARK.vcf AGBL4_dataset_ld_MARK.png --begin=0 --end=1000
ld.py GAN.vcf AGBL4_dataset_ld_GAN.png --begin=0 --end=1000
ld.py RBM.vcf AGBL4_dataset_ld_RBM.png --begin=0 --end=1000
ld.py CRBM.vcf AGBL4_dataset_ld_CRBM.png --begin=0 --end=1000
