#!/bin/bash
#SBATCH --job-name=slurmssh-example
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err
#SBATCH --time=00:05:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1GB

echo "Your arguments are: $@"
