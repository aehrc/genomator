if command -v sbatch &> /dev/null
then
  sbatch "$@"
else
  source "$@" 2> "$@"_results.txt
fi
