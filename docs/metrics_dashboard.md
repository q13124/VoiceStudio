# VoiceStudio Ultimate - Quality Metrics Dashboard

## Overview

VoiceStudio Ultimate features a comprehensive quality metrics dashboard that provides real-time monitoring and analysis of voice cloning performance, quality metrics, and system health.

## Features

- **Real-Time Monitoring**: Live updates of quality metrics and performance data
- **Interactive Charts**: Dynamic charts with Plotly for voice similarity, engine performance, audio quality, and processing time
- **Quality Alerts**: Automated alerts for quality issues and performance degradation
- **Multi-Engine Support**: Performance comparison across different voice cloning engines
- **Export Capabilities**: Export metrics data in JSON and CSV formats
- **REST API**: Complete API for metrics collection and retrieval
- **Database Storage**: Persistent storage of metrics data with SQLite
- **Customizable Thresholds**: Configurable quality thresholds and alert levels

## Dashboard Components

### Summary Cards
- **Overall Quality**: Average voice similarity score
- **Success Rate**: Percentage of successful operations
- **Average Processing Time**: Mean processing time in seconds
- **Active Engines**: Number of active voice cloning engines

### Charts
- **Voice Similarity Over Time**: Line chart showing similarity trends
- **Engine Performance Comparison**: Bar chart comparing engine performance
- **Audio Quality Distribution**: Pie chart showing quality level distribution
- **Processing Time Distribution**: Histogram of processing times

### Alerts
- **Quality Alerts**: Real-time alerts for quality issues
- **Performance Alerts**: Alerts for slow processing or low success rates
- **System Alerts**: System health and error alerts

## Quality Metrics

### Voice Similarity
- **Metric Type**: Voice similarity score (0.0 - 1.0)
- **Description**: Measures similarity between cloned and reference voices
- **Quality Levels**: Excellent (0.9+), Good (0.8+), Fair (0.7+), Poor (0.6+), Very Poor (<0.6)

### Audio Quality
- **Metric Type**: Audio quality assessment (0.0 - 1.0)
- **Description**: Overall audio quality including clarity, naturalness, and artifacts
- **Quality Levels**: Based on comprehensive audio analysis

### Processing Time
- **Metric Type**: Processing time in seconds
- **Description**: Time taken to complete voice cloning operations
- **Thresholds**: Alert if processing time exceeds 60 seconds

### Success Rate
- **Metric Type**: Success rate (0.0 - 1.0)
- **Description**: Percentage of successful voice cloning operations
- **Thresholds**: Alert if success rate drops below 80%

## API Endpoints

### Add Metric

#### POST /api/v1/metrics/add-metric

Add a quality metric to the dashboard.

**Request:**
```json
{
  "metric_type": "voice_similarity",
  "value": 0.85,
  "engine": "xtts",
  "language": "en",
  "user_id": "user123",
  "session_id": "session456",
  "metadata": {
    "text_length": 50,
    "reference_duration": 3.2
  }
}
```

**Response:**
```json
{
  "success": true,
  "metric_id": "metric_1642780800.123",
  "message": "Metric added successfully"
}
```

### Get Metrics

#### GET /api/v1/metrics/metrics

Get quality metrics with optional filtering.

**Parameters:**
- `metric_type`: Filter by metric type
- `engine`: Filter by engine
- `language`: Filter by language
- `hours`: Time range in hours (default: 24)
- `limit`: Maximum number of results (default: 100)

**Response:**
```json
{
  "success": true,
  "metrics": [
    {
      "metric_id": "metric_1642780800.123",
      "metric_type": "voice_similarity",
      "value": 0.85,
      "quality_level": "good",
      "timestamp": "2025-01-21T12:00:00Z",
      "engine": "xtts",
      "language": "en",
      "user_id": "user123",
      "session_id": "session456",
      "metadata": {
        "text_length": 50,
        "reference_duration": 3.2
      }
    }
  ],
  "total_count": 1,
  "filtered_count": 1
}
```

### Get Summary

#### GET /api/v1/metrics/summary

Get metrics summary statistics.

**Response:**
```json
{
  "success": true,
  "summary": {
    "total_metrics": 150,
    "time_range_hours": 24,
    "engines": ["xtts", "openvoice", "cosyvoice"],
    "languages": ["en", "es", "fr"],
    "metric_types": ["voice_similarity", "audio_quality", "processing_time"],
    "averages": {
      "voice_similarity": {
        "count": 50,
        "average": 0.87,
        "min": 0.65,
        "max": 0.98
      },
      "audio_quality": {
        "count": 50,
        "average": 0.82,
        "min": 0.58,
        "max": 0.95
      }
    },
    "quality_distribution": {
      "excellent": 15,
      "good": 25,
      "fair": 8,
      "poor": 2,
      "very_poor": 0
    }
  }
}
```

### Get Alerts

#### GET /api/v1/metrics/alerts

