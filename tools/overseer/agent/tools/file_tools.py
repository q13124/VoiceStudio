"""
File Tools

Governed file operations: read, write, delete.
"""

from pathlib import Path

from .base_tool import BaseTool, ToolResult


class ReadFileTool(BaseTool):
    """Read a file from the filesystem."""

    name = "ReadFile"
    description = "Read contents of a file"
    required_params = ("path",)
    optional_params = {"encoding": "utf-8", "binary": False}

    def execute(self, **params) -> ToolResult:
        """
        Read a file.

        Args:
            path: Path to the file
            encoding: Text encoding (default: utf-8)
            binary: If True, read as binary

        Returns:
            ToolResult with file contents
        """
        path = Path(params["path"])
        encoding = self.get_param(params, "encoding", "utf-8")
        binary = self.get_param(params, "binary", False)

        try:
            if not path.exists():
                return ToolResult.fail(f"File not found: {path}")

            if not path.is_file():
                return ToolResult.fail(f"Not a file: {path}")

            content = path.read_bytes() if binary else path.read_text(encoding=encoding)

            return ToolResult.ok(
                output=content,
                path=str(path),
                size=path.stat().st_size,
            )

        except PermissionError:
            return ToolResult.fail(f"Permission denied: {path}")
        except Exception as e:
            return ToolResult.fail(f"Error reading file: {e}")


class WriteFileTool(BaseTool):
    """Write content to a file."""

    name = "WriteFile"
    description = "Write contents to a file"
    required_params = ("path", "content")
    optional_params = {"encoding": "utf-8", "binary": False, "create_dirs": True}

    def execute(self, **params) -> ToolResult:
        """
        Write to a file.

        Args:
            path: Path to the file
            content: Content to write
            encoding: Text encoding (default: utf-8)
            binary: If True, write as binary
            create_dirs: If True, create parent directories

        Returns:
            ToolResult with write confirmation
        """
        path = Path(params["path"])
        content = params["content"]
        encoding = self.get_param(params, "encoding", "utf-8")
        binary = self.get_param(params, "binary", False)
        create_dirs = self.get_param(params, "create_dirs", True)

        try:
            # Create parent directories if needed
            if create_dirs and not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)

            if binary:
                if isinstance(content, str):
                    content = content.encode(encoding)
                path.write_bytes(content)
            else:
                if isinstance(content, bytes):
                    content = content.decode(encoding)
                path.write_text(content, encoding=encoding)

            return ToolResult.ok(
                output=f"Wrote {len(content)} bytes to {path}",
                path=str(path),
                size=len(content),
            )

        except PermissionError:
            return ToolResult.fail(f"Permission denied: {path}")
        except Exception as e:
            return ToolResult.fail(f"Error writing file: {e}")


class DeleteFileTool(BaseTool):
    """Delete a file from the filesystem."""

    name = "DeleteFile"
    description = "Delete a file"
    required_params = ("path",)
    optional_params = {"missing_ok": True}

    def execute(self, **params) -> ToolResult:
        """
        Delete a file.

        Args:
            path: Path to the file
            missing_ok: If True, don't error if file doesn't exist

        Returns:
            ToolResult with deletion confirmation
        """
        path = Path(params["path"])
        missing_ok = self.get_param(params, "missing_ok", True)

        try:
            if not path.exists():
                if missing_ok:
                    return ToolResult.ok(
                        output=f"File already deleted: {path}",
                        path=str(path),
                    )
                else:
                    return ToolResult.fail(f"File not found: {path}")

            if not path.is_file():
                return ToolResult.fail(f"Not a file: {path}")

            size = path.stat().st_size
            path.unlink()

            return ToolResult.ok(
                output=f"Deleted {path}",
                path=str(path),
                size=size,
            )

        except PermissionError:
            return ToolResult.fail(f"Permission denied: {path}")
        except Exception as e:
            return ToolResult.fail(f"Error deleting file: {e}")
