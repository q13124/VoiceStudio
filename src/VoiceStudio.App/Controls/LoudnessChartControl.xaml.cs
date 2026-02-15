using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using System.Collections.Generic;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Loudness (LUFS) chart visualization. Renders time-series LUFS data
    /// with optional integrated/peak reference lines and playback position.
    /// </summary>
    public sealed partial class LoudnessChartControl : UserControl
    {
        public static readonly DependencyProperty TimesProperty =
            DependencyProperty.Register(nameof(Times), typeof(IList<double>), typeof(LoudnessChartControl),
                new PropertyMetadata(null, OnDataChanged));
        public static readonly DependencyProperty LufsValuesProperty =
            DependencyProperty.Register(nameof(LufsValues), typeof(IList<double>), typeof(LoudnessChartControl),
                new PropertyMetadata(null, OnDataChanged));
        public static readonly DependencyProperty IntegratedLufsProperty =
            DependencyProperty.Register(nameof(IntegratedLufs), typeof(double?), typeof(LoudnessChartControl),
                new PropertyMetadata(null, OnDataChanged));
        public static readonly DependencyProperty PeakLufsProperty =
            DependencyProperty.Register(nameof(PeakLufs), typeof(double?), typeof(LoudnessChartControl),
                new PropertyMetadata(null, OnDataChanged));
        public static readonly DependencyProperty DurationProperty =
            DependencyProperty.Register(nameof(Duration), typeof(double), typeof(LoudnessChartControl),
                new PropertyMetadata(0.0, OnDataChanged));
        public static readonly DependencyProperty LineColorProperty =
            DependencyProperty.Register(nameof(LineColor), typeof(Brush), typeof(LoudnessChartControl),
                new PropertyMetadata(null));
        public static readonly DependencyProperty PlaybackPositionProperty =
            DependencyProperty.Register(nameof(PlaybackPosition), typeof(double), typeof(LoudnessChartControl),
                new PropertyMetadata(-1.0, OnDataChanged));

        public IList<double>? Times { get => (IList<double>?)GetValue(TimesProperty); set => SetValue(TimesProperty, value); }
        public IList<double>? LufsValues { get => (IList<double>?)GetValue(LufsValuesProperty); set => SetValue(LufsValuesProperty, value); }
        public double? IntegratedLufs { get => (double?)GetValue(IntegratedLufsProperty); set => SetValue(IntegratedLufsProperty, value); }
        public double? PeakLufs { get => (double?)GetValue(PeakLufsProperty); set => SetValue(PeakLufsProperty, value); }
        public double Duration { get => (double)GetValue(DurationProperty); set => SetValue(DurationProperty, value); }
        public Brush? LineColor { get => (Brush?)GetValue(LineColorProperty); set => SetValue(LineColorProperty, value); }
        public double PlaybackPosition { get => (double)GetValue(PlaybackPositionProperty); set => SetValue(PlaybackPositionProperty, value); }

        private static void OnDataChanged(DependencyObject d, DependencyPropertyChangedEventArgs e) => ((LoudnessChartControl)d).UpdateVisual();

        public LoudnessChartControl()
        {
            InitializeComponent();
            Loaded += (_, _) => UpdateVisual();
            SizeChanged += (_, _) => UpdateVisual();
        }

        private void UpdateVisual()
        {
            var times = Times;
            var values = LufsValues;
            if (times == null || values == null || times.Count == 0 || values.Count == 0 || times.Count != values.Count)
            {
                LoudnessPath.Data = null;
                IntegratedLine.Visibility = Visibility.Collapsed;
                PeakLine.Visibility = Visibility.Collapsed;
                PlaybackLine.Visibility = Visibility.Collapsed;
                EmptyStateText.Visibility = Visibility.Visible;
                return;
            }

            EmptyStateText.Visibility = Visibility.Collapsed;
            double w = LoudnessContainer.ActualWidth;
            double h = LoudnessContainer.ActualHeight;
            if (w <= 0 || h <= 0) return;

            double dur = Duration > 0 ? Duration : 1.0;
            double minLufs = -60;
            double maxLufs = 0;
            foreach (var v in values)
            {
                if (v < minLufs) minLufs = v;
                if (v > maxLufs) maxLufs = v;
            }
            if (maxLufs <= minLufs) maxLufs = minLufs + 1;

            var pg = new PathGeometry();
            var pf = new PathFigure();
            for (int i = 0; i < times.Count; i++)
            {
                double x = (times[i] / dur) * w;
                double y = h - ((values[i] - minLufs) / (maxLufs - minLufs)) * h;
                if (i == 0) pf.StartPoint = new Windows.Foundation.Point(x, y);
                else pf.Segments.Add(new LineSegment { Point = new Windows.Foundation.Point(x, y) });
            }
            pg.Figures.Add(pf);
            LoudnessPath.Data = pg;
            if (LineColor != null) LoudnessPath.Stroke = LineColor;

            double pad = 4;
            IntegratedLine.Visibility = IntegratedLufs.HasValue ? Visibility.Visible : Visibility.Collapsed;
            if (IntegratedLufs.HasValue)
            {
                double yy = h - ((IntegratedLufs.Value - minLufs) / (maxLufs - minLufs)) * h;
                IntegratedLine.X1 = pad; IntegratedLine.X2 = w - pad;
                IntegratedLine.Y1 = yy; IntegratedLine.Y2 = yy;
            }

            PeakLine.Visibility = PeakLufs.HasValue ? Visibility.Visible : Visibility.Collapsed;
            if (PeakLufs.HasValue)
            {
                double yy = h - ((PeakLufs.Value - minLufs) / (maxLufs - minLufs)) * h;
                PeakLine.X1 = pad; PeakLine.X2 = w - pad;
                PeakLine.Y1 = yy; PeakLine.Y2 = yy;
            }

            PlaybackLine.Visibility = PlaybackPosition >= 0 && PlaybackPosition <= dur ? Visibility.Visible : Visibility.Collapsed;
            if (PlaybackPosition >= 0 && PlaybackPosition <= dur)
            {
                double xx = (PlaybackPosition / dur) * w;
                PlaybackLine.X1 = xx; PlaybackLine.X2 = xx;
                PlaybackLine.Y1 = 0; PlaybackLine.Y2 = h;
            }
        }
    }
}
