#!/bin/bash
set -exuo pipefail
INPUT_VCF_PREFIX=/data/805_SNP_1000G_real_split_haplotypes

from_vcfshark () {
    vcfshark decompress "/data/vcfshark/attribute/${1}_${2}.vcfshark" $3
}

GENOMATOR () {
    genomator $1 $2 1000 1 1
}
MARK () {
    MARK_run.py $1 $2 1000 --window_leng=10
}
GAN () {
    GAN_run.py $1 gan 1000 --dump_output_interval=20000 --epochs=20010 --layer_multiplier=1.0
    pickle_to_vcf.py gan20000.pickle $1 $2
}
RBM () {
    RBM_run.py $1 rbm 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=500 --lr=0.01
    pickle_to_vcf.py rbm1201.pickle $1 $2
}
CRBM () {
    CRBM_run.py $1 crbm 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=500 --fixnodes=300
    pickle_to_vcf.py crbm1201.pickle $1 $2
}

RESULTS_DIR=$1
result_file="${RESULTS_DIR}/attribute_inference_median_distance.tsv"
echo -e "Method\tIn-Data Distance\tOut-Data Distance" > "$result_file"
for alg in GENOMATOR MARK GAN RBM CRBM; do
    for i in "A" "B"; do
        vcf="${alg}_${i}.vcf"
        if [[ "${alg}" == "GENOMATOR" ]]; then
            $alg "${INPUT_VCF_PREFIX}${i}.vcf" "$vcf"
        else
            from_vcfshark $alg $i "$vcf"
        fi
    done
    echo -en "${alg}\t" >> $result_file
    attribute_inference_experiment.py "${INPUT_VCF_PREFIX}A.vcf" "${INPUT_VCF_PREFIX}B.vcf" "${alg}_A.vcf" "${alg}_B.vcf" >> $result_file
done
