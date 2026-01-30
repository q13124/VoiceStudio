using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Shapes;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Waveform visualization control using Path-based rendering.
    /// Supports peak and RMS modes, zoom, and playback position indicator.
    /// </summary>
    public sealed partial class WaveformControl : UserControl
    {
        private Path? _waveformPath;
        private Line? _playbackLine;
        private const double MinSampleHeight = 0.01;
        private const double MaxSampleHeight = 1.0;

        public static readonly DependencyProperty SamplesProperty =
            DependencyProperty.Register(
                nameof(Samples),
                typeof(object),
                typeof(WaveformControl),
                new PropertyMetadata(null, OnSamplesChanged));

        public static readonly DependencyProperty ModeProperty =
            DependencyProperty.Register(
                nameof(Mode),
                typeof(string),
                typeof(WaveformControl),
                new PropertyMetadata("peak", OnVisualPropertyChanged));

        public static readonly DependencyProperty WaveformColorProperty =
            DependencyProperty.Register(
                nameof(WaveformColor),
                typeof(string),
                typeof(WaveformControl),
                new PropertyMetadata("Cyan", OnVisualPropertyChanged));

        public static readonly DependencyProperty ZoomLevelProperty =
            DependencyProperty.Register(
                nameof(ZoomLevel),
                typeof(double),
                typeof(WaveformControl),
                new PropertyMetadata(1.0, OnVisualPropertyChanged));

        public static readonly DependencyProperty PlaybackPositionProperty =
            DependencyProperty.Register(
                nameof(PlaybackPosition),
                typeof(double),
                typeof(WaveformControl),
                new PropertyMetadata(-1.0, OnPlaybackPositionChanged));

        public WaveformControl()
        {
            InitializeComponent();
            this.SizeChanged += WaveformControl_SizeChanged;
        }

        private static void OnSamplesChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is WaveformControl control)
            {
                control.UpdateWaveform();
            }
        }

        private static void OnVisualPropertyChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is WaveformControl control)
            {
                control.UpdateWaveform();
            }
        }

        private static void OnPlaybackPositionChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is WaveformControl control)
            {
                control.UpdatePlaybackPosition();
            }
        }

        private void WaveformControl_SizeChanged(object sender, SizeChangedEventArgs e)
        {
            UpdateWaveform();
            UpdatePlaybackPosition();
        }

        public object? Samples
        {
            get => GetValue(SamplesProperty);
            set => SetValue(SamplesProperty, value);
        }

        public string Mode
        {
            get => (string)GetValue(ModeProperty);
            set => SetValue(ModeProperty, value);
        }

        public string WaveformColor
        {
            get => (string)GetValue(WaveformColorProperty);
            set => SetValue(WaveformColorProperty, value);
        }

        public double ZoomLevel
        {
            get => (double)GetValue(ZoomLevelProperty);
            set => SetValue(ZoomLevelProperty, value);
        }

        public double PlaybackPosition
        {
            get => (double)GetValue(PlaybackPositionProperty);
            set => SetValue(PlaybackPositionProperty, value);
        }

        private List<float>? GetSamplesList()
        {
            var samples = Samples;
            if (samples == null)
                return null;

            // Handle ObservableCollection<float>
            if (samples is System.Collections.ObjectModel.ObservableCollection<float> observableCollection)
            {
                return observableCollection.ToList();
            }

            // Handle IList<float>
            if (samples is IList<float> floatList)
            {
                return floatList.ToList();
            }

            // Handle IEnumerable<float>
            if (samples is IEnumerable<float> floatEnumerable)
            {
                return floatEnumerable.ToList();
            }

            // Handle float[] array
            if (samples is float[] floatArray)
            {
                return floatArray.ToList();
            }

            // Handle IEnumerable (generic)
            if (samples is IEnumerable enumerable)
            {
                var result = new List<float>();
                foreach (var item in enumerable)
                {
                    if (item is float f)
                        result.Add(f);
                    else if (item != null && float.TryParse(item.ToString(), out var parsed))
                        result.Add(parsed);
                }
                return result.Count > 0 ? result : null;
            }

            return null;
        }

        private void UpdateWaveform()
        {
            if (_waveformPath == null)
                return;

            var samples = GetSamplesList();
            if (samples == null || samples.Count == 0)
            {
                _waveformPath.Data = null;
                return;
            }

            var actualWidth = ActualWidth > 0 ? ActualWidth : 800;
            var actualHeight = ActualHeight > 0 ? ActualHeight : 200;
            var centerY = actualHeight / 2.0;

            // Apply zoom to width (zoom > 1 = zoom in, < 1 = zoom out)
            var zoomedWidth = actualWidth * ZoomLevel;
            var samplesToDisplay = samples.Count;
            
            // If zoomed, show fewer samples
            if (ZoomLevel > 1.0)
            {
                samplesToDisplay = Math.Max(1, (int)(samples.Count / ZoomLevel));
            }

            // Downsample if needed for performance
            var displaySamples = DownsampleSamples(samples, samplesToDisplay);
            if (displaySamples.Count == 0)
                return;

            var sampleSpacing = zoomedWidth / displaySamples.Count;
            var pathGeometry = new PathGeometry();
            var pathFigure = new PathFigure();

            // Start at left center
            pathFigure.StartPoint = new Windows.Foundation.Point(0, centerY);

            // Build waveform path
            var isPeakMode = Mode.Equals("peak", StringComparison.OrdinalIgnoreCase);
            
            for (int i = 0; i < displaySamples.Count; i++)
            {
                var sample = displaySamples[i];
                var x = i * sampleSpacing;
                
                // Normalize sample to [-1, 1] range, then scale to visual height
                var normalizedSample = Math.Clamp(sample, -1.0f, 1.0f);
                var sampleHeight = normalizedSample * (actualHeight * 0.4); // Use 40% of height for waveform amplitude
                
                var y = centerY - sampleHeight;
                pathFigure.Segments.Add(new LineSegment { Point = new Windows.Foundation.Point(x, y) });
            }

            // Mirror for bottom half if in peak mode
            if (isPeakMode)
            {
                for (int i = displaySamples.Count - 1; i >= 0; i--)
                {
                    var sample = displaySamples[i];
                    var x = i * sampleSpacing;
                    var normalizedSample = Math.Clamp(sample, -1.0f, 1.0f);
                    var sampleHeight = normalizedSample * (actualHeight * 0.4);
                    var y = centerY + Math.Abs(sampleHeight); // Mirror below center
                    pathFigure.Segments.Add(new LineSegment { Point = new Windows.Foundation.Point(x, y) });
                }
                
                // Close the path
                pathFigure.Segments.Add(new LineSegment { Point = new Windows.Foundation.Point(0, centerY) });
            }

            pathGeometry.Figures.Add(pathFigure);
            _waveformPath.Data = pathGeometry;

            // Set color
            try
            {
                var color = GetColorFromString(WaveformColor);
                _waveformPath.Stroke = new SolidColorBrush(color);
                _waveformPath.Fill = isPeakMode ? new SolidColorBrush(color) { Opacity = 0.3 } : null;
            }
            catch
            {
                // Fallback to cyan if color parsing fails
                _waveformPath.Stroke = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 0, 255, 255));
                _waveformPath.Fill = isPeakMode ? new SolidColorBrush(Windows.UI.Color.FromArgb(76, 0, 255, 255)) : null;
            }
        }

        private List<float> DownsampleSamples(List<float> samples, int targetCount)
        {
            if (samples.Count <= targetCount)
                return samples;

            var result = new List<float>(targetCount);
            var step = (double)samples.Count / targetCount;

            for (int i = 0; i < targetCount; i++)
            {
                var startIdx = (int)(i * step);
                var endIdx = Math.Min((int)((i + 1) * step), samples.Count);
                
                if (Mode.Equals("peak", StringComparison.OrdinalIgnoreCase))
                {
                    // Peak mode: take max absolute value
                    var max = 0f;
                    for (int j = startIdx; j < endIdx; j++)
                    {
                        max = Math.Max(max, Math.Abs(samples[j]));
                    }
                    result.Add(max * Math.Sign(samples[startIdx]));
                }
                else
                {
                    // RMS mode: average
                    var sum = 0f;
                    var count = endIdx - startIdx;
                    for (int j = startIdx; j < endIdx; j++)
                    {
                        sum += samples[j];
                    }
                    result.Add(count > 0 ? sum / count : 0f);
                }
            }

            return result;
        }

        private void UpdatePlaybackPosition()
        {
            if (_playbackLine == null || PlaybackPosition < 0)
            {
                if (_playbackLine != null)
                    _playbackLine.Visibility = Visibility.Collapsed;
                return;
            }

            var actualWidth = ActualWidth > 0 ? ActualWidth : 800;
            var actualHeight = ActualHeight > 0 ? ActualHeight : 200;
            
            // PlaybackPosition is typically 0-1 (normalized) or seconds
            // Assume it's normalized for now
            var position = Math.Clamp(PlaybackPosition, 0.0, 1.0);
            var x = position * actualWidth;

            _playbackLine.X1 = x;
            _playbackLine.Y1 = 0;
            _playbackLine.X2 = x;
            _playbackLine.Y2 = actualHeight;
            _playbackLine.Visibility = Visibility.Visible;
        }

        private Windows.UI.Color GetColorFromString(string colorName)
        {
            if (string.IsNullOrWhiteSpace(colorName))
                return Windows.UI.Color.FromArgb(255, 0, 255, 255); // Cyan default

            // Try to parse as hex color (#RRGGBB or #AARRGGBB)
            if (colorName.StartsWith("#"))
            {
                var hex = colorName.Substring(1);
                var r = Convert.ToByte(hex.Length >= 2 ? hex.Substring(0, 2) : "00", 16);
                var g = Convert.ToByte(hex.Length >= 4 ? hex.Substring(2, 2) : "00", 16);
                var b = Convert.ToByte(hex.Length >= 6 ? hex.Substring(4, 2) : "00", 16);
                var a = hex.Length == 8 ? Convert.ToByte(hex.Substring(6, 2), 16) : (byte)255;
                return Windows.UI.Color.FromArgb(a, r, g, b);
            }

            // Try named colors
            var color = Microsoft.UI.Colors.Transparent;
            try
            {
                var colorProperty = typeof(Microsoft.UI.Colors).GetProperty(colorName, 
                    System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.IgnoreCase);
                if (colorProperty != null)
                {
                    color = (Windows.UI.Color)colorProperty.GetValue(null)!;
                }
            }
            catch
            {
                // Fallback to cyan
                color = Windows.UI.Color.FromArgb(255, 0, 255, 255);
            }

            return color;
        }

        private void InitializeControls()
        {
            if (_waveformPath == null && Content is Grid grid)
            {
                _waveformPath = grid.FindName("WaveformPath") as Path;
                _playbackLine = grid.FindName("PlaybackLine") as Line;
                
                if (_waveformPath == null || _playbackLine == null)
                {
                    // Controls not found in XAML, create them programmatically
                    _waveformPath = new Path
                    {
                        Name = "WaveformPath",
                        StrokeThickness = 1.5,
                        StrokeLineJoin = PenLineJoin.Round,
                        StrokeEndLineCap = PenLineCap.Round,
                        StrokeStartLineCap = PenLineCap.Round,
                        HorizontalAlignment = HorizontalAlignment.Stretch,
                        VerticalAlignment = VerticalAlignment.Stretch
                    };
                    
                    _playbackLine = new Line
                    {
                        Name = "PlaybackLine",
                        Stroke = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 255, 255, 0)), // Yellow
                        StrokeThickness = 2,
                        Visibility = Visibility.Collapsed,
                        StrokeDashArray = new DoubleCollection { 5, 5 }
                    };
                    
                    grid.Children.Add(_waveformPath);
                    grid.Children.Add(_playbackLine);
                }
                
                UpdateWaveform();
                UpdatePlaybackPosition();
            }
        }
    }
}

