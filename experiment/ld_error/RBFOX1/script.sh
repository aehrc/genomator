genomator ../../sources/RBFOX1_split1.vcf.gz GENOMATOR.vcf 1000 1 1
stochastic_sanity_checker.py  ../../sources/RBFOX1_split1.vcf.gz GENOMATOR.vcf
MARK_run.py ../../sources/RBFOX1_split1.vcf.gz MARKOV.vcf 1000 --window_leng=10
GAN_run_orig.py ../../sources/RBFOX1_split1.vcf.gz GAN 1000 --dump_output_interval=20000 --epochs=20010
RBM_run.py ../../sources/RBFOX1_split1.vcf.gz RBM 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250
CRBM_run.py ../../sources/RBFOX1_split1.vcf.gz CRBM 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250

pickle_to_vcf.py GAN20000.pickle ../../sources/RBFOX1_split1.vcf.gz GAN.vcf
pickle_to_vcf.py RBM1201.pickle ../../sources/RBFOX1_split1.vcf.gz RBM.vcf
pickle_to_vcf.py CRBM1201.pickle ../../sources/RBFOX1_split1.vcf.gz CRBM.vcf

ld14.py ../../sources/RBFOX1_split2.vcf.gz CRBM.vcf GAN.vcf GENOMATOR.vcf MARKOV.vcf RBM.vcf --max_offset=500 --max_y_limit=0.025 --chunk_size=15
echo results > results.txt
ld_window_analysis.py ../../sources/RBFOX1_split2.vcf.gz CRBM.vcf GAN.vcf GENOMATOR.vcf MARKOV.vcf RBM.vcf --max_offset=500 --max_y_limit=0.045 --chunk_size=15 --output_image_file=LD_window.png >> results.txt
ld11.py ../../sources/RBFOX1_split2.vcf.gz >> results.txt
echo average >> results.txt
ld10.py ../../sources/RBFOX1_split2.vcf.gz CRBM.vcf GAN.vcf GENOMATOR.vcf MARKOV.vcf RBM.vcf >> results.txt
echo correlation >> results.txt
get_correlation.py ../../sources/RBFOX1_split2.vcf.gz CRBM.vcf >> results.txt
get_correlation.py ../../sources/RBFOX1_split2.vcf.gz GAN.vcf >> results.txt
get_correlation.py ../../sources/RBFOX1_split2.vcf.gz GENOMATOR.vcf >> results.txt
get_correlation.py ../../sources/RBFOX1_split2.vcf.gz MARKOV.vcf >> results.txt
get_correlation.py ../../sources/RBFOX1_split2.vcf.gz RBM.vcf >> results.txt

