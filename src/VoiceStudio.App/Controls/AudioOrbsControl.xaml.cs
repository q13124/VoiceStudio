using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// AudioOrbs visualization control.
    ///
    /// NOTE: Win2D/CanvasControl rendering is temporarily disabled to restore XAML compiler stability
    /// during Phase 0 (build reliability). This stub preserves the public surface for bindings.
    /// </summary>
    public sealed class AudioOrbsControl : UserControl
    {
        public AudioOrbsControl()
        {
            // NOTE: XAML-backed implementation temporarily removed to avoid XamlCompiler.exe crashes.
            Content = new TextBlock
            {
                Text = "Audio orbs visualization temporarily disabled (XAML compiler stability)",
                TextWrapping = TextWrapping.Wrap,
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center,
                Opacity = 0.7
            };
        }

        public AudioOrbsData? Data { get; set; }
    }
}

