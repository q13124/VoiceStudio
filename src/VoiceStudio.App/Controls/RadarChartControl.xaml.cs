using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using System;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Radar/spider chart for multi-axis magnitude data (e.g. frequency bands).
    /// </summary>
    public sealed partial class RadarChartControl : UserControl
    {
        public static readonly DependencyProperty DataProperty =
            DependencyProperty.Register(nameof(Data), typeof(RadarData), typeof(RadarChartControl),
                new PropertyMetadata(null, OnDataChanged));
        public static readonly DependencyProperty RadarColorProperty =
            DependencyProperty.Register(nameof(RadarColor), typeof(Brush), typeof(RadarChartControl),
                new PropertyMetadata(null, OnDataChanged));

        public RadarData? Data { get => (RadarData?)GetValue(DataProperty); set => SetValue(DataProperty, value); }
        public Brush? RadarColor { get => (Brush?)GetValue(RadarColorProperty); set => SetValue(RadarColorProperty, value); }

        private static void OnDataChanged(DependencyObject d, DependencyPropertyChangedEventArgs e) => ((RadarChartControl)d).UpdateVisual();

        public RadarChartControl()
        {
            InitializeComponent();
            Loaded += (_, _) => UpdateVisual();
            SizeChanged += (_, _) => UpdateVisual();
        }

        private void UpdateVisual()
        {
            var data = Data;
            if (data?.Magnitudes == null || data.Magnitudes.Count == 0)
            {
                RadarPath.Data = null;
                RadarPath.Visibility = Visibility.Collapsed;
                EmptyStateText.Visibility = Visibility.Visible;
                return;
            }
            EmptyStateText.Visibility = Visibility.Collapsed;
            RadarPath.Visibility = Visibility.Visible;
            if (RadarColor != null) RadarPath.Stroke = RadarPath.Fill = RadarColor;

            double w = RadarContainer.ActualWidth;
            double h = RadarContainer.ActualHeight;
            if (w <= 0 || h <= 0) return;
            double cx = w / 2;
            double cy = h / 2;
            double r = Math.Min(w, h) / 2 - 8;
            int n = data.Magnitudes.Count;
            if (n == 0) return;

            var pg = new PathGeometry();
            var pf = new PathFigure();
            for (int i = 0; i <= n; i++)
            {
                int idx = i % n;
                double mag = data.Magnitudes[idx] < 0 ? 0 : (data.Magnitudes[idx] > 1 ? 1 : data.Magnitudes[idx]);
                double angle = Math.PI * 2 * idx / n - Math.PI / 2;
                double x = cx + r * mag * Math.Cos(angle);
                double y = cy + r * mag * Math.Sin(angle);
                if (i == 0) pf.StartPoint = new Windows.Foundation.Point(x, y);
                else pf.Segments.Add(new LineSegment { Point = new Windows.Foundation.Point(x, y) });
            }
            pg.Figures.Add(pf);
            RadarPath.Data = pg;
        }
    }
}
