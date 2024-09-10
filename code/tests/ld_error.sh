#!/bin/bash
#### Takes too long to run on Code Ocean
set -exuo pipefail
INPUT_VCF_PREFIX=/data/
INPUT_VCF_SUFFIX=_split1.vcf
COMPARE_VCF_SUFFIX=_split2.vcf

from_vcfshark () {
    vcfshark decompress "/data/vcfshark/ld_error/${2}/${1}.vcfshark" $3
}

GENOMATOR () {
    genomator $1 $2 1000 1 1
}
MARK () {
    MARK_run.py $1 $2 1000 --window_leng=10
}
GAN () {
    GAN_run.py $1 gan 1000 --dump_output_interval=20000 --epochs=20010
    pickle_to_vcf.py gan20000.pickle $1 $2
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
# leaving out "CCSER1" "FHIT" "RBFOX1", as they take too long to run
for gene in "AGBL4"; do
    out_dir="${RESULTS_DIR}/${gene}"
    mkdir $gene
    mkdir "${out_dir}"
    base_vcf="${INPUT_VCF_PREFIX}${gene}"
    compare_vcf="${base_vcf}${COMPARE_VCF_SUFFIX}"
    vcf_paths=($compare_vcf)
    for alg in GENOMATOR MARK GAN RBM CRBM; do
        vcf="${gene}/${alg}.vcf"
        if [[ "${alg}" == "GENOMATOR" ]]; then
            $alg "${base_vcf}${INPUT_VCF_SUFFIX}" "$vcf"
        else
            from_vcfshark $alg $gene "$vcf"
        fi
        vcf_paths=("${vcf_paths[@]}" "../../${vcf}")
    done
    if [[ $gene == "CCSER1" ]]; then
        # To keep all the data in the image
        y_lim=0.055
    else
        y_lim=0.045
    fi
    cd $out_dir
    echo results > results.txt
    ld_window_analysis.py "${vcf_paths[@]}" --max_offset=500 --max_y_limit=$y_lim --chunk_size=15 --output_image_file=LD_window.png >> results.txt
    ld11.py $compare_vcf >> results.txt
    echo average >> results.txt
    ld10.py "${vcf_paths[@]}" >> results.txt
    echo correlation >> results.txt
    for vcf_file in "${vcf_paths[@]}"; do
        if [[ $vcf_file != $compare_vcf ]]; then
            get_correlation.py $compare_vcf $vcf_file >> results.txt
        fi
    done
    cd ../..
done
