

# generate scripts for running attribute_inference experiment for genomator with perturbed parameters

from source_gen import *
out_template = "../attribute_perturbation/{}.vcf.pickle"


nerfed_virga_methods = {}

def genomator_run(f,i,z,n,ii,solver,looseness,postpend=""):
  out_file1 = out_template.format(f"genomator_split1_{i}_{z}_{n}_{ii}_{solver}_{looseness}_{postpend}")
  out_file2 = out_template.format(f"genomator_split2_{i}_{z}_{n}_{ii}_{solver}_{looseness}_{postpend}")
  f.write(f"/usr/bin/time -v genomator {vcf_file_split1_pickle} {out_file1} 120 0 0 --sample_group_size={i} --exception_space=-{z} --solver_name={solver} --difference_samples=10000 --noise={n} --involutions={ii} --looseness={looseness}\n")
  f.write(f"/usr/bin/time -v genomator {vcf_file_split2_pickle} {out_file2} 120 0 0 --sample_group_size={i} --exception_space=-{z} --solver_name={solver} --difference_samples=10000 --noise={n} --involutions={ii} --looseness={looseness}\n")
nerfed_virga_methods[genomator_run.__name__] = genomator_run


nerfed_virga_experiments = []
parameters = [
        (150,1.5,0.99),

        (180,1.5,0.99),
        (210,1.5,0.99),
        (120,1.5,0.99),
        ( 90,1.5,0.99),

        (150,1.7,0.99),
        (150,1.9,0.99),
        (150,1.3,0.99),
        (150,1.1,0.99),

        (150,1.5,0.994),
        (150,1.5,0.998),
        (150,1.5,0.986),
        (150,1.5,0.982),
    ]
for s,z,l in parameters:
    nerfed_virga_experiments.append(["genomator_run",s,z,0,1,"tinicard",l,""])




script_prepend = "./attribute_scripts/{}"

with open(script_prepend.format("virga_run.sh"),'w') as virga_f:
    for e in nerfed_virga_experiments:
        filename = "_".join([str(ee) for ee in e]) + ".sh"
        with open(script_prepend.format(filename),"w") as f:
            f.write(virga_header_nerfed)
            nerfed_virga_methods[e[0]](*([f]+e[1:]))
        virga_f.write(f". sbatch.sh {filename}\n")

