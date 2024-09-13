
genomator ../sources/AGBL4.vcf.gz GENOMATOR_10_0.vcf 1000 1 1 --sample_group_size=10 --exception_space=0 --max_restarts=-1
genomator ../sources/AGBL4.vcf.gz GENOMATOR_15_1.vcf 1000 1 1 --sample_group_size=15 --exception_space=-1.0 --max_restarts=-1
genomator ../sources/AGBL4.vcf.gz GENOMATOR_20_2.vcf 1000 1 1 --sample_group_size=20 --exception_space=-2.0 --max_restarts=-1
genomator ../sources/AGBL4.vcf.gz GENOMATOR_25_3.vcf 1000 1 1 --sample_group_size=25 --exception_space=-3.0 --max_restarts=-1
genomator ../sources/AGBL4.vcf.gz GENOMATOR_30_4.vcf 1000 1 1 --sample_group_size=30 --exception_space=-4.0 --max_restarts=-1
genomator ../sources/AGBL4.vcf.gz GENOMATOR_35_5.vcf 1000 1 1 --sample_group_size=35 --exception_space=-5.0 --max_restarts=-1
genomator ../sources/AGBL4.vcf.gz GENOMATOR_40_6.vcf 1000 1 1 --sample_group_size=40 --exception_space=-6.0 --max_restarts=-1

stochastic_sanity_checker.py  ../sources/AGBL4.vcf.gz GENOMATOR_10_0.vcf
stochastic_sanity_checker.py  ../sources/AGBL4.vcf.gz GENOMATOR_15_1.vcf
stochastic_sanity_checker.py  ../sources/AGBL4.vcf.gz GENOMATOR_20_2.vcf
stochastic_sanity_checker.py  ../sources/AGBL4.vcf.gz GENOMATOR_25_3.vcf
stochastic_sanity_checker.py  ../sources/AGBL4.vcf.gz GENOMATOR_30_4.vcf
stochastic_sanity_checker.py  ../sources/AGBL4.vcf.gz GENOMATOR_35_5.vcf
stochastic_sanity_checker.py  ../sources/AGBL4.vcf.gz GENOMATOR_40_6.vcf

MARK_run.py ../sources/AGBL4.vcf.gz MARKOV_20.vcf 1000 --window_leng=20
MARK_run.py ../sources/AGBL4.vcf.gz MARKOV_40.vcf 1000 --window_leng=40
MARK_run.py ../sources/AGBL4.vcf.gz MARKOV_60.vcf 1000 --window_leng=60
MARK_run.py ../sources/AGBL4.vcf.gz MARKOV_80.vcf 1000 --window_leng=80
MARK_run.py ../sources/AGBL4.vcf.gz MARKOV_100.vcf 1000 --window_leng=100
MARK_run.py ../sources/AGBL4.vcf.gz MARKOV_120.vcf 1000 --window_leng=120
MARK_run.py ../sources/AGBL4.vcf.gz MARKOV_140.vcf 1000 --window_leng=140
MARK_run.py ../sources/AGBL4.vcf.gz MARKOV_160.vcf 1000 --window_leng=160
MARK_run.py ../sources/AGBL4.vcf.gz MARKOV_180.vcf 1000 --window_leng=180
MARK_run.py ../sources/AGBL4.vcf.gz MARKOV_200.vcf 1000 --window_leng=200
GAN_run_orig.py ../sources/AGBL4.vcf.gz GAN_A 1000 --dump_output_interval=20000 --epochs=20010 --layer_multiplier=1.0
GAN_run_orig.py ../sources/AGBL4.vcf.gz GAN_B 1000 --dump_output_interval=20000 --epochs=20010 --layer_multiplier=0.7
GAN_run_orig.py ../sources/AGBL4.vcf.gz GAN_C 1000 --dump_output_interval=20000 --epochs=20010 --layer_multiplier=1.3
GAN_run_orig.py ../sources/AGBL4.vcf.gz GAN_D 1000 --dump_output_interval=20000 --epochs=20010 --layer_multiplier=1.6
RBM_run.py ../sources/AGBL4.vcf.gz RBM_A 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=500 --lr=0.01
RBM_run.py ../sources/AGBL4.vcf.gz RBM_B 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=700 --lr=0.01
RBM_run.py ../sources/AGBL4.vcf.gz RBM_C 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=500 --lr=0.005
RBM_run.py ../sources/AGBL4.vcf.gz RBM_D 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=700 --lr=0.005
CRBM_run.py ../sources/AGBL4.vcf.gz CRBM_A 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=500 --fixnodes=300
CRBM_run.py ../sources/AGBL4.vcf.gz CRBM_B 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=500 --fixnodes=400
CRBM_run.py ../sources/AGBL4.vcf.gz CRBM_C 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=700 --fixnodes=300
CRBM_run.py ../sources/AGBL4.vcf.gz CRBM_D 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=700 --fixnodes=400

pickle_to_vcf.py GAN_A20000.pickle ../sources/AGBL4.vcf.gz GAN_A.vcf
pickle_to_vcf.py GAN_B20000.pickle ../sources/AGBL4.vcf.gz GAN_B.vcf
pickle_to_vcf.py GAN_C20000.pickle ../sources/AGBL4.vcf.gz GAN_C.vcf
pickle_to_vcf.py GAN_D20000.pickle ../sources/AGBL4.vcf.gz GAN_D.vcf

pickle_to_vcf.py RBM_A1201.pickle ../sources/AGBL4.vcf.gz RBM_A.vcf
pickle_to_vcf.py RBM_B1201.pickle ../sources/AGBL4.vcf.gz RBM_B.vcf
pickle_to_vcf.py RBM_C1201.pickle ../sources/AGBL4.vcf.gz RBM_C.vcf
pickle_to_vcf.py RBM_D1201.pickle ../sources/AGBL4.vcf.gz RBM_D.vcf

pickle_to_vcf.py CRBM_A1201.pickle ../sources/AGBL4.vcf.gz CRBM_A.vcf
pickle_to_vcf.py CRBM_B1201.pickle ../sources/AGBL4.vcf.gz CRBM_B.vcf
pickle_to_vcf.py CRBM_C1201.pickle ../sources/AGBL4.vcf.gz CRBM_C.vcf
pickle_to_vcf.py CRBM_D1201.pickle ../sources/AGBL4.vcf.gz CRBM_D.vcf

python analyse.py
