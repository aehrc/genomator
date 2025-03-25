from random import randint
indices = [4**i*100 for i in range(9)] + ['']

from source_gen import *

methods = {
  "CRBM":     ("CRBM_run.py   ../sources/chr_filtered_{0}.vcf.gz.pickle dummy_output_CRBM{0} 1 --fixnodes=5000 --dump_output_interval=20000 --ep_max=20001 --gpu=True","virga_header"),
  "WGAN":     ("WGAN_run.py   ../sources/chr_filtered_{0}.vcf.gz.pickle dummy_output_WGAN{0} 1 --dump_output_interval=3500 --epochs=3501","virga_header"),
  "MARK":     ("MARK_run.py  ../sources/chr_filtered_{0}.vcf.gz.pickle dummy_output_MARK{0} 1 --window_leng=330","petrichor_header"),
  "GENOMATOR":("genomator     ../sources/chr_filtered_{0}.vcf.gz.pickle dummy_output_GENO{0} 1 0 0 --sample_group_size=150 --exception_space=-1.5 --solver_name=tinicard --difference_samples=100 --noise=0 --involutions=1 --looseness=0.99","virga_header_nerfed")
}


import os
os.chdir("runtime_scripts")

# blank out the runscirpts
for k in methods.keys():
    line,header = methods[k]
    with open(f"run_{header.split('_')[0]}.sh","w") as f:
        f.write("")

# outlay all executable scripts
for k in methods.keys():
    line,header = methods[k]
    header_string = globals()[header]
    with open(f"run_{header.split('_')[0]}.sh","a") as f:
        for index in indices:
            print(k,index)
            filename = "{}_{}.sh".format(k,index)
            with open(filename,"w") as ff:
                ff.write(header_string)
                ff.write("echo {}{}\n".format(k,index))
                ff.write("/usr/bin/time -v "+line.format(index))
            f.write("sbatch {}\n".format(filename))

