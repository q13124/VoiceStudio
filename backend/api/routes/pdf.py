"""
PDF Processing Routes

Endpoints for reading and extracting text from PDF files (protected and unprotected).
Useful for extracting text from PDFs for voice synthesis.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

from ...mcp_bridge.pdf_unlocker_client import PDFUnlockerClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pdf", tags=["pdf"])

# Initialize PDF unlocker client
_pdf_client: Optional[PDFUnlockerClient] = None


def get_pdf_client() -> PDFUnlockerClient:
    """Get or create PDF unlocker client."""
    global _pdf_client
    if _pdf_client is None:
        _pdf_client = PDFUnlockerClient()
    return _pdf_client


class PDFReadRequest(BaseModel):
    """Request to read a PDF file."""

    file_path: str
    password: Optional[str] = None
    pages: Optional[List[int]] = None


class PDFReadResponse(BaseModel):
    """Response from reading a PDF."""

    success: bool
    is_encrypted: bool
    total_pages: int
    extracted_pages: List[int]
    metadata: dict
    content: dict
    error: Optional[str] = None
    password_required: Optional[bool] = None


class PDFTextExtractRequest(BaseModel):
    """Request to extract text from PDF for TTS."""

    file_path: str
    password: Optional[str] = None
    page_range: Optional[tuple] = None


class PDFTextExtractResponse(BaseModel):
    """Response with extracted text."""

    success: bool
    text: str
    page_count: int
    error: Optional[str] = None


@router.post("/read", response_model=PDFReadResponse)
async def read_pdf(request: PDFReadRequest):
    """
    Read a PDF file and extract its text content.

    Works with both protected and unprotected PDFs.
    """
    try:
        client = get_pdf_client()
        result = client.read_pdf(
            file_path=request.file_path,
            password=request.password,
            pages=request.pages
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to read PDF")
            )

        return PDFReadResponse(
            success=result.get("success", False),
            is_encrypted=result.get("is_encrypted", False),
            total_pages=result.get("total_pages", 0),
            extracted_pages=result.get("extracted_pages", []),
            metadata=result.get("metadata", {}),
            content=result.get("content", {}),
            error=result.get("error"),
            password_required=result.get("password_required")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading PDF: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error reading PDF: {str(e)}"
        ) from e


@router.post("/extract-text", response_model=PDFTextExtractResponse)
async def extract_text_for_tts(request: PDFTextExtractRequest):
    """
    Extract text from a PDF file for text-to-speech synthesis.

    This endpoint is optimized for TTS use cases, returning clean text
    that can be directly used for voice synthesis.
    """
    try:
        client = get_pdf_client()
        
        # Read the PDF
        pdf_result = client.read_pdf(
            file_path=request.file_path,
            password=request.password
        )

        if not pdf_result.get("success"):
            return PDFTextExtractResponse(
                success=False,
                text="",
                page_count=0,
                error=pdf_result.get("error", "Failed to read PDF")
            )

        # Extract text for TTS
        text = client.extract_text_for_tts(
            pdf_result=pdf_result,
            page_range=request.page_range
        )

        return PDFTextExtractResponse(
            success=True,
            text=text,
            page_count=pdf_result.get("total_pages", 0),
            error=None
        )
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting text: {str(e)}"
        ) from e


@router.get("/page-count")
async def get_page_count(file_path: str):
    """
    Get the number of pages in a PDF without extracting all content.

    Useful for quick PDF information retrieval.
    """
    try:
        client = get_pdf_client()
        page_count = client.get_page_count(file_path)
        
        return {
            "success": True,
            "file_path": file_path,
            "page_count": page_count
        }
    except Exception as e:
        logger.error(f"Error getting page count: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting page count: {str(e)}"
        ) from e


@router.get("/health")
async def pdf_health_check():
    """Check if PDF unlocker service is available."""
    try:
        client = get_pdf_client()
        available = client.server_available
        
        return {
            "service": "pdf-unlocker",
            "available": available,
            "server_path": str(client.server_path)
        }
    except Exception as e:
        logger.error(f"Error checking PDF service health: {e}")
        return {
            "service": "pdf-unlocker",
            "available": False,
            "error": str(e)
        }

