using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Ensemble timeline control.
    ///
    /// NOTE: Rendering/interaction is temporarily disabled to restore XAML compiler stability
    /// during Phase 0 (build reliability). This stub preserves the MixMode binding surface.
    /// </summary>
    public sealed partial class EnsembleTimelineControl : UserControl
    {
        public EnsembleTimelineControl()
        {
            InitializeComponent();
        }

        public string MixMode { get; set; } = "sequential";

        /// <summary>
        /// Sets the timeline blocks (placeholder implementation).
        /// </summary>
        public void SetTimelineBlocks(System.Collections.Generic.List<VoiceTimelineBlock> blocks)
        {
            // TODO: Implement timeline block rendering
            // This is a placeholder to restore compilation
        }
    }
}

