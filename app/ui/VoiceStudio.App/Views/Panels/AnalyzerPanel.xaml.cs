using Microsoft.UI.Xaml.Controls;
using VoiceStudio.App.Views.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Views.Panels
{
    public sealed partial class AnalyzerPanel : UserControl
    {
        public AnalyzerViewModel ViewModel { get; }

        public AnalyzerPanel()
        {
            this.InitializeComponent();
            var backendClient = ServiceProvider.GetBackendClient();
            ViewModel = new AnalyzerViewModel(backendClient);
            DataContext = ViewModel;
        }

        private void TabView_SelectionChanged(TabView sender, TabViewSelectionChangedEventArgs args)
        {
            if (args.SelectedItem is TabViewItem selectedTab)
            {
                ViewModel.SelectedTab = selectedTab.Header?.ToString() ?? "Waveform";
            }
        }
    }
}

