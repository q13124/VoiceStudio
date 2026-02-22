"""
MCP Client for PDF Unlocker Server

This client integrates the mcp-unlock-pdf server to provide PDF reading
and text extraction capabilities for VoiceStudio.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class PDFUnlockerClient:
    """Client for interacting with the mcp-unlock-pdf MCP server."""

    def __init__(self, server_path: str | None = None):
        """
        Initialize the PDF Unlocker client.

        Args:
            server_path: Path to the mcp-unlock-pdf server directory.
                        Defaults to backend/mcp_servers/mcp-unlock-pdf
        """
        if server_path is None:
            # Default to the integrated server location
            base_dir = Path(__file__).parent.parent.parent
            server_path = str(base_dir / "backend" / "mcp_servers" / "mcp-unlock-pdf")

        self.server_path = Path(server_path)
        self.server_available = self._check_server_available()

    def _check_server_available(self) -> bool:
        """Check if the MCP server is available."""
        main_py = self.server_path / "main.py"
        return main_py.exists()

    def read_pdf(
        self, file_path: str, password: str | None = None, pages: list[int] | None = None
    ) -> dict[str, Any]:
        """
        Read a PDF file and extract its text.

        Args:
            file_path: Path to the PDF file
            password: Optional password for protected PDFs
            pages: Optional list of page numbers to extract (1-indexed)

        Returns:
            Dictionary containing PDF content and metadata
        """
        if not self.server_available:
            return {
                "success": False,
                "error": "PDF unlocker MCP server not available. Please ensure it's installed.",
            }

        # Normalize file path
        file_path = os.path.abspath(os.path.expanduser(file_path))

        if not os.path.exists(file_path):
            return {"success": False, "error": f"File not found: {file_path}"}

        try:
            # Use PyPDF2 directly (same library the MCP server uses)
            # This avoids subprocess overhead for simple operations
            import PyPDF2

            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)

                # Check if PDF is encrypted
                is_encrypted = pdf_reader.is_encrypted

                # Try to decrypt if necessary
                if is_encrypted:
                    if password is None:
                        return {
                            "success": False,
                            "error": "This PDF is password-protected. Please provide a password.",
                            "is_encrypted": True,
                            "password_required": True,
                        }
                    decrypt_success = pdf_reader.decrypt(password)
                    if not decrypt_success:
                        return {
                            "success": False,
                            "error": "Incorrect password or PDF could not be decrypted",
                            "is_encrypted": True,
                            "password_required": True,
                        }

                # Extract metadata
                metadata = {}
                if pdf_reader.metadata:
                    for key, value in pdf_reader.metadata.items():
                        if key.startswith("/"):
                            metadata[key[1:]] = value
                        else:
                            metadata[key] = value

                # Determine which pages to extract
                total_pages = len(pdf_reader.pages)
                pages_to_extract = pages or list(range(1, total_pages + 1))

                # Convert to 0-indexed for internal use
                zero_indexed_pages = [p - 1 for p in pages_to_extract if 1 <= p <= total_pages]

                # Extract content from requested pages
                content = {}
                for page_number in zero_indexed_pages:
                    page = pdf_reader.pages[page_number]
                    content[page_number + 1] = page.extract_text()

                return {
                    "success": True,
                    "is_encrypted": is_encrypted,
                    "total_pages": total_pages,
                    "extracted_pages": list(content.keys()),
                    "metadata": metadata,
                    "content": content,
                }

        except ImportError:
            logger.warning("PyPDF2 not available, falling back to MCP server subprocess")
            # Note: This would require async implementation
            return {
                "success": False,
                "error": "PyPDF2 library not available. Please install it: pip install PyPDF2",
            }
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            return {"success": False, "error": f"Error processing PDF: {e!s}"}

    def extract_text_for_tts(
        self, pdf_result: dict[str, Any], page_range: tuple | None = None
    ) -> str:
        """
        Extract text from PDF result for text-to-speech synthesis.

        Args:
            pdf_result: Result from read_pdf()
            page_range: Optional tuple (start_page, end_page) to extract specific pages

        Returns:
            Combined text from all pages (or specified range)
        """
        if not pdf_result.get("success"):
            return ""

        content = pdf_result.get("content", {})

        if page_range:
            start_page, end_page = page_range
            pages_to_extract = [p for p in content if start_page <= p <= end_page]
        else:
            pages_to_extract = sorted(content.keys())

        text_parts = []
        for page_num in pages_to_extract:
            page_text = content.get(page_num, "").strip()
            if page_text:
                text_parts.append(page_text)

        return "\n\n".join(text_parts)

    def get_page_count(self, file_path: str) -> int:
        """
        Get the number of pages in a PDF without extracting all content.

        Args:
            file_path: Path to the PDF file

        Returns:
            Number of pages, or 0 if error
        """
        result = self.read_pdf(file_path, pages=[1])  # Just read first page for metadata
        if result.get("success"):
            return int(result.get("total_pages", 0))
        return 0
