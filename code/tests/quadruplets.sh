#!/bin/bash
set -exuo pipefail
INPUT_VCF=/data/AGBL4.vcf.gz

from_vcfshark () {
    for file in "/data/vcfshark/quadruplets/${1}"*.vcfshark; do
        vcfshark decompress "${file}" "$(basename ${file%shark})"
    done
}

GENOMATOR () {
    for sgs in $(seq 10 5 40); do
        es=$(((sgs-10)/5))
        genomator $1 "GENOMATOR_${sgs}_${es}.vcf" 1000 1 1 --sample_group_size="${sgs}" --exception_space="-${es}" --max_restarts=-1
    done
}
MARKOV () {
    for wl in $(seq 20 20 200); do
        MARKOV_run.py $1 "MARKOV_${wl}.vcf" 1000 --window_leng=$wl
    done
}
GAN () {
    for lm in $(seq 0.7 0.3 1.6); do
        GAN_run.py $1 gan 1000 --dump_output_interval=20000 --epochs=20010 --layer_multiplier=$lm
        pickle_to_vcf.py gan20000.pickle $1 "GAN_${lm}.vcf"
    done
}
RBM () {
    for nh in 500 700; do
        for lr in "01" "005"; do
            RBM_run.py $1 rbm 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=$nh --lr="0.${lr}"
            pickle_to_vcf.py rbm1201.pickle $1 "RBM_${nh}_${lr}.vcf"
        done
    done
}
CRBM () {
    for nh in 500 700; do
        for fn in 300 400; do
            CRBM_run.py $1 crbm 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250 --nh=$nh --fixnodes=$fn
            pickle_to_vcf.py crbm1201.pickle $1 "CRBM_${nh}_${fn}.vcf"
        done
    done
}

RESULTS_DIR=$1

for alg in GENOMATOR MARKOV GAN RBM CRBM; do
    if [[ "${alg}" == "None!" ]]; then
        $alg "$INPUT_VCF"
    else
        from_vcfshark $alg
    fi
done

for produced_file in *.vcf; do
    file_pairs=("${file_pairs[@]}" "../${produced_file}" "$INPUT_VCF")
done

cd $RESULTS_DIR
rare_SNP_diagnosis8.py "${file_pairs[@]}" --degree=4 --trials=100000 --output_image_file=quadruplets_analysis.png > results1.txt
rare_SNP_diagnosis8.py "${file_pairs[@]}" --degree=7 --trials=10000 --output_image_file=septuplets_analysis.png > results2.txt
