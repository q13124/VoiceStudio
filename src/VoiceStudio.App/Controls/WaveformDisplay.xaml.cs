using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.UI;
using Microsoft.UI.Input;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Shapes;
using Windows.Foundation;
using Colors = Microsoft.UI.Colors;

namespace VoiceStudio.App.Controls;

/// <summary>
/// DAW-inspired waveform display control with zoom, scrub, and selection.
/// 
/// Phase 11.3: DAW-Inspired Patterns
/// Features:
/// - High-resolution waveform rendering
/// - Zoom and pan with mouse wheel
/// - Click-to-seek and drag selection
/// - Markers and regions
/// - Timeline ruler with adaptive scale
/// </summary>
public sealed partial class WaveformDisplay : UserControl
{
    #region Dependency Properties

    public static readonly DependencyProperty AudioDurationProperty =
        DependencyProperty.Register(
            nameof(AudioDuration),
            typeof(TimeSpan),
            typeof(WaveformDisplay),
            new PropertyMetadata(TimeSpan.Zero, OnAudioDurationChanged));

    public static readonly DependencyProperty CurrentPositionProperty =
        DependencyProperty.Register(
            nameof(CurrentPosition),
            typeof(TimeSpan),
            typeof(WaveformDisplay),
            new PropertyMetadata(TimeSpan.Zero, OnCurrentPositionChanged));

    public static readonly DependencyProperty SelectionStartProperty =
        DependencyProperty.Register(
            nameof(SelectionStart),
            typeof(TimeSpan?),
            typeof(WaveformDisplay),
            new PropertyMetadata(null, OnSelectionChanged));

    public static readonly DependencyProperty SelectionEndProperty =
        DependencyProperty.Register(
            nameof(SelectionEnd),
            typeof(TimeSpan?),
            typeof(WaveformDisplay),
            new PropertyMetadata(null, OnSelectionChanged));

    public static readonly DependencyProperty WaveformColorProperty =
        DependencyProperty.Register(
            nameof(WaveformColor),
            typeof(Color),
            typeof(WaveformDisplay),
            new PropertyMetadata(Colors.DodgerBlue, OnWaveformColorChanged));

    public static readonly DependencyProperty IsLoadingProperty =
        DependencyProperty.Register(
            nameof(IsLoading),
            typeof(bool),
            typeof(WaveformDisplay),
            new PropertyMetadata(false, OnIsLoadingChanged));

    public TimeSpan AudioDuration
    {
        get => (TimeSpan)GetValue(AudioDurationProperty);
        set => SetValue(AudioDurationProperty, value);
    }

    public TimeSpan CurrentPosition
    {
        get => (TimeSpan)GetValue(CurrentPositionProperty);
        set => SetValue(CurrentPositionProperty, value);
    }

    public TimeSpan? SelectionStart
    {
        get => (TimeSpan?)GetValue(SelectionStartProperty);
        set => SetValue(SelectionStartProperty, value);
    }

    public TimeSpan? SelectionEnd
    {
        get => (TimeSpan?)GetValue(SelectionEndProperty);
        set => SetValue(SelectionEndProperty, value);
    }

    public Color WaveformColor
    {
        get => (Color)GetValue(WaveformColorProperty);
        set => SetValue(WaveformColorProperty, value);
    }

    public bool IsLoading
    {
        get => (bool)GetValue(IsLoadingProperty);
        set => SetValue(IsLoadingProperty, value);
    }

    #endregion

    #region Events

    public event EventHandler<TimeSpan>? PositionRequested;
    public event EventHandler<(TimeSpan Start, TimeSpan End)>? SelectionChanged;

    #endregion

    #region Private Fields

    private float[] _waveformData = Array.Empty<float>();
    private double _zoomLevel = 1.0;
    private double _scrollOffset = 0.0;
    private bool _isDragging = false;
    private bool _isSelecting = false;
    private Point _dragStartPoint;
    private TimeSpan _selectionStartTime;
    private readonly List<WaveformMarker> _markers = new();
    private Brush _waveformBrush;
    private Brush _selectionBrush;

    #endregion

    public WaveformDisplay()
    {
        this.InitializeComponent();

        _waveformBrush = new SolidColorBrush(WaveformColor);
        _selectionBrush = new SolidColorBrush(Color.FromArgb(80, 100, 149, 237));

        this.SizeChanged += WaveformDisplay_SizeChanged;
        this.Loaded += WaveformDisplay_Loaded;
    }

    #region Public Methods

