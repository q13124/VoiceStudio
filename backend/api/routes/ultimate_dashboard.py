"""
Ultimate Dashboard Routes

Endpoints for the master dashboard that aggregates data from multiple sources.
"""

import logging
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
    In production, this would make multiple API calls and cache results.
    """
    try:
        # Aggregate data from multiple backend APIs
        import os
        from datetime import datetime, timedelta

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
        
        # Aggregate data from various APIs
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Get projects count
                try:
                    projects_response = await client.get(f"{base_url}/api/projects")
                    if projects_response.status_code == 200:
                        projects_data = projects_response.json()
                        if isinstance(projects_data, list):
                            total_projects = len(projects_data)
                except Exception:
                    ...
                
                # Get profiles count
                try:
                    profiles_response = await client.get(f"{base_url}/api/profiles")
                    if profiles_response.status_code == 200:
                        profiles_data = profiles_response.json()
                        if isinstance(profiles_data, list):
                            total_profiles = len(profiles_data)
                except Exception:
                    ...
                
                # Get batch jobs status
                try:
                    jobs_response = await client.get(f"{base_url}/api/batch/queue/status")
                    if jobs_response.status_code == 200:
                        jobs_data = jobs_response.json()
                        if isinstance(jobs_data, dict):
                            active_jobs = jobs_data.get("active", 0)
                            completed = jobs_data.get("completed", 0)
                            # Estimate today's completed jobs (simplified)
                            completed_jobs_today = max(0, completed // 30)  # Rough estimate
                except Exception:
                    ...
                
                # Get GPU status
                try:
                    gpu_response = await client.get(f"{base_url}/api/gpu-status")
                    if gpu_response.status_code == 200:
                        gpu_data = gpu_response.json()
                        if isinstance(gpu_data, dict):
                            devices = gpu_data.get("devices", [])
                            gpu_available = len(devices) > 0
                            if devices:
                                # Get utilization from first device
                                gpu_utilization = devices[0].get("utilization_percent", 0.0)
                except Exception:
                    ...
                
                # Get analytics summary for audio files estimate
                try:
                    analytics_response = await client.get(f"{base_url}/api/analytics/summary")
                    if analytics_response.status_code == 200:
                        analytics_data = analytics_response.json()
                        if isinstance(analytics_data, dict):
                            total_audio_files = analytics_data.get("total_audio_processed", 0)
                except Exception:
                    ...
        except Exception as e:
            logger.warning(f"Failed to aggregate some dashboard data: {e}")
        
        # Get system metrics
        try:
            process = psutil.Process(os.getpid())
            cpu_utilization = process.cpu_percent(interval=0.1)
            memory_info = process.memory_info()
            system_memory = psutil.virtual_memory()
            memory_usage_percent = system_memory.percent
        except Exception:
            ...
        
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

        # Get recent activities from various sources
        recent_activities = []
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Get recent projects
                try:
                    projects_response = await client.get(f"{base_url}/api/projects?limit=5")
                    if projects_response.status_code == 200:
                        projects_data = projects_response.json()
                        if isinstance(projects_data, list):
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
                except Exception:
                    ...
                
                # Get recent profiles
                try:
                    profiles_response = await client.get(f"{base_url}/api/profiles?limit=3")
                    if profiles_response.status_code == 200:
                        profiles_data = profiles_response.json()
                        if isinstance(profiles_data, list):
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
                except Exception:
                    ...
        except Exception:
            ...
        
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
@cache_response(ttl=10)  # Cache for 10 seconds (summary updates frequently)
async def get_dashboard_summary():
    """Get dashboard summary only."""
    try:
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

