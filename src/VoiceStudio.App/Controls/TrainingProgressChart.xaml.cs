using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using System.Collections.Generic;
using System.Linq;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Training progress chart: loss and quality metrics over epochs.
    /// </summary>
    public sealed partial class TrainingProgressChart : UserControl
    {
        private List<TrainingQualityMetrics> _dataPoints = new();

        public TrainingProgressChart()
        {
            InitializeComponent();
            Loaded += (_, _) => Redraw();
            SizeChanged += (_, _) => Redraw();
        }

        public void UpdateChart(IEnumerable<TrainingQualityMetrics>? dataPoints)
        {
            _dataPoints = dataPoints?.ToList() ?? new List<TrainingQualityMetrics>();
            Redraw();
        }

        private void Redraw()
        {
            if (_dataPoints.Count == 0)
            {
                LossPath.Data = null;
                QualityPath.Data = null;
                EmptyStateText.Visibility = Visibility.Visible;
                return;
            }
            EmptyStateText.Visibility = Visibility.Collapsed;
            double w = ChartContainer.ActualWidth;
            double h = ChartContainer.ActualHeight;
            if (w <= 0 || h <= 0) return;

            double maxEpoch = _dataPoints.Max(x => x.Epoch);
            if (maxEpoch <= 0) maxEpoch = 1;
            double minLoss = _dataPoints.Min(x => x.TrainingLoss ?? x.ValidationLoss ?? 0);
            double maxLoss = _dataPoints.Max(x => x.TrainingLoss ?? x.ValidationLoss ?? 1);
            if (maxLoss <= minLoss) maxLoss = minLoss + 0.01;
            double minQ = _dataPoints.Min(x => x.QualityScore ?? x.MosScore ?? 0);
            double maxQ = _dataPoints.Max(x => x.QualityScore ?? x.MosScore ?? 1);
            if (maxQ <= minQ) maxQ = minQ + 0.01;

            var lossFig = new PathFigure();
            var qualityFig = new PathFigure();
            for (int i = 0; i < _dataPoints.Count; i++)
            {
                var p = _dataPoints[i];
                double x = (p.Epoch / maxEpoch) * w;
                double yLoss = h - ((p.TrainingLoss ?? p.ValidationLoss ?? 0) - minLoss) / (maxLoss - minLoss) * h;
                double yQ = h - ((p.QualityScore ?? p.MosScore ?? 0) - minQ) / (maxQ - minQ) * h;
                if (i == 0)
                {
                    lossFig.StartPoint = new Windows.Foundation.Point(x, yLoss);
                    qualityFig.StartPoint = new Windows.Foundation.Point(x, yQ);
                }
                else
                {
                    lossFig.Segments.Add(new LineSegment { Point = new Windows.Foundation.Point(x, yLoss) });
                    qualityFig.Segments.Add(new LineSegment { Point = new Windows.Foundation.Point(x, yQ) });
                }
            }
            LossPath.Data = new PathGeometry { Figures = { lossFig } };
            QualityPath.Data = new PathGeometry { Figures = { qualityFig } };
        }
    }
}
