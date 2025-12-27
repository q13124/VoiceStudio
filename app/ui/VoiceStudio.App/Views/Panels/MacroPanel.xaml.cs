using Microsoft.UI.Xaml.Controls;
using VoiceStudio.App.Views.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Views.Panels
{
    public sealed partial class MacroPanel : UserControl
    {
        public MacroViewModel ViewModel { get; }

        public MacroPanel()
        {
            this.InitializeComponent();
            var backendClient = ServiceProvider.GetBackendClient();
            ViewModel = new MacroViewModel(backendClient);
            DataContext = ViewModel;
        }
    }
}

