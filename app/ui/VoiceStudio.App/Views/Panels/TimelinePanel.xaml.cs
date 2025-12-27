using Microsoft.UI.Xaml.Controls;
using VoiceStudio.App.Views.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Views.Panels
{
    public sealed partial class TimelinePanel : UserControl
    {
        public TimelineViewModel ViewModel { get; }

        public TimelinePanel()
        {
            this.InitializeComponent();
            var backendClient = ServiceProvider.GetBackendClient();
            ViewModel = new TimelineViewModel(backendClient);
            DataContext = ViewModel;
        }
    }
}

