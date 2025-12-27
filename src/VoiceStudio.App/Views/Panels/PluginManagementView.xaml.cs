using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using VoiceStudio.App.ViewModels;
using VoiceStudio.App.Controls;
using VoiceStudio.App.Services;
using Windows.System;

namespace VoiceStudio.App.Views.Panels
{
    public sealed partial class PluginManagementView : UserControl
    {
        public PluginManagementViewModel ViewModel { get; }

        public PluginManagementView()
        {
            this.InitializeComponent();
            ViewModel = new PluginManagementViewModel();
            this.DataContext = ViewModel;

            // Add keyboard navigation
            this.KeyDown += PluginManagementView_KeyDown;

            // Setup keyboard navigation
            this.Loaded += PluginManagementView_KeyboardNavigation_Loaded;

            // Setup Escape key to close help overlay
            KeyboardNavigationHelper.SetupEscapeKeyHandling(this, () =>
            {
                if (HelpOverlay.IsVisible)
                {
                    HelpOverlay.IsVisible = false;
                }
            });
        }

        private void PluginManagementView_KeyboardNavigation_Loaded(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
        {
            KeyboardNavigationHelper.SetupTabNavigation(this);
        }

        private void PluginManagementView_KeyDown(object sender, KeyRoutedEventArgs e)
        {
            // F5 refreshes plugins
            if (e.Key == VirtualKey.F5)
            {
                if (ViewModel.RefreshPluginsCommand.CanExecute(null))
                {
                    ViewModel.RefreshPluginsCommand.Execute(null);
                    e.Handled = true;
                }
            }
            // Ctrl+F focuses search
            else if (e.Key == VirtualKey.F)
            {
                if (InputHelper.IsControlPressed())
                {
                    // Focus search TextBox
                    SearchQueryTextBox?.Focus(Microsoft.UI.Xaml.FocusState.Keyboard);
                    e.Handled = true;
                }
            }
            // Delete key disables selected plugin
            else if (e.Key == VirtualKey.Delete)
            {
                if (ViewModel.SelectedPlugin != null && ViewModel.SelectedPlugin.IsEnabled && ViewModel.DisablePluginCommand.CanExecute(ViewModel.SelectedPlugin))
                {
                    ViewModel.DisablePluginCommand.Execute(ViewModel.SelectedPlugin);
                    e.Handled = true;
                }
            }
        }

        private void HelpButton_Click(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
        {
            HelpOverlay.Title = "Plugin Management Help";
            HelpOverlay.HelpText = "The Plugin Management panel allows you to view, enable, disable, and reload plugins. Plugins extend VoiceStudio's functionality with additional features and panels. Use the search box to find specific plugins, and select a plugin to view its details and manage its state.";

            HelpOverlay.Shortcuts.Clear();
            HelpOverlay.Shortcuts.Add(new Controls.KeyboardShortcut { Key = "F5", Description = "Refresh plugins" });
            HelpOverlay.Shortcuts.Add(new Controls.KeyboardShortcut { Key = "Ctrl+F", Description = "Focus search" });

            HelpOverlay.Tips.Clear();
            HelpOverlay.Tips.Add("Plugins are loaded from the Plugins directory at startup.");
            HelpOverlay.Tips.Add("Disabled plugins remain installed but are not active.");
            HelpOverlay.Tips.Add("Reload a plugin to refresh its state after changes.");
            HelpOverlay.Tips.Add("Plugin errors are displayed in the plugin details.");

            HelpOverlay.Visibility = Microsoft.UI.Xaml.Visibility.Visible;
            HelpOverlay.Show();
        }
    }
}

