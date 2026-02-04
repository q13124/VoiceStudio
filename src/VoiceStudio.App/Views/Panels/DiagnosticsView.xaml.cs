using Microsoft.UI.Xaml.Controls;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.App.Services;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls.Primitives;

namespace VoiceStudio.App.Views.Panels
{
  public sealed partial class DiagnosticsView : UserControl
  {
    public DiagnosticsViewModel ViewModel { get; }
    private ToastNotificationService? _toastService;

    public DiagnosticsView()
    {
      this.InitializeComponent();
      // Wire DataContext with BackendClient from service provider
      ViewModel = new DiagnosticsViewModel(AppServices.GetRequiredService<VoiceStudio.Core.Services.IViewModelContext>(), ServiceProvider.GetBackendClient());
      this.DataContext = ViewModel;

      // Initialize services
      _toastService = ServiceProvider.GetToastNotificationService();

      // Subscribe to ViewModel events for toast notifications
      ViewModel.PropertyChanged += (s, e) =>
      {
        if (e.PropertyName == nameof(DiagnosticsViewModel.ErrorMessage) && !string.IsNullOrEmpty(ViewModel.ErrorMessage))
        {
          _toastService?.ShowToast(ToastType.Error, "Diagnostics Error", ViewModel.ErrorMessage);
        }
      };

      // Setup keyboard navigation
      this.Loaded += DiagnosticsView_KeyboardNavigation_Loaded;

      // Setup Escape key to close help overlay
      KeyboardNavigationHelper.SetupEscapeKeyHandling(this, () =>
      {
        if (HelpOverlay.IsVisible)
        {
          HelpOverlay.Hide();
        }
      });
    }

    private void DiagnosticsView_KeyboardNavigation_Loaded(object sender, RoutedEventArgs e)
    {
      // Setup Tab navigation order for this panel
      KeyboardNavigationHelper.SetupTabNavigation(this, 0);

      // Setup tab selection changed handler
      DiagnosticsTabView.SelectionChanged += TabView_SelectionChanged;

      // Initialize Errors tab as visible (default selected)
      ErrorsTabGrid.Visibility = Visibility.Visible;
    }

    private void TabView_SelectionChanged(object? sender, Microsoft.UI.Xaml.Controls.SelectionChangedEventArgs e)
    {
      // Show/hide tab content based on selection
      if (DiagnosticsTabView?.SelectedItem is TabViewItem selectedTab)
      {
        // Hide all tab grids
        ErrorsTabGrid.Visibility = Visibility.Collapsed;
        AuditLogTabGrid.Visibility = Visibility.Collapsed;
        AnalyticsTabGrid.Visibility = Visibility.Collapsed;
        PerformanceTabGrid.Visibility = Visibility.Collapsed;
        FeatureFlagsTabGrid.Visibility = Visibility.Collapsed;
        EnvironmentTabGrid.Visibility = Visibility.Collapsed;

        // Show selected tab grid based on header
        switch (selectedTab.Header?.ToString())
        {
          case "Errors":
            ErrorsTabGrid.Visibility = Visibility.Visible;
            break;
          case "Audit Log":
            AuditLogTabGrid.Visibility = Visibility.Visible;
            // Load audit entries when tab is selected
            _ = ViewModel.LoadAuditEntriesAsync();
            break;
          case "Analytics":
            AnalyticsTabGrid.Visibility = Visibility.Visible;
            break;
          case "Performance":
            PerformanceTabGrid.Visibility = Visibility.Visible;
            break;
          case "Feature Flags":
            FeatureFlagsTabGrid.Visibility = Visibility.Visible;
            break;
          case "Environment":
            EnvironmentTabGrid.Visibility = Visibility.Visible;
            break;
        }
      }
    }

    private void HelpButton_Click(object _, RoutedEventArgs __)
    {
      HelpOverlay.Title = "Diagnostics Help";
      HelpOverlay.HelpText = "The Diagnostics panel provides system health monitoring, telemetry data, and comprehensive logging. Monitor CPU, GPU, and RAM usage in real-time. View application logs and error logs with filtering options. Check system health status and connection status. Use auto-refresh to keep telemetry data up to date. Export error logs for debugging purposes. The panel also shows memory breakdown by component and system performance metrics.";

      HelpOverlay.Shortcuts.Clear();
      HelpOverlay.Shortcuts.Add(new Controls.KeyboardShortcut { Key = "F5", Description = "Refresh telemetry" });
      HelpOverlay.Shortcuts.Add(new Controls.KeyboardShortcut { Key = "Ctrl+A", Description = "Select all logs (in log view)" });
      HelpOverlay.Shortcuts.Add(new Controls.KeyboardShortcut { Key = "Escape", Description = "Clear selection / Close help" });

      HelpOverlay.Tips.Clear();
      HelpOverlay.Tips.Add("Enable auto-refresh to monitor system metrics continuously");
      HelpOverlay.Tips.Add("Use error log filters to find specific errors or warnings");
      HelpOverlay.Tips.Add("Export error logs to share with support or for debugging");
      HelpOverlay.Tips.Add("Monitor VRAM usage to avoid memory issues during synthesis");
      HelpOverlay.Tips.Add("Check health status to ensure all components are functioning");
      HelpOverlay.Tips.Add("The degraded mode warning indicates system issues that need attention");
      HelpOverlay.Tips.Add("Memory breakdown shows resource usage by UI, audio, and engines");
      HelpOverlay.Tips.Add("Connection status shows backend connectivity and queued operations");

      HelpOverlay.Visibility = Visibility.Visible;
      HelpOverlay.Show();
    }
  }
}