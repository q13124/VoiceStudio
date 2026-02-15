using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using System;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Multi-curve automation editor: draws the selected curve.
    /// </summary>
    public sealed partial class AutomationCurvesEditorControl : UserControl
    {
        public static readonly DependencyProperty SelectedTrackIdProperty =
            DependencyProperty.Register(nameof(SelectedTrackId), typeof(string), typeof(AutomationCurvesEditorControl),
                new PropertyMetadata(string.Empty, OnSelectionChanged));
        public static readonly DependencyProperty SelectedCurveProperty =
            DependencyProperty.Register(nameof(SelectedCurve), typeof(AutomationCurve), typeof(AutomationCurvesEditorControl),
                new PropertyMetadata(null, OnSelectionChanged));

        public string SelectedTrackId { get => (string)GetValue(SelectedTrackIdProperty); set => SetValue(SelectedTrackIdProperty, value); }
        public AutomationCurve? SelectedCurve { get => (AutomationCurve?)GetValue(SelectedCurveProperty); set => SetValue(SelectedCurveProperty, value); }

        private static void OnSelectionChanged(DependencyObject d, DependencyPropertyChangedEventArgs e) => ((AutomationCurvesEditorControl)d).UpdateVisual();

        public AutomationCurvesEditorControl()
        {
            InitializeComponent();
            Loaded += (_, _) => UpdateVisual();
            SizeChanged += (_, _) => UpdateVisual();
        }

        private void UpdateVisual()
        {
            var curve = SelectedCurve;
            if (curve?.Points == null || curve.Points.Count == 0)
            {
                CurvePath.Data = null;
                EmptyText.Visibility = Visibility.Visible;
                return;
            }
            EmptyText.Visibility = Visibility.Collapsed;
            double w = Root.ActualWidth;
            double h = Root.ActualHeight;
            if (w <= 0 || h <= 0) return;

            double maxT = 0.001;
            double minV = 0, maxV = 1;
            foreach (var p in curve.Points) { if (p.Time > maxT) maxT = p.Time; if (p.Value < minV) minV = p.Value; if (p.Value > maxV) maxV = p.Value; }
            if (maxT <= 0) maxT = 1;
            if (maxV <= minV) maxV = minV + 0.01;

            var pf = new PathFigure();
            for (int i = 0; i < curve.Points.Count; i++)
            {
                var p = curve.Points[i];
                double x = (p.Time / maxT) * w;
                double y = h - (p.Value - minV) / (maxV - minV) * h;
                if (i == 0) pf.StartPoint = new Windows.Foundation.Point(x, y);
                else pf.Segments.Add(new LineSegment { Point = new Windows.Foundation.Point(x, y) });
            }
            CurvePath.Data = new PathGeometry { Figures = { pf } };
        }
    }
}
