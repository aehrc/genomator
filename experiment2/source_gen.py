

prepend = "https://gitlab.inria.fr/ml_genetics/public/artificial_genomes/-/blob/master/1000G_real_genomes/"
hapt_file = "65K_SNP_1000G_real.hapt.zip"
legend_file = "65K_SNP.legend"
hapt_file = "65K_SNP_1000G_real.hapt"
vcf_file = "65K_SNP_1000G_real.vcf"
vcf_file_gz = vcf_file+".gz"
vcf_file_split1 = "65K_SNP_1000G_real_split1.vcf"
vcf_file_split2 = "65K_SNP_1000G_real_split2.vcf"
vcf_file_split1_gz = vcf_file_split1+".gz"
vcf_file_split2_gz = vcf_file_split2+".gz"
vcf_file_pickle = vcf_file+".pickle"
vcf_file_split1_pickle = vcf_file_split1+".pickle"
vcf_file_split2_pickle = vcf_file_split2+".pickle"

source_files = [k for k in globals().keys() if k[:3]=="vcf"]

# do downloading and processing
if __name__ == "__main__":
    import os
    def running(a):
        print("RUNNING: {}".format(a))
        os.system(a)

    commands = ["cd sources",
        "wget {}{}".format(prepend,hapt_file),
        "wget {}{}".format(prepend,legend_file),
        "unzip {}".format(hapt_file),
        "convert_hapt_to_vcf_haplotypes.py {} {} {}".format(hapt_file,legend_file,vcf_file),
        "bgzip {}".format(vcf_file),
        "tabix {}".format(vcf_file.gz),
        "splitter.py {} {} {}".format(vcf_file_gz,vcf_file_split1,vcf_file_split2),
        "bgzip {}".format(vcf_file_split1),
        "bgzip {}".format(vcf_file_split2),
        "tabix {}".format(vcf_file_split1_gz),
        "tabix {}".format(vcf_file_split2_gz),
        f"vcf_to_pickle.py {0} {0}.pickle".format(vcf_file_gz),
        f"vcf_to_pickle.py {0} {0}.pickle".format(vcf_file_split1_gz),
        f"vcf_to_pickle.py {0} {0}.pickle".format(vcf_file_split2_gz)]

    import tqdm as tqdm
    print("DOWNLOADING AND PROCESSING SOURCES:")
    for c in tqdm(commands):
        running(c)
    print("FINISHED DOWNLOADING AND PROCESSING SOURCES")

# append a prepend so that these files can be inported from adjacent folders
for s in source_files:
    globals()[s] = "./sources/"+globals()[s]