    /// <summary>
    /// Load waveform data from audio samples.
    /// </summary>
    /// <param name="samples">Audio samples (normalized -1 to 1).</param>
    /// <param name="sampleRate">Sample rate in Hz.</param>
    public async Task LoadWaveformAsync(float[] samples, int sampleRate)
    {
        IsLoading = true;

        try
        {
            // Generate downsampled waveform data for display
            await Task.Run(() =>
            {
                int targetPoints = Math.Max(1000, (int)(ActualWidth * 4));
                _waveformData = GenerateWaveformData(samples, targetPoints);
            });

            RedrawWaveform();
        }
        finally
        {
            IsLoading = false;
        }
    }

    /// <summary>
    /// Set waveform data directly (pre-computed peaks).
    /// </summary>
    /// <param name="peaks">Array of peak values (0 to 1).</param>
    public void SetWaveformData(float[] peaks)
    {
        _waveformData = peaks;
        RedrawWaveform();
    }

    /// <summary>
    /// Add a marker at the specified time.
    /// </summary>
    public void AddMarker(TimeSpan time, string label, Color color)
    {
        _markers.Add(new WaveformMarker
        {
            Time = time,
            Label = label,
            Color = color
        });
        RedrawMarkers();
    }

    /// <summary>
    /// Clear all markers.
    /// </summary>
    public void ClearMarkers()
    {
        _markers.Clear();
        MarkersCanvas.Children.Clear();
    }

    /// <summary>
    /// Zoom to fit the entire waveform.
    /// </summary>
    public void ZoomToFit()
    {
        _zoomLevel = 1.0;
        _scrollOffset = 0.0;
        ZoomSlider.Value = 1;
        RedrawWaveform();
    }

    /// <summary>
    /// Zoom to selection if available.
    /// </summary>
    public void ZoomToSelection()
    {
        if (SelectionStart.HasValue && SelectionEnd.HasValue && AudioDuration.TotalSeconds > 0)
        {
            var start = SelectionStart.Value;
            var end = SelectionEnd.Value;
            var selectionDuration = (end - start).TotalSeconds;
            
            _zoomLevel = AudioDuration.TotalSeconds / selectionDuration;
            _scrollOffset = start.TotalSeconds / AudioDuration.TotalSeconds;
            
            ZoomSlider.Value = Math.Min(100, _zoomLevel);
            RedrawWaveform();
        }
    }

    #endregion

    #region Event Handlers

    private void WaveformDisplay_Loaded(object sender, RoutedEventArgs e)
    {
        RedrawWaveform();
        UpdateTimeDisplay();
    }

    private void WaveformDisplay_SizeChanged(object sender, SizeChangedEventArgs e)
    {
        Playhead.Height = WaveformCanvas.ActualHeight;
        RedrawWaveform();
        RedrawTimeline();
        RedrawSelection();
        RedrawMarkers();
    }

    private void WaveformCanvas_PointerPressed(object sender, PointerRoutedEventArgs e)
    {
        var point = e.GetCurrentPoint(WaveformCanvas);
        _dragStartPoint = point.Position;

        if (point.Properties.IsLeftButtonPressed)
        {
            if (e.KeyModifiers.HasFlag(Windows.System.VirtualKeyModifiers.Shift))
            {
                // Start selection
                _isSelecting = true;
                _selectionStartTime = PositionFromX(point.Position.X);
                SelectionStart = _selectionStartTime;
                SelectionEnd = _selectionStartTime;
            }
            else
            {
                // Seek to position
                var seekTime = PositionFromX(point.Position.X);
                PositionRequested?.Invoke(this, seekTime);
            }
        }
        else if (point.Properties.IsMiddleButtonPressed)
        {
            // Start panning
            _isDragging = true;
        }

        WaveformCanvas.CapturePointer(e.Pointer);
        e.Handled = true;
    }

    private void WaveformCanvas_PointerMoved(object sender, PointerRoutedEventArgs e)
    {
        var point = e.GetCurrentPoint(WaveformCanvas);

        if (_isSelecting)
        {
            SelectionEnd = PositionFromX(point.Position.X);
            RedrawSelection();
        }
        else if (_isDragging)
        {
            var deltaX = point.Position.X - _dragStartPoint.X;
            var deltaTime = (deltaX / WaveformCanvas.ActualWidth) / _zoomLevel;
            _scrollOffset = Math.Clamp(_scrollOffset - deltaTime, 0, 1 - 1 / _zoomLevel);
            _dragStartPoint = point.Position;
            RedrawWaveform();
            RedrawTimeline();
        }

        // Update cursor position display
        var hoverTime = PositionFromX(point.Position.X);
        CurrentTimeText.Text = FormatTime(hoverTime);

        e.Handled = true;
    }

