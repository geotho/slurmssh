import argparse
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from slurmssh import SlurmSSH, main


class TestSlurmSSH:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.host = "test-cluster.example.com"
        self.username = "testuser"
        self.script_path = "test_job.slurm"

        # Create a temporary script file for testing
        self.temp_script = tempfile.NamedTemporaryFile(
            mode="w", suffix=".slurm", delete=False
        )
        self.temp_script.write(
            "#!/bin/bash\n#SBATCH --job-name=test\necho 'Hello World'\n"
        )
        self.temp_script.close()

        self.slurm = SlurmSSH(
            host=self.host,
            username=self.username,
            launch_script_path=self.temp_script.name,
        )

    def teardown_method(self):
        """Clean up after each test method."""
        Path(self.temp_script.name).unlink(missing_ok=True)

    @patch("slurmssh.subprocess.run")
    def test_submit_job_without_args(self, mock_run):
        """Test _submit_job method without additional arguments."""
        # Mock successful sbatch submission
        mock_run.return_value = Mock(
            returncode=0, stdout="Submitted batch job 12345\n", stderr=""
        )

        job_id = self.slurm._submit_job()

        # Verify the command was called correctly
        expected_cmd = f"cd {self.slurm.remote_dir} && sbatch {self.temp_script.name}"
        mock_run.assert_called_once_with(
            ["ssh", f"{self.username}@{self.host}", expected_cmd],
            capture_output=True,
            text=True,
        )

        assert job_id == "12345"

    @patch("slurmssh.subprocess.run")
    def test_submit_job_with_args(self, mock_run):
        """Test _submit_job method with additional sbatch arguments."""
        # Mock successful sbatch submission
        mock_run.return_value = Mock(
            returncode=0, stdout="Submitted batch job 67890\n", stderr=""
        )

        sbatch_args = ["--time=10:00", "--mem=4G", "arg1", "arg2"]
        job_id = self.slurm._submit_job(sbatch_args=sbatch_args)

        # Verify the command includes the additional arguments
        expected_cmd = f"cd {self.slurm.remote_dir} && sbatch --time=10:00 --mem=4G arg1 arg2 {self.temp_script.name}"
        mock_run.assert_called_once_with(
            ["ssh", f"{self.username}@{self.host}", expected_cmd],
            capture_output=True,
            text=True,
        )

        assert job_id == "67890"

    @patch("slurmssh.subprocess.run")
    def test_submit_job_failure(self, mock_run):
        """Test _submit_job method when sbatch fails."""
        # Mock failed sbatch submission
        mock_run.return_value = Mock(
            returncode=1, stdout="", stderr="sbatch: error: Invalid partition name"
        )

        with pytest.raises(RuntimeError, match="Failed to submit job"):
            self.slurm._submit_job(sbatch_args=["--partition=invalid"])

    @patch("slurmssh.subprocess.run")
    def test_submit_job_unexpected_output(self, mock_run):
        """Test _submit_job method with unexpected sbatch output."""
        # Mock sbatch with unexpected output
        mock_run.return_value = Mock(
            returncode=0, stdout="Unexpected output format\n", stderr=""
        )

        with pytest.raises(RuntimeError, match="Unexpected sbatch output"):
            self.slurm._submit_job()

    @patch.object(SlurmSSH, "_sync_code")
    @patch.object(SlurmSSH, "_submit_job")
    def test_submit_with_sbatch_args(self, mock_submit_job, mock_sync_code):
        """Test submit method passes sbatch_args correctly."""
        mock_submit_job.return_value = "12345"

        sbatch_args = ["--nodes=2", "--ntasks=8"]
        self.slurm.submit(sbatch_args=sbatch_args)

        mock_sync_code.assert_called_once_with(exclude=None)
        mock_submit_job.assert_called_once_with(sbatch_args=sbatch_args)

    @patch.object(SlurmSSH, "_sync_code")
    @patch.object(SlurmSSH, "_submit_job")
    def test_submit_with_exclude_and_sbatch_args(self, mock_submit_job, mock_sync_code):
        """Test submit method with both exclude and sbatch_args."""
        mock_submit_job.return_value = "12345"

        exclude_patterns = ["*.log", "temp/"]
        sbatch_args = ["--time=05:00", "input_file.txt"]

        self.slurm.submit(exclude=exclude_patterns, sbatch_args=sbatch_args)

        mock_sync_code.assert_called_once_with(exclude=exclude_patterns)
        mock_submit_job.assert_called_once_with(sbatch_args=sbatch_args)


