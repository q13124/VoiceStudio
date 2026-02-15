using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Shapes;
using System.Collections.Generic;
using System.Linq;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Ensemble timeline: horizontal bars per voice block (StartTime, Duration, RowIndex).
    /// </summary>
    public sealed partial class EnsembleTimelineControl : UserControl
    {
        private List<VoiceTimelineBlock> _blocks = new();

        public EnsembleTimelineControl()
        {
            InitializeComponent();
            Loaded += (_, _) => Redraw();
            SizeChanged += (_, _) => Redraw();
        }

        public string MixMode { get; set; } = "sequential";

        public void SetTimelineBlocks(List<VoiceTimelineBlock>? blocks)
        {
            _blocks = blocks ?? new List<VoiceTimelineBlock>();
            Redraw();
        }

        private void Redraw()
        {
            TimelineCanvas.Children.Clear();
            if (_blocks.Count == 0)
            {
                EmptyText.Visibility = Visibility.Visible;
                return;
            }
            EmptyText.Visibility = Visibility.Collapsed;
            double w = Root.ActualWidth;
            double h = Root.ActualHeight;
            if (w <= 0 || h <= 0) return;

            double maxTime = _blocks.Max(b => b.StartTime + b.Duration);
            if (maxTime <= 0) maxTime = 1;
            int rows = (_blocks.Max(b => b.RowIndex) + 1);
            if (rows <= 0) rows = 1;
            double rowH = (h - 8) / rows;
            double pad = 4;

            foreach (var b in _blocks)
            {
                int row = b.RowIndex >= 0 ? b.RowIndex : 0;
                double x = (b.StartTime / maxTime) * (w - 2 * pad) + pad;
                double bw = System.Math.Max(4, (b.Duration / maxTime) * (w - 2 * pad));
                double y = pad + row * rowH + 2;
                double bh = rowH - 4;
                var rect = new Rectangle
                {
                    Width = bw,
                    Height = bh,
                    Fill = new SolidColorBrush(Microsoft.UI.Colors.SteelBlue),
                    Stroke = new SolidColorBrush(Microsoft.UI.Colors.White),
                    StrokeThickness = 1,
                    RadiusX = 2,
                    RadiusY = 2
                };
                Canvas.SetLeft(rect, x);
                Canvas.SetTop(rect, y);
                TimelineCanvas.Children.Add(rect);
            }
        }
    }
}
