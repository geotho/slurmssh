#!/bin/bash
#SBATCH --job-name=basic_usage
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4GB

echo "Job ID: $SLURM_JOB_ID"
echo "Job Name: $SLURM_JOB_NAME"
echo "Node: $SLURM_NODELIST"
echo "Started at: $(date)"
echo "Working directory: $(pwd)"
echo

echo "Running Python script: examples/basic_usage.py"
uv run examples/basic_usage.py

echo "Job completed at: $(date)"
