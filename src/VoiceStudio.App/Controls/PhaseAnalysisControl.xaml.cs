using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Shapes;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Controls
{
  /// <summary>
  /// Phase analysis visualization control using Path-based rendering.
  /// Displays phase correlation and stereo width over time.
  /// </summary>
  public sealed partial class PhaseAnalysisControl : UserControl
  {
    private Path? _correlationPath;
    private Path? _stereoWidthPath;
    private Line? _playbackLine;

    public PhaseAnalysisControl()
    {
      InitializeComponent();
      this.SizeChanged += PhaseAnalysisControl_SizeChanged;
      this.Loaded += (_, _) => InitializeControls();
    }

    private void PhaseAnalysisControl_SizeChanged(object _, SizeChangedEventArgs e)
    {
      UpdatePhase();
      UpdatePlaybackPosition();
    }

    public PhaseData? Data { get; set; }
    public double PlaybackPosition { get; set; } = -1.0;

    private void UpdatePhase()
    {
      if (Data == null || Data.Times == null || Data.Correlation == null || Data.Times.Count == 0)
      {
        if (_correlationPath != null)
          _correlationPath.Data = null;
        if (_stereoWidthPath != null)
          _stereoWidthPath.Data = null;
        return;
      }

      var actualWidth = ActualWidth > 0 ? ActualWidth : 800;
      var actualHeight = ActualHeight > 0 ? ActualHeight : 200;
      const double padding = 40.0;
      var chartWidth = actualWidth - (2 * padding);
      var chartHeight = actualHeight - (2 * padding);
      var centerY = padding + (chartHeight / 2.0);

      var maxTime = Data.Duration > 0 ? Data.Duration : Data.Times.Max();
      if (maxTime < 0.1f) maxTime = 1.0f;

      // Build correlation path
      if (_correlationPath != null)
      {
        var pathGeometry = new PathGeometry();
        var pathFigure = new PathFigure();

        var x = padding;
        var y = centerY - (Data.Correlation[0] * chartHeight / 2.0);
        pathFigure.StartPoint = new Windows.Foundation.Point(x, y);

        for (int i = 1; i < Data.Times.Count && i < Data.Correlation.Count; i++)
        {
          x = padding + (Data.Times[i] / maxTime * chartWidth);
          y = centerY - (Data.Correlation[i] * chartHeight / 2.0);
          pathFigure.Segments.Add(new LineSegment { Point = new Windows.Foundation.Point(x, y) });
        }

        pathGeometry.Figures.Add(pathFigure);
        _correlationPath.Data = pathGeometry;
      }

      // Build stereo width path if available
      if (_stereoWidthPath != null && Data.StereoWidth?.Count > 0)
      {
        var pathGeometry = new PathGeometry();
        var pathFigure = new PathFigure();

        var x = padding;
        var y = actualHeight - padding - (Data.StereoWidth[0] * chartHeight);
        pathFigure.StartPoint = new Windows.Foundation.Point(x, y);

        var stereoCount = Math.Min(Data.Times.Count, Data.StereoWidth.Count);
        for (int i = 1; i < stereoCount; i++)
        {
          x = padding + (Data.Times[i] / maxTime * chartWidth);
          y = actualHeight - padding - (Data.StereoWidth[i] * chartHeight);
          pathFigure.Segments.Add(new LineSegment { Point = new Windows.Foundation.Point(x, y) });
        }

        pathGeometry.Figures.Add(pathFigure);
        _stereoWidthPath.Data = pathGeometry;
        _stereoWidthPath.Visibility = Visibility.Visible;
      }
      else if (_stereoWidthPath != null)
      {
        _stereoWidthPath.Visibility = Visibility.Collapsed;
      }

      // Draw average correlation line if available
      if (Data.AverageCorrelation.HasValue && _correlationPath != null)
      {
        // Average line could be drawn as a horizontal reference line
        // For now, we'll just show it in the correlation path
      }
    }

    private void UpdatePlaybackPosition()
    {
      if (_playbackLine == null || PlaybackPosition < 0 || Data == null || Data.Duration <= 0)
      {
        if (_playbackLine != null)
          _playbackLine.Visibility = Visibility.Collapsed;
        return;
      }

      var actualWidth = ActualWidth > 0 ? ActualWidth : 800;
      var actualHeight = ActualHeight > 0 ? ActualHeight : 200;
      const double padding = 40.0;

      var position = Math.Clamp(PlaybackPosition / Data.Duration, 0.0, 1.0);
      var x = padding + (position * (actualWidth - (2 * padding)));

      _playbackLine.X1 = x;
      _playbackLine.Y1 = padding;
      _playbackLine.X2 = x;
      _playbackLine.Y2 = actualHeight - padding;
      _playbackLine.Visibility = Visibility.Visible;
    }

    private void InitializeControls()
    {
      if (Content is Grid grid)
      {
        _correlationPath = grid.FindName("CorrelationPath") as Path;
        _stereoWidthPath = grid.FindName("StereoWidthPath") as Path;
        _playbackLine = grid.FindName("PlaybackLine") as Line;

        if (_correlationPath != null && _stereoWidthPath != null && _playbackLine != null)
        {
          UpdatePhase();
          UpdatePlaybackPosition();
        }
      }
    }

    protected override void OnApplyTemplate()
    {
      base.OnApplyTemplate();
      InitializeControls();
    }
  }
}