Get quality alerts.

**Response:**
```json
{
  "success": true,
  "alerts": [
    {
      "id": "alert_123",
      "message": "Low voice similarity detected",
      "severity": "high",
      "timestamp": "2025-01-21T12:30:00Z",
      "data": {
        "average_similarity": 0.55,
        "threshold": 0.6
      }
    }
  ],
  "total_count": 1
}
```

### Export Metrics

#### GET /api/v1/metrics/export

Export metrics data.

**Parameters:**
- `format`: Export format ("json" or "csv")
- `hours`: Time range in hours (default: 24)
- `metric_type`: Filter by metric type

**Response:**
```json
{
  "success": true,
  "format": "json",
  "data": [...],
  "count": 150
}
```

## Command Line Usage

### Launch Dashboard

```bash
python tools/launch_metrics_dashboard.py \
  --host 127.0.0.1 \
  --port 8050 \
  --debug
```

### Generate Sample Data

```bash
python tools/launch_metrics_dashboard.py \
  --generate-samples 100
```

### Worker Usage

```bash
# Add metric
python workers/metrics_dashboard_worker.py \
  --action add \
  --metric-data metric.json

# Get summary
python workers/metrics_dashboard_worker.py \
  --action summary \
  --hours 24

# Get alerts
python workers/metrics_dashboard_worker.py \
  --action alerts \
  --limit 50
```

## Configuration

### Dashboard Settings

```json
{
  "dashboard": {
    "enabled": true,
    "host": "127.0.0.1",
    "port": 8050,
    "refresh_interval": 30,
    "max_data_points": 1000,
    "auto_refresh": true,
    "theme": "bootstrap"
  }
}
```

### Quality Thresholds

```json
{
  "quality_thresholds": {
    "excellent": 0.9,
    "good": 0.8,
    "fair": 0.7,
    "poor": 0.6,
    "very_poor": 0.0
  }
}
```

### Alert Thresholds

```json
{
  "alert_thresholds": {
    "low_quality": 0.6,
    "slow_processing": 60.0,
    "low_success_rate": 0.8,
    "high_error_rate": 0.1
  }
}
```

## Integration

### VoiceStudio Integration
- **Automatic Metrics**: Metrics automatically collected from voice cloning operations
- **Real-Time Updates**: Dashboard updates in real-time as operations complete
- **Engine Monitoring**: Performance monitoring across all voice cloning engines
- **Quality Tracking**: Continuous quality assessment and tracking

### API Integration
- **REST API**: Complete REST API for metrics collection and retrieval
- **WebSocket Support**: Real-time updates via WebSocket connections
- **Export Options**: Multiple export formats for data analysis
- **Custom Dashboards**: Build custom dashboards using the API

## Performance

### Dashboard Performance
- **Refresh Rate**: 30-second auto-refresh interval
- **Data Points**: Up to 1000 data points in memory
- **Database**: SQLite for persistent storage
- **Charts**: Plotly for interactive visualizations

### Scalability
- **Concurrent Users**: Supports multiple concurrent dashboard users
- **Data Retention**: Configurable data retention periods
- **Storage**: Efficient storage with automatic cleanup
- **Memory Usage**: Optimized memory usage for large datasets

## Best Practices

### Metrics Collection
- **Consistent Timing**: Collect metrics at consistent intervals
- **Quality Validation**: Validate metric values before storage
- **Error Handling**: Implement proper error handling for failed operations
- **Metadata**: Include relevant metadata for better analysis

### Dashboard Usage
- **Regular Monitoring**: Monitor dashboard regularly for quality issues
- **Alert Configuration**: Configure appropriate alert thresholds
- **Data Export**: Export data regularly for backup and analysis
- **Performance Tuning**: Adjust refresh rates based on system performance

### Integration
- **API Usage**: Use API endpoints for custom integrations
- **WebSocket**: Use WebSocket for real-time updates
- **Batch Operations**: Use batch operations for bulk metrics
- **Error Recovery**: Implement error recovery for failed operations

## Use Cases

### Quality Assurance
- **Real-Time Monitoring**: Monitor voice cloning quality in real-time
- **Performance Tracking**: Track performance across different engines
- **Quality Alerts**: Receive alerts for quality issues
- **Trend Analysis**: Analyze quality trends over time

### System Optimization
- **Performance Analysis**: Analyze processing times and bottlenecks
- **Engine Comparison**: Compare performance across engines
- **Resource Monitoring**: Monitor system resource usage
- **Capacity Planning**: Plan system capacity based on usage patterns

### Research and Development
- **Quality Research**: Research voice cloning quality factors
- **Performance Studies**: Study performance characteristics
- **Algorithm Development**: Develop and test new algorithms
- **Benchmarking**: Benchmark against quality standards

---

**Quality Metrics Dashboard** - Comprehensive voice cloning quality monitoring and analysis
