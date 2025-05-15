from source_gen import *
out_template = "../attribute_larger/{}.vcf.pickle"

virga_methods = {}
def crbm_run1(f):
  out_file1 = out_template.format("crbm_split1_bigger")
  f.write(f"/usr/bin/time -v CRBM_run.py {vcf_file_split1_pickle} {out_file1} 2500 --fixnodes=5000 --dump_output_interval=20000 --ep_max=20001 --gpu=True\n")
virga_methods[crbm_run1.__name__] = crbm_run1
def wgan_run1(f):
  out_file1 = out_template.format("wgan_split1_bigger")
  out_file2 = out_template.format("wgan_split2_bigger")
  f.write(f"/usr/bin/time -v WGAN_run.py {vcf_file_split1_pickle} {out_file1} 2500 --dump_output_interval=3500 --epochs=3501\n")
virga_methods[wgan_run1.__name__] = wgan_run1

petrichor_methods = {}
def mark_run(f,i):
  out_file1 = out_template.format(f"mark_split1_{i}_bigger")
  f.write(f"/usr/bin/time -v MARK_run.py {vcf_file_split1_pickle} {out_file1} 2500 --window_leng={i} \n")
petrichor_methods[mark_run.__name__] = mark_run

nerfed_virga_methods = {}
def genomator_run(f,i,z,n,ii,solver,looseness,postpend=""):
  out_file1 = out_template.format(f"genomator_split1_{i}_{z}_{n}_{ii}_{solver}_{looseness}_{postpend}")
  f.write(f"/usr/bin/time -v genomator {vcf_file_split1_pickle} {out_file1} 2500 0 0 --sample_group_size={i} --exception_space=-{z} --solver_name={solver} --difference_samples=10000 --noise={n} --involutions={ii} --looseness={looseness}\n")
nerfed_virga_methods[genomator_run.__name__] = genomator_run


petrichor_experiments = []
petrichor_experiments.append(['mark_run',330])

nerfed_virga_experiments = []
s=150
z = s*1.0/100
l=0.99
nerfed_virga_experiments.append(["genomator_run",s,z,0,1,"tinicard",l,"bigger"])


virga_experiments = []
virga_experiments.append(["crbm_run1"])
virga_experiments.append(["wgan_run1"])


script_prepend = "./attribute_scripts/{}"

with open(script_prepend.format("petrichor_run.sh"),'w') as petrichor_f:
    for e in petrichor_experiments:
        filename = "_".join([str(ee) for ee in e]) + ".sh"
        with open(script_prepend.format(filename),"w") as f:
            f.write(petrichor_header)
            petrichor_methods[e[0]](*([f]+e[1:]))
        petrichor_f.write(f". sbatch.sh {filename}\n")
with open(script_prepend.format("virga_run.sh"),'w') as virga_f:
    for e in virga_experiments:
        filename = "_".join([str(ee) for ee in e]) + ".sh"
        with open(script_prepend.format(filename),"w") as f:
            f.write(virga_header)
            virga_methods[e[0]](*([f]+e[1:]))
        virga_f.write(f". sbatch.sh {filename}\n")
    for e in nerfed_virga_experiments:
        filename = "_".join([str(ee) for ee in e]) + ".sh"
        with open(script_prepend.format(filename),"w") as f:
            f.write(virga_header_nerfed)
            nerfed_virga_methods[e[0]](*([f]+e[1:]))
        virga_f.write(f". sbatch.sh {filename}\n")

