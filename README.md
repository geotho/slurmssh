# SlurmSSH

Run jobs on your Slurm cluster just like it's your local machine.

SlurmSSH syncs your code to the cluster, then submits your job and prints its output.

Your code is synced over SSH (rsync) and the job will continue running if your local machine is offline.

Write and run a Python script locally to submit your job to the cluster.

## Features

- Write your Slurm jobs as Python scripts.
- Sync your code to the cluster using rsync.
- Submit your job to the cluster using sbatch.
- Prints your logs in real-time.

## Installation

```bash
pip install slurmssh
```

## Usage

```python

from slurmssh import SlurmSSH

slurm = SlurmSSH(
    host="my-slurm-login-node",
    username="my-username",
    launch_script_path="my-slurm-job.slurm",
)

# Automatically syncs code to the cluster, puts it in ~/slurmssh/{project-name}/
slurm.submit()

# Or with custom exclusions and options
slurm.submit(exclude=["data/", "*.log"], wait_for_running=False)
```
