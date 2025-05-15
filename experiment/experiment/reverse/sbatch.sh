if command -v sbatch &> /dev/null
then
  sbatch "$@"
else
  source "$@"
fi
