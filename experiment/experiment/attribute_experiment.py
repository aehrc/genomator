
# generate scripts for running attribute_inference experiment for genomator with perturbed parameters

from source_gen import *
out_template = "../attribute/{}.vcf.pickle"

virga_methods = {}

def crbm_run1(f):
  out_file1 = out_template.format("crbm_split1_bigger")
  out_file2 = out_template.format("crbm_split2_bigger")
  f.write(f"/usr/bin/time -v CRBM_run.py {vcf_file_split1_pickle} {out_file1} 120 --fixnodes=5000 --dump_output_interval=20000 --ep_max=20001 --gpu=True\n")
def crbm_run2(f):
  out_file1 = out_template.format("crbm_split1_bigger")
  out_file2 = out_template.format("crbm_split2_bigger")
  f.write(f"/usr/bin/time -v CRBM_run.py {vcf_file_split2_pickle} {out_file2} 120 --fixnodes=5000 --dump_output_interval=20000 --ep_max=20001 --gpu=True\n")
virga_methods[crbm_run1.__name__] = crbm_run1
virga_methods[crbm_run2.__name__] = crbm_run2

def wgan_run1(f):
  out_file1 = out_template.format("wgan_split1_bigger")
  out_file2 = out_template.format("wgan_split2_bigger")
  f.write(f"/usr/bin/time -v WGAN_run.py {vcf_file_split1_pickle} {out_file1} 120 --dump_output_interval=3500 --epochs=3501\n")
def wgan_run2(f):
  out_file1 = out_template.format("wgan_split1_bigger")
  out_file2 = out_template.format("wgan_split2_bigger")
  f.write(f"/usr/bin/time -v WGAN_run.py {vcf_file_split2_pickle} {out_file2} 120 --dump_output_interval=3500 --epochs=3501\n")
virga_methods[wgan_run1.__name__] = wgan_run1
virga_methods[wgan_run2.__name__] = wgan_run2


petrichor_methods = {}

def mark_run(f,i):
  out_file1 = out_template.format(f"mark_split1_{i}")
  out_file2 = out_template.format(f"mark_split2_{i}")
  f.write(f"/usr/bin/time -v MARK_run.py {vcf_file_split1_pickle} {out_file1} 120 --window_leng={i} \n")
  f.write(f"/usr/bin/time -v MARK_run.py {vcf_file_split2_pickle} {out_file2} 120 --window_leng={i} \n")
petrichor_methods[mark_run.__name__] = mark_run

nerfed_virga_methods = {}

def genomator_run(f,i,z,n,ii,solver,looseness,postpend=""):
  out_file1 = out_template.format(f"genomator_split1_{i}_{z}_{n}_{ii}_{solver}_{looseness}_{postpend}")
  out_file2 = out_template.format(f"genomator_split2_{i}_{z}_{n}_{ii}_{solver}_{looseness}_{postpend}")
  f.write(f"/usr/bin/time -v genomator {vcf_file_split1_pickle} {out_file1} 120 0 0 --sample_group_size={i} --exception_space=-{z} --solver_name={solver} --difference_samples=10000 --noise={n} --involutions={ii} --looseness={looseness}\n")
  f.write(f"/usr/bin/time -v genomator {vcf_file_split2_pickle} {out_file2} 120 0 0 --sample_group_size={i} --exception_space=-{z} --solver_name={solver} --difference_samples=10000 --noise={n} --involutions={ii} --looseness={looseness}\n")
nerfed_virga_methods[genomator_run.__name__] = genomator_run


petrichor_experiments = []
i_range =  [10,50,90,130,170,210,250,290,330,370,410,450,490,530,570,610,650,690]
for ii,i in enumerate(i_range):
    petrichor_experiments.append(['mark_run',i])

nerfed_virga_experiments = []
for s in [50,75,100,125,150,175,200,225,250]:
    z = s*1.0/100
    l=0.99
    nerfed_virga_experiments.append(["genomator_run",s,z,0,1,"tinicard",l,""])


virga_experiments = []
virga_experiments.append(["crbm_run1"])
virga_experiments.append(["crbm_run2"])
virga_experiments.append(["wgan_run1"])
virga_experiments.append(["wgan_run2"])


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

