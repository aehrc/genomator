from source_gen import *

petrichor_header = '''#!/bin/bash
#SBATCH --time=48:00:00
#SBATCH --mem=80GB
#SBATCH --ntasks-per-node=1
#SBATCH --account=OD-224204
module add python
source /datasets/work/hb-spiked-genome/work/marks_combine_code_test3/env/bin/activate

'''
virga_header = '''#!/bin/bash
#SBATCH --time=48:00:00
#SBATCH --mem=80GB
#SBATCH --ntasks-per-node=1
#SBATCH --account=OD-224204
#SBATCH --gres=gpu:1
module add python
module add cuda
module add tensorflow
source /datasets/work/hb-spiked-genome/work/marks_combine_code_test3/env/bin/activate

'''
out_template = "./attribute/{}.vcf.pickle"


virga_methods = {}

def crbm_run(f):
  out_file1 = out_template.format("crbm_split1")
  out_file2 = out_template.format("crbm_split2")
  f.write(f"CRBM_run.py {vcf_file_split1_pickle} {out_file1} 2500 --fixnodes=5000 --dump_output_interval=100 --ep_max=2001 --gpu=True\n")
  f.write(f"CRBM_run.py {vcf_file_split2_pickle} {out_file2} 2500 --fixnodes=5000 --dump_output_interval=100 --ep_max=2001 --gpu=True\n")
  f.write(f"attribute_inference_experiment.py {vcf_file_split1_pickle} {vcf_file_split2_pickle} {out_file1} {out_file2} >> results.txt\n")
  f.write(f"echo CRBM >> results.txt\n")
virga_methods[crbm_run.__name__] = crbm_run

def wgan_run(f):
  out_file1 = out_template.format("wgan_split1")
  out_file2 = out_template.format("wgan_split2")
  f.write(f"WGAN_run.py {vcf_file_split1_pickle} {out_file1} 2500 --dump_output_interval=10 --epochs=201\n")
  f.write(f"WGAN_run.py {vcf_file_split2_pickle} {out_file2} 2500 --dump_output_interval=10 --epochs=201\n")
  f.write(f"attribute_inference_experiment.py {vcf_file_split1_pickle} {vcf_file_split2_pickle} {out_file1} {out_file2} >> results.txt\n")
  f.write(f"echo WGAN >> results.txt\n")
virga_methods[wgan_run.__name__] = wgan_run


petrichor_methods = {}

def mark_run(f,i,parallel=False):
  out_file1 = out_template.format("mark_split1")
  out_file2 = out_template.format("mark_split2")
  f.write(f"MARK_run.py {vcf_file_split1_pickle} {out_file1} 2500 --window_leng={i} \n")
  f.write(f"MARK_run.py {vcf_file_split2_pickle} {out_file2} 2500 --window_leng={i} \n")
  f.write(f"attribute_inference_experiment.py {vcf_file_split1_pickle} {vcf_file_split2_pickle} {out_file1} {out_file2} >> results.txt\n")
  f.write(f"echo MARK{postpend}_{i} >> results.txt\n")
petrichor_methods[mark_run.__name__] = mark_run

def genomator_run(f,i,z,postpend=""):
  out_file1 = out_template.format("genomator_split1")
  out_file2 = out_template.format("genomator_split2")
  f.write(f"genomator {vcf_file_split1_pickle} {out_file1} 2500 0 0 --sample_group_size={i} --exception_space=-{z} --solver_name=tinicard --difference_samples=100 --noise=-0.1\n")
  f.write(f"genomator {vcf_file_split2_pickle} {out_file2} 2500 0 0 --sample_group_size={i} --exception_space=-{z} --solver_name=tinicard --difference_samples=100 --noise=-0.1\n")
  f.write(f"attribute_inference_experiment.py {vcf_file_split1_pickle} {vcf_file_split2_pickle} {out_file1} {out_file2} >> results.txt\n")
  f.write(f"echo GENOMATOR{postpend}_{i}_{z}_n1 >> results.txt\n")
petrichor_methods[genomator_run.__name__] = genomator_run


petrichor_experiments = []
i_range = list(range(10,300,30))
for ii,i in enumerate(i_range):
    petrichor_experiments.append('mark_run',f,i,(ii%1!=0))
i_range = list(range(10,100,10))+list(range(100,200,20))+list(range(200,301,40))
z_range = [(i-10)/40 for i in i_range]
for i,z in zip(i_range,z_range):
    petrichor_experiments.append("genomator_run",f,i,z,"")





with open("petrichor_run.sh",'w') as petrichor_f:
    for e in petrichor_experiments:
        filename = "_".join([str(ee) for ee in e]) + ".sh"
        with open(filename,"w") as f:
            f.write(petrichor_header)
            petrichor_methods[e[0]](*([f]+e[1:]))
        petrichor_f.write(f"sbatch {filename}\n")
with open("virga_run.sh",'w') as virga_f:
    for e in virga_experiments:
        filename = "_".join([str(ee) for ee in e]) + ".sh"
        with open(filename,"w") as f:
            f.write(virga_header)
            virga_methods[e[0]](*([f]+e[1:]))
        virga_f.write(f"sbatch {filename}\n")


