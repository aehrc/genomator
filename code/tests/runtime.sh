#!/bin/bash
set -exuo pipefail
INPUT_VCF_DIR=/data/pickles/
INPUT_FILE_PREFIX=chr_filtered_
INPUT_VCF_SUFFIX=.vcf.gz.pickle
TAR_SUFFIX=.tar.gz


GENOMATOR () {
    \time --format=%U --output=$2 genomator $1 dummy_output.pickle 1 1 1
}
MARKOV () {
    \time --format=%U --output=$2 MARKOV_run.py $1 dummy_output.pickle 1 --window_leng=10
}
GAN () {
    \time --format=%U --output=$2 GAN_run.py $1 "dummy_output_GAN_${3}" 1 --dump_output_interval=20000 --epochs=20010
}
RBM () {
    \time --format=%U --output=$2 RBM_run.py $1 dummy_output 1 --dump_output_interval=30000 --gpu=True --ep_max=1200
}
CRBM () {
    \time --format=%U --output=$2 CRBM_run.py $1 dummy_output 1 --dump_output_interval=30000 --gpu=True --ep_max=1200
}

RESULTS_DIR=$1
RESULTS_FILE="${RESULTS_DIR}/runtime_results.tsv"
TEMP_RUNTIME_FILE=runtime.txt

echo -e "Method\tSNPs\tTime(s)" > $RESULTS_FILE
for alg in GENOMATOR MARKOV GAN RBM CRBM; do
    if [[ "${alg}" == "GENOMATOR" ]]; then
        for i in 100 400 1600 6400 25600 102400 409600 1638400 6553600 11757483; do
            input_vcf="${INPUT_FILE_PREFIX}${i}${INPUT_VCF_SUFFIX}"
            tar -xzf "${INPUT_VCF_DIR}${input_vcf}${TAR_SUFFIX}" --no-same-owner -O > $input_vcf
            $alg $input_vcf $TEMP_RUNTIME_FILE $i
            echo -en "${alg}\t${i}\t" >> $RESULTS_FILE
            cat $TEMP_RUNTIME_FILE >> $RESULTS_FILE
            rm $input_vcf
        done
    else
        continue
    fi
done

runtime_produce_graph.py $RESULTS_FILE "${RESULTS_DIR}/runtime_graph.png"
