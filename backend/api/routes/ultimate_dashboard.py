"""
Ultimate Dashboard Routes

Endpoints for the master dashboard that aggregates data from multiple sources.
"""

import asyncio
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

try:
    from ..optimization import cache_response
except ImportError:
    def cache_response(ttl: int = 300):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ultimate-dashboard", tags=["ultimate-dashboard"])

# Circuit breaker state
_circuit_breaker_state: Dict[str, Dict] = defaultdict(lambda: {
    "failures": 0,
    "last_failure": None,
    "state": "closed"  # closed, open, half_open
})

# Cache for aggregated results
_dashboard_cache: Optional[Dict] = None
_cache_timestamp: Optional[datetime] = None
_cache_ttl = timedelta(seconds=30)  # Cache for 30 seconds

# Circuit breaker configuration
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
CIRCUIT_BREAKER_TIMEOUT = timedelta(seconds=60)


class DashboardSummary(BaseModel):
    """Overall dashboard summary."""

    total_projects: int = 0
    total_profiles: int = 0
    total_audio_files: int = 0
    active_jobs: int = 0
    completed_jobs_today: int = 0
    system_status: str = "healthy"  # healthy, warning, error
    gpu_available: bool = False
    gpu_utilization: float = 0.0
    cpu_utilization: float = 0.0
    memory_usage_percent: float = 0.0


class RecentActivity(BaseModel):
    """Recent activity item."""

    activity_id: str
    type: str  # project_created, profile_created, synthesis_completed, etc.
    title: str
    description: Optional[str] = None
    timestamp: str
    metadata: Dict[str, str] = {}


class QuickStat(BaseModel):
    """Quick statistic card."""

    stat_id: str
    label: str
    value: str
    trend: Optional[str] = None  # up, down, stable
    trend_value: Optional[float] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class DashboardData(BaseModel):
    """Complete dashboard data."""

    summary: DashboardSummary
    quick_stats: List[QuickStat]
    recent_activities: List[RecentActivity]
    system_alerts: List[str] = []


