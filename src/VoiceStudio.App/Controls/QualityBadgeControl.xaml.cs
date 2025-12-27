using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using VoiceStudio.Core.Models;
using System;
using Windows.UI;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Quality badge control for panel headers.
    /// Implements IDEA 8: Real-Time Quality Metrics Badge in Panel Headers.
    /// </summary>
    public sealed partial class QualityBadgeControl : UserControl
    {
        public static readonly DependencyProperty QualityMetricsProperty =
            DependencyProperty.Register(
                nameof(QualityMetrics),
                typeof(QualityMetrics),
                typeof(QualityBadgeControl),
                new PropertyMetadata(null, OnQualityMetricsChanged));

        public static readonly DependencyProperty QualityTextProperty =
            DependencyProperty.Register(
                nameof(QualityText),
                typeof(string),
                typeof(QualityBadgeControl),
                new PropertyMetadata("—"));

        public static readonly DependencyProperty QualityBrushProperty =
            DependencyProperty.Register(
                nameof(QualityBrush),
                typeof(Brush),
                typeof(QualityBadgeControl),
                new PropertyMetadata(new SolidColorBrush(Microsoft.UI.Colors.Gray)));

        public static readonly DependencyProperty TooltipTextProperty =
            DependencyProperty.Register(
                nameof(TooltipText),
                typeof(string),
                typeof(QualityBadgeControl),
                new PropertyMetadata("No quality metrics available"));

        public static readonly DependencyProperty QualityScoreProperty =
            DependencyProperty.Register(
                nameof(QualityScore),
                typeof(double?),
                typeof(QualityBadgeControl),
                new PropertyMetadata(null, OnQualityScoreChanged));

        public event EventHandler<RoutedEventArgs>? BadgeClicked;

        public QualityMetrics? QualityMetrics
        {
            get => (QualityMetrics?)GetValue(QualityMetricsProperty);
            set => SetValue(QualityMetricsProperty, value);
        }

        public double? QualityScore
        {
            get => (double?)GetValue(QualityScoreProperty);
            set => SetValue(QualityScoreProperty, value);
        }

        public string QualityText
        {
            get => (string)GetValue(QualityTextProperty);
            private set => SetValue(QualityTextProperty, value);
        }

        public Brush QualityBrush
        {
            get => (Brush)GetValue(QualityBrushProperty);
            private set => SetValue(QualityBrushProperty, value);
        }

        public string TooltipText
        {
            get => (string)GetValue(TooltipTextProperty);
            private set => SetValue(TooltipTextProperty, value);
        }

        public QualityBadgeControl()
        {
            this.InitializeComponent();
            UpdateBadge();
            
            // Make the badge clickable
            BadgeBorder.PointerPressed += (s, e) =>
            {
                BadgeClicked?.Invoke(this, e);
            };
            // Cursor property not available in WinUI 3 - use PointerEntered/PointerExited events instead
            BadgeBorder.PointerEntered += (s, e) => { /* Visual feedback can be handled via styling */ };
        }

        private static void OnQualityScoreChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is QualityBadgeControl control)
            {
                control.UpdateBadge();
            }
        }

        private static void OnQualityMetricsChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is QualityBadgeControl control)
            {
                control.UpdateBadge();
            }
        }

        private void UpdateBadge()
        {
            // Priority: QualityScore (direct) > QualityMetrics (detailed)
            double? qualityScore = QualityScore;

            if (!qualityScore.HasValue && QualityMetrics != null)
            {
                // Determine quality score from QualityMetrics (prefer MOS, fallback to similarity or naturalness)
                if (QualityMetrics.MosScore.HasValue)
                {
                    qualityScore = QualityMetrics.MosScore.Value;
                }
                else if (QualityMetrics.Similarity.HasValue)
                {
                    // Convert similarity (0-1) to MOS-like scale (1-5)
                    qualityScore = 1.0 + (QualityMetrics.Similarity.Value * 4.0);
                }
                else if (QualityMetrics.Naturalness.HasValue)
                {
                    // Convert naturalness (0-1) to MOS-like scale (1-5)
                    qualityScore = 1.0 + (QualityMetrics.Naturalness.Value * 4.0);
                }
            }

            if (!qualityScore.HasValue)
            {
                QualityText = "—";
                QualityBrush = new SolidColorBrush(Microsoft.UI.Colors.Gray);
                TooltipText = "No quality metrics available";
                ToolTipService.SetToolTip(BadgeBorder, TooltipText);
                return;
            }

            // Format quality score (show 1 decimal place)
            QualityText = qualityScore.Value.ToString("F1");

            // Set color based on quality score
            // Green: ≥4.0, Yellow/Orange: 3.0-3.9, Red: <3.0
            if (qualityScore.Value >= 4.0)
            {
                QualityBrush = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 0, 200, 0)); // Green
            }
            else if (qualityScore.Value >= 3.0)
            {
                QualityBrush = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 255, 180, 0)); // Yellow/Orange
            }
            else
            {
                QualityBrush = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 255, 80, 80)); // Red
            }

            // Build detailed tooltip text
            var tooltipParts = new System.Collections.Generic.List<string>();
            
            if (QualityMetrics != null)
            {
                // Use detailed metrics if available
                if (QualityMetrics.MosScore.HasValue)
                {
                    tooltipParts.Add($"MOS: {QualityMetrics.MosScore.Value:F2}/5.0");
                }
                if (QualityMetrics.Similarity.HasValue)
                {
                    tooltipParts.Add($"Similarity: {QualityMetrics.Similarity.Value * 100:F1}%");
                }
                if (QualityMetrics.Naturalness.HasValue)
                {
                    tooltipParts.Add($"Naturalness: {QualityMetrics.Naturalness.Value * 100:F1}%");
                }
                if (QualityMetrics.SnrDb.HasValue)
                {
                    tooltipParts.Add($"SNR: {QualityMetrics.SnrDb.Value:F1} dB");
                }
            }
            
            // Fallback to simple quality score if no detailed metrics
            if (tooltipParts.Count == 0)
            {
                tooltipParts.Add($"Quality Score: {qualityScore.Value:F2}");
            }

            TooltipText = string.Join(" | ", tooltipParts);
            
            // Add click hint to tooltip
            if (BadgeClicked != null)
            {
                TooltipText += "\n\nClick for detailed quality information";
            }

            // Set tooltip on the border
            ToolTipService.SetToolTip(BadgeBorder, TooltipText);
        }
    }
}

