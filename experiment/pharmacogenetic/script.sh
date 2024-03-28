genomator ../sources/ALL.chr10_and_16.cleaned.vcf.pickle GENOMATOR_.pickle 1000 0 0 --solver_name=tinicard -nb --sample_group_size=40 --difference_samples=10000
pickle_to_vcf.py GENOMATOR_.pickle ../sources/ALL.chr10_and_16.cleaned.vcf GENOMATOR_.vcf
