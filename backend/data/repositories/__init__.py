"""
Data Repositories.

Backend-Frontend Integration Plan - Phase 1.
Database-backed repositories replacing in-memory storage.
"""

from backend.data.repositories.job_repository import JobEntity, JobRepository, JobStatus
from backend.data.repositories.library_repository import (
    AssetType,
    LibraryAssetEntity,
    LibraryAssetRepository,
    LibraryFolderEntity,
    LibraryFolderRepository,
    get_library_asset_repository,
    get_library_folder_repository,
)
from backend.data.repositories.session_repository import SessionEntity, SessionRepository
from backend.data.repositories.training_repository import TrainingJobEntity, TrainingJobRepository
from backend.data.repositories.transcription_repository import (
    TranscriptionEntity,
    TranscriptionRepository,
    get_transcription_repository,
)

__all__ = [
    "AssetType",
    "JobEntity",
    "JobRepository",
    "JobStatus",
    "LibraryAssetEntity",
    "LibraryAssetRepository",
    "LibraryFolderEntity",
    "LibraryFolderRepository",
    "SessionEntity",
    "SessionRepository",
    "TrainingJobEntity",
    "TrainingJobRepository",
    "TranscriptionEntity",
    "TranscriptionRepository",
    "get_library_asset_repository",
    "get_library_folder_repository",
    "get_transcription_repository",
]
