using Microsoft.UI.Xaml.Controls;
using VoiceStudio.App.Views.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Views.Panels
{
    public sealed partial class ProfilesPanel : UserControl
    {
        public ProfilesViewModel ViewModel { get; }

        public ProfilesPanel()
        {
            this.InitializeComponent();
            var backendClient = ServiceProvider.GetBackendClient();
            ViewModel = new ProfilesViewModel(backendClient);
            DataContext = ViewModel;
        }
    }
}

