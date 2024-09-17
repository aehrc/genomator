import os
import subprocess

print("Doing Large Scale Runtime Experiment")
methods = {
    "MARK":"MARK_run.py ../sources/chr_filtered_{}.vcf.gz.pickle dummy_output.pickle 1 --window_leng=10 2>&1 > MARK_debug.txt",
    "GENOMATOR":"genomator ../sources/chr_filtered_{}.vcf.gz.pickle dummy_output.pickle 1 1 1 2>&1 > GENOMATOR_debug.txt",
    "GAN":"GAN_run_orig.py ../sources/chr_filtered_{}.vcf.gz.pickle dummy_output_GAN_{} 1 --dump_output_interval=20000 --epochs=20010 2>&1 > GAN_debug.txt",
    "RBM":"RBM_run.py ../sources/chr_filtered_{}.vcf.gz.pickle dummy_output 1 --dump_output_interval=30000 --gpu=True --ep_max=1200 2>&1 > RBM_debug.txt",
    "CRBM":"CRBM_run.py ../sources/chr_filtered_{}.vcf.gz.pickle dummy_output 1 --dump_output_interval=30000 --gpu=True --ep_max=1200 2>&1 > CRBM_debug.txt"
}
indices = [4**i*100 for i in range(9)] + ['']
with open("runtime_results.txt","w") as f:
    f.write(f"METHOD,SCALE,TIME\n")
for k in methods.keys():
    for index in indices:
        print(k,index)
        t = subprocess.getoutput("\\time --format=%U " + methods[k].format(index))
        t = t.split("\n")[-1]
        os.system("rm dummy_output*")
        with open("runtime_results.txt","a") as f:
            f.write(f"{k},{index},{t}\n")

