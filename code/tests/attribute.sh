#!/bin/bash
set -exuo pipefail
INPUT_VCF_PREFIX=/data/805_SNP_1000G_real_split_haplotypes

from_vcfshark () {
    vcfshark decompress "/data/vcfshark/attribute/${1}shark" "${1}"
}

GENOMATOR_ITERATOR () {
    for i in $(seq 15 5 45) $(seq 50 10 90) $(seq 100 20 180) $(seq 200 40 280); do
        z=$(((i-10)/5))
        echo "${i}_${z}"
    done
}
GENOMATOR () {
    sgs="${3%_*}"  # first part of the string
    es="${3#*_}"  # second part of the string
    genomator $1 $2 2504 1 1 --sample_group_size="${sgs}" --exception_space="-${es}"
}

MARKOV_ITERATOR () {
    echo $(seq 2 2 22)
}
MARKOV () {
    MARK_run.py $1 $2 2504 --window_leng="${3}"
}

GAN_ITERATOR () {
    echo $(seq 0.1 0.3 4.9)
}
GAN () {
    GAN_run.py $1 gan 2504 --dump_output_interval=20000 --epochs=20010 --layer_multiplier="${3}"
    pickle_to_vcf.py gan20000.pickle $1 $2
}

RBM_ITERATOR () {
    for nh in $(seq 100 100 2000); do
        for lr in "0.01" "0.005"; do
            echo "${nh}_${lr}"
        done
    done
}
RBM () {
    nh="${3%_*}"  # first part of the string
    lr="${3#*_}"  # second part of the string
    RBM_run.py $1 rbm 2504 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh="${nh}" --lr="${lr}"
    pickle_to_vcf.py rbm1201.pickle $1 $2
}

CRBM_ITERATOR () {
    echo $(seq 100 100 2000)
}
CRBM () {
    CRBM_run.py $1 crbm 2504 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh="${3}"
    pickle_to_vcf.py crbm1201.pickle $1 $2
}

run_attribute_inference () {
    files=("${INPUT_VCF_PREFIX}A.vcf.gz" "${INPUT_VCF_PREFIX}B.vcf.gz")
    for a in "A" "B"; do
        vcf="${1}_${a}_${2}.vcf"
        bgzip "${vcf}" -f
        tabix "${vcf}.gz"
        files+=("${vcf}.gz")
    done
    echo -en "${1}_${2}\t" >> $result_file
    attribute_inference_experiment.py "${files[@]}" --silent=True >> $result_file
}

RESULTS_DIR=$1
result_file="${RESULTS_DIR}/attribute_inference_median_distance.tsv"
echo -e "Method\tIn-Data Distance\tOut-Data Distance" > "$result_file"
for alg in GENOMATOR MARKOV GAN RBM CRBM; do
    for args in $("${alg}_ITERATOR"); do
        for a in "A" "B"; do
            vcf="${alg}_${a}_${args}.vcf"
            if [[ "${alg}" == "GENOMATOR" ]]; then
                "${alg}" "${INPUT_VCF_PREFIX}${a}.vcf.gz" "${vcf}" "${args}"
            else
                from_vcfshark "${vcf}"
            fi
        done
        run_attribute_inference "${alg}" "${args}"
    done
done

cat "${result_file}" > attribute_process.py > "${RESULTS_DIR}/results_raw.tsv"
cat "${result_file}" > attribute_find_nearest_zero.py > "${RESULTS_DIR}/results_closest.tsv"
