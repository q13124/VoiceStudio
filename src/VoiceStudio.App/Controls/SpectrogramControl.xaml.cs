using Microsoft.UI.Xaml.Controls;
using System.Collections.Generic;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Spectrogram visualization control.
    ///
    /// NOTE: Win2D/CanvasControl rendering is temporarily disabled to restore XAML compiler stability
    /// during Phase 0 (build reliability). This stub preserves the public surface for bindings.
    /// </summary>
    public sealed partial class SpectrogramControl : UserControl
    {
        public SpectrogramControl()
        {
            InitializeComponent();
        }

        public List<SpectrogramFrame> Frames { get; set; } = new();
        public double ZoomLevel { get; set; } = 1.0;
        public double PlaybackPosition { get; set; } = -1.0;
    }

    /// <summary>
    /// Represents a single frame of spectrogram data.
    /// </summary>
    public class SpectrogramFrame
    {
        public double Time { get; set; }
        public List<float> Frequencies { get; set; } = new();
    }
}

