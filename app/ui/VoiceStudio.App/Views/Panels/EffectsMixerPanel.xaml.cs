using Microsoft.UI.Xaml.Controls;
using VoiceStudio.App.Views.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Views.Panels
{
    public sealed partial class EffectsMixerPanel : UserControl
    {
        public EffectsMixerViewModel ViewModel { get; }

        public EffectsMixerPanel()
        {
            this.InitializeComponent();
            var backendClient = ServiceProvider.GetBackendClient();
            ViewModel = new EffectsMixerViewModel(backendClient);
            DataContext = ViewModel;
        }
    }
}

