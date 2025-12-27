using Microsoft.UI.Xaml.Controls;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Radar/spider chart visualization control.
    ///
    /// NOTE: Win2D/CanvasControl rendering is temporarily disabled to restore XAML compiler stability
    /// during Phase 0 (build reliability). This stub preserves the public surface for bindings.
    /// </summary>
    public sealed partial class RadarChartControl : UserControl
    {
        public RadarChartControl()
        {
            InitializeComponent();
        }

        public RadarData? Data { get; set; }
    }
}

