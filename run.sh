echo "Have you downloaded appropriate mouse dataset files from (https://datadryad.org/stash/dataset/doi:10.5061/dryad.2rs41):"
echo "Such that: geno.txt.gz, pheno.csv, map.txt - are in current directory."
read -p "Confirm you have downloaded appropriate files (y/n)?" CONT
if [ "$CONT" = "y" ]; then
  # download original dataset
  gzip -d geno.txt.gz
  # clone and patch files from gretel
  git clone https://github.com/gretelai/synthetic-data-genomics.git
  cd ./synthetic-data-genomics
  git checkout 607a78ad08d20ede9dc25ae3a5c6d99866c71de0
  cd ..
  cp -r synthetic-data-genomics/research_paper_code/src ./
  jupyter nbconvert --to script ./synthetic-data-genomics/research_paper_code/notebooks/map_synth.ipynb
  jupyter nbconvert --to script ./synthetic-data-genomics/research_paper_code/notebooks/map.ipynb
  jupyter nbconvert --to script ./synthetic-data-genomics/research_paper_code/notebooks/Manhattan\ plot.ipynb
  jupyter nbconvert --to script ./synthetic-data-genomics/synthetics/05_compare_associations.ipynb
  patch ./synthetic-data-genomics/research_paper_code/notebooks/map_synth.r ./patches/map_synth.r.patch
  patch ./synthetic-data-genomics/research_paper_code/notebooks/map.r ./patches/map.r.patch
  patch ./synthetic-data-genomics/research_paper_code/notebooks/Manhattan\ plot.py ./patches/Manhattan\ plot.py.patch
  patch ./synthetic-data-genomics/synthetics/05_compare_associations.py ./patches/05_compare_associations.py.patch
  mv ./synthetic-data-genomics/research_paper_code/notebooks/map_synth.r ./
  mv ./synthetic-data-genomics/research_paper_code/notebooks/map.r ./
  mv ./synthetic-data-genomics/research_paper_code/notebooks/Manhattan\ plot.py ./plot.py
  mv ./synthetic-data-genomics/synthetics/05_compare_associations.py ./compare_associations.py
  # do actual processing
  rm ./out/*
  Rscript map.r
  python format_and_filter_input.py
  python generate_synthetic_data.py
  python convert_vcf_to_txt.py new_genomes.vcf new_genomes.txt
  rm ./out_synth/*
  Rscript map_synth.r
  python plot.py
  python rare_SNP_diagnosis9.py ./new_genomes.vcf ./geno.vcf
  python compare_associations.py > recall_results.txt
else
  echo "please download dataset to run analysis";
fi
