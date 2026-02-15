"""
Process Tools

Governed process execution.
"""

import subprocess

from .base_tool import BaseTool, ToolResult


class RunProcessTool(BaseTool):
    """Execute a subprocess."""

    name = "RunProcess"
    description = "Execute a process with arguments"
    required_params = ("exe",)
    optional_params = {
        "args": [],
        "cwd": None,
        "env": None,
        "timeout": 300,
        "capture_output": True,
    }

    def execute(self, **params) -> ToolResult:
        """
        Execute a process.

        Args:
            exe: Executable path or name
            args: Arguments to pass
            cwd: Working directory
            env: Environment variables (extends current env)
            timeout: Timeout in seconds
            capture_output: Whether to capture stdout/stderr

        Returns:
            ToolResult with process output
        """
        import os

        exe = params["exe"]
        args = self.get_param(params, "args", [])
        cwd = self.get_param(params, "cwd", None)
        env_override = self.get_param(params, "env", None)
        timeout = self.get_param(params, "timeout", 300)
        capture_output = self.get_param(params, "capture_output", True)

        # Build command
        if isinstance(args, str):
            args = args.split()
        cmd = [exe, *list(args)]

        # Build environment
        env = os.environ.copy()
        if env_override:
            env.update(env_override)

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                env=env,
                capture_output=capture_output,
                timeout=timeout,
                text=True,
            )

            output = {
                "returncode": result.returncode,
                "stdout": result.stdout if capture_output else None,
                "stderr": result.stderr if capture_output else None,
            }

            if result.returncode == 0:
                return ToolResult.ok(
                    output=output,
                    command=" ".join(cmd),
                )
            else:
                return ToolResult.fail(
                    error=f"Process exited with code {result.returncode}",
                    command=" ".join(cmd),
                    returncode=result.returncode,
                    stdout=result.stdout if capture_output else None,
                    stderr=result.stderr if capture_output else None,
                )

        except subprocess.TimeoutExpired:
            return ToolResult.fail(
                error=f"Process timed out after {timeout}s",
                command=" ".join(cmd),
            )
        except FileNotFoundError:
            return ToolResult.fail(
                error=f"Executable not found: {exe}",
                command=" ".join(cmd),
            )
        except PermissionError:
            return ToolResult.fail(
                error=f"Permission denied: {exe}",
                command=" ".join(cmd),
            )
        except Exception as e:
            return ToolResult.fail(
                error=f"Error executing process: {e}",
                command=" ".join(cmd),
            )
