using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System;
using System.Collections.Generic;
using System.Linq;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Controls
{
  /// <summary>
  /// Training progress chart control for visualizing training metrics over time.
  /// Implements IDEA 28: Voice Training Progress Visualization.
  ///
  /// DEFERRED FEATURE: Visual charts for training loss, quality metrics.
  /// Win2D/CanvasControl rendering disabled during Phase 0 for XAML compiler stability.
  /// Full implementation planned for v1.1+ release.
  /// See: docs/governance/FUTURE_WORK.md
  /// </summary>
  public sealed class TrainingProgressChart : UserControl
  {
    private List<TrainingQualityMetrics> _dataPoints = new();

    public TrainingProgressChart()
    {
      // Phase 0: XAML compiler stability - code-only placeholder.
      Content = new TextBlock
      {
        Text = "Training progress chart temporarily disabled (XAML compiler stability)",
        TextWrapping = TextWrapping.Wrap,
        HorizontalAlignment = HorizontalAlignment.Center,
        VerticalAlignment = VerticalAlignment.Center,
        Opacity = 0.7
      };
    }

    /// <summary>
    /// Updates the chart with new data points.
    /// </summary>
    public void UpdateChart(IEnumerable<TrainingQualityMetrics> dataPoints)
    {
      _dataPoints = dataPoints?.ToList() ?? new List<TrainingQualityMetrics>();
      // Placeholder: no rendering during Phase 0 stability work.
    }
  }
}