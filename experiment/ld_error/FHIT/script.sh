genomator ../../sources/FHIT_split1.vcf GENOMATOR.vcf 1000 1 1
stochastic_sanity_checker.py  ../../sources/FHIT_split1.vcf GENOMATOR.vcf
MARK_run.py ../../sources/FHIT_split1.vcf MARKOV.vcf 1000 --window_leng=10
GAN_run_orig.py ../../sources/FHIT_split1.vcf GAN 1000 --dump_output_interval=20000 --epochs=20010
RBM_run.py ../../sources/FHIT_split1.vcf RBM 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250
CRBM_run.py ../../sources/FHIT_split1.vcf CRBM 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250

pickle_to_vcf.py GAN20000.pickle ../../sources/FHIT_split1.vcf GAN.vcf
pickle_to_vcf.py RBM1201.pickle ../../sources/FHIT_split1.vcf RBM.vcf
pickle_to_vcf.py CRBM1201.pickle ../../sources/FHIT_split1.vcf CRBM.vcf

ld14.py ../../sources/FHIT_split2.vcf CRBM.vcf GAN.vcf GENOMATOR.vcf MARKOV.vcf RBM.vcf --max_offset=500 --max_y_limit=0.025 --chunk_size=15
echo results > results.txt
ld_window_analysis.py ../../sources/FHIT_split2.vcf CRBM.vcf GAN.vcf GENOMATOR.vcf MARKOV.vcf RBM.vcf --max_offset=500 --max_y_limit=0.045 --chunk_size=15 --output_image_file=LD_window.png >> results.txt
ld11.py ../../sources/FHIT_split2.vcf >> results.txt
echo average >> results.txt
ld10.py ../../sources/FHIT_split2.vcf CRBM.vcf GAN.vcf GENOMATOR.vcf MARKOV.vcf RBM.vcf >> results.txt
echo correlation >> results.txt
get_correlation.py ../../sources/FHIT_split2.vcf CRBM.vcf >> results.txt
get_correlation.py ../../sources/FHIT_split2.vcf GAN.vcf >> results.txt
get_correlation.py ../../sources/FHIT_split2.vcf GENOMATOR.vcf >> results.txt
get_correlation.py ../../sources/FHIT_split2.vcf MARKOV.vcf >> results.txt
get_correlation.py ../../sources/FHIT_split2.vcf RBM.vcf >> results.txt