class TestArgumentParsing:
    def test_parse_args_without_sbatch_args(self):
        """Test argument parsing without additional sbatch arguments."""
        test_args = ["--ssh", "user@host", "script.slurm", "--exclude", "*.log"]

        with patch("sys.argv", ["slurmssh"] + test_args):
            with patch("slurmssh.Path.exists", return_value=True):
                parser = argparse.ArgumentParser()
                parser.add_argument("--ssh", required=True)
                parser.add_argument("script")
                parser.add_argument("--exclude", nargs="*", default=[])
                parser.add_argument("sbatch_args", nargs="*")

                args = parser.parse_args(test_args)

                assert args.ssh == "user@host"
                assert args.script == "script.slurm"
                assert args.exclude == ["*.log"]
                assert args.sbatch_args == []

    def test_parse_args_with_sbatch_args(self):
        """Test argument parsing with additional sbatch arguments."""
        test_args = [
            "--ssh",
            "user@host",
            "script.slurm",
            "--exclude",
            "*.log",
            "temp/",
            "--time=10:00",
            "--mem=8G",
            "input.txt",
            "output.txt",
        ]

        parser = argparse.ArgumentParser()
        parser.add_argument("--ssh", required=True)
        parser.add_argument("script")
        parser.add_argument("--exclude", nargs="*", default=[])
        parser.add_argument("sbatch_args", nargs="*")

        args, unknown = parser.parse_known_args(test_args)

        # Add any unknown arguments to sbatch_args (simulating main() logic)
        if unknown:
            args.sbatch_args.extend(unknown)

        assert args.ssh == "user@host"
        assert args.script == "script.slurm"
        assert args.exclude == ["*.log", "temp/"]
        assert args.sbatch_args == [
            "--time=10:00",
            "--mem=8G",
            "input.txt",
            "output.txt",
        ]

    def test_parse_args_only_sbatch_args(self):
        """Test argument parsing with only sbatch arguments (no exclude)."""
        test_args = ["--ssh", "user@host", "script.slurm", "arg1", "arg2", "arg3"]

        parser = argparse.ArgumentParser()
        parser.add_argument("--ssh", required=True)
        parser.add_argument("script")
        parser.add_argument("--exclude", nargs="*", default=[])
        parser.add_argument("sbatch_args", nargs="*")

        args = parser.parse_args(test_args)

        assert args.ssh == "user@host"
        assert args.script == "script.slurm"
        assert args.exclude == []
        assert args.sbatch_args == ["arg1", "arg2", "arg3"]


