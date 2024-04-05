genomator ../../sources/AGBL4.vcf.gz GENOMATOR.vcf 1000 1 1
MARK_run.py ../../sources/AGBL4.vcf.gz MARKOV.vcf 1000 --window_leng=30
GAN_run.py ../../sources/AGBL4.vcf.gz GAN 1000 --dump_output_interval=300 --epochs=310
RBM_run.py ../../sources/AGBL4.vcf.gz RBM 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250
CRBM_run.py ../../sources/AGBL4.vcf.gz CRBM 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250

pickle_to_vcf.py GAN300.pickle ../../sources/AGBL4.vcf.gz GAN.vcf
pickle_to_vcf.py RBM1201.pickle ../../sources/AGBL4.vcf.gz RBM.vcf
pickle_to_vcf.py CRBM1201.pickle ../../sources/AGBL4.vcf.gz CRBM.vcf

ld14.py ../../sources/AGBL4.vcf.gz CRBM.vcf GAN.vcf GENOMATOR.vcf MARKOV.vcf RBM.vcf --max_offset=500 --max_y_limit=0.025 --chunk_size=15
echo results > results.txt
ld_window_analysis.py ../../sources/AGBL4.vcf.gz CRBM.vcf GAN.vcf GENOMATOR.vcf MARKOV.vcf RBM.vcf --max_offset=500 --max_y_limit=0.025 --chunk_size=15 --output_image_file=LD_window.png >> results.txt
ld11.py ../../sources/AGBL4.vcf.gz >> results.txt
echo average >> results.txt
ld10.py ../../sources/AGBL4.vcf.gz CRBM.vcf GAN.vcf GENOMATOR.vcf MARKOV.vcf RBM.vcf >> results.txt
echo correlation >> results.txt
get_correlation.py ../../sources/AGBL4.vcf.gz CRBM.vcf >> results.txt
get_correlation.py ../../sources/AGBL4.vcf.gz GAN.vcf >> results.txt
get_correlation.py ../../sources/AGBL4.vcf.gz GENOMATOR.vcf >> results.txt
get_correlation.py ../../sources/AGBL4.vcf.gz MARKOV.vcf >> results.txt
get_correlation.py ../../sources/AGBL4.vcf.gz RBM.vcf >> results.txt

