// Phase 5.5: Chart Control Implementations
// Task 5.5.1: Spectrum Analyzer visualization control

using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Shapes;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Spectrum analyzer visualization control.
    /// Displays frequency spectrum data as vertical bars with peak hold indicators.
    /// </summary>
    public sealed partial class SpectrumAnalyzerControl : UserControl
    {
        private readonly List<Rectangle> _bars = new();
        private readonly List<Rectangle> _peakBars = new();
        private readonly List<float> _peakValues = new();
        private readonly List<int> _peakHoldCounters = new();
        private const int DefaultBarCount = 32;
        private const int PeakHoldTime = 30; // Frames to hold peak
        private const float PeakFallRate = 0.02f; // How fast peaks fall

        public static readonly DependencyProperty SpectrumDataProperty =
            DependencyProperty.Register(
                nameof(SpectrumData),
                typeof(object),
                typeof(SpectrumAnalyzerControl),
                new PropertyMetadata(null, OnSpectrumDataChanged));

        public static readonly DependencyProperty BarCountProperty =
            DependencyProperty.Register(
                nameof(BarCount),
                typeof(int),
                typeof(SpectrumAnalyzerControl),
                new PropertyMetadata(DefaultBarCount, OnBarCountChanged));

        public static readonly DependencyProperty BarSpacingProperty =
            DependencyProperty.Register(
                nameof(BarSpacing),
                typeof(double),
                typeof(SpectrumAnalyzerControl),
                new PropertyMetadata(2.0, OnVisualPropertyChanged));

        public static readonly DependencyProperty BarColorProperty =
            DependencyProperty.Register(
                nameof(BarColor),
                typeof(Brush),
                typeof(SpectrumAnalyzerControl),
                new PropertyMetadata(null, OnVisualPropertyChanged));

        public static readonly DependencyProperty PeakColorProperty =
            DependencyProperty.Register(
                nameof(PeakColor),
                typeof(Brush),
                typeof(SpectrumAnalyzerControl),
                new PropertyMetadata(null, OnVisualPropertyChanged));

        public static readonly DependencyProperty ShowPeaksProperty =
            DependencyProperty.Register(
                nameof(ShowPeaks),
                typeof(bool),
                typeof(SpectrumAnalyzerControl),
                new PropertyMetadata(true, OnVisualPropertyChanged));

        public static readonly DependencyProperty UseGradientProperty =
            DependencyProperty.Register(
                nameof(UseGradient),
                typeof(bool),
                typeof(SpectrumAnalyzerControl),
                new PropertyMetadata(true, OnVisualPropertyChanged));

        public SpectrumAnalyzerControl()
        {
            InitializeComponent();
            SizeChanged += OnSizeChanged;
            Loaded += OnLoaded;
        }

        public object? SpectrumData
        {
            get => GetValue(SpectrumDataProperty);
            set => SetValue(SpectrumDataProperty, value);
        }

        public int BarCount
        {
            get => (int)GetValue(BarCountProperty);
            set => SetValue(BarCountProperty, value);
        }

        public double BarSpacing
        {
            get => (double)GetValue(BarSpacingProperty);
            set => SetValue(BarSpacingProperty, value);
        }

        public Brush? BarColor
        {
            get => (Brush?)GetValue(BarColorProperty);
            set => SetValue(BarColorProperty, value);
        }

        public Brush? PeakColor
        {
            get => (Brush?)GetValue(PeakColorProperty);
            set => SetValue(PeakColorProperty, value);
        }

        public bool ShowPeaks
        {
            get => (bool)GetValue(ShowPeaksProperty);
            set => SetValue(ShowPeaksProperty, value);
        }

        public bool UseGradient
        {
            get => (bool)GetValue(UseGradientProperty);
            set => SetValue(UseGradientProperty, value);
        }

        private static void OnSpectrumDataChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is SpectrumAnalyzerControl control)
            {
                control.UpdateSpectrum();
            }
        }

        private static void OnBarCountChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is SpectrumAnalyzerControl control)
            {
                control.InitializeBars();
            }
        }

        private static void OnVisualPropertyChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is SpectrumAnalyzerControl control)
            {
                control.UpdateVisualProperties();
            }
        }

        private void OnLoaded(object sender, RoutedEventArgs e)
        {
            InitializeBars();
        }

        private void OnSizeChanged(object sender, SizeChangedEventArgs e)
        {
            UpdateBarLayout();
        }

        private void InitializeBars()
        {
            if (Content is not Canvas canvas)
                return;

            canvas.Children.Clear();
            _bars.Clear();
            _peakBars.Clear();
            _peakValues.Clear();
            _peakHoldCounters.Clear();

            var defaultBarBrush = CreateGradientBrush();
            var defaultPeakBrush = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 255, 255, 0));

            for (int i = 0; i < BarCount; i++)
            {
                // Peak indicator (top of bar)
                var peakBar = new Rectangle
                {
                    Fill = PeakColor ?? defaultPeakBrush,
                    Height = 3,
                    RadiusX = 1,
                    RadiusY = 1
                };
                _peakBars.Add(peakBar);
                _peakValues.Add(0);
                _peakHoldCounters.Add(0);
                canvas.Children.Add(peakBar);

                // Main bar
                var bar = new Rectangle
                {
                    Fill = BarColor ?? defaultBarBrush,
                    RadiusX = 2,
                    RadiusY = 2
                };
                _bars.Add(bar);
                canvas.Children.Add(bar);
            }

            UpdateBarLayout();
        }

        private void UpdateBarLayout()
        {
            if (Content is not Canvas canvas || _bars.Count == 0)
                return;

            var width = ActualWidth;
            var height = ActualHeight;

            if (width <= 0 || height <= 0)
                return;

            var totalSpacing = BarSpacing * (BarCount - 1);
            var barWidth = (width - totalSpacing) / BarCount;

            for (int i = 0; i < _bars.Count; i++)
            {
                var x = i * (barWidth + BarSpacing);

                _bars[i].Width = Math.Max(1, barWidth);
                Canvas.SetLeft(_bars[i], x);
                // WinUI 3 doesn't have Canvas.SetBottom - bars grow from bottom via Top + Height
                // Top will be adjusted dynamically in UpdateSpectrum based on bar height

                _peakBars[i].Width = Math.Max(1, barWidth);
                Canvas.SetLeft(_peakBars[i], x);
            }
        }

        private void UpdateSpectrum()
        {
            var data = GetSpectrumList();
            if (data == null || data.Count == 0 || _bars.Count == 0)
            {
                // Reset all bars
                foreach (var bar in _bars)
                {
                    bar.Height = 0;
                }
                return;
            }

            var height = ActualHeight;
            if (height <= 0)
                return;

            // Resample data to match bar count
            var resampledData = ResampleData(data, BarCount);

            for (int i = 0; i < BarCount && i < resampledData.Count; i++)
            {
                var value = Math.Clamp(resampledData[i], 0, 1);
                var barHeight = value * height;

                _bars[i].Height = barHeight;

                // Update peak
                if (ShowPeaks)
                {
                    UpdatePeak(i, value, height);
                }
            }
        }

        private void UpdatePeak(int index, float currentValue, double height)
        {
            if (currentValue > _peakValues[index])
            {
                _peakValues[index] = currentValue;
                _peakHoldCounters[index] = PeakHoldTime;
            }
            else if (_peakHoldCounters[index] > 0)
            {
                _peakHoldCounters[index]--;
            }
            else
            {
                _peakValues[index] = Math.Max(0, _peakValues[index] - PeakFallRate);
            }

            var peakY = height - (_peakValues[index] * height) - 3;
            Canvas.SetTop(_peakBars[index], Math.Max(0, peakY));
            _peakBars[index].Visibility = _peakValues[index] > 0.01 ? Visibility.Visible : Visibility.Collapsed;
        }

        private List<float> ResampleData(List<float> source, int targetCount)
        {
            if (source.Count == targetCount)
                return source;

            var result = new List<float>(targetCount);
            var ratio = (double)source.Count / targetCount;

            for (int i = 0; i < targetCount; i++)
            {
                var startIdx = (int)(i * ratio);
                var endIdx = Math.Min((int)((i + 1) * ratio), source.Count);

                if (startIdx >= source.Count)
                {
                    result.Add(0);
                    continue;
                }

                // Take average of samples in this bin
                var sum = 0f;
                var count = 0;
                for (int j = startIdx; j < endIdx; j++)
                {
                    sum += source[j];
                    count++;
                }
                result.Add(count > 0 ? sum / count : 0);
            }

            return result;
        }

        private List<float>? GetSpectrumList()
        {
            var data = SpectrumData;
            if (data == null)
                return null;

            if (data is IList<float> floatList)
                return floatList.ToList();

            if (data is float[] floatArray)
                return floatArray.ToList();

            if (data is IEnumerable<float> floatEnumerable)
                return floatEnumerable.ToList();

            if (data is double[] doubleArray)
                return doubleArray.Select(d => (float)d).ToList();

            if (data is IList<double> doubleList)
                return doubleList.Select(d => (float)d).ToList();

            return null;
        }

        private void UpdateVisualProperties()
        {
            Brush? gradientBrush = UseGradient ? CreateGradientBrush() : null;
            Brush defaultBrush = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 0, 255, 255));

            foreach (var bar in _bars)
            {
                bar.Fill = BarColor ?? gradientBrush ?? defaultBrush;
            }

            var defaultPeakBrush = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 255, 255, 0));
            foreach (var peakBar in _peakBars)
            {
                peakBar.Fill = PeakColor ?? defaultPeakBrush;
                peakBar.Visibility = ShowPeaks ? Visibility.Visible : Visibility.Collapsed;
            }

            UpdateBarLayout();
        }

        private LinearGradientBrush CreateGradientBrush()
        {
            return new LinearGradientBrush
            {
                StartPoint = new Windows.Foundation.Point(0.5, 1),
                EndPoint = new Windows.Foundation.Point(0.5, 0),
                GradientStops = new GradientStopCollection
                {
                    new GradientStop { Color = Windows.UI.Color.FromArgb(255, 0, 100, 255), Offset = 0 },
                    new GradientStop { Color = Windows.UI.Color.FromArgb(255, 0, 255, 255), Offset = 0.5 },
                    new GradientStop { Color = Windows.UI.Color.FromArgb(255, 0, 255, 128), Offset = 0.75 },
                    new GradientStop { Color = Windows.UI.Color.FromArgb(255, 255, 255, 0), Offset = 0.9 },
                    new GradientStop { Color = Windows.UI.Color.FromArgb(255, 255, 0, 0), Offset = 1 }
                }
            };
        }

        /// <summary>
        /// Reset all peaks immediately.
        /// </summary>
        public void ResetPeaks()
        {
            for (int i = 0; i < _peakValues.Count; i++)
            {
                _peakValues[i] = 0;
                _peakHoldCounters[i] = 0;
            }
        }

        /// <summary>
        /// Clear all spectrum data.
        /// </summary>
        public void Clear()
        {
            foreach (var bar in _bars)
            {
                bar.Height = 0;
            }
            ResetPeaks();
        }
    }
}
