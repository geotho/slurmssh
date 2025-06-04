# SlurmSSH Examples

This directory contains examples demonstrating how to use the SlurmSSH library to submit jobs to Slurm clusters.

## Files

- **`basic_usage.py`** - Main example script showing how to use SlurmSSH
- **`job.slurm`** - Sample Slurm job script with common SBATCH directives
- **`example_task.py`** - Python script that gets executed by the Slurm job
- **`README.md`** - This file

## Setup

Before running the example, you need to:

1. **Configure cluster credentials** in `basic_usage.py`:

   ```python
   host = "your-cluster-login-node.edu"  # Your cluster's login node
   username = "your-username"            # Your username on the cluster
   ```

2. **Set up SSH key authentication** for passwordless access to your cluster

3. **Customize the Slurm job script** (`job.slurm`) for your cluster:
   - Adjust partition name (`--partition=normal`)
   - Modify resource requirements (time, memory, CPUs)
   - Add any required module loads
   - Update paths as needed

## Running the Example

From the `examples/` directory:

```bash
cd examples/
python3 basic_usage.py
```

## What the Example Does

1. **Code Sync**: Uses `rsync` to sync the current directory to the cluster
2. **Job Submission**: Submits the Slurm job using `sbatch job.slurm`
3. **Computation**: The job runs `example_task.py` which:
   - Approximates π using Monte Carlo method
   - Reports progress and environment information
   - Writes results to `computation_results.txt`

## Expected Output

When you run the example, you'll see:

```
SlurmSSH Basic Usage Example
========================================
Cluster: your-cluster-login-node.edu
Username: your-username
Job script: job.slurm
Remote directory: ~/slurmssh/slurmssh/

Submitting job...
Code synced to your-cluster-login-node.edu:~/slurmssh/slurmssh/
Job submitted with ID: 12345
Job submitted successfully!
```

## Checking Job Status

After submission, you can check your job status on the cluster:

```bash
# SSH to your cluster
ssh your-username@your-cluster-login-node.edu

# Check job status
squeue -u your-username

# View job output (replace 12345 with your job ID)
cat ~/slurmssh/slurmssh/slurm-12345.out
```

## Customization

You can customize the example by:

- Modifying the computational task in `example_task.py`
- Adjusting Slurm parameters in `job.slurm`
- Adding custom exclusion patterns in `basic_usage.py`
- Creating additional job scripts for different types of workloads

## Troubleshooting

Common issues and solutions:

1. **SSH connection fails**: Ensure SSH key authentication is set up
2. **Permission denied**: Check that your username and host are correct
3. **Job fails to start**: Verify Slurm partition and resource limits
4. **Module not found**: Update module load commands in `job.slurm`
