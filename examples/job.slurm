#!/bin/bash
#SBATCH --job-name=slurmssh-example
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err
#SBATCH --time=00:05:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1GB

echo "Job ID: $SLURM_JOB_ID"
echo "Job Name: $SLURM_JOB_NAME"
echo "Node: $SLURM_NODELIST"
echo "Started at: $(date)"
echo "Working directory: $(pwd)"
echo


echo "Running example Python script..."
python3 example_job.py

echo "Job completed at: $(date)"
