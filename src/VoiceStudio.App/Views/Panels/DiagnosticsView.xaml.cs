using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.App.Controls;
using VoiceStudio.App.Core.Commands;
using VoiceStudio.App.Services;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls.Primitives;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.Linq;
using UIColors = Microsoft.UI.Colors;

namespace VoiceStudio.App.Views.Panels
{
  public sealed partial class DiagnosticsView : UserControl
  {
    public DiagnosticsViewModel ViewModel { get; }
    private ToastNotificationService? _toastService;
    private IUnifiedCommandRegistry? _commandRegistry;
    private ObservableCollection<CommandHealthItem> _commandHealthItems = new();

    public DiagnosticsView()
    {
      this.InitializeComponent();
      // Wire DataContext with BackendClient from service provider
      ViewModel = new DiagnosticsViewModel(AppServices.GetRequiredService<VoiceStudio.Core.Services.IViewModelContext>(), ServiceProvider.GetBackendClient());
      this.DataContext = ViewModel;

      // Initialize services
      _toastService = ServiceProvider.GetToastNotificationService();
      _commandRegistry = AppServices.TryGetCommandRegistry();

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

      // Initialize System Info tab as visible (default selected)
      SystemInfoGrid.Visibility = Visibility.Visible;

      // Configure virtualization for all ListViews to optimize large lists
      VirtualizedListHelper.ConfigureListView(LogsListView);
      VirtualizedListHelper.ConfigureListView(TracesListView);
      VirtualizedListHelper.ConfigureListView(EnginesListView);
      VirtualizedListHelper.ConfigureListView(CommandsListView);
      VirtualizedListHelper.ConfigureListView(EnvVarsListView);
    }

