genomator ../sources/ALL.chr10_and_16.cleaned.vcf.pickle ./GENOMATOR_.pickle 1000 1 1 --looseness=0.99 -exception_space=-1.5 --sample_group_size=150
pickle_to_vcf.py  ./GENOMATOR_.pickle ../sources/ALL.chr10_and_16.cleaned.vcf  ./GENOMATOR_.vcf
stochastic_sanity_checker.py  ../sources/ALL.chr10_and_16.cleaned.vcf  ./GENOMATOR_.vcf
genomator ../sources/ALL.chr10_and_16.cleaned.vcf.pickle  ./GENOMATOR_N10Z0L0.pickle 1000 1 1 --looseness=0 -exception_space=0 --sample_group_size=10
pickle_to_vcf.py  ./GENOMATOR_N10Z0L0.pickle ../sources/ALL.chr10_and_16.cleaned.vcf  ./GENOMATOR_N10Z0L0.vcf
rare_SNP_diagnosis8.py ./GENOMATOR_N10Z0L0.pickle ../sources/ALL.chr10_and_16.cleaned.vcf ./GENOMATOR_.pickle ../sources/ALL.chr10_and_16.cleaned.vcf --degree=4 --trials=10000 --output_image_file=pharmacogenomic_quadruplets_analysis.png > pharmacogenomic_quadruplets.txt
