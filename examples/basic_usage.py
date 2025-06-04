#!/usr/bin/env python3
"""
Basic example of using SlurmSSH to submit a job to a Slurm cluster.

This example demonstrates:
1. Setting up SlurmSSH with cluster credentials
2. Submitting a job with code sync
3. Using custom exclusion patterns for rsync

Before running this example:
1. Update the host, username, and launch_script_path variables below
2. Ensure you have SSH key-based authentication set up for the cluster
3. Make sure the Slurm job script (job.slurm) is configured correctly
"""

from slurmssh import SlurmSSH

SLURM_LOGIN_NODE = "slurmus-login-001"
SLURM_USERNAME = "george_convergence_ai"
SLURM_LAUNCH_SCRIPT_PATH = "job.slurm"


def main():
    # Create SlurmSSH instance
    client = SlurmSSH(
        host=SLURM_LOGIN_NODE,
        username=SLURM_USERNAME,
        launch_script_path=SLURM_LAUNCH_SCRIPT_PATH,
    )

    # Define files/patterns to exclude from sync
    # These are in addition to the default exclusions (.git/, __pycache__/, etc.)
    exclude_patterns = ["*.log", "data/large_files/", "temp/", "*.tmp"]

    try:
        print("Submitting job...")
        client.submit(exclude=exclude_patterns)
        print("Job submitted successfully!")

    except Exception as e:
        print(f"Failed to submit job: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
