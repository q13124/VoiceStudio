using Microsoft.UI.Xaml.Controls;
using System.Collections.Generic;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Loudness (LUFS) chart visualization control.
    ///
    /// NOTE: Win2D/CanvasControl rendering is temporarily disabled to restore XAML compiler stability
    /// during Phase 0 (build reliability). This stub preserves the public surface for bindings.
    /// </summary>
    public sealed partial class LoudnessChartControl : UserControl
    {
        public LoudnessChartControl()
        {
            InitializeComponent();
        }

        public List<double> Times { get; set; } = new();
        public List<double> LufsValues { get; set; } = new();
        public double? IntegratedLufs { get; set; }
        public double? PeakLufs { get; set; }
        public double PlaybackPosition { get; set; } = -1.0;
    }
}

