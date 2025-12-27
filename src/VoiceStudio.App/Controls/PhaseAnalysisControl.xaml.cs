using Microsoft.UI.Xaml.Controls;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Phase analysis visualization control.
    ///
    /// NOTE: Win2D/CanvasControl rendering is temporarily disabled to restore XAML compiler stability
    /// during Phase 0 (build reliability). This stub preserves the public surface for bindings.
    /// </summary>
    public sealed partial class PhaseAnalysisControl : UserControl
    {
        public PhaseAnalysisControl()
        {
            InitializeComponent();
        }

        public PhaseData? Data { get; set; }
        public double PlaybackPosition { get; set; } = -1.0;
    }
}

