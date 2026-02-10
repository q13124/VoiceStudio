"""
File Upload Scanning.

Task 2.2.2: Antivirus integration for uploads.
Scans uploaded files for security threats.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import mimetypes
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class ScanStatus(Enum):
    """Status of file scan."""
    CLEAN = "clean"
    INFECTED = "infected"
    SUSPICIOUS = "suspicious"
    ERROR = "error"
    SKIPPED = "skipped"


class ThreatType(Enum):
    """Types of detected threats."""
    MALWARE = "malware"
    EXECUTABLE = "executable"
    SCRIPT = "script"
    MACRO = "macro"
    ARCHIVE_BOMB = "archive_bomb"
    OVERSIZED = "oversized"
    INVALID_TYPE = "invalid_type"
    SUSPICIOUS_CONTENT = "suspicious_content"


@dataclass
class ScanResult:
    """Result of a file scan."""
    file_path: str
    file_hash: str
    status: ScanStatus
    threats: List[ThreatType] = field(default_factory=list)
    details: str = ""
    scan_time_ms: float = 0
    scanned_at: datetime = field(default_factory=datetime.now)


@dataclass
class ScannerConfig:
    """Configuration for file scanner."""
    max_file_size_mb: int = 100
    allowed_extensions: Set[str] = field(default_factory=lambda: {
        ".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac",  # Audio
        ".txt", ".json", ".csv",  # Text
        ".vsproj",  # Project files
    })
    blocked_extensions: Set[str] = field(default_factory=lambda: {
        ".exe", ".bat", ".cmd", ".ps1", ".sh", ".vbs", ".js",
        ".dll", ".so", ".dylib",
        ".msi", ".deb", ".rpm",
    })
    scan_archives: bool = True
    quarantine_path: str = "data/quarantine"


class FileScanner:
    """
    File upload scanner.
    
    Features:
    - Extension validation
    - Size limits
    - Magic byte checking
    - Suspicious content detection
    - Quarantine support
    """
    
    # Magic bytes for common file types
    MAGIC_BYTES = {
        b"RIFF": [".wav"],
        b"ID3": [".mp3"],
        b"\xff\xfb": [".mp3"],
        b"fLaC": [".flac"],
        b"OggS": [".ogg"],
        b"\x00\x00\x00": [".m4a", ".mp4"],
        b"PK": [".zip", ".docx", ".xlsx"],
        b"\x1f\x8b": [".gz"],
        b"MZ": [".exe", ".dll"],  # Executables - dangerous
    }
    
    # Suspicious patterns in text files
    SUSPICIOUS_PATTERNS = [
        b"<script",
        b"eval(",
        b"exec(",
        b"os.system",
        b"subprocess",
        b"__import__",
        b"powershell",
        b"cmd.exe",
    ]
    
    def __init__(self, config: Optional[ScannerConfig] = None):
        self.config = config or ScannerConfig()
        
        self._quarantine_path = Path(self.config.quarantine_path)
        self._quarantine_path.mkdir(parents=True, exist_ok=True)
        
        self._scan_count = 0
        self._threat_count = 0
    
    async def scan_file(self, file_path: str) -> ScanResult:
        """
        Scan a file for security threats.
        
        Args:
            file_path: Path to file to scan
            
        Returns:
            ScanResult with status and details
        """
        start_time = asyncio.get_event_loop().time()
        path = Path(file_path)
        
        if not path.exists():
            return ScanResult(
                file_path=file_path,
                file_hash="",
                status=ScanStatus.ERROR,
                details="File not found",
            )
        
        # Calculate hash
        file_hash = await self._calculate_hash(path)
        
        threats: List[ThreatType] = []
        details = []
        
        try:
            # Check extension
            ext = path.suffix.lower()
            
            if ext in self.config.blocked_extensions:
                threats.append(ThreatType.EXECUTABLE)
                details.append(f"Blocked extension: {ext}")
            
            if ext not in self.config.allowed_extensions:
                threats.append(ThreatType.INVALID_TYPE)
                details.append(f"Not in allowed extensions: {ext}")
            
            # Check size
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > self.config.max_file_size_mb:
                threats.append(ThreatType.OVERSIZED)
                details.append(f"File size {size_mb:.1f}MB exceeds limit")
            
            # Check magic bytes
            magic_threat = await self._check_magic_bytes(path)
            if magic_threat:
                threats.append(magic_threat)
                details.append("File type mismatch detected")
            
            # Check for suspicious content in text files
            if ext in {".txt", ".json", ".csv"}:
                suspicious = await self._check_suspicious_content(path)
                if suspicious:
                    threats.append(ThreatType.SUSPICIOUS_CONTENT)
                    details.append("Suspicious content patterns detected")
            
            # Determine status
            if threats:
                if ThreatType.EXECUTABLE in threats or ThreatType.MALWARE in threats:
                    status = ScanStatus.INFECTED
                else:
                    status = ScanStatus.SUSPICIOUS
            else:
                status = ScanStatus.CLEAN
            
        except Exception as e:
            logger.error(f"Scan error for {file_path}: {e}")
            status = ScanStatus.ERROR
            details.append(str(e))
        
        scan_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        self._scan_count += 1
        if status != ScanStatus.CLEAN:
            self._threat_count += 1
        
        return ScanResult(
            file_path=file_path,
            file_hash=file_hash,
            status=status,
            threats=threats,
            details="; ".join(details),
            scan_time_ms=scan_time,
        )
    
    async def _calculate_hash(self, path: Path) -> str:
        """Calculate SHA-256 hash of file."""
        sha256 = hashlib.sha256()
        
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        
        return sha256.hexdigest()
    
    async def _check_magic_bytes(self, path: Path) -> Optional[ThreatType]:
        """Check if magic bytes match extension."""
        with open(path, "rb") as f:
            header = f.read(8)
        
        ext = path.suffix.lower()
        
        for magic, extensions in self.MAGIC_BYTES.items():
            if header.startswith(magic):
                # Check if MZ (executable)
                if magic == b"MZ":
                    return ThreatType.EXECUTABLE
                
                # Check if extension matches
                if ext not in extensions:
                    return ThreatType.INVALID_TYPE
                
                return None
        
        return None
    
    async def _check_suspicious_content(self, path: Path) -> bool:
        """Check for suspicious patterns in text files."""
        try:
            with open(path, "rb") as f:
                content = f.read(10000)  # First 10KB
            
            for pattern in self.SUSPICIOUS_PATTERNS:
                if pattern in content.lower():
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def quarantine(self, file_path: str, reason: str = "") -> Optional[str]:
        """
        Move a file to quarantine.
        
        Returns:
            Quarantine path if successful, None otherwise
        """
        source = Path(file_path)
        if not source.exists():
            return None
        
        # Create unique quarantine name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        quarantine_name = f"{timestamp}_{source.name}"
        dest = self._quarantine_path / quarantine_name
        
        try:
            source.rename(dest)
            
            # Write metadata
            meta_path = dest.with_suffix(dest.suffix + ".meta")
            with open(meta_path, "w") as f:
                f.write(f"Original path: {file_path}\n")
                f.write(f"Quarantined at: {datetime.now().isoformat()}\n")
                f.write(f"Reason: {reason}\n")
            
            logger.info(f"Quarantined file: {file_path} -> {dest}")
            return str(dest)
            
        except Exception as e:
            logger.error(f"Quarantine failed: {e}")
            return None
    
    async def scan_directory(
        self,
        directory: str,
        recursive: bool = True,
    ) -> List[ScanResult]:
        """Scan all files in a directory."""
        results = []
        path = Path(directory)
        
        if recursive:
            files = path.rglob("*")
        else:
            files = path.glob("*")
        
        for file_path in files:
            if file_path.is_file():
                result = await self.scan_file(str(file_path))
                results.append(result)
        
        return results
    
    def get_stats(self) -> Dict:
        """Get scanner statistics."""
        return {
            "total_scans": self._scan_count,
            "threats_detected": self._threat_count,
            "allowed_extensions": list(self.config.allowed_extensions),
            "blocked_extensions": list(self.config.blocked_extensions),
            "max_file_size_mb": self.config.max_file_size_mb,
        }


# Global scanner
_scanner: Optional[FileScanner] = None


def get_file_scanner() -> FileScanner:
    """Get or create the global file scanner."""
    global _scanner
    if _scanner is None:
        _scanner = FileScanner()
    return _scanner
