using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using VoiceStudio.App.Controls;
using VoiceStudio.App.Services;
using VoiceStudio.App.Views.Panels;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Views.Panels
{
    /// <summary>
    /// Advanced Search with Natural Language view.
    /// Implements IDEA 36: Advanced Search with Natural Language.
    /// </summary>
    public sealed partial class AdvancedSearchView : UserControl
    {
        public AdvancedSearchViewModel ViewModel { get; }

        public AdvancedSearchView()
        {
            this.InitializeComponent();
            ViewModel = new AdvancedSearchViewModel(
                ServiceProvider.GetBackendClient()
            );
            this.DataContext = ViewModel;
            
            // Setup keyboard navigation
            this.Loaded += AdvancedSearchView_KeyboardNavigation_Loaded;
            
            // Setup Escape key to close help overlay
            KeyboardNavigationHelper.SetupEscapeKeyHandling(this, () =>
            {
                if (HelpOverlay.IsVisible)
                {
                    HelpOverlay.IsVisible = false;
                }
            });
        }
        
        private void AdvancedSearchView_KeyboardNavigation_Loaded(object sender, RoutedEventArgs e)
        {
            KeyboardNavigationHelper.SetupTabNavigation(this);
        }

        private async void SearchBox_QuerySubmitted(AutoSuggestBox sender, AutoSuggestBoxQuerySubmittedEventArgs args)
        {
            if (!string.IsNullOrWhiteSpace(args.QueryText))
            {
                await ViewModel.PerformSearchAsync(args.QueryText);
            }
        }

        private void SearchBox_TextChanged(AutoSuggestBox sender, AutoSuggestBoxTextChangedEventArgs args)
        {
            if (args.Reason == AutoSuggestionBoxTextChangeReason.UserInput)
            {
                sender.ItemsSource = ViewModel.QuerySuggestions;
            }
        }

        private void SearchBox_SuggestionChosen(AutoSuggestBox sender, AutoSuggestBoxSuggestionChosenEventArgs args)
        {
            sender.Text = args.SelectedItem?.ToString() ?? string.Empty;
        }

        private async void QueryHistory_ItemClick(object sender, ItemClickEventArgs e)
        {
            if (e.ClickedItem is string query)
            {
                ViewModel.SearchQuery = query;
                await ViewModel.PerformSearchAsync(query);
            }
        }

        private void RemoveFilter_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.CommandParameter is SearchFilter filter)
            {
                ViewModel.ActiveFilters.Remove(filter);
            }
        }

        private void ResultItem_PointerPressed(object sender, Microsoft.UI.Xaml.Input.PointerRoutedEventArgs e)
        {
            if (sender is FrameworkElement element && element.Tag is SearchResult result)
            {
                NavigateToResult(result);
            }
        }

        private void OpenResult_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.CommandParameter is SearchResult result)
            {
                NavigateToResult(result);
            }
        }

        private void NavigateToResult(SearchResult result)
        {
            // Navigate based on result type
            var mainWindow = Microsoft.UI.Xaml.Application.Current as App;
            if (mainWindow != null)
            {
                // Switch to appropriate panel based on result type
                var type = result.Type.ToLower();
                if (type == "profile")
                {
                    // Navigate to Profiles panel and select the profile
                    // This would be handled by MainWindow panel switching logic
                }
                else if (type == "audio")
                {
                    // Navigate to Timeline or Analyzer panel
                }
                else if (type == "project")
                {
                    // Navigate to project view
                }
            }
        }

        private void HelpButton_Click(object sender, RoutedEventArgs e)
        {
            // Phase 0: placeholder help overlay.
            if (HelpOverlay != null)
            {
                HelpOverlay.Title = "Advanced Search Help";
                HelpOverlay.HelpText = "Advanced Search is temporarily simplified for build stability.";
                HelpOverlay.Visibility = Visibility.Visible;
                HelpOverlay.Show();
            }
        }
    }
}

