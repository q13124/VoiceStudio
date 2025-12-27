using VoiceStudio.Core.Models;
using System.Collections.ObjectModel;

namespace VoiceStudio.App.Views.Shell
{
    public class StatusBarViewModel
    {
        public string StatusText { get; set; } = "Ready";
        public string? ActiveJob { get; set; }
        public double JobProgress { get; set; }
        public MeterReading CurrentMetrics { get; set; } = new MeterReading();
    }
}

