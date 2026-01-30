using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Shapes;
using System;
using System.Collections.Generic;
using System.Linq;
using VoiceStudio.Core.Models;
using Windows.Foundation;
using Colors = Microsoft.UI.Colors;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Visual timeline control for batch processing queue (IDEA 23).
    /// Shows visual representation of batch jobs in queue with estimated completion times.
    /// </summary>
    public sealed partial class BatchQueueTimelineControl : UserControl
    {
        private const double PIXELS_PER_SECOND = 50.0;
        private const double MIN_ZOOM = 0.5;
        private const double MAX_ZOOM = 5.0;
        private const double DEFAULT_ZOOM = 1.0;
        private const double ESTIMATED_SECONDS_PER_CHARACTER = 0.05; // Rough estimate: 0.05 seconds per character
        
        private double _zoomLevel = DEFAULT_ZOOM;
        private double _totalDuration = 0.0;
        private List<JobTimelineBlock> _jobBlocks = new();
        private Point? _lastPointerPosition;
        
        public BatchQueueTimelineControl()
        {
            this.InitializeComponent();
            UpdateTimeScale();
        }
        
        /// <summary>
        /// Job timeline block data.
        /// </summary>
        public class JobTimelineBlock
        {
            public string JobId { get; set; } = string.Empty;
            public string JobName { get; set; } = string.Empty;
            public string EngineId { get; set; } = string.Empty;
            public string VoiceProfileId { get; set; } = string.Empty;
            public double StartTime { get; set; }
            public double EstimatedDuration { get; set; }
            public double Progress { get; set; } // 0.0 to 1.0
            public JobStatus Status { get; set; } = JobStatus.Pending;
            public string Priority { get; set; } = "medium"; // high, medium, low
            public int RowIndex { get; set; }
        }
        
        /// <summary>
        /// Total estimated duration of the queue in seconds.
        /// </summary>
        public double TotalDuration
        {
            get => _totalDuration;
            set
            {
                _totalDuration = value;
                UpdateTimeline();
            }
        }
        
        /// <summary>
        /// Zoom level (1.0 = normal, 2.0 = 2x zoom, etc.).
        /// </summary>
        public double ZoomLevel
        {
            get => _zoomLevel;
            set
            {
                _zoomLevel = Math.Clamp(value, MIN_ZOOM, MAX_ZOOM);
                UpdateTimeline();
            }
        }
        
        /// <summary>
        /// Estimated completion time for entire queue in seconds.
        /// </summary>
        public double EstimatedQueueCompletionTime
        {
            get
            {
                if (_jobBlocks.Count == 0)
                    return 0.0;
                
                // Calculate based on remaining jobs (pending + running)
                double totalTime = 0.0;
                double currentTime = 0.0;
                
                foreach (var job in _jobBlocks.OrderBy(j => j.StartTime))
                {
                    if (job.Status == JobStatus.Completed)
                    {
                        currentTime = job.StartTime + job.EstimatedDuration;
                    }
                    else if (job.Status == JobStatus.Running)
                    {
                        // Estimate remaining time for running job
                        var remaining = job.EstimatedDuration * (1.0 - job.Progress);
                        totalTime = currentTime + remaining;
                        currentTime = totalTime;
                    }
                    else if (job.Status == JobStatus.Pending)
                    {
                        // Add estimated duration for pending jobs
                        totalTime = currentTime + job.EstimatedDuration;
                        currentTime = totalTime;
                    }
                }
                
                return totalTime;
            }
        }
        
        /// <summary>
        /// Set batch jobs for the timeline.
        /// </summary>
        public void SetJobs(List<BatchJob> jobs)
        {
            _jobBlocks = new List<JobTimelineBlock>();
            
            if (jobs == null || jobs.Count == 0)
            {
                _totalDuration = 0.0;
                UpdateTimeline();
                return;
            }
            
            // Sort jobs by creation time (or status for queue order)
            var sortedJobs = jobs.OrderBy(j => j.Created).ThenBy(j => j.Status == JobStatus.Running ? 0 : 1).ToList();
            
            double currentTime = 0.0;
            int rowIndex = 0;
            
            foreach (var job in sortedJobs)
            {
                // Estimate duration based on text length
                var estimatedDuration = EstimateJobDuration(job);
                
                // For sequential queue: jobs run one after another
                var startTime = currentTime;
                
                // If job is completed, use actual completion time
                if (job.Status == JobStatus.Completed && job.Completed.HasValue && job.Started.HasValue)
                {
                    var actualDuration = (job.Completed.Value - job.Started.Value).TotalSeconds;
                    estimatedDuration = Math.Max(estimatedDuration, actualDuration);
                }
                
                var block = new JobTimelineBlock
                {
                    JobId = job.Id,
                    JobName = job.Name,
                    EngineId = job.EngineId,
                    VoiceProfileId = job.VoiceProfileId,
                    StartTime = startTime,
                    EstimatedDuration = estimatedDuration,
                    Progress = job.Progress,
                    Status = job.Status,
                    Priority = DeterminePriority(job),
                    RowIndex = rowIndex
                };
                
                _jobBlocks.Add(block);
                
                // Move to next job's start time (sequential execution)
                if (job.Status == JobStatus.Running)
                {
                    // For running jobs, estimate based on progress
                    currentTime = startTime + (estimatedDuration * (1.0 - job.Progress));
                }
                else if (job.Status == JobStatus.Pending)
                {
                    currentTime = startTime + estimatedDuration;
                }
                else if (job.Status == JobStatus.Completed)
                {
                    currentTime = startTime + estimatedDuration;
                }
                
                rowIndex++;
            }
            
            // Calculate total duration
            _totalDuration = _jobBlocks.Count > 0 
                ? _jobBlocks.Max(b => b.StartTime + b.EstimatedDuration) 
                : 0.0;
            
            UpdateTimeline();
        }
        
        private double EstimateJobDuration(BatchJob job)
        {
            // Estimate based on text length and engine
            var baseTimePerChar = ESTIMATED_SECONDS_PER_CHARACTER;
            
            // Adjust based on engine (some engines are faster/slower)
            var engineMultiplier = job.EngineId.ToLower() switch
            {
                "xtts_v2" => 1.0,
                "chatterbox" => 0.8,
                "tortoise" => 2.0,
                _ => 1.0
            };
            
            var textLength = job.Text?.Length ?? 100;
            var estimatedSeconds = textLength * baseTimePerChar * engineMultiplier;
            
            // Minimum 2 seconds, maximum 60 seconds per job
            return Math.Clamp(estimatedSeconds, 2.0, 60.0);
        }
        
        private string DeterminePriority(BatchJob job)
        {
            // Priority can be determined by:
            // - Quality threshold (higher threshold = higher priority)
            // - Creation time (older = higher priority)
            // - Status (running = highest)
            
            if (job.Status == JobStatus.Running)
                return "high";
            
            if (job.QualityThreshold.HasValue && job.QualityThreshold.Value > 0.8)
                return "high";
            
            // Check creation time (jobs older than 5 minutes get higher priority)
            var age = DateTime.UtcNow - job.Created;
            if (age.TotalMinutes > 5)
                return "high";
            
            return "medium";
        }
        
        private void UpdateTimeline()
        {
            if (TimelineCanvas == null)
                return;
                
            // Calculate canvas size
            var canvasWidth = Math.Max(800, _totalDuration * PIXELS_PER_SECOND * _zoomLevel);
            var canvasHeight = Math.Max(150, (_jobBlocks.Count + 1) * 40);
            
            TimelineCanvas.Width = canvasWidth;
            TimelineCanvas.Height = canvasHeight;
            
            // Clear existing children
            var childrenToRemove = TimelineCanvas.Children
                .OfType<FrameworkElement>()
                .Where(c => c.Tag?.ToString() == "job_block" || c.Tag?.ToString() == "time_marker")
                .ToList();
            
            foreach (var child in childrenToRemove)
            {
                TimelineCanvas.Children.Remove(child);
            }
            
            // Draw time markers
            DrawTimeMarkers(canvasWidth);
            
            // Draw job blocks
            DrawJobBlocks();
            
            UpdateTimeScale();
        }
        
        private void DrawTimeMarkers(double canvasWidth)
        {
            var markerInterval = 1.0; // 1 second intervals
            
            for (double time = 0; time <= _totalDuration; time += markerInterval)
            {
                var x = time * PIXELS_PER_SECOND * _zoomLevel;
                
                // Major marker (every 5 seconds)
                if (time % 5.0 < 0.1)
                {
                    var majorLine = new Line
                    {
                        X1 = x,
                        Y1 = 0,
                        X2 = x,
                        Y2 = TimelineCanvas.Height,
                        Stroke = new SolidColorBrush(Colors.Gray),
                        StrokeThickness = 1,
                        Opacity = 0.5,
                        Tag = "time_marker"
                    };
                    TimelineCanvas.Children.Add(majorLine);
                    
                    // Time label
                    var label = new TextBlock
                    {
                        Text = FormatTime(time),
                        FontSize = 10,
                        Foreground = new SolidColorBrush(Colors.Gray),
                        Margin = new Thickness(x + 2, 2, 0, 0),
                        Tag = "time_marker"
                    };
                    TimelineCanvas.Children.Add(label);
                }
                else
                {
                    // Minor marker
                    var minorLine = new Line
                    {
                        X1 = x,
                        Y1 = 0,
                        X2 = x,
                        Y2 = 20,
                        Stroke = new SolidColorBrush(Colors.Gray),
                        StrokeThickness = 0.5,
                        Opacity = 0.3,
                        Tag = "time_marker"
                    };
                    TimelineCanvas.Children.Add(minorLine);
                }
            }
        }
        
        private void DrawJobBlocks()
        {
            var rowHeight = 35.0;
            var rowSpacing = 5.0;
            var yOffset = 25.0; // Space for time markers
            
            for (int i = 0; i < _jobBlocks.Count; i++)
            {
                var block = _jobBlocks[i];
                var y = yOffset + (i * (rowHeight + rowSpacing));
                
                // Calculate position and size
                var x = block.StartTime * PIXELS_PER_SECOND * _zoomLevel;
                var width = block.EstimatedDuration * PIXELS_PER_SECOND * _zoomLevel;
                
                // Job block border
                var border = new Border
                {
                    Width = width,
                    Height = rowHeight,
                    Background = GetStatusColor(block.Status),
                    BorderBrush = GetPriorityBorderColor(block.Priority),
                    BorderThickness = new Thickness(block.Priority == "high" ? 2 : 1),
                    CornerRadius = new CornerRadius(4),
                    Tag = "job_block",
                    Opacity = block.Status == JobStatus.Completed ? 1.0 : 0.7
                };
                
                Canvas.SetLeft(border, x);
                Canvas.SetTop(border, y);
                TimelineCanvas.Children.Add(border);
                
                // Progress indicator (overlay)
                if (block.Progress > 0 && block.Progress < 1.0 && block.Status == JobStatus.Running)
                {
                    var progressWidth = width * block.Progress;
                    var progressBar = new Border
                    {
                        Width = progressWidth,
                        Height = rowHeight,
                        Background = new SolidColorBrush(Colors.Cyan),
                        Opacity = 0.4,
                        Tag = "job_block"
                    };
                    
                    Canvas.SetLeft(progressBar, x);
                    Canvas.SetTop(progressBar, y);
                    TimelineCanvas.Children.Add(progressBar);
                }
                
                // Priority indicator (left edge)
                if (block.Priority == "high")
                {
                    var priorityIndicator = new Border
                    {
                        Width = 3,
                        Height = rowHeight,
                        Background = new SolidColorBrush(Colors.Yellow),
                        Tag = "job_block"
                    };
                    
                    Canvas.SetLeft(priorityIndicator, x);
                    Canvas.SetTop(priorityIndicator, y);
                    TimelineCanvas.Children.Add(priorityIndicator);
                }
                
                // Job label
                var labelText = $"{block.JobName} ({block.EngineId})";
                var label = new TextBlock
                {
                    Text = labelText,
                    FontSize = 10,
                    Foreground = new SolidColorBrush(Colors.White),
                    Margin = new Thickness(4, 4, 0, 0),
                    TextTrimming = TextTrimming.CharacterEllipsis,
                    MaxWidth = width - 8,
                    Tag = "job_block"
                };
                
                Canvas.SetLeft(label, x + 4);
                Canvas.SetTop(label, y + 4);
                TimelineCanvas.Children.Add(label);
                
                // Estimated duration label
                if (width > 80)
                {
                    var durationLabel = new TextBlock
                    {
                        Text = FormatTime(block.EstimatedDuration),
                        FontSize = 9,
                        Foreground = new SolidColorBrush(Colors.White),
                        Opacity = 0.8,
                        Tag = "job_block"
                    };
                    
                    Canvas.SetLeft(durationLabel, x + width - (durationLabel.Text.Length * 6) - 4);
                    Canvas.SetTop(durationLabel, y + rowHeight - 14);
                    TimelineCanvas.Children.Add(durationLabel);
                }
            }
        }
        
        private SolidColorBrush GetStatusColor(JobStatus status)
        {
            return status switch
            {
                JobStatus.Completed => new SolidColorBrush(Colors.Green),
                JobStatus.Running => new SolidColorBrush(Colors.Orange),
                JobStatus.Failed => new SolidColorBrush(Colors.Red),
                JobStatus.Cancelled => new SolidColorBrush(Colors.Gray),
                _ => new SolidColorBrush(Colors.Gray) // Pending
            };
        }
        
        private SolidColorBrush GetPriorityBorderColor(string priority)
        {
            return priority switch
            {
                "high" => new SolidColorBrush(Colors.Yellow),
                "medium" => new SolidColorBrush(Colors.Cyan),
                _ => new SolidColorBrush(Colors.Gray) // low
            };
        }
        
        private string FormatTime(double seconds)
        {
            var minutes = (int)(seconds / 60);
            var secs = (int)(seconds % 60);
            return $"{minutes}:{secs:D2}";
        }
        
        private void UpdateTimeScale()
        {
            if (TimeScaleText != null)
            {
                TimeScaleText.Text = $"Duration: {FormatTime(_totalDuration)} | Zoom: {_zoomLevel:F1}x";
            }
            
            if (EstimatedTimeText != null)
            {
                var estimatedTime = EstimatedQueueCompletionTime;
                if (estimatedTime > 0)
                {
                    EstimatedTimeText.Text = $"Est. Queue Completion: {FormatTime(estimatedTime)}";
                    EstimatedTimeText.Visibility = Visibility.Visible;
                }
                else
                {
                    EstimatedTimeText.Visibility = Visibility.Collapsed;
                }
            }
        }
        
        private void ZoomIn_Click(object sender, RoutedEventArgs e)
        {
            ZoomLevel *= 1.5;
        }
        
        private void ZoomOut_Click(object sender, RoutedEventArgs e)
        {
            ZoomLevel /= 1.5;
        }
        
        private void Fit_Click(object sender, RoutedEventArgs e)
        {
            if (_totalDuration > 0 && TimelineCanvas != null)
            {
                var availableWidth = TimelineCanvas.ActualWidth > 0 ? TimelineCanvas.ActualWidth : 800;
                ZoomLevel = availableWidth / (_totalDuration * PIXELS_PER_SECOND);
            }
            else
            {
                ZoomLevel = DEFAULT_ZOOM;
            }
        }
        
        private void TimelineCanvas_PointerPressed(object sender, PointerRoutedEventArgs e)
        {
            _lastPointerPosition = e.GetCurrentPoint(TimelineCanvas).Position;
        }
        
        private void TimelineCanvas_PointerMoved(object sender, PointerRoutedEventArgs e)
        {
            // Could implement panning here
        }
        
        private void TimelineCanvas_PointerReleased(object sender, PointerRoutedEventArgs e)
        {
            _lastPointerPosition = null;
        }
    }
}

