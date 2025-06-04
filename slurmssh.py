import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

import toml


class SlurmSSH:
    def __init__(self, host: str, username: str, launch_script_path: str):
        """
        Initialize SlurmSSH client.

        Args:
            host: SSH hostname of the Slurm login node
            username: SSH username for the cluster
            launch_script_path: Path to the Slurm job script (.slurm file)
        """
        self.host = host
        self.username = username
        self.launch_script_path = launch_script_path
        self.project_name = self._get_project_name()
        self.remote_dir = f"~/slurmssh/{self.project_name}/"

    def _get_project_name(self) -> str:
        """
        Determine project name from pyproject.toml or fallback to launch script parent dir.
        """
        # Try to get project name from pyproject.toml
        try:
            if Path("pyproject.toml").exists():
                with open("pyproject.toml", "r") as f:
                    config = toml.load(f)
                    if "project" in config and "name" in config["project"]:
                        return config["project"]["name"]
        except Exception:
            pass

        # Fallback to parent directory of launch script
        script_path = Path(self.launch_script_path)
        if script_path.parent != Path("."):
            return script_path.parent.name

        # Final fallback to current directory name
        return Path.cwd().name

    def _run_ssh_command(self, command: str) -> subprocess.CompletedProcess:
        """Execute a command on the remote host via SSH."""
        ssh_cmd = ["ssh", f"{self.username}@{self.host}", command]
        return subprocess.run(ssh_cmd, capture_output=True, text=True)

    def _sync_code(self, exclude: Optional[List[str]] = None):
        """Sync current directory to the cluster using rsync."""
        # Create remote directory
        mkdir_cmd = f"mkdir -p {self.remote_dir}"
        result = self._run_ssh_command(mkdir_cmd)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to create remote directory: {result.stderr}")

        # Build rsync command with exclusions
        rsync_cmd = ["rsync", "-avz", "--delete"]

        # Add default exclusions
        default_excludes = [
            ".git/",
            "__pycache__/",
            "*.pyc",
            ".DS_Store",
            ".vscode/",
            ".idea/",
            ".venv/",
        ]
        all_excludes = default_excludes + (exclude or [])

        for pattern in all_excludes:
            rsync_cmd.extend(["--exclude", pattern])

        rsync_cmd.extend(["./", f"{self.username}@{self.host}:{self.remote_dir}"])

        result = subprocess.run(rsync_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to sync code: {result.stderr}")

        print(f"Code synced to {self.host}:{self.remote_dir}")

    def _submit_job(self) -> str:
        sbatch_cmd = f"cd {self.remote_dir} && sbatch {self.launch_script_path}"

        result = self._run_ssh_command(sbatch_cmd)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to submit job: {result.stderr}")

        # Extract job ID from sbatch output (e.g., "Submitted batch job 12345")
        output = result.stdout.strip()
        if "Submitted batch job" in output:
            job_id = output.split()[-1]
            print(f"Job submitted with ID: {job_id}")
            return job_id
        else:
            raise RuntimeError(f"Unexpected sbatch output: {output}")

    def submit(self, exclude: Optional[List[str]] = None):
        """
        Main method to sync code and submit job.

        Args:
            exclude: List of additional patterns to exclude from rsync
        """
        try:
            self._sync_code(exclude=exclude)
            self._submit_job()

        except Exception as e:
            print(f"Error: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(
        description="Sync code and submit jobs to Slurm cluster",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  slurmssh --ssh username@hostname script.slurm
  slurmssh --ssh user@cluster job.slurm --exclude "data/" "*.log"
        """
    )
    
    parser.add_argument(
        "--ssh", 
        required=True,
        help="SSH connection string (username@hostname)"
    )
    
    parser.add_argument(
        "script",
        help="Path to Slurm job script (.slurm file)"
    )
    
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[],
        help="Additional patterns to exclude from rsync"
    )
    
    args = parser.parse_args()
    
    # Parse SSH connection string
    if "@" not in args.ssh:
        print("Error: SSH connection must be in format username@hostname", file=sys.stderr)
        sys.exit(1)
    
    username, host = args.ssh.split("@", 1)
    
    # Check if script exists
    if not Path(args.script).exists():
        print(f"Error: Script file '{args.script}' not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        slurm = SlurmSSH(
            host=host,
            username=username, 
            launch_script_path=args.script
        )
        
        slurm.submit(exclude=args.exclude)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
