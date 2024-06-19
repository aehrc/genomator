#!/bin/bash
set -exuo pipefail
INPUT_VCF=/data/AGBL4.vcf.gz

from_vcfshark () {
    vcfshark decompress "/data/vcfshark/ld/${1}.vcfshark" $2
}

GENOMATOR () {
    genomator $1 $2 1000 1 1
}
MARK () {
    MARK_run.py $1 $2 1000 --window_leng=30
}
GAN () {
    GAN_run.py $1 gan 1000 --dump_output_interval=300 --epochs=310
    pickle_to_vcf.py gan300.pickle $1 $2
}
RBM () {
    RBM_run.py $1 rbm 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250
    pickle_to_vcf.py rbm1201.pickle $1 $2
}
CRBM () {
    CRBM_run.py $1 crbm 1000 --dump_output_interval=1200 --gpu=True --ep_max=1250
    pickle_to_vcf.py crbm1201.pickle $1 $2
}

RESULTS_DIR=$1

ld_png () {
    ld.py $1 "${RESULTS_DIR}/AGBL4_dataset_ld_${2}.png" --begin=0 --end=1000
}


ld_png $INPUT_VCF REF
for alg in GENOMATOR MARK GAN RBM CRBM; do
    vcf="${alg}.vcf"
    if [[ "${alg}" == "GENOMATOR" ]]; then
        $alg "$INPUT_VCF" "$vcf"
    else
        from_vcfshark $alg "$vcf"
    fi
    ld_png $vcf $alg
done
