using Microsoft.UI.Xaml.Controls;
using System.Collections.Generic;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Waveform visualization control.
    ///
    /// NOTE: Win2D/CanvasControl rendering is temporarily disabled to restore XAML compiler stability
    /// during Phase 0 (build reliability). This stub preserves the public surface for bindings.
    /// </summary>
    public sealed partial class WaveformControl : UserControl
    {
        public WaveformControl()
        {
            InitializeComponent();
        }

        public List<float> Samples { get; set; } = new();
        public string Mode { get; set; } = "peak";
        public double ZoomLevel { get; set; } = 1.0;
        public double PlaybackPosition { get; set; } = -1.0;
    }
}

