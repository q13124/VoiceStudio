// Phase 5.5: Chart Control Implementations
// Task 5.5.2: VU Meter visualization control

using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Shapes;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// VU Meter orientation.
    /// </summary>
    public enum VUMeterOrientation
    {
        Horizontal,
        Vertical
    }

    /// <summary>
    /// VU Meter visualization control for audio level monitoring.
    /// Supports peak hold, clip indicators, and multiple display modes.
    /// </summary>
    public sealed partial class VUMeterControl : UserControl
    {
        private Rectangle? _levelBar;
        private Rectangle? _peakIndicator;
        private Rectangle? _clipIndicator;
        private double _peakValue;
        private int _peakHoldCounter;
        private int _clipHoldCounter;
        private const int PeakHoldTime = 60;
        private const int ClipHoldTime = 30;
        private const float PeakFallRate = 0.005f;
        private const float ClipThreshold = 0.95f;

        public static readonly DependencyProperty LevelProperty =
            DependencyProperty.Register(
                nameof(Level),
                typeof(double),
                typeof(VUMeterControl),
                new PropertyMetadata(0.0, OnLevelChanged));

        public static readonly DependencyProperty MinLevelProperty =
            DependencyProperty.Register(
                nameof(MinLevel),
                typeof(double),
                typeof(VUMeterControl),
                new PropertyMetadata(-60.0));

        public static readonly DependencyProperty MaxLevelProperty =
            DependencyProperty.Register(
                nameof(MaxLevel),
                typeof(double),
                typeof(VUMeterControl),
                new PropertyMetadata(0.0));

        public static readonly DependencyProperty OrientationProperty =
            DependencyProperty.Register(
                nameof(Orientation),
                typeof(VUMeterOrientation),
                typeof(VUMeterControl),
                new PropertyMetadata(VUMeterOrientation.Vertical, OnLayoutPropertyChanged));

        public static readonly DependencyProperty ShowPeakProperty =
            DependencyProperty.Register(
                nameof(ShowPeak),
                typeof(bool),
                typeof(VUMeterControl),
                new PropertyMetadata(true));

        public static readonly DependencyProperty ShowClipProperty =
            DependencyProperty.Register(
                nameof(ShowClip),
                typeof(bool),
                typeof(VUMeterControl),
                new PropertyMetadata(true));

        public static readonly DependencyProperty LevelColorProperty =
            DependencyProperty.Register(
                nameof(LevelColor),
                typeof(Brush),
                typeof(VUMeterControl),
                new PropertyMetadata(null, OnVisualPropertyChanged));

        public static readonly DependencyProperty PeakColorProperty =
            DependencyProperty.Register(
                nameof(PeakColor),
                typeof(Brush),
                typeof(VUMeterControl),
                new PropertyMetadata(null, OnVisualPropertyChanged));

        public static readonly DependencyProperty ClipColorProperty =
            DependencyProperty.Register(
                nameof(ClipColor),
                typeof(Brush),
                typeof(VUMeterControl),
                new PropertyMetadata(null, OnVisualPropertyChanged));

        public static readonly DependencyProperty UseGradientProperty =
            DependencyProperty.Register(
                nameof(UseGradient),
                typeof(bool),
                typeof(VUMeterControl),
                new PropertyMetadata(true, OnVisualPropertyChanged));

        public VUMeterControl()
        {
            InitializeComponent();
            SizeChanged += OnSizeChanged;
            Loaded += OnLoaded;
        }

        /// <summary>
        /// Current audio level (in dB if using dB scale, or 0-1 for linear).
        /// </summary>
        public double Level
        {
            get => (double)GetValue(LevelProperty);
            set => SetValue(LevelProperty, value);
        }

        /// <summary>
        /// Minimum level for the meter scale.
        /// </summary>
        public double MinLevel
        {
            get => (double)GetValue(MinLevelProperty);
            set => SetValue(MinLevelProperty, value);
        }

        /// <summary>
        /// Maximum level for the meter scale.
        /// </summary>
        public double MaxLevel
        {
            get => (double)GetValue(MaxLevelProperty);
            set => SetValue(MaxLevelProperty, value);
        }

        /// <summary>
        /// Meter orientation.
        /// </summary>
        public VUMeterOrientation Orientation
        {
            get => (VUMeterOrientation)GetValue(OrientationProperty);
            set => SetValue(OrientationProperty, value);
        }

        /// <summary>
        /// Whether to show the peak hold indicator.
        /// </summary>
        public bool ShowPeak
        {
            get => (bool)GetValue(ShowPeakProperty);
            set => SetValue(ShowPeakProperty, value);
        }

        /// <summary>
        /// Whether to show the clip indicator.
        /// </summary>
        public bool ShowClip
        {
            get => (bool)GetValue(ShowClipProperty);
            set => SetValue(ShowClipProperty, value);
        }

        public Brush? LevelColor
        {
            get => (Brush?)GetValue(LevelColorProperty);
            set => SetValue(LevelColorProperty, value);
        }

        public Brush? PeakColor
        {
            get => (Brush?)GetValue(PeakColorProperty);
            set => SetValue(PeakColorProperty, value);
        }

        public Brush? ClipColor
        {
            get => (Brush?)GetValue(ClipColorProperty);
            set => SetValue(ClipColorProperty, value);
        }

        public bool UseGradient
        {
            get => (bool)GetValue(UseGradientProperty);
            set => SetValue(UseGradientProperty, value);
        }

        private static void OnLevelChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is VUMeterControl control)
            {
                control.UpdateLevel();
            }
        }

        private static void OnLayoutPropertyChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is VUMeterControl control)
            {
                control.UpdateLayout();
            }
        }

        private static void OnVisualPropertyChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is VUMeterControl control)
            {
                control.UpdateVisualProperties();
            }
        }

        private void OnLoaded(object sender, RoutedEventArgs e)
        {
            InitializeControls();
        }

        private void OnSizeChanged(object sender, SizeChangedEventArgs e)
        {
            UpdateLayout();
        }

        private void InitializeControls()
        {
            if (Content is not Grid grid)
                return;

            grid.Children.Clear();

            // Background track
            var track = new Rectangle
            {
                Fill = new SolidColorBrush(Windows.UI.Color.FromArgb(40, 255, 255, 255)),
                RadiusX = 2,
                RadiusY = 2,
                HorizontalAlignment = HorizontalAlignment.Stretch,
                VerticalAlignment = VerticalAlignment.Stretch
            };
            grid.Children.Add(track);

            // Level bar
            _levelBar = new Rectangle
            {
                Fill = LevelColor ?? CreateGradientBrush(),
                RadiusX = 2,
                RadiusY = 2,
                HorizontalAlignment = Orientation == VUMeterOrientation.Horizontal 
                    ? HorizontalAlignment.Left 
                    : HorizontalAlignment.Stretch,
                VerticalAlignment = Orientation == VUMeterOrientation.Vertical 
                    ? VerticalAlignment.Bottom 
                    : VerticalAlignment.Stretch
            };
            grid.Children.Add(_levelBar);

            // Peak indicator
            _peakIndicator = new Rectangle
            {
                Fill = PeakColor ?? new SolidColorBrush(Windows.UI.Color.FromArgb(255, 255, 255, 0)),
                Height = Orientation == VUMeterOrientation.Vertical ? 3 : double.NaN,
                Width = Orientation == VUMeterOrientation.Horizontal ? 3 : double.NaN,
                HorizontalAlignment = Orientation == VUMeterOrientation.Horizontal 
                    ? HorizontalAlignment.Left 
                    : HorizontalAlignment.Stretch,
                VerticalAlignment = Orientation == VUMeterOrientation.Vertical 
                    ? VerticalAlignment.Bottom 
                    : VerticalAlignment.Stretch,
                Visibility = ShowPeak ? Visibility.Visible : Visibility.Collapsed
            };
            grid.Children.Add(_peakIndicator);

            // Clip indicator
            _clipIndicator = new Rectangle
            {
                Fill = ClipColor ?? new SolidColorBrush(Windows.UI.Color.FromArgb(255, 255, 0, 0)),
                Height = Orientation == VUMeterOrientation.Vertical ? 6 : double.NaN,
                Width = Orientation == VUMeterOrientation.Horizontal ? 6 : double.NaN,
                HorizontalAlignment = Orientation == VUMeterOrientation.Horizontal 
                    ? HorizontalAlignment.Right 
                    : HorizontalAlignment.Stretch,
                VerticalAlignment = Orientation == VUMeterOrientation.Vertical 
                    ? VerticalAlignment.Top 
                    : VerticalAlignment.Stretch,
                Visibility = Visibility.Collapsed
            };
            grid.Children.Add(_clipIndicator);

            UpdateLayout();
        }

        private void UpdateLevel()
        {
            if (_levelBar == null)
                return;

            // Normalize level to 0-1 range
            var normalizedLevel = (Level - MinLevel) / (MaxLevel - MinLevel);
            normalizedLevel = Math.Clamp(normalizedLevel, 0, 1);

            var width = ActualWidth;
            var height = ActualHeight;

            if (width <= 0 || height <= 0)
                return;

            // Update level bar
            if (Orientation == VUMeterOrientation.Vertical)
            {
                _levelBar.Height = normalizedLevel * height;
            }
            else
            {
                _levelBar.Width = normalizedLevel * width;
            }

            // Update peak
            if (ShowPeak && _peakIndicator != null)
            {
                UpdatePeak(normalizedLevel, width, height);
            }

            // Check for clipping
            if (ShowClip && _clipIndicator != null)
            {
                UpdateClip(normalizedLevel);
            }
        }

        private void UpdatePeak(double currentLevel, double width, double height)
        {
            if (_peakIndicator == null)
                return;

            if (currentLevel > _peakValue)
            {
                _peakValue = currentLevel;
                _peakHoldCounter = PeakHoldTime;
            }
            else if (_peakHoldCounter > 0)
            {
                _peakHoldCounter--;
            }
            else
            {
                _peakValue = Math.Max(0, _peakValue - PeakFallRate);
            }

            if (Orientation == VUMeterOrientation.Vertical)
            {
                var peakY = height - (_peakValue * height);
                _peakIndicator.Margin = new Thickness(0, peakY, 0, 0);
                _peakIndicator.VerticalAlignment = VerticalAlignment.Top;
            }
            else
            {
                var peakX = _peakValue * width;
                _peakIndicator.Margin = new Thickness(peakX - 1.5, 0, 0, 0);
                _peakIndicator.HorizontalAlignment = HorizontalAlignment.Left;
            }

            _peakIndicator.Visibility = _peakValue > 0.01 ? Visibility.Visible : Visibility.Collapsed;
        }

        private void UpdateClip(double currentLevel)
        {
            if (_clipIndicator == null)
                return;

            if (currentLevel >= ClipThreshold)
            {
                _clipHoldCounter = ClipHoldTime;
                _clipIndicator.Visibility = Visibility.Visible;
            }
            else if (_clipHoldCounter > 0)
            {
                _clipHoldCounter--;
            }
            else
            {
                _clipIndicator.Visibility = Visibility.Collapsed;
            }
        }

        private new void UpdateLayout()
        {
            if (_levelBar == null)
                return;

            _levelBar.HorizontalAlignment = Orientation == VUMeterOrientation.Horizontal
                ? HorizontalAlignment.Left
                : HorizontalAlignment.Stretch;
            _levelBar.VerticalAlignment = Orientation == VUMeterOrientation.Vertical
                ? VerticalAlignment.Bottom
                : VerticalAlignment.Stretch;

            if (_peakIndicator != null)
            {
                _peakIndicator.Height = Orientation == VUMeterOrientation.Vertical ? 3 : double.NaN;
                _peakIndicator.Width = Orientation == VUMeterOrientation.Horizontal ? 3 : double.NaN;
            }

            if (_clipIndicator != null)
            {
                _clipIndicator.Height = Orientation == VUMeterOrientation.Vertical ? 6 : double.NaN;
                _clipIndicator.Width = Orientation == VUMeterOrientation.Horizontal ? 6 : double.NaN;
                _clipIndicator.HorizontalAlignment = Orientation == VUMeterOrientation.Horizontal
                    ? HorizontalAlignment.Right
                    : HorizontalAlignment.Stretch;
                _clipIndicator.VerticalAlignment = Orientation == VUMeterOrientation.Vertical
                    ? VerticalAlignment.Top
                    : VerticalAlignment.Stretch;
            }

            UpdateLevel();
        }

        private void UpdateVisualProperties()
        {
            if (_levelBar != null)
            {
                _levelBar.Fill = LevelColor ?? (UseGradient ? CreateGradientBrush() : new SolidColorBrush(Windows.UI.Color.FromArgb(255, 0, 255, 0)));
            }

            if (_peakIndicator != null)
            {
                _peakIndicator.Fill = PeakColor ?? new SolidColorBrush(Windows.UI.Color.FromArgb(255, 255, 255, 0));
            }

            if (_clipIndicator != null)
            {
                _clipIndicator.Fill = ClipColor ?? new SolidColorBrush(Windows.UI.Color.FromArgb(255, 255, 0, 0));
            }
        }

        private LinearGradientBrush CreateGradientBrush()
        {
            var isVertical = Orientation == VUMeterOrientation.Vertical;

            return new LinearGradientBrush
            {
                StartPoint = isVertical ? new Windows.Foundation.Point(0.5, 1) : new Windows.Foundation.Point(0, 0.5),
                EndPoint = isVertical ? new Windows.Foundation.Point(0.5, 0) : new Windows.Foundation.Point(1, 0.5),
                GradientStops = new GradientStopCollection
                {
                    new GradientStop { Color = Windows.UI.Color.FromArgb(255, 0, 128, 0), Offset = 0 },
                    new GradientStop { Color = Windows.UI.Color.FromArgb(255, 0, 255, 0), Offset = 0.6 },
                    new GradientStop { Color = Windows.UI.Color.FromArgb(255, 255, 255, 0), Offset = 0.85 },
                    new GradientStop { Color = Windows.UI.Color.FromArgb(255, 255, 128, 0), Offset = 0.95 },
                    new GradientStop { Color = Windows.UI.Color.FromArgb(255, 255, 0, 0), Offset = 1 }
                }
            };
        }

        /// <summary>
        /// Reset the peak hold indicator.
        /// </summary>
        public void ResetPeak()
        {
            _peakValue = 0;
            _peakHoldCounter = 0;
            if (_peakIndicator != null)
            {
                _peakIndicator.Visibility = Visibility.Collapsed;
            }
        }

        /// <summary>
        /// Reset the clip indicator.
        /// </summary>
        public void ResetClip()
        {
            _clipHoldCounter = 0;
            if (_clipIndicator != null)
            {
                _clipIndicator.Visibility = Visibility.Collapsed;
            }
        }

        /// <summary>
        /// Reset all indicators.
        /// </summary>
        public void Reset()
        {
            ResetPeak();
            ResetClip();
            Level = MinLevel;
        }
    }
}
