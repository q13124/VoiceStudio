using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml;
using System.Collections.ObjectModel;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Custom control for rendering analytics metrics as a time-series line chart.
    /// Displays metric values over time with grid lines and labels.
    /// </summary>
    public sealed class AnalyticsChartControl : UserControl
    {
        private ObservableCollection<AnalyticsMetricItem> _metrics = new();

        public AnalyticsChartControl()
        {
            // NOTE: XAML-backed implementation temporarily removed to avoid XamlCompiler.exe crashes.
            Content = new TextBlock
            {
                Text = "Analytics chart temporarily disabled (XAML compiler stability)",
                TextWrapping = TextWrapping.Wrap,
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center,
                Opacity = 0.7
            };
        }

        /// <summary>
        /// Analytics metrics to display in the chart.
        /// </summary>
        public ObservableCollection<AnalyticsMetricItem> Metrics
        {
            get => _metrics;
            set
            {
                if (_metrics != null)
                {
                    _metrics.CollectionChanged -= Metrics_CollectionChanged;
                }

                _metrics = value ?? new ObservableCollection<AnalyticsMetricItem>();

                if (_metrics != null)
                {
                    _metrics.CollectionChanged += Metrics_CollectionChanged;
                }
            }
        }

        private void Metrics_CollectionChanged(object? sender, System.Collections.Specialized.NotifyCollectionChangedEventArgs e)
        {
            // Rendering is intentionally disabled while XAML compiler stability is being restored.
        }
    }
}