    private void WaveformCanvas_PointerReleased(object sender, PointerRoutedEventArgs e)
    {
        if (_isSelecting && SelectionStart.HasValue && SelectionEnd.HasValue)
        {
            // Ensure start < end
            if (SelectionStart > SelectionEnd)
            {
                (SelectionStart, SelectionEnd) = (SelectionEnd, SelectionStart);
            }

            SelectionChanged?.Invoke(this, (SelectionStart.Value, SelectionEnd.Value));
        }

        _isDragging = false;
        _isSelecting = false;
        WaveformCanvas.ReleasePointerCapture(e.Pointer);
        e.Handled = true;
    }

    private void WaveformCanvas_PointerWheelChanged(object sender, PointerRoutedEventArgs e)
    {
        var point = e.GetCurrentPoint(WaveformCanvas);
        var delta = point.Properties.MouseWheelDelta;

        if (e.KeyModifiers.HasFlag(Windows.System.VirtualKeyModifiers.Control))
        {
            // Zoom around mouse position
            var mouseRatio = point.Position.X / WaveformCanvas.ActualWidth;
            var timeAtMouse = _scrollOffset + mouseRatio / _zoomLevel;

            var zoomFactor = delta > 0 ? 1.2 : 0.8;
            _zoomLevel = Math.Clamp(_zoomLevel * zoomFactor, 1.0, 100.0);

            // Adjust scroll to keep time under mouse stationary
            _scrollOffset = Math.Clamp(timeAtMouse - mouseRatio / _zoomLevel, 0, 1 - 1 / _zoomLevel);

            ZoomSlider.Value = _zoomLevel;
            RedrawWaveform();
            RedrawTimeline();
        }
        else
        {
            // Horizontal scroll
            var scrollAmount = (delta > 0 ? -1 : 1) * 0.1 / _zoomLevel;
            _scrollOffset = Math.Clamp(_scrollOffset + scrollAmount, 0, 1 - 1 / _zoomLevel);
            RedrawWaveform();
            RedrawTimeline();
        }

        e.Handled = true;
    }

    private void ZoomInButton_Click(object sender, RoutedEventArgs e)
    {
        ZoomSlider.Value = Math.Min(100, ZoomSlider.Value * 1.5);
    }

    private void ZoomOutButton_Click(object sender, RoutedEventArgs e)
    {
        ZoomSlider.Value = Math.Max(1, ZoomSlider.Value / 1.5);
    }

    private void ZoomSlider_ValueChanged(object sender, Microsoft.UI.Xaml.Controls.Primitives.RangeBaseValueChangedEventArgs e)
    {
        _zoomLevel = e.NewValue;
        _scrollOffset = Math.Clamp(_scrollOffset, 0, Math.Max(0, 1 - 1 / _zoomLevel));
        RedrawWaveform();
        RedrawTimeline();
    }

    #endregion

    #region Private Methods

