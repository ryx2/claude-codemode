"""Claude Code runner for executing codemode tasks."""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

from .types import CodeModeConfig, CodeModeResult


class ClaudeCodeRunner:
    """Manages Claude Code subprocess execution."""

    def __init__(self, config: Optional[CodeModeConfig] = None):
        """Initialize the runner.

        Args:
            config: Configuration for codemode execution
        """
        self.config = config or CodeModeConfig()

    def create_workspace(self, runner_code: str) -> Path:
        """Create a temporary workspace with agentRunner.py.

        Args:
            runner_code: The generated agentRunner.py code

        Returns:
            Path to the workspace directory
        """
        if self.config.workspace_dir:
            workspace = Path(self.config.workspace_dir)
            workspace.mkdir(parents=True, exist_ok=True)
        else:
            workspace = Path(tempfile.mkdtemp(prefix="codemode_"))

        # Write agentRunner.py
        runner_file = workspace / "agentRunner.py"
        runner_file.write_text(runner_code)

        if self.config.verbose:
            print(f"Created workspace at: {workspace}")
            print(f"Generated agentRunner.py:\n{runner_code}\n")

        return workspace

    def execute_with_claude_code(
        self, workspace: Path, instructions: str
    ) -> Tuple[bool, str, str]:
        """Execute the task using Claude Code.

        Args:
            workspace: Path to the workspace directory
            instructions: Instructions for Claude Code

        Returns:
            Tuple of (success, stdout, stderr)
        """
        # Create a message file with instructions
        message_file = workspace / ".codemode_instructions.txt"
        message_file.write_text(instructions)

        # Build Claude Code command
        # Use --print for non-interactive mode
        # Use --dangerously-skip-permissions to bypass file edit permissions
        cmd = [
            self.config.claude_code_path,
            "--print",
            "--dangerously-skip-permissions",
            instructions,
        ]

        if self.config.verbose:
            print(f"Executing: {' '.join(cmd)}")
            print(f"Working directory: {workspace}")

        try:
            result = subprocess.run(
                cmd,
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
            )

            if self.config.verbose:
                print(f"Return code: {result.returncode}")
                print(f"STDOUT:\n{result.stdout}")
                print(f"STDERR:\n{result.stderr}")

            return result.returncode == 0, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            return False, "", f"Execution timed out after {self.config.timeout} seconds"
        except FileNotFoundError:
            return (
                False,
                "",
                f"Claude Code not found at: {self.config.claude_code_path}. "
                "Make sure Claude Code is installed and in your PATH.",
            )
        except Exception as e:
            return False, "", f"Execution error: {str(e)}"

    def extract_result(self, workspace: Path, stdout: str, stderr: str) -> CodeModeResult:
        """Extract the result from execution output.

        Args:
            workspace: Path to the workspace directory
            stdout: Standard output from execution
            stderr: Standard error from execution

        Returns:
            CodeModeResult object
        """
        # Look for CODEMODE_RESULT marker in output
        full_output = stdout + "\n" + stderr

        # Try to find the result marker
        result_pattern = r"CODEMODE_RESULT:\s*({.*})"
        matches = re.findall(result_pattern, full_output, re.DOTALL)

        if matches:
            try:
                result_data = json.loads(matches[-1])  # Use the last match
                if result_data.get("success"):
                    return CodeModeResult(
                        output=result_data.get("result"),
                        execution_log=full_output,
                        success=True,
                    )
                else:
                    return CodeModeResult(
                        output=None,
                        execution_log=full_output,
                        success=False,
                        error=result_data.get("error", "Unknown error"),
                    )
            except json.JSONDecodeError as e:
                return CodeModeResult(
                    output=None,
                    execution_log=full_output,
                    success=False,
                    error=f"Failed to parse result: {e}",
                )

        # If no marker found, try to execute agentRunner.py directly
        return self._execute_runner_directly(workspace, full_output)

    def _execute_runner_directly(self, workspace: Path, previous_output: str) -> CodeModeResult:
        """Execute agentRunner.py directly to get the result.

        Args:
            workspace: Path to the workspace directory
            previous_output: Previous execution output for logging

        Returns:
            CodeModeResult object
        """
        runner_file = workspace / "agentRunner.py"

        if not runner_file.exists():
            return CodeModeResult(
                output=None,
                execution_log=previous_output,
                success=False,
                error="agentRunner.py not found in workspace",
            )

        try:
            result = subprocess.run(
                ["python", str(runner_file)],
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=60,
            )

            full_output = previous_output + "\n\nDirect execution:\n" + result.stdout

            if result.returncode == 0:
                # Try to extract CODEMODE_RESULT
                result_pattern = r"CODEMODE_RESULT:\s*({.*})"
                matches = re.findall(result_pattern, result.stdout, re.DOTALL)

                if matches:
                    result_data = json.loads(matches[-1])
                    if result_data.get("success"):
                        return CodeModeResult(
                            output=result_data.get("result"),
                            execution_log=full_output,
                            success=True,
                        )

            return CodeModeResult(
                output=None,
                execution_log=full_output + "\n" + result.stderr,
                success=False,
                error="Failed to execute agentRunner.py",
            )

        except Exception as e:
            return CodeModeResult(
                output=None,
                execution_log=previous_output,
                success=False,
                error=f"Failed to execute runner: {e}",
            )

    def cleanup_workspace(self, workspace: Path) -> None:
        """Clean up the workspace directory.

        Args:
            workspace: Path to the workspace directory
        """
        if not self.config.preserve_workspace:
            import shutil

            try:
                shutil.rmtree(workspace)
                if self.config.verbose:
                    print(f"Cleaned up workspace: {workspace}")
            except Exception as e:
                if self.config.verbose:
                    print(f"Failed to clean up workspace: {e}")
