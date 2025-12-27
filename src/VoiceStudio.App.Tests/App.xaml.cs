using Microsoft.UI.Xaml;

namespace VoiceStudio.App.Tests
{
    public partial class App : Application
    {
        public App()
        {
            this.InitializeComponent();
        }

        protected override void OnLaunched(Microsoft.UI.Xaml.LaunchActivatedEventArgs args)
        {
            // Test app initialization - no window needed for unit tests
        }
    }
}