    private static void OnAudioDurationChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        if (d is WaveformDisplay display)
        {
            display.UpdateTimeDisplay();
            display.RedrawTimeline();
        }
    }

    private static void OnCurrentPositionChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        if (d is WaveformDisplay display)
        {
            display.UpdatePlayhead();
        }
    }

    private static void OnSelectionChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        if (d is WaveformDisplay display)
        {
            display.RedrawSelection();
        }
    }

    private static void OnWaveformColorChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        if (d is WaveformDisplay display)
        {
            display._waveformBrush = new SolidColorBrush((Color)e.NewValue);
            display.RedrawWaveform();
        }
    }

    private static void OnIsLoadingChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        if (d is WaveformDisplay display)
        {
            display.LoadingOverlay.Visibility = (bool)e.NewValue ? Visibility.Visible : Visibility.Collapsed;
        }
    }

    private float[] GenerateWaveformData(float[] samples, int targetPoints)
    {
        if (samples.Length == 0) return Array.Empty<float>();

        var result = new float[targetPoints];
        var samplesPerPoint = samples.Length / (double)targetPoints;

        for (int i = 0; i < targetPoints; i++)
        {
            int start = (int)(i * samplesPerPoint);
            int end = Math.Min((int)((i + 1) * samplesPerPoint), samples.Length);

            float maxAbs = 0;
            for (int j = start; j < end; j++)
            {
                maxAbs = Math.Max(maxAbs, Math.Abs(samples[j]));
            }
            result[i] = maxAbs;
        }

        return result;
    }

    private void RedrawWaveform()
    {
        WaveformCanvas.Children.Clear();

        if (_waveformData.Length == 0 || WaveformCanvas.ActualWidth <= 0 || WaveformCanvas.ActualHeight <= 0)
            return;

        var width = WaveformCanvas.ActualWidth;
        var height = WaveformCanvas.ActualHeight;
        var centerY = height / 2;

        // Calculate visible range
        int startIndex = (int)(_scrollOffset * _waveformData.Length);
        int visiblePoints = (int)(_waveformData.Length / _zoomLevel);
        int endIndex = Math.Min(startIndex + visiblePoints, _waveformData.Length);

        if (endIndex <= startIndex) return;

        var pointsToRender = endIndex - startIndex;
        var pixelsPerPoint = width / pointsToRender;

        // Create polyline for waveform
        var pathGeometry = new PathGeometry();
        var figure = new PathFigure { IsClosed = true };

        // Top half
        for (int i = 0; i < pointsToRender; i++)
        {
            int dataIndex = startIndex + i;
            if (dataIndex >= _waveformData.Length) break;

            var x = i * pixelsPerPoint;
            var amplitude = _waveformData[dataIndex] * (height / 2 - 4);

            if (i == 0)
            {
                figure.StartPoint = new Point(x, centerY - amplitude);
            }
            else
            {
                figure.Segments.Add(new LineSegment { Point = new Point(x, centerY - amplitude) });
            }
        }

        // Bottom half (reverse)
        for (int i = pointsToRender - 1; i >= 0; i--)
        {
            int dataIndex = startIndex + i;
            if (dataIndex >= _waveformData.Length) continue;

            var x = i * pixelsPerPoint;
            var amplitude = _waveformData[dataIndex] * (height / 2 - 4);

            figure.Segments.Add(new LineSegment { Point = new Point(x, centerY + amplitude) });
        }

        pathGeometry.Figures.Add(figure);

        var path = new Path
        {
            Data = pathGeometry,
            Fill = _waveformBrush,
            Opacity = 0.8
        };

        WaveformCanvas.Children.Add(path);

        // Draw center line
        var centerLine = new Line
        {
            X1 = 0,
            Y1 = centerY,
            X2 = width,
            Y2 = centerY,
            Stroke = new SolidColorBrush(Colors.White),
            StrokeThickness = 0.5,
            Opacity = 0.3
        };
        WaveformCanvas.Children.Add(centerLine);
    }

    private void RedrawTimeline()
    {
        TimelineRuler.Children.Clear();

        if (AudioDuration.TotalSeconds <= 0 || TimelineRuler.ActualWidth <= 0)
            return;

        var width = TimelineRuler.ActualWidth;
        var visibleDuration = AudioDuration.TotalSeconds / _zoomLevel;
        var startTime = _scrollOffset * AudioDuration.TotalSeconds;

        // Determine tick interval based on visible duration
        var tickInterval = GetOptimalTickInterval(visibleDuration);
        var majorTickInterval = tickInterval * 5;

        // Draw ticks
        var currentTime = Math.Ceiling(startTime / tickInterval) * tickInterval;
        while (currentTime < startTime + visibleDuration)
        {
            var x = ((currentTime - startTime) / visibleDuration) * width;
            var isMajor = (currentTime % majorTickInterval) < 0.001;

            var line = new Line
            {
                X1 = x,
                Y1 = isMajor ? 0 : 12,
                X2 = x,
                Y2 = 24,
                Stroke = new SolidColorBrush(Colors.White),
                StrokeThickness = 1,
                Opacity = isMajor ? 0.7 : 0.3
            };
            TimelineRuler.Children.Add(line);

            if (isMajor)
            {
                var text = new TextBlock
                {
                    Text = FormatTimeShort(TimeSpan.FromSeconds(currentTime)),
                    FontSize = 10,
                    Foreground = new SolidColorBrush(Colors.White),
                    Opacity = 0.7
                };
                Canvas.SetLeft(text, x + 2);
                Canvas.SetTop(text, 2);
                TimelineRuler.Children.Add(text);
            }

            currentTime += tickInterval;
        }
    }

    private void RedrawSelection()
    {
        SelectionCanvas.Children.Clear();

        if (!SelectionStart.HasValue || !SelectionEnd.HasValue || AudioDuration.TotalSeconds <= 0)
            return;

        var start = Math.Min(SelectionStart.Value.TotalSeconds, SelectionEnd.Value.TotalSeconds);
        var end = Math.Max(SelectionStart.Value.TotalSeconds, SelectionEnd.Value.TotalSeconds);

        var visibleDuration = AudioDuration.TotalSeconds / _zoomLevel;
        var visibleStart = _scrollOffset * AudioDuration.TotalSeconds;

        var startX = ((start - visibleStart) / visibleDuration) * SelectionCanvas.ActualWidth;
        var endX = ((end - visibleStart) / visibleDuration) * SelectionCanvas.ActualWidth;

        var rect = new Rectangle
        {
            Width = Math.Max(0, endX - startX),
            Height = SelectionCanvas.ActualHeight,
            Fill = _selectionBrush
        };
        Canvas.SetLeft(rect, startX);
        SelectionCanvas.Children.Add(rect);
    }

    private void RedrawMarkers()
    {
        MarkersCanvas.Children.Clear();

        if (AudioDuration.TotalSeconds <= 0 || _markers.Count == 0)
            return;

        var height = MarkersCanvas.ActualHeight;
        var width = MarkersCanvas.ActualWidth;
        var visibleDuration = AudioDuration.TotalSeconds / _zoomLevel;
        var visibleStart = _scrollOffset * AudioDuration.TotalSeconds;

        foreach (var marker in _markers)
        {
            var markerTime = marker.Time.TotalSeconds;
            if (markerTime < visibleStart || markerTime > visibleStart + visibleDuration)
                continue;

            var x = ((markerTime - visibleStart) / visibleDuration) * width;

            var line = new Line
            {
                X1 = x,
                Y1 = 0,
                X2 = x,
                Y2 = height,
                Stroke = new SolidColorBrush(marker.Color),
                StrokeThickness = 2,
                StrokeDashArray = new DoubleCollection { 4, 2 }
            };
            MarkersCanvas.Children.Add(line);

            if (!string.IsNullOrEmpty(marker.Label))
            {
                var label = new TextBlock
                {
                    Text = marker.Label,
                    FontSize = 10,
                    Foreground = new SolidColorBrush(marker.Color),
                    Padding = new Thickness(2)
                };
                Canvas.SetLeft(label, x + 2);
                Canvas.SetTop(label, 2);
                MarkersCanvas.Children.Add(label);
            }
        }
    }

    private void UpdatePlayhead()
    {
        if (AudioDuration.TotalSeconds <= 0)
            return;

        var visibleDuration = AudioDuration.TotalSeconds / _zoomLevel;
        var visibleStart = _scrollOffset * AudioDuration.TotalSeconds;
        var position = CurrentPosition.TotalSeconds;

        var x = ((position - visibleStart) / visibleDuration) * PlayheadCanvas.ActualWidth;
        Canvas.SetLeft(Playhead, x);

        // Update time display
        CurrentTimeText.Text = FormatTime(CurrentPosition);
    }

    private void UpdateTimeDisplay()
    {
        DurationText.Text = FormatTime(AudioDuration);
    }

    private TimeSpan PositionFromX(double x)
    {
        var ratio = x / WaveformCanvas.ActualWidth;
        var visibleDuration = AudioDuration.TotalSeconds / _zoomLevel;
        var visibleStart = _scrollOffset * AudioDuration.TotalSeconds;
        var time = visibleStart + ratio * visibleDuration;
        return TimeSpan.FromSeconds(Math.Clamp(time, 0, AudioDuration.TotalSeconds));
    }

    private double GetOptimalTickInterval(double visibleDuration)
    {
        // Choose tick interval based on visible duration
        double[] intervals = { 0.1, 0.5, 1, 2, 5, 10, 30, 60, 120, 300, 600 };
        foreach (var interval in intervals)
        {
            if (visibleDuration / interval <= 20)
                return interval;
        }
        return 600;
    }

    private static string FormatTime(TimeSpan time)
    {
        return $"{(int)time.TotalMinutes:D2}:{time.Seconds:D2}.{time.Milliseconds:D3}";
    }

    private static string FormatTimeShort(TimeSpan time)
    {
        if (time.TotalMinutes >= 1)
            return $"{(int)time.TotalMinutes}:{time.Seconds:D2}";
        else
            return $"{time.Seconds}.{time.Milliseconds / 100}";
    }

    #endregion
}

/// <summary>
/// Waveform marker data.
/// </summary>
public class WaveformMarker
{
    public TimeSpan Time { get; set; }
    public string Label { get; set; } = string.Empty;
    public Color Color { get; set; } = Colors.Yellow;
}
