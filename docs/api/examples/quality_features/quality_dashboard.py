"""
Quality Dashboard Example

This example demonstrates how to use the quality dashboard endpoint
to get visual overview of quality metrics, trends, and insights (IDEA 49).
"""

from typing import Optional

import requests

BASE_URL = "http://localhost:8000/api"


def get_quality_dashboard(project_id=None, days=30):
    """
    Get quality metrics dashboard data.
    
    Args:
        project_id: Optional project ID to filter by
        days: Number of days to include in trends (default: 30)
    
    Returns:
        QualityDashboardResponse with overview, trends, distribution, alerts, and insights
    """
    url = f"{BASE_URL}/quality/dashboard"
    
    params = {
        "days": days
    }
    
    if project_id:
        params["project_id"] = project_id
    
    print(f"Fetching quality dashboard data...")
    if project_id:
        print(f"  Project ID: {project_id}")
    print(f"  Time Range: Last {days} days")
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    result = response.json()
    
    print(f"\n✅ Dashboard data received!")
    
    # Overview
    if 'overview' in result:
        overview = result['overview']
        print(f"\n📊 Overview:")
        print(f"  Total Syntheses: {overview.get('total_syntheses', 0)}")
        print(f"  Average MOS Score: {overview.get('average_mos_score', 0):.2f}")
        print(f"  Average Similarity: {overview.get('average_similarity', 0):.3f}")
        print(f"  Average Naturalness: {overview.get('average_naturalness', 0):.3f}")
        
        if 'quality_tier_distribution' in overview:
            print(f"\n  Quality Tier Distribution:")
            tier_dist = overview['quality_tier_distribution']
            for tier, count in tier_dist.items():
                print(f"    {tier.capitalize()}: {count}")
    
    # Trends
    if 'trends' in result:
        trends = result['trends']
        print(f"\n📈 Trends (Last {days} days):")
        
        if trends.get('dates') and len(trends['dates']) > 0:
            print(f"  Data Points: {len(trends['dates'])}")
            
            if trends.get('mos_score'):
                mos_trend = trends['mos_score']
                if len(mos_trend) > 0:
                    print(f"  MOS Score Range: {min(mos_trend):.2f} - {max(mos_trend):.2f}")
                    print(f"  Average MOS: {sum(mos_trend)/len(mos_trend):.2f}")
        else:
            print(f"  No trend data available")
    
    # Distribution
    if 'distribution' in result:
        dist = result['distribution']
        print(f"\n📊 Quality Distribution:")
        
        for metric, distribution in dist.items():
            if distribution:
                print(f"  {metric.replace('_', ' ').title()}:")
                # Show sample of distribution
                sample_items = list(distribution.items())[:5]
                for key, value in sample_items:
                    print(f"    {key}: {value}")
                if len(distribution) > 5:
                    print(f"    ... and {len(distribution) - 5} more")
    
    # Alerts
    if 'alerts' in result and result['alerts']:
        print(f"\n⚠️  Quality Alerts ({len(result['alerts'])}):")
        for alert in result['alerts'][:5]:  # Show first 5
            if isinstance(alert, dict):
                print(f"  - {alert.get('message', alert)}")
            else:
                print(f"  - {alert}")
        if len(result['alerts']) > 5:
            print(f"  ... and {len(result['alerts']) - 5} more alerts")
    else:
        print(f"\n✅ No quality alerts")
    
    # Insights
    if 'insights' in result and result['insights']:
        print(f"\n💡 Quality Insights ({len(result['insights'])}):")
        for insight in result['insights'][:5]:  # Show first 5
            print(f"  • {insight}")
        if len(result['insights']) > 5:
            print(f"  ... and {len(result['insights']) - 5} more insights")
    
    return result


def monitor_quality_trends(project_id=None, days_list=[7, 30, 90]):
    """
    Monitor quality trends across different time ranges.
    
    Args:
        project_id: Optional project ID
        days_list: List of day ranges to check
    
    Returns:
        Dictionary of dashboard data for each time range
    """
    results = {}
    
    for days in days_list:
        print(f"\n{'='*80}")
        print(f"Quality Dashboard - Last {days} Days")
        print(f"{'='*80}")
        
        result = get_quality_dashboard(project_id=project_id, days=days)
        results[f"{days}_days"] = result
    
    # Compare trends
    print(f"\n{'='*80}")
    print("Trend Comparison")
    print(f"{'='*80}")
    
    for days_key, dashboard in results.items():
        days = days_key.replace('_days', '')
        overview = dashboard.get('overview', {})
        avg_mos = overview.get('average_mos_score', 0)
        print(f"  Last {days} days: Average MOS = {avg_mos:.2f}")
    
    return results


# Example usage
if __name__ == "__main__":
    # Example 1: Basic dashboard
    print("Example 1: Basic Quality Dashboard")
    print("-" * 80)
    result = get_quality_dashboard(days=30)
    
    # Example 2: Project-specific dashboard
    print("\n\nExample 2: Project-Specific Dashboard")
    print("-" * 80)
    result = get_quality_dashboard(project_id="project-123", days=30)
    
    # Example 3: Monitor trends across time ranges
    print("\n\nExample 3: Monitor Trends Across Time Ranges")
    print("-" * 80)
    results = monitor_quality_trends(days_list=[7, 30, 90])
    
    # Example 4: Short-term dashboard
    print("\n\nExample 4: Short-Term Dashboard (7 days)")
    print("-" * 80)
    result = get_quality_dashboard(days=7)

