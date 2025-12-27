using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.UI;
using Windows.UI;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Visual queue control for batch processing jobs (IDEA 23).
    /// Shows visual representation of job queue with status, progress, and reordering.
    /// </summary>
    public sealed partial class BatchQueueVisualControl : UserControl
    {
        private List<QueueJobItem> _queueItems = new();
        
        public BatchQueueVisualControl()
        {
            this.InitializeComponent();
        }
        
        /// <summary>
        /// Queue job item data.
        /// </summary>
        public class QueueJobItem
        {
            public string JobId { get; set; } = string.Empty;
            public string Name { get; set; } = string.Empty;
            public string Status { get; set; } = "Pending"; // Pending, Running, Completed, Failed, Cancelled
            public double Progress { get; set; } // 0.0 to 1.0
            public string EngineId { get; set; } = string.Empty;
            public int Priority { get; set; } = 0; // Higher = more priority
            public string? QualityScore { get; set; }
        }
        
        /// <summary>
        /// Current queue position indicator.
        /// </summary>
        public int QueuePosition
        {
            get => _queueItems.Count;
        }
        
        /// <summary>
        /// Set queue items to display.
        /// </summary>
        public void SetQueueItems(List<QueueJobItem> items)
        {
            _queueItems = items ?? new List<QueueJobItem>();
            UpdateQueueDisplay();
        }
        
        /// <summary>
        /// Add a job to the queue.
        /// </summary>
        public void AddJob(QueueJobItem job)
        {
            _queueItems.Add(job);
            UpdateQueueDisplay();
        }
        
        /// <summary>
        /// Remove a job from the queue.
        /// </summary>
        public void RemoveJob(string jobId)
        {
            _queueItems.RemoveAll(j => j.JobId == jobId);
            UpdateQueueDisplay();
        }
        
        /// <summary>
        /// Update a job in the queue.
        /// </summary>
        public void UpdateJob(QueueJobItem job)
        {
            var index = _queueItems.FindIndex(j => j.JobId == job.JobId);
            if (index >= 0)
            {
                _queueItems[index] = job;
                UpdateQueueDisplay();
            }
        }
        
        private void UpdateQueueDisplay()
        {
            if (QueueItemsPanel == null)
                return;
                
            // Clear existing items
            QueueItemsPanel.Children.Clear();
            
            // Sort by priority (higher first), then by status (Running > Pending > others)
            var sortedItems = _queueItems.OrderByDescending(j => j.Priority)
                .ThenByDescending(j => j.Status == "Running" ? 1 : 0)
                .ThenByDescending(j => j.Status == "Pending" ? 1 : 0)
                .ToList();
            
            // Create visual items
            for (int i = 0; i < sortedItems.Count; i++)
            {
                var job = sortedItems[i];
                var itemControl = CreateQueueItemControl(job, i);
                QueueItemsPanel.Children.Add(itemControl);
            }
            
            // Update queue position
            OnPropertyChanged(nameof(QueuePosition));
        }
        
        private FrameworkElement CreateQueueItemControl(QueueJobItem job, int index)
        {
            var border = new Border
            {
                Background = GetStatusBackground(job.Status),
                BorderBrush = new SolidColorBrush(Microsoft.UI.Colors.Gray),
                BorderThickness = new Thickness(1),
                CornerRadius = new CornerRadius(4),
                Padding = new Thickness(8),
                Margin = new Thickness(0, 0, 0, 4),
                Tag = job.JobId
            };
            
            var grid = new Grid();
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Auto) }); // Position
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) }); // Name/Info
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Auto) }); // Status
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Auto) }); // Progress
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Auto) }); // Quality
            
            // Position indicator
            var positionText = new TextBlock
            {
                Text = $"{index + 1}",
                FontSize = 16,
                FontWeight = Microsoft.UI.Text.FontWeights.Bold,
                Foreground = new SolidColorBrush(Microsoft.UI.Colors.White),
                VerticalAlignment = VerticalAlignment.Center,
                Margin = new Thickness(0, 0, 12, 0)
            };
            Grid.SetColumn(positionText, 0);
            grid.Children.Add(positionText);
            
            // Job name and details
            var nameStack = new StackPanel
            {
                Orientation = Orientation.Vertical,
                Spacing = 2
            };
            
            var nameText = new TextBlock
            {
                Text = job.Name,
                FontSize = 12,
                FontWeight = Microsoft.UI.Text.FontWeights.SemiBold,
                Foreground = new SolidColorBrush(Microsoft.UI.Colors.White),
                TextTrimming = TextTrimming.CharacterEllipsis
            };
            nameStack.Children.Add(nameText);
            
            var engineText = new TextBlock
            {
                Text = $"Engine: {job.EngineId}",
                FontSize = 10,
                Foreground = new SolidColorBrush(Microsoft.UI.Colors.LightGray),
                Opacity = 0.8
            };
            nameStack.Children.Add(engineText);
            
            Grid.SetColumn(nameStack, 1);
            grid.Children.Add(nameStack);
            
            // Status badge
            var statusBadge = new Border
            {
                Background = GetStatusColor(job.Status),
                CornerRadius = new CornerRadius(12),
                Padding = new Thickness(8, 4, 8, 4),
                Margin = new Thickness(8, 0, 8, 0)
            };
            
            var statusText = new TextBlock
            {
                Text = job.Status,
                FontSize = 10,
                FontWeight = Microsoft.UI.Text.FontWeights.SemiBold,
                Foreground = new SolidColorBrush(Microsoft.UI.Colors.White)
            };
            statusBadge.Child = statusText;
            
            Grid.SetColumn(statusBadge, 2);
            grid.Children.Add(statusBadge);
            
            // Progress bar (for running jobs)
            if (job.Status == "Running" || job.Status == "Pending")
            {
                var progressStack = new StackPanel
                {
                    Orientation = Orientation.Vertical,
                    Spacing = 2,
                    Width = 100,
                    Margin = new Thickness(8, 0, 8, 0)
                };
                
                var progressBar = new ProgressBar
                {
                    Value = job.Progress * 100,
                    Maximum = 100,
                    Height = 8,
                    Foreground = new SolidColorBrush(Microsoft.UI.Colors.Cyan)
                };
                progressStack.Children.Add(progressBar);
                
                var progressText = new TextBlock
                {
                    Text = $"{job.Progress:P0}",
                    FontSize = 9,
                    Foreground = new SolidColorBrush(Microsoft.UI.Colors.White),
                    HorizontalAlignment = HorizontalAlignment.Center
                };
                progressStack.Children.Add(progressText);
                
                Grid.SetColumn(progressStack, 3);
                grid.Children.Add(progressStack);
            }
            else
            {
                // Empty space for non-running jobs
                var emptySpace = new Border { Width = 100, Margin = new Thickness(8, 0, 8, 0) };
                Grid.SetColumn(emptySpace, 3);
                grid.Children.Add(emptySpace);
            }
            
            // Quality score (if available)
            if (!string.IsNullOrEmpty(job.QualityScore))
            {
                var qualityText = new TextBlock
                {
                    Text = $"Q: {job.QualityScore}",
                    FontSize = 10,
                    FontWeight = Microsoft.UI.Text.FontWeights.SemiBold,
                    Foreground = GetQualityColor(job.QualityScore),
                    VerticalAlignment = VerticalAlignment.Center,
                    Margin = new Thickness(8, 0, 0, 0)
                };
                Grid.SetColumn(qualityText, 4);
                grid.Children.Add(qualityText);
            }
            
            border.Child = grid;
            return border;
        }
        
        private Brush GetStatusBackground(string status)
        {
            return status switch
            {
                "Running" => new SolidColorBrush(Windows.UI.Color.FromArgb(255, 30, 60, 90)), // Dark blue
                "Pending" => new SolidColorBrush(Windows.UI.Color.FromArgb(255, 60, 60, 60)), // Dark gray
                "Completed" => new SolidColorBrush(Windows.UI.Color.FromArgb(255, 30, 80, 30)), // Dark green
                "Failed" => new SolidColorBrush(Windows.UI.Color.FromArgb(255, 80, 30, 30)), // Dark red
                "Cancelled" => new SolidColorBrush(Windows.UI.Color.FromArgb(255, 50, 50, 50)), // Gray
                _ => new SolidColorBrush(Windows.UI.Color.FromArgb(255, 50, 50, 50))
            };
        }
        
        private Brush GetStatusColor(string status)
        {
            return status switch
            {
                "Running" => new SolidColorBrush(Microsoft.UI.Colors.Orange),
                "Pending" => new SolidColorBrush(Microsoft.UI.Colors.Gray),
                "Completed" => new SolidColorBrush(Microsoft.UI.Colors.Green),
                "Failed" => new SolidColorBrush(Microsoft.UI.Colors.Red),
                "Cancelled" => new SolidColorBrush(Microsoft.UI.Colors.DarkGray),
                _ => new SolidColorBrush(Microsoft.UI.Colors.Gray)
            };
        }
        
        private Brush GetQualityColor(string qualityScore)
        {
            if (double.TryParse(qualityScore.Replace("%", ""), out var score))
            {
                if (score >= 80) return new SolidColorBrush(Microsoft.UI.Colors.Green);
                if (score >= 60) return new SolidColorBrush(Microsoft.UI.Colors.Orange);
                return new SolidColorBrush(Microsoft.UI.Colors.Red);
            }
            return new SolidColorBrush(Microsoft.UI.Colors.White);
        }
        
        private void ClearQueue_Click(object sender, RoutedEventArgs e)
        {
            // Clear completed and failed jobs
            _queueItems.RemoveAll(j => j.Status == "Completed" || j.Status == "Failed" || j.Status == "Cancelled");
            UpdateQueueDisplay();
        }
        
        private void OnPropertyChanged(string propertyName)
        {
            // Simple property change notification
            // In a full implementation, this would use INotifyPropertyChanged
        }
    }
}

