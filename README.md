# SlurmSSH

Run jobs on your Slurm cluster just like it's your local machine.

SlurmSSH syncs your code to the cluster, then submits your job and prints its output.

Your code is synced over SSH (rsync) and the job will continue running if your local machine is offline.

Use it as a command line tool or as a Python library.

## CLI Usage

After installing, use the `slurmssh` command to sync and submit jobs:

```bash
# Basic usage
slurmssh --ssh username@hostname script.slurm

# With custom exclusions
slurmssh --ssh username@hostname script.slurm --exclude "data/" "*.log"

# Show help
slurmssh --help
```

## Library Usage

Import and use SlurmSSH in your Python scripts:

```python
from slurmssh import SlurmSSH

slurm = SlurmSSH(
    host="my-slurm-login-node",
    username="my-username",
    launch_script_path="my-slurm-job.slurm",
)

# Automatically syncs code to the cluster, puts it in ~/slurmssh/{project-name}/, and submits your job.
slurm.submit()

# Or with custom exclusions.
slurm.submit(exclude=["data/", "*.log"])
```

## Features

- Write your Slurm jobs as Python scripts.
- Sync your code to the cluster using rsync.
- Submit your job to the cluster using sbatch.
- Prints your logs in real-time.

## Installation

Ensure you have rsync installed locally:

```bash
brew install rsync
```

### CLI Installation

Install globally with uvx for command line usage:

```bash
uvx install "slurmssh @ git+https://github.com/geotho/slurmssh"
```

### Library Installation

Add slurmssh to your project:

```bash
uv add "slurmssh @ git+https://github.com/geotho/slurmssh"
```