class TestMainFunction:
    @patch("slurmssh.SlurmSSH")
    @patch("slurmssh.Path.exists")
    def test_main_with_sbatch_args(self, mock_path_exists, mock_slurm_class):
        """Test main function with sbatch arguments."""
        mock_path_exists.return_value = True
        mock_slurm_instance = Mock()
        mock_slurm_class.return_value = mock_slurm_instance

        test_args = [
            "slurmssh",
            "--ssh",
            "testuser@testhost",
            "job.slurm",
            "--exclude",
            "*.pyc",
            "--time=02:00",
            "--mem=4G",
            "input_data.txt",
        ]

        with patch("sys.argv", test_args):
            main()

        # Verify SlurmSSH was initialized correctly
        mock_slurm_class.assert_called_once_with(
            host="testhost", username="testuser", launch_script_path="job.slurm"
        )

        # Verify submit was called with correct arguments
        mock_slurm_instance.submit.assert_called_once_with(
            exclude=["*.pyc"],
            sbatch_args=["--time=02:00", "--mem=4G", "input_data.txt"],
        )

    @patch("slurmssh.SlurmSSH")
    @patch("slurmssh.Path.exists")
    def test_main_without_sbatch_args(self, mock_path_exists, mock_slurm_class):
        """Test main function without sbatch arguments."""
        mock_path_exists.return_value = True
        mock_slurm_instance = Mock()
        mock_slurm_class.return_value = mock_slurm_instance

        test_args = ["slurmssh", "--ssh", "testuser@testhost", "job.slurm"]

        with patch("sys.argv", test_args):
            main()

        # Verify submit was called with empty sbatch_args
        mock_slurm_instance.submit.assert_called_once_with(exclude=[], sbatch_args=[])

    @patch("slurmssh.Path.exists")
    def test_main_script_not_found(self, mock_path_exists):
        """Test main function when script file doesn't exist."""
        mock_path_exists.return_value = False

        test_args = ["slurmssh", "--ssh", "testuser@testhost", "nonexistent.slurm"]

        with patch("sys.argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

    def test_main_invalid_ssh_format(self):
        """Test main function with invalid SSH connection string."""
        test_args = ["slurmssh", "--ssh", "invalid-format", "job.slurm"]

        with patch("sys.argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1


class TestIntegrationScenarios:
    """Integration tests for realistic usage scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_script = tempfile.NamedTemporaryFile(
            mode="w", suffix=".slurm", delete=False
        )
        self.temp_script.write(
            "#!/bin/bash\n#SBATCH --job-name=test\necho 'Hello World'\n"
        )
        self.temp_script.close()

    def teardown_method(self):
        """Clean up after each test."""
        Path(self.temp_script.name).unlink(missing_ok=True)

    @patch("slurmssh.subprocess.run")
    def test_machine_learning_job_scenario(self, mock_run):
        """Test scenario: submitting a machine learning job with GPU requirements."""
        # Mock rsync success
        mock_run.side_effect = [
            Mock(returncode=0, stdout="", stderr=""),  # mkdir
            Mock(returncode=0, stdout="", stderr=""),  # rsync
            Mock(
                returncode=0, stdout="Submitted batch job 98765\n", stderr=""
            ),  # sbatch
        ]

        slurm = SlurmSSH(
            host="gpu-cluster.edu",
            username="researcher",
            launch_script_path=self.temp_script.name,
        )

        sbatch_args = [
            "--gres=gpu:v100:2",
            "--time=24:00:00",
            "--mem=32G",
            "train.py",
            "--epochs",
            "100",
            "--batch-size",
            "64",
        ]

        slurm.submit(sbatch_args=sbatch_args)

        # Verify the final sbatch command includes all arguments
        final_call = mock_run.call_args_list[-1]
        # The call is subprocess.run(["ssh", "user@host", "command"], ...)
        command = final_call[0][0][2]  # Get the SSH command string

        assert "--gres=gpu:v100:2" in command
        assert "--time=24:00:00" in command
        assert "--mem=32G" in command
        assert "train.py" in command
        assert "--epochs 100" in command
        assert "--batch-size 64" in command

    @patch("slurmssh.subprocess.run")
    def test_array_job_scenario(self, mock_run):
        """Test scenario: submitting an array job with input/output files."""
        # Mock successful operations
        mock_run.side_effect = [
            Mock(returncode=0, stdout="", stderr=""),  # mkdir
            Mock(returncode=0, stdout="", stderr=""),  # rsync
            Mock(
                returncode=0, stdout="Submitted batch job 55555\n", stderr=""
            ),  # sbatch
        ]

        slurm = SlurmSSH(
            host="hpc.university.edu",
            username="student",
            launch_script_path=self.temp_script.name,
        )

        sbatch_args = [
            "--array=1-100",
            "--time=01:00:00",
            "process_data.py",
            "input_${SLURM_ARRAY_TASK_ID}.txt",
            "output_${SLURM_ARRAY_TASK_ID}.txt",
        ]

        exclude_patterns = ["results/", "*.log", "__pycache__/"]

        slurm.submit(exclude=exclude_patterns, sbatch_args=sbatch_args)

        # Verify rsync excludes
        rsync_call = mock_run.call_args_list[1]
        rsync_args = rsync_call[0][0]

        assert "--exclude" in rsync_args
        assert "results/" in rsync_args
        assert "*.log" in rsync_args

        # Verify sbatch command
        final_call = mock_run.call_args_list[-1]
        # The call is subprocess.run(["ssh", "user@host", "command"], ...)
        command = final_call[0][0][2]  # Get the SSH command string

        assert "--array=1-100" in command
        assert "process_data.py" in command
        assert "input_${SLURM_ARRAY_TASK_ID}.txt" in command
