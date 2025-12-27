using Microsoft.UI.Xaml.Controls;
using System;

namespace VoiceStudio.App.Views.Shell
{
    public sealed partial class StatusBarView : UserControl, IDisposable
    {
        private System.Threading.Timer? _clockTimer;
        private bool _disposed = false;

        public StatusBarView()
        {
            this.InitializeComponent();
            UpdateClock();
            
            // Update clock every minute
            _clockTimer = new System.Threading.Timer(_ => 
            {
                if (!_disposed)
                {
                    this.DispatcherQueue.TryEnqueue(() => UpdateClock());
                }
            }, null, TimeSpan.Zero, TimeSpan.FromMinutes(1));
        }

        private void UpdateClock()
        {
            ClockText.Text = DateTime.Now.ToString("h:mm tt");
        }

        public void SetStatus(string status)
        {
            StatusText.Text = status;
        }

        public void SetActiveJob(string jobName, double progress)
        {
            ActiveJobText.Text = jobName;
            ActiveJobText.Visibility = Microsoft.UI.Xaml.Visibility.Visible;
            JobProgress.Value = progress;
            JobProgress.Visibility = Microsoft.UI.Xaml.Visibility.Visible;
        }

        public void ClearActiveJob()
        {
            ActiveJobText.Visibility = Microsoft.UI.Xaml.Visibility.Collapsed;
            JobProgress.Visibility = Microsoft.UI.Xaml.Visibility.Collapsed;
        }

        public void UpdateMetrics(double cpu, double gpu, double ram)
        {
            CpuMeter.Value = cpu;
            GpuMeter.Value = gpu;
            RamMeter.Value = ram;
        }

        public void Dispose()
        {
            if (_disposed)
                return;

            _clockTimer?.Dispose();
            _clockTimer = null;
            _disposed = true;
        }
    }
}

