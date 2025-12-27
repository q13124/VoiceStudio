using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// VU meter visualization control.
    ///
    /// NOTE: Win2D/CanvasControl rendering is temporarily disabled to restore XAML compiler stability
    /// during Phase 0 (build reliability). This stub preserves the public surface for bindings.
    /// </summary>
    public sealed partial class VUMeterControl : UserControl
    {
        public VUMeterControl()
        {
            InitializeComponent();
        }

        public double PeakLevel { get; set; }
        public double RmsLevel { get; set; }
    }
}

