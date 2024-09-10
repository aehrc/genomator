#!/bin/bash
set -exuo pipefail
INPUT_VCF=/data/805_SNP_1000G_real_haplotypes.vcf.gz

from_vcfshark () {
    vcfshark decompress "/data/vcfshark/805/${2}/${1}.vcfshark" $3
}

GENOMATOR () {
    genomator $1 $2 1000 1 1
}
MARK () {
    MARK_run.py $1 $2 1000 --window_leng=10
}
GAN () {
    GAN_run.py $1 gan 1000 --dump_output_interval=20000 --epochs=20010
    pickle_to_vcf.py gan20000.pickle $1 $2 --ploidy=1
}
RBM () {
    RBM_run.py $1 rbm 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250
    pickle_to_vcf.py rbm1201.pickle $1 $2 --ploidy=1
}
CRBM () {
    CRBM_run.py $1 crbm 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250
    pickle_to_vcf.py crbm1201.pickle $1 $2 --ploidy=1
}

RESULTS_DIR=$1
for alg in GENOMATOR MARK GAN RBM CRBM; do
    output="${RESULTS_DIR}/wasserstein_${alg}.tsv"
    echo -e "run\tavg\tstdev" > $output
    for i in {1..9}; do
        vcf="${alg}_${i}.vcf"
        if [[ "${alg}" == "GENOMATOR" ]]; then
            $alg "$INPUT_VCF" "$vcf"
        else
            from_vcfshark $alg $i "$vcf"
        fi
        pca_plot_genomes_vcf2.py "$INPUT_VCF" "$vcf" "${RESULTS_DIR}/${alg}_${i}.png"
        echo -ne "${i}\t" >> $output
        wasserstein_analyse_pca.py "$INPUT_VCF" "$vcf" >> $output
    done
done
