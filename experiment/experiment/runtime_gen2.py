
# generate scripts for conducting runtime experiments for genomator with scale of number of genomes

from random import randint
from source_gen import *

indices = [
(1,150,1.5,0.99),
(10,150,1.5,0.99),
(100,150,1.5,0.99),
(1000,150,1.5,0.99),
(10000,150,1.5,0.99),
]


line = "genomator     ../sources/chr_filtered_{4}.vcf.gz.pickle dummy_output_GENO{1}{2}{3} {0} 0 0 --sample_group_size={1} --exception_space=-{2} --solver_name=tinicard --difference_samples=100 --noise=0 --involutions=1 --looseness={3} --kull=420 -nb"
header = "virga_header_nerfed"
k = 'GENOMATOR'

import os
os.chdir("runtime_scripts2")

# blank out the runscirpts
with open(f"run_{header.split('_')[0]}.sh","w") as f:
    f.write("")

# outlay all executable scripts
header_string = globals()[header]
with open(f"run_{header.split('_')[0]}.sh","a") as f:
    for n,N,Z,L in indices:
        print(k,n,N,Z,L)
        filename = f"{k}_{n}{N}{Z}{L}.sh"
        with open(filename,"w") as ff:
            ff.write(header_string)
            ff.write(f"echo {n}{k}{N}{Z}{L}\n")
            ff.write("/usr/bin/time -v "+line.format(n,N,Z,L,25600))
        f.write(". sbatch.sh {}\n".format(filename))