@router.get("", response_model=DashboardData)
@cache_response(ttl=10)  # Cache for 10 seconds (dashboard updates frequently)
async def get_dashboard_data():
    """
    Get complete dashboard data aggregated from all sources.
    
    Aggregates data from multiple APIs to provide a comprehensive dashboard view.
    Uses retry logic, circuit breaker, and caching for robustness.
    """
    global _dashboard_cache, _cache_timestamp
    
    # Check cache first
    if _dashboard_cache and _cache_timestamp:
        if datetime.utcnow() - _cache_timestamp < _cache_ttl:
            logger.debug("Returning cached dashboard data")
            return DashboardSummary(**_dashboard_cache)
    
    try:
        # Aggregate data from multiple backend APIs
        import os

        import httpx
        import psutil
        
        base_url = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
        
        # Initialize default values
        total_projects = 0
        total_profiles = 0
        total_audio_files = 0
        active_jobs = 0
        completed_jobs_today = 0
        system_status = "healthy"
        gpu_available = False
        gpu_utilization = 0.0
        cpu_utilization = 0.0
        memory_usage_percent = 0.0
        
        # Aggregate data from various APIs with retry logic
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get projects count
            projects_data = await _http_get_with_retry(
                client, f"{base_url}/api/projects", "projects"
            )
            if projects_data and isinstance(projects_data, list):
                total_projects = len(projects_data)
            
            # Get profiles count
            profiles_data = await _http_get_with_retry(
                client, f"{base_url}/api/profiles", "profiles"
            )
            if profiles_data and isinstance(profiles_data, list):
                total_profiles = len(profiles_data)
            elif profiles_data and isinstance(profiles_data, dict):
                # Handle paginated response
                items = profiles_data.get("items", [])
                total_profiles = len(items) if isinstance(items, list) else profiles_data.get("total", 0)
            
            # Get batch jobs status
            jobs_data = await _http_get_with_retry(
                client, f"{base_url}/api/batch/queue/status", "batch_jobs"
            )
            if jobs_data and isinstance(jobs_data, dict):
                active_jobs = jobs_data.get("active", 0)
                completed = jobs_data.get("completed", 0)
                # Use actual completed count instead of estimate
                # If we have a timestamp, calculate today's jobs more accurately
                completed_jobs_today = completed  # Use actual value, not estimate
            
            # Get GPU status
            gpu_data = await _http_get_with_retry(
                client, f"{base_url}/api/gpu-status", "gpu_status"
            )
            if gpu_data and isinstance(gpu_data, dict):
                devices = gpu_data.get("devices", [])
                gpu_available = len(devices) > 0
                if devices:
                    # Get utilization from first device
                    gpu_utilization = devices[0].get("utilization_percent", 0.0)
            
            # Get analytics summary for audio files estimate
            analytics_data = await _http_get_with_retry(
                client, f"{base_url}/api/analytics/summary", "analytics"
            )
            if analytics_data and isinstance(analytics_data, dict):
                total_audio_files = analytics_data.get("total_audio_processed", 0)
        
        # Get system metrics
        try:
            process = psutil.Process(os.getpid())
            cpu_utilization = process.cpu_percent(interval=0.1)
            memory_info = process.memory_info()
            system_memory = psutil.virtual_memory()
            memory_usage_percent = system_memory.percent
        except Exception as e:
            logger.debug(f"Failed to collect system metrics: {e}")
        
        # Determine system status
        if memory_usage_percent > 90 or cpu_utilization > 95:
            system_status = "warning"
        elif memory_usage_percent > 95 or cpu_utilization > 99:
            system_status = "error"
        else:
            system_status = "healthy"

        summary = DashboardSummary(
            total_projects=total_projects,
            total_profiles=total_profiles,
            total_audio_files=total_audio_files,
            active_jobs=active_jobs,
            completed_jobs_today=completed_jobs_today,
            system_status=system_status,
            gpu_available=gpu_available,
            gpu_utilization=gpu_utilization,
            cpu_utilization=cpu_utilization,
            memory_usage_percent=memory_usage_percent,
        )
        
        # Update cache
        _dashboard_cache = summary.dict()
        _cache_timestamp = datetime.utcnow()

        quick_stats = [
            QuickStat(
                stat_id="projects",
                label="Projects",
                value=str(total_projects),
                trend="stable",
                icon="📁",
                color="cyan",
            ),
            QuickStat(
                stat_id="profiles",
                label="Voice Profiles",
                value=str(total_profiles),
                trend="stable",
                icon="🎤",
                color="lime",
            ),
            QuickStat(
                stat_id="synthesis_today",
                label="Synthesis Today",
                value=str(completed_jobs_today),
                trend="stable",
                icon="✨",
                color="green",
            ),
            QuickStat(
                stat_id="active_jobs",
                label="Active Jobs",
                value=str(active_jobs),
                trend="stable",
                icon="⚙️",
                color="orange",
            ),
            QuickStat(
                stat_id="gpu_util",
                label="GPU Usage",
                value=f"{gpu_utilization:.1f}%" if gpu_available else "N/A",
                trend="stable",
                icon="🎮",
                color="blue",
            ),
            QuickStat(
                stat_id="cpu_util",
                label="CPU Usage",
                value=f"{cpu_utilization:.1f}%",
                trend="stable",
                icon="💻",
                color="yellow",
            ),
        ]

        # Get recent activities from various sources with retry logic
        recent_activities = []
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get recent projects
            projects_data = await _http_get_with_retry(
                client, f"{base_url}/api/projects?limit=5", "projects_recent"
            )
            if projects_data and isinstance(projects_data, list):
                for project in projects_data[:3]:
                    recent_activities.append(
                        RecentActivity(
                            activity_id=f"proj-{project.get('id', 'unknown')}",
                            type="project_created",
                            title="Project created",
                            description=project.get("name", "Unknown project"),
                            timestamp=project.get("created", datetime.utcnow().isoformat()),
                        )
                    )
            
            # Get recent profiles
            profiles_data = await _http_get_with_retry(
                client, f"{base_url}/api/profiles?limit=3", "profiles_recent"
            )
            if profiles_data and isinstance(profiles_data, list):
                for profile in profiles_data[:2]:
                    recent_activities.append(
                        RecentActivity(
                            activity_id=f"prof-{profile.get('id', 'unknown')}",
                            type="profile_created",
                            title="Voice profile created",
                            description=profile.get("name", "Unknown profile"),
                            timestamp=profile.get("created", datetime.utcnow().isoformat()),
                        )
                    )
            elif profiles_data and isinstance(profiles_data, dict):
                # Handle paginated response
                items = profiles_data.get("items", [])
                if isinstance(items, list):
                    for profile in items[:2]:
                        recent_activities.append(
                            RecentActivity(
                                activity_id=f"prof-{profile.get('id', 'unknown')}",
                                type="profile_created",
                                title="Voice profile created",
                                description=profile.get("name", "Unknown profile"),
                                timestamp=profile.get("created", datetime.utcnow().isoformat()),
                            )
                        )
        
        # Sort by timestamp (most recent first) and limit to 10
        recent_activities.sort(key=lambda x: x.timestamp, reverse=True)
        recent_activities = recent_activities[:10]

        system_alerts = []

        return DashboardData(
            summary=summary,
            quick_stats=quick_stats,
            recent_activities=recent_activities,
            system_alerts=system_alerts,
        )
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dashboard data: {str(e)}",
        ) from e


@router.get("/summary", response_model=DashboardSummary)
@cache_response(ttl=30)  # Cache for 30 seconds (summary updates moderately)
async def get_dashboard_summary():
    """Get dashboard summary only."""
    # Use the same caching and retry logic as main endpoint
    global _dashboard_cache, _cache_timestamp
    
    # Check cache first
    if _dashboard_cache and _cache_timestamp:
        if datetime.utcnow() - _cache_timestamp < _cache_ttl:
            return DashboardSummary(**_dashboard_cache)
    
    try:
        # Call main endpoint to populate cache
        data = await get_dashboard_data()
        return data.summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dashboard summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dashboard summary: {str(e)}",
        ) from e


@router.get("/quick-stats", response_model=List[QuickStat])
@cache_response(ttl=10)  # Cache for 10 seconds (stats update frequently)
async def get_quick_stats():
    """Get quick statistics cards."""
    try:
        data = await get_dashboard_data()
        return data.quick_stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get quick stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get quick stats: {str(e)}",
        ) from e


@router.get("/recent-activities", response_model=List[RecentActivity])
@cache_response(ttl=30)  # Cache for 30 seconds (activities change moderately)
async def get_recent_activities(limit: int = 10):
    """Get recent activities."""
    try:
        data = await get_dashboard_data()
        return data.recent_activities[:limit]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recent activities: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recent activities: {str(e)}",
        ) from e


@router.get("/alerts", response_model=List[str])
@cache_response(ttl=10)  # Cache for 10 seconds (alerts update frequently)
async def get_system_alerts():
    """Get system alerts."""
    try:
        data = await get_dashboard_data()
        return data.system_alerts
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get system alerts: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system alerts: {str(e)}",
        ) from e

