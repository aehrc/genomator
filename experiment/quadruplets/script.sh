genomator ../sources/AGBL4.vcf.gz GENOMATOR_10.vcf 1000 1 1
stochastic_sanity_checker.py  ../sources/AGBL4.vcf.gz GENOMATOR_10.vcf
genomator ../sources/AGBL4.vcf.gz GENOMATOR-P_.vcf 1000 1 1 --sample_group_size=30 --exception_space=1
stochastic_sanity_checker.py  ../sources/AGBL4.vcf.gz GENOMATOR-P_.vcf
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
GAN_run.py ../sources/AGBL4.vcf.gz GAN_A 1000 --dump_output_interval=300 --epochs=310 --base_layer_size=500
GAN_run.py ../sources/AGBL4.vcf.gz GAN_B 1000 --dump_output_interval=300 --epochs=310 --base_layer_size=600
GAN_run.py ../sources/AGBL4.vcf.gz GAN_C 1000 --dump_output_interval=300 --epochs=310 --base_layer_size=700
GAN_run.py ../sources/AGBL4.vcf.gz GAN_D 1000 --dump_output_interval=300 --epochs=310 --base_layer_size=800
RBM_run.py ../sources/AGBL4.vcf.gz RBM_A 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=500 --lr=0.01
RBM_run.py ../sources/AGBL4.vcf.gz RBM_B 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=700 --lr=0.01
RBM_run.py ../sources/AGBL4.vcf.gz RBM_C 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=500 --lr=0.005
RBM_run.py ../sources/AGBL4.vcf.gz RBM_D 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=700 --lr=0.005
CRBM_run.py ../sources/AGBL4.vcf.gz CRBM_A 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=500 --fixnodes=300
CRBM_run.py ../sources/AGBL4.vcf.gz CRBM_B 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=500 --fixnodes=400
CRBM_run.py ../sources/AGBL4.vcf.gz CRBM_C 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=700 --fixnodes=300
CRBM_run.py ../sources/AGBL4.vcf.gz CRBM_D 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=700 --fixnodes=400

pickle_to_vcf.py GAN_A300.pickle ../sources/AGBL4.vcf.gz GAN_A.vcf
pickle_to_vcf.py GAN_B300.pickle ../sources/AGBL4.vcf.gz GAN_B.vcf
pickle_to_vcf.py GAN_C300.pickle ../sources/AGBL4.vcf.gz GAN_C.vcf
pickle_to_vcf.py GAN_D300.pickle ../sources/AGBL4.vcf.gz GAN_D.vcf

pickle_to_vcf.py RBM_A1201.pickle ../sources/AGBL4.vcf.gz RBM_A.vcf
pickle_to_vcf.py RBM_B1201.pickle ../sources/AGBL4.vcf.gz RBM_B.vcf
pickle_to_vcf.py RBM_C1201.pickle ../sources/AGBL4.vcf.gz RBM_C.vcf
pickle_to_vcf.py RBM_D1201.pickle ../sources/AGBL4.vcf.gz RBM_D.vcf

pickle_to_vcf.py CRBM_A1201.pickle ../sources/AGBL4.vcf.gz CRBM_A.vcf
pickle_to_vcf.py CRBM_B1201.pickle ../sources/AGBL4.vcf.gz CRBM_B.vcf
pickle_to_vcf.py CRBM_C1201.pickle ../sources/AGBL4.vcf.gz CRBM_C.vcf
pickle_to_vcf.py CRBM_D1201.pickle ../sources/AGBL4.vcf.gz CRBM_D.vcf

python analyse.py
