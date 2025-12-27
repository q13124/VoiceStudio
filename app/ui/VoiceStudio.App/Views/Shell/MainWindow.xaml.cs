using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using VoiceStudio.App.Views.Panels;

namespace VoiceStudio.App.Views.Shell
{
    public sealed partial class MainWindow : Window
    {
        private ProfilesPanel? _profilesPanel;
        private LibraryPanel? _libraryPanel;

        public MainWindow()
        {
            this.InitializeComponent();
            InitializeNavigation();
        }

        private void InitializeNavigation()
        {
            // Store panel references
            _profilesPanel = ProfilesPanelContent;
            _libraryPanel = new LibraryPanel();

            // Wire up navigation toggle buttons
            NavProfiles.Click += (s, e) => 
            { 
                NavProfiles.IsChecked = true;
                NavLibrary.IsChecked = false;
                NavBatch.IsChecked = false;
                SwitchLeftPanel("Profiles");
            };
            
            NavLibrary.Click += (s, e) => 
            { 
                NavLibrary.IsChecked = true;
                NavProfiles.IsChecked = false;
                NavBatch.IsChecked = false;
                SwitchLeftPanel("Library");
            };
            
            NavBatch.Click += (s, e) => 
            { 
                NavBatch.IsChecked = true;
                NavProfiles.IsChecked = false;
                NavLibrary.IsChecked = false;
                SwitchLeftPanel("Batch");
            };
        }

        private void SwitchLeftPanel(string panelName)
        {
            switch (panelName)
            {
                case "Profiles":
                    LeftPanelHost.Content = _profilesPanel;
                    LeftPanelHost.Title = "Profiles";
                    LeftPanelHost.IconGlyph = "\uE8A5";
                    break;
                case "Library":
                    if (_libraryPanel == null) _libraryPanel = new LibraryPanel();
                    LeftPanelHost.Content = _libraryPanel;
                    LeftPanelHost.Title = "Library";
                    LeftPanelHost.IconGlyph = "\uE8F1";
                    break;
                case "Batch":
                    // Placeholder for future Batch panel
                    LeftPanelHost.Title = "Batch";
                    LeftPanelHost.IconGlyph = "\uE8F5";
                    break;
            }
        }
    }
}