    private void TabView_SelectionChanged(object? sender, Microsoft.UI.Xaml.Controls.SelectionChangedEventArgs e)
    {
      // Show/hide tab content based on selection
      if (DiagnosticsTabView?.SelectedItem is TabViewItem selectedTab)
      {
        // Hide all content grids
        SystemInfoGrid.Visibility = Visibility.Collapsed;
        LogsGrid.Visibility = Visibility.Collapsed;
        TracesGrid.Visibility = Visibility.Collapsed;
        NetworkGrid.Visibility = Visibility.Collapsed;
        EnginesGrid.Visibility = Visibility.Collapsed;
        CommandsGrid.Visibility = Visibility.Collapsed;
        EnvironmentGrid.Visibility = Visibility.Collapsed;

        // Legacy grids
        ErrorsTabGrid.Visibility = Visibility.Collapsed;
        AuditLogTabGrid.Visibility = Visibility.Collapsed;
        AnalyticsTabGrid.Visibility = Visibility.Collapsed;
        PerformanceTabGrid.Visibility = Visibility.Collapsed;
        FeatureFlagsTabGrid.Visibility = Visibility.Collapsed;
        EnvironmentTabGrid.Visibility = Visibility.Collapsed;

        // Show selected tab grid based on header
        switch (selectedTab.Header?.ToString())
        {
          case "System Info":
            SystemInfoGrid.Visibility = Visibility.Visible;
            break;
          case "Logs":
            LogsGrid.Visibility = Visibility.Visible;
            break;
          case "Traces":
            TracesGrid.Visibility = Visibility.Visible;
            _ = ViewModel.LoadTracesAsync();
            break;
          case "Network":
            NetworkGrid.Visibility = Visibility.Visible;
            break;
          case "Engines":
            EnginesGrid.Visibility = Visibility.Visible;
            break;
          case "Commands":
            CommandsGrid.Visibility = Visibility.Visible;
            LoadCommandHealth();
            break;
          case "Environment":
            EnvironmentGrid.Visibility = Visibility.Visible;
            break;
          case "Errors":
            ErrorsTabGrid.Visibility = Visibility.Visible;
            break;
          case "Audit Log":
            AuditLogTabGrid.Visibility = Visibility.Visible;
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

    private void RefreshCommands_Click(object sender, RoutedEventArgs e)
    {
      LoadCommandHealth();
    }

    private void LoadCommandHealth()
    {
      if (_commandRegistry == null)
      {
        Debug.WriteLine("[DiagnosticsView] Command registry not available");
        return;
      }

      try
      {
        var allCommands = _commandRegistry.GetAllCommands();
        _commandHealthItems.Clear();

        int totalCommands = 0;
        int workingCount = 0;
        int brokenCount = 0;
        int totalExecutions = 0;

        foreach (var descriptor in allCommands)
        {
          totalCommands++;
          
          // Get runtime state for this command
          var state = _commandRegistry.GetState(descriptor.Id);
          var status = state?.Status ?? CommandStatus.Unknown;
          var successCount = state?.SuccessCount ?? 0;
          var failureCount = state?.FailureCount ?? 0;
          var avgMs = state?.AverageExecutionMs ?? 0.0;
          var lastError = state?.LastError;
          var lastExecuted = state?.LastExecuted;
          
          // Check live CanExecute status
          var canExecute = _commandRegistry.CanExecute(descriptor.Id, null);
          
          if (status == CommandStatus.Working)
            workingCount++;
          else if (status == CommandStatus.Broken)
            brokenCount++;

          totalExecutions += successCount + failureCount;

          _commandHealthItems.Add(new CommandHealthItem
          {
            CommandId = descriptor.Id,
            Title = descriptor.Title,
            Shortcut = descriptor.KeyboardShortcut ?? "",
            Status = status,
            CanExecute = canExecute,
            SuccessCount = successCount,
            FailureCount = failureCount,
            AvgExecutionMs = avgMs.ToString("F1"),
            LastError = lastError,
            LastExecuted = lastExecuted
          });
        }

        // Update summary counts
        TotalCommandsCount.Text = totalCommands.ToString();
        WorkingCommandsCount.Text = workingCount.ToString();
        BrokenCommandsCount.Text = brokenCount.ToString();
        TotalExecutionsCount.Text = totalExecutions.ToString();

        CommandsListView.ItemsSource = _commandHealthItems;

        Debug.WriteLine($"[DiagnosticsView] Loaded {totalCommands} commands");
      }
      catch (System.Exception ex)
      {
        Debug.WriteLine($"[DiagnosticsView] Failed to load command health: {ex.Message}");
      }
    }
  }

  /// <summary>
  /// View model for command health display in diagnostics.
  /// </summary>
  public sealed class CommandHealthItem
  {
    public string CommandId { get; set; } = "";
    public string Title { get; set; } = "";
    public string Shortcut { get; set; } = "";
    public CommandStatus Status { get; set; }
    public bool CanExecute { get; set; }
    public int SuccessCount { get; set; }
    public int FailureCount { get; set; }
    public string AvgExecutionMs { get; set; } = "0.0";
    public string? LastError { get; set; }
    public DateTime? LastExecuted { get; set; }

    public string StatusGlyph => Status switch
    {
      CommandStatus.Working => "\uE73E",  // Checkmark
      CommandStatus.Broken => "\uE711",   // Error
      CommandStatus.Disabled => "\uE8D8", // Pause
      _ => "\uE9CE"                       // Question mark
    };

    public SolidColorBrush StatusColor => Status switch
    {
      CommandStatus.Working => new SolidColorBrush(UIColors.Green),
      CommandStatus.Broken => new SolidColorBrush(UIColors.Red),
      CommandStatus.Disabled => new SolidColorBrush(UIColors.Gray),
      _ => new SolidColorBrush(UIColors.Orange)
    };

    public string StatusText => Status switch
    {
      CommandStatus.Working => "Working",
      CommandStatus.Broken => "Broken",
      CommandStatus.Disabled => "Disabled",
      CommandStatus.Unknown => "Unknown",
      _ => "Unknown"
    };

    public string CanExecuteGlyph => CanExecute ? "\uE73E" : "\uE711";  // Check or X

    public SolidColorBrush CanExecuteColor => CanExecute 
      ? new SolidColorBrush(UIColors.Green) 
      : new SolidColorBrush(UIColors.Red);

    public string CanExecuteText => CanExecute ? "Ready" : "Blocked";

    public string LastExecutedText => LastExecuted.HasValue 
      ? LastExecuted.Value.ToLocalTime().ToString("HH:mm:ss") 
      : "Never";

    public SolidColorBrush FailureColor => FailureCount > 0 
      ? new SolidColorBrush(UIColors.Red) 
      : new SolidColorBrush(UIColors.Gray);
  }
}