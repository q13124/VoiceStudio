using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Controls.Primitives;
using VoiceStudio.App.Views.Panels;
using VoiceStudio.App.Views;
using VoiceStudio.App.Services;
using VoiceStudio.App.Utilities;
using VoiceStudio.App.ViewModels;
using Windows.System;
using Windows.Storage;
using Windows.Foundation;
using Windows.UI;
using System.Threading.Tasks;
using System.Diagnostics;
using System;
using System.Linq;
using System.Collections.Generic;
using System.IO;
using Microsoft.UI.Xaml.Media.Animation;
using VoiceStudio.App.Controls;
using VoiceStudio.App.Views.Dialogs;
using Microsoft.UI.Xaml.Media;
using Windows.ApplicationModel;
using VoiceStudio.App.Logging;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.App
{
  public sealed partial class MainWindow : Window
  {
    private readonly KeyboardShortcutService _keyboardShortcutService;
    private readonly IUpdateService _updateService;
    private readonly PanelStateService? _panelStateService;
    private readonly RecentProjectsService? _recentProjectsService;
    private const string ShowWelcomeKey = "ShowWelcomeDialog";
    private bool _disposed;
    private System.Threading.Timer? _clockTimer;
    private PanelPreviewPopup? _panelPreviewPopup;
    private System.Threading.Timer? _previewHideTimer;
    private Popup? _panelQuickSwitchPopup;
    private PanelQuickSwitchIndicator? _panelQuickSwitchIndicator;
    private DispatcherTimer? _quickSwitchHideTimer;
    private bool _isMiniTimelineVisible;

    // Phase 0: avoid MenuBar XAML compiler crashes by creating menu items in code.
    private MenuFlyoutSubItem? _recentProjectsSubMenu;
    private MenuFlyoutItem? _toggleMiniTimelineMenuItem;
    private MenuFlyoutItem? _customizeToolbarMenuItem;
    private MenuFlyoutItem? _checkForUpdatesMenuItem;
    private MenuFlyoutItem? _keyboardShortcutsMenuItem;

    private T? FindInContent<T>(string name) where T : class
    {
      return (Content as FrameworkElement)?.FindName(name) as T;
    }

    private object? FindNameOnContent(string name)
    {
      return FindInContent<object>(name);
    }

    public MainWindow()
    {
      using var profiler = PerformanceProfiler.Start("MainWindow Construction");
      profiler.Checkpoint("Start");

      this.InitializeComponent();
      profiler.Checkpoint("InitializeComponent");

      _keyboardShortcutService = ServiceProvider.GetKeyboardShortcutService();
      profiler.Checkpoint("KeyboardShortcutService Created");

      _updateService = ServiceProvider.GetUpdateService();
      profiler.Checkpoint("UpdateService Retrieved");

      _panelStateService = ServiceProvider.GetPanelStateService();
      profiler.Checkpoint("PanelStateService Retrieved");

      _recentProjectsService = ServiceProvider.GetRecentProjectsService();
      profiler.Checkpoint("RecentProjectsService Retrieved");

      // Initialize Toast Notification Service (IDEA 11)
      var toastContainer = FindInContent<StackPanel>("ToastContainer");
      if (toastContainer != null)
      {
        var toastService = new ToastNotificationService(toastContainer);
        ServiceProvider.RegisterToastNotificationService(toastService);
        profiler.Checkpoint("ToastNotificationService Initialized");
      }

      RegisterKeyboardShortcuts();
      profiler.Checkpoint("Keyboard Shortcuts Registered");

      // Menu items (not in XAML during Phase 0)
      _recentProjectsSubMenu = new MenuFlyoutSubItem { Text = "Recent Projects" };
      _toggleMiniTimelineMenuItem = new MenuFlyoutItem { Text = "Toggle Mini Timeline" };
      _toggleMiniTimelineMenuItem.Click += ToggleMiniTimelineMenuItem_Click;
      _customizeToolbarMenuItem = new MenuFlyoutItem { Text = "Customize Toolbar..." };
      _customizeToolbarMenuItem.Click += CustomizeToolbarMenuItem_Click;
      _checkForUpdatesMenuItem = new MenuFlyoutItem { Text = "Check for Updates..." };
      _checkForUpdatesMenuItem.Click += CheckForUpdatesMenuItem_Click;
      _keyboardShortcutsMenuItem = new MenuFlyoutItem { Text = "Keyboard Shortcuts" };
      _keyboardShortcutsMenuItem.Click += KeyboardShortcutsMenuItem_Click;
      profiler.Checkpoint("Menu Items Created");

      InitializeMenuBar();
      profiler.Checkpoint("Menu Bar Initialized");

      // Enable keyboard navigation - will attach in MainWindow_Activated handler
      // Also register Activated handler for welcome dialog
      this.Activated += MainWindow_Activated;
      profiler.Checkpoint("Event Handlers Registered");

      // Set PanelRegion for each PanelHost
      var leftPanelHost = FindNameOnContent("LeftPanelHost") as Controls.PanelHost;
      var centerPanelHost = FindNameOnContent("CenterPanelHost") as Controls.PanelHost;
      var rightPanelHost = FindNameOnContent("RightPanelHost") as Controls.PanelHost;
      var bottomPanelHost = FindNameOnContent("BottomPanelHost") as Controls.PanelHost;
      if (leftPanelHost != null) leftPanelHost.PanelRegion = PanelRegion.Left;
      if (centerPanelHost != null) centerPanelHost.PanelRegion = PanelRegion.Center;
      if (rightPanelHost != null) rightPanelHost.PanelRegion = PanelRegion.Right;
      if (bottomPanelHost != null) bottomPanelHost.PanelRegion = PanelRegion.Bottom;
      profiler.Checkpoint("PanelRegions Set");

      // Wire up panel docking handlers (IDEA 14)
      if (leftPanelHost != null) leftPanelHost.OnPanelDockRequested += PanelHost_OnPanelDockRequested;
      if (centerPanelHost != null) centerPanelHost.OnPanelDockRequested += PanelHost_OnPanelDockRequested;
      if (rightPanelHost != null) rightPanelHost.OnPanelDockRequested += PanelHost_OnPanelDockRequested;
      if (bottomPanelHost != null) bottomPanelHost.OnPanelDockRequested += PanelHost_OnPanelDockRequested;
      profiler.Checkpoint("Panel Docking Handlers Wired");

      // Load workspace layout before assigning panels
      LoadWorkspaceLayout();
      profiler.Checkpoint("Workspace Layout Loaded");

      // Subscribe to workspace profile changes
      if (_panelStateService != null)
      {
        _panelStateService.WorkspaceProfileChanged += OnWorkspaceProfileChanged;
      }
      profiler.Checkpoint("Workspace Profile Subscription");

      // Temporary content assignment (will be replaced with panel registry later)
      // If workspace layout has saved panels, restore them; otherwise use defaults
      if (!RestorePanelsFromLayout())
      {
        if (leftPanelHost != null) leftPanelHost.Content = new ProfilesView();
        profiler.Checkpoint("ProfilesView Created (Default)");

        if (centerPanelHost != null) centerPanelHost.Content = new TimelineView();
        profiler.Checkpoint("TimelineView Created (Default)");

        if (rightPanelHost != null) rightPanelHost.Content = new EffectsMixerView();
        profiler.Checkpoint("EffectsMixerView Created (Default)");

        // BottomPanelHost can show MiniTimeline or MacroView
        // Default to MacroView (MiniTimeline can be toggled via View menu - IDEA 6)
        if (bottomPanelHost != null) bottomPanelHost.Content = new MacroView();
        profiler.Checkpoint("MacroView Created (Default)");
      }

      SetActiveNavButton("NavStudio");

      // Update menu item state for Mini Timeline toggle (IDEA 6)
      UpdateMiniTimelineMenuItem();

      // Save workspace layout on window close
      this.Closed += MainWindow_Closed;

      // Show welcome dialog on first run
      this.Activated += MainWindow_Activated;

      // Wire up Global Search navigation
      var globalSearchView = FindNameOnContent("GlobalSearchView") as Views.GlobalSearchView;
      if (globalSearchView != null)
      {
        globalSearchView.NavigateRequested += GlobalSearchView_NavigateRequested;
      }

      // Populate Recent Projects menu (IDEA 16)
      PopulateRecentProjectsMenu();

      // Subscribe to recent projects changes
      if (_recentProjectsService != null)
      {
        _recentProjectsService.PropertyChanged += (s, e) =>
        {
          if (e.PropertyName == nameof(RecentProjectsService.AllProjects) ||
                      e.PropertyName == nameof(RecentProjectsService.PinnedProjects) ||
                      e.PropertyName == nameof(RecentProjectsService.RecentProjects))
          {
            PopulateRecentProjectsMenu();
          }
        };
      }

      // Wire up status bar activity indicators (IDEA 19)
      WireUpStatusBarIndicators();
      profiler.Checkpoint("Status Bar Indicators Wired");

      // Start clock timer
      UpdateClock();
      _clockTimer = new System.Threading.Timer(_ =>
      {
        if (!_disposed)
        {
          this.DispatcherQueue.TryEnqueue(() => UpdateClock());
        }
      }, null, TimeSpan.Zero, TimeSpan.FromMinutes(1));

      profiler.Checkpoint("MainWindow Construction Complete");

      Debug.WriteLine(profiler.GetReport());
    }

    #region Navigation Button Click Handlers

    private void NavStudio_Click(object _, RoutedEventArgs __)
    {
      SwitchToPanel(PanelRegion.Center, "Timeline", () => new TimelineView());
      SetActiveNavButton("NavStudio");
    }

    private void NavProfiles_Click(object _, RoutedEventArgs __)
    {
      SwitchToPanel(PanelRegion.Left, "Profiles", () => new ProfilesView());
      SetActiveNavButton("NavProfiles");
    }

    private void NavLibrary_Click(object _, RoutedEventArgs __)
    {
      SwitchToPanel(PanelRegion.Left, "Library", () => new LibraryView());
      SetActiveNavButton("NavLibrary");
    }

    private void NavEffects_Click(object _, RoutedEventArgs __)
    {
      SwitchToPanel(PanelRegion.Right, "Effects Mixer", () => new EffectsMixerView());
      SetActiveNavButton("NavEffects");
    }

    private void NavTrain_Click(object _, RoutedEventArgs __)
    {
      SwitchToPanel(PanelRegion.Left, "Training", () => new TrainingView());
      SetActiveNavButton("NavTrain");
    }

    private void NavAnalyze_Click(object _, RoutedEventArgs __)
    {
      SwitchToPanel(PanelRegion.Right, "Analyzer", () => new AnalyzerView());
      SetActiveNavButton("NavAnalyze");
    }

    private void NavSettings_Click(object _, RoutedEventArgs __)
    {
      SwitchToPanel(PanelRegion.Right, "Settings", () => new SettingsView());
      SetActiveNavButton("NavSettings");
    }

    private void NavLogs_Click(object _, RoutedEventArgs __)
    {
      SwitchToPanel(PanelRegion.Bottom, "Diagnostics", () => new DiagnosticsView());
      SetActiveNavButton("NavLogs");
    }

    #endregion Navigation Button Click Handlers

    private void SetActiveNavButton(string activeButtonName)
    {
      var navButtons = new[]
      {
        FindNameOnContent("NavStudio") as ToggleButton,
        FindNameOnContent("NavProfiles") as ToggleButton,
        FindNameOnContent("NavLibrary") as ToggleButton,
        FindNameOnContent("NavEffects") as ToggleButton,
        FindNameOnContent("NavTrain") as ToggleButton,
        FindNameOnContent("NavAnalyze") as ToggleButton,
        FindNameOnContent("NavSettings") as ToggleButton,
        FindNameOnContent("NavLogs") as ToggleButton
      };

      foreach (var navButton in navButtons)
      {
        if (navButton == null)
        {
          continue;
        }

        navButton.IsChecked = string.Equals(navButton.Name, activeButtonName, StringComparison.Ordinal);
      }
    }

    internal async Task<(string[] Steps, bool TimedOut, string? TimedOutStep)> RunGateCUiSmokeNavigationAsync(string crashDir)
    {
      // Deterministic Gate C UI smoke: exercise primary nav buttons to surface binding failures.
      var executed = new List<string>();

      var perStepTimeout = TimeSpan.FromSeconds(12);
      var warmupTimeout = TimeSpan.FromSeconds(30);
      var stepsLogPath = System.IO.Path.Combine(crashDir, "ui_smoke_steps_latest.log");
      try
      {
        System.IO.Directory.CreateDirectory(crashDir);
        System.IO.File.WriteAllText(
          stepsLogPath,
          $"timestamp_utc\t{DateTime.UtcNow:o}{Environment.NewLine}",
          System.Text.Encoding.UTF8);
      }
      catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {ex.Message}", "MainWindow.Task");
      }

      void AppendStepLog(string line)
      {
        try
        {
          System.IO.File.AppendAllText(
            stepsLogPath,
            $"{DateTime.UtcNow:o}\t{line}{Environment.NewLine}",
            System.Text.Encoding.UTF8);
        }
        catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {ex.Message}", "MainWindow.AppendStepLog");
      }
      }

      var dispatcher = this.DispatcherQueue;
      Task RunOnUiThreadAsync(string stepName, Action action)
      {
        var tcs = new TaskCompletionSource<object?>(TaskCreationOptions.RunContinuationsAsynchronously);

        try
        {
          var enqueued = dispatcher.TryEnqueue(() =>
          {
            try
            {
              AppendStepLog($"DISPATCH_ENTER\t{stepName}");
              action();
              AppendStepLog($"DISPATCH_EXIT\t{stepName}");
              tcs.TrySetResult(null);
            }
            catch (Exception ex)
            {
              AppendStepLog($"DISPATCH_EXCEPTION\t{stepName}\t{ex.GetType().Name}\t{ex.Message}");
              tcs.TrySetException(ex);
            }
          });

          if (!enqueued)
          {
            AppendStepLog($"ENQUEUE_FAILED\t{stepName}");
            tcs.TrySetException(new InvalidOperationException("Failed to enqueue UI smoke step onto DispatcherQueue."));
          }
        }
        catch (Exception ex)
        {
          AppendStepLog($"ENQUEUE_EXCEPTION\t{stepName}\t{ex.GetType().Name}\t{ex.Message}");
          tcs.TrySetException(ex);
        }

        return tcs.Task;
      }

      // Warm up: verify the UI thread is pumping the DispatcherQueue before we attempt navigation.
      AppendStepLog("WARMUP_BEGIN");
      var warmupTask = RunOnUiThreadAsync("Warmup", () => { });
      var warmupCompleted = await Task.WhenAny(warmupTask, Task.Delay(warmupTimeout)).ConfigureAwait(false);
      if (warmupCompleted != warmupTask)
      {
        AppendStepLog($"WARMUP_TIMEOUT\ttimeout_sec={(int)warmupTimeout.TotalSeconds}");
        return (executed.ToArray(), true, "Warmup");
      }

      try
      {
        await warmupTask.ConfigureAwait(false);
      }
      catch (Exception ex)
      {
        AppendStepLog($"WARMUP_EXCEPTION\t{ex.GetType().Name}\t{ex.Message}");
        throw;
      }

      AppendStepLog("WARMUP_DONE");

      var steps = new (string Name, Action Action)[]
      {
        // Primary navigation buttons (8 steps)
        ("NavStudio", () => NavStudio_Click(this, new RoutedEventArgs())),
        ("NavProfiles", () => NavProfiles_Click(this, new RoutedEventArgs())),
        ("NavLibrary", () => NavLibrary_Click(this, new RoutedEventArgs())),
        ("NavTrain", () => NavTrain_Click(this, new RoutedEventArgs())),
        ("NavEffects", () => NavEffects_Click(this, new RoutedEventArgs())),
        ("NavAnalyze", () => NavAnalyze_Click(this, new RoutedEventArgs())),
        ("NavSettings", () => NavSettings_Click(this, new RoutedEventArgs())),
        ("NavLogs", () => NavLogs_Click(this, new RoutedEventArgs())),

        // Core synthesis panels (4 steps)
        ("PanelVoiceSynthesis", () => SwitchToPanel(PanelRegion.Center, "Voice Synthesis", () => new VoiceSynthesisView())),
        ("PanelEnsembleSynthesis", () => SwitchToPanel(PanelRegion.Center, "Ensemble Synthesis", () => new EnsembleSynthesisView())),
        ("PanelBatchProcessing", () => SwitchToPanel(PanelRegion.Center, "Batch Processing", () => new BatchProcessingView())),
        ("PanelTextSpeechEditor", () => SwitchToPanel(PanelRegion.Center, "Text Speech Editor", () => new TextSpeechEditorView())),

        // Training panels (3 steps)
        ("PanelTrainingDatasetEditor", () => SwitchToPanel(PanelRegion.Center, "Training Dataset Editor", () => new TrainingDatasetEditorView())),
        ("PanelModelManager", () => SwitchToPanel(PanelRegion.Center, "Model Manager", () => new ModelManagerView())),
        ("PanelTraining", () => SwitchToPanel(PanelRegion.Center, "Training", () => new TrainingView())),

        // Audio processing panels (4 steps)
        ("PanelTranscribe", () => SwitchToPanel(PanelRegion.Center, "Transcribe", () => new TranscribeView())),
        ("PanelRecording", () => SwitchToPanel(PanelRegion.Center, "Recording", () => new RecordingView())),
        ("PanelAudioAnalysis", () => SwitchToPanel(PanelRegion.Center, "Audio Analysis", () => new AudioAnalysisView())),
        ("PanelQualityControl", () => SwitchToPanel(PanelRegion.Right, "Quality Control", () => new QualityControlView())),

        // Utility panels (3 steps)
        ("PanelTimeline", () => SwitchToPanel(PanelRegion.Center, "Timeline", () => new TimelineView())),
        ("PanelDiagnostics", () => SwitchToPanel(PanelRegion.Right, "Diagnostics", () => new DiagnosticsView())),
        ("PanelHelp", () => SwitchToPanel(PanelRegion.Right, "Help", () => new HelpView())),

        // Voice control panels (3 steps)
        ("PanelVoiceMorph", () => SwitchToPanel(PanelRegion.Center, "Voice Morph", () => new VoiceMorphView())),
        ("PanelProsody", () => SwitchToPanel(PanelRegion.Right, "Prosody", () => new ProsodyView())),
        ("PanelEmotionControl", () => SwitchToPanel(PanelRegion.Right, "Emotion Control", () => new EmotionControlView())),
      };

      foreach (var step in steps)
      {
        executed.Add(step.Name);
        AppendStepLog($"STEP_BEGIN\t{step.Name}");

        var stepTask = RunOnUiThreadAsync(step.Name, step.Action);
        var completed = await Task.WhenAny(stepTask, Task.Delay(perStepTimeout)).ConfigureAwait(false);
        if (completed != stepTask)
        {
          AppendStepLog($"STEP_TIMEOUT\t{step.Name}\ttimeout_sec={(int)perStepTimeout.TotalSeconds}");
          return (executed.ToArray(), true, step.Name);
        }

        try
        {
          await stepTask.ConfigureAwait(false);
        }
        catch (Exception ex)
        {
          AppendStepLog($"STEP_EXCEPTION\t{step.Name}\t{ex.GetType().Name}\t{ex.Message}");
          throw;
        }

        AppendStepLog($"STEP_DONE\t{step.Name}");
        await Task.Delay(250).ConfigureAwait(false);
      }

      return (executed.ToArray(), false, null);
    }

    #region Status Bar Activity Indicators (IDEA 19)

    /// <summary>
    /// Wires up status bar activity indicators to the StatusBarActivityService.
    /// </summary>
    private void WireUpStatusBarIndicators()
    {
      var activityService = ServiceProvider.TryGetStatusBarActivityService();
      if (activityService == null)
        return;

      // Subscribe to activity status changes
      activityService.ActivityStatusChanged += ActivityService_ActivityStatusChanged;

      // Update initial state
      UpdateActivityIndicators(activityService);
    }

    /// <summary>
    /// Handles activity status changes and updates UI indicators.
    /// </summary>
    private void ActivityService_ActivityStatusChanged(object? sender, ActivityStatusChangedEventArgs e)
    {
      // Update on UI thread
      this.DispatcherQueue.TryEnqueue(() => UpdateActivityIndicators(e));
    }

    /// <summary>
    /// Updates activity indicators based on current status.
    /// </summary>
    private void UpdateActivityIndicators(StatusBarActivityService? service = null)
    {
      if (service == null)
        service = ServiceProvider.TryGetStatusBarActivityService();

      if (service == null)
        return;

      var status = new ActivityStatusChangedEventArgs
      {
        ProcessingStatus = service.ProcessingStatus,
        NetworkStatus = service.NetworkStatus,
        EngineStatus = service.EngineStatus,
        ActiveJobCount = service.ActiveJobCount,
        QueuedOperationCount = service.QueuedOperationCount
      };

      UpdateActivityIndicators(status);
    }

    /// <summary>
    /// Updates activity indicators based on status event args.
    /// </summary>
    private void UpdateActivityIndicators(ActivityStatusChangedEventArgs status)
    {
      // Update Processing Indicator
      UpdateProcessingIndicator(status.ProcessingStatus, status.ActiveJobCount, status.QueuedOperationCount);

      // Update Network Indicator
      UpdateNetworkIndicator(status.NetworkStatus);

      // Update Engine Indicator
      UpdateEngineIndicator(status.EngineStatus);

      // Update status text
      UpdateStatusText(status);
    }

    /// <summary>
    /// Updates the processing indicator.
    /// </summary>
    private void UpdateProcessingIndicator(ProcessingStatus status, int activeJobCount, int queuedCount)
    {
      if (!(FindNameOnContent("ProcessingIndicator") is FrameworkElement processingIndicator))
        return;

      var tooltip = status switch
      {
        ProcessingStatus.Processing => $"Processing: {activeJobCount} active job(s), {queuedCount} queued",
        ProcessingStatus.Paused => "Processing: Paused",
        ProcessingStatus.Error => "Processing: Error",
        _ => "Processing: Idle"
      };

      ToolTipService.SetToolTip(processingIndicator, tooltip);

      var color = status switch
      {
        ProcessingStatus.Processing => Windows.UI.Color.FromArgb(255, 0, 255, 127), // Green
        ProcessingStatus.Paused => Windows.UI.Color.FromArgb(255, 255, 255, 0), // Yellow
        ProcessingStatus.Error => Windows.UI.Color.FromArgb(255, 255, 0, 0), // Red
        _ => Windows.UI.Color.FromArgb(255, 128, 128, 128) // Gray
      };

      processingIndicator.SetValue(Control.BackgroundProperty, new SolidColorBrush(color));
      processingIndicator.Opacity = status == ProcessingStatus.Idle ? 0.3 : 1.0;
    }

    /// <summary>
    /// Updates the network indicator.
    /// </summary>
    private void UpdateNetworkIndicator(NetworkStatus status)
    {
      if (!(FindNameOnContent("NetworkIndicator") is FrameworkElement networkIndicator))
        return;

      var tooltip = status switch
      {
        NetworkStatus.Connected => "Network: Connected",
        NetworkStatus.Disconnected => "Network: Disconnected",
        NetworkStatus.Reconnecting => "Network: Reconnecting...",
        _ => "Network: Error"
      };

      ToolTipService.SetToolTip(networkIndicator, tooltip);

      var color = status switch
      {
        NetworkStatus.Connected => Windows.UI.Color.FromArgb(255, 0, 255, 127), // Green
        NetworkStatus.Reconnecting => Windows.UI.Color.FromArgb(255, 255, 255, 0), // Yellow
        _ => Windows.UI.Color.FromArgb(255, 255, 0, 0) // Red
      };

      networkIndicator.SetValue(Control.BackgroundProperty, new SolidColorBrush(color));
      networkIndicator.Opacity = status == NetworkStatus.Connected ? 1.0 : 0.7;
    }

    /// <summary>
    /// Updates the engine indicator.
    /// </summary>
    private void UpdateEngineIndicator(EngineStatus status)
    {
      if (!(FindNameOnContent("EngineIndicator") is FrameworkElement engineIndicator))
        return;

      var tooltip = status switch
      {
        EngineStatus.Ready => "Engine: Ready",
        EngineStatus.Busy => "Engine: Busy",
        EngineStatus.Starting => "Engine: Starting...",
        EngineStatus.Offline => "Engine: Offline",
        _ => "Engine: Error"
      };

      ToolTipService.SetToolTip(engineIndicator, tooltip);

      var color = status switch
      {
        EngineStatus.Ready => Color.FromArgb(255, 0, 255, 127), // Green
        EngineStatus.Busy => Color.FromArgb(255, 0, 120, 212), // Blue
        EngineStatus.Starting => Color.FromArgb(255, 255, 255, 0), // Yellow
        _ => Color.FromArgb(255, 255, 0, 0) // Red
      };

      engineIndicator.SetValue(Control.BackgroundProperty, new SolidColorBrush(color));
      engineIndicator.Opacity = status == EngineStatus.Ready ? 1.0 : 0.8;
    }

    /// <summary>
    /// Updates the status text based on current activity.
    /// </summary>
    private void UpdateStatusText(ActivityStatusChangedEventArgs status)
    {
      if (!(FindNameOnContent("StatusText") is TextBlock statusText))
        return;

      statusText.Text = status.ProcessingStatus switch
      {
        ProcessingStatus.Processing => $"Processing ({status.ActiveJobCount} job(s))",
        ProcessingStatus.Paused => "Paused",
        ProcessingStatus.Error => "Error",
        _ => "Ready"
      };
    }

    /// <summary>
    /// Updates the clock display in the status bar.
    /// </summary>
    private void UpdateClock()
    {
      var clockText = FindNameOnContent("ClockText") as TextBlock;
      if (clockText != null)
      {
        clockText.Text = DateTime.Now.ToString("h:mm tt");
      }
    }

    #endregion Status Bar Activity Indicators (IDEA 19)

    #region Panel Preview on Hover (IDEA 20)

    /// <summary>
    /// Handles pointer entered event for navigation buttons to show panel preview.
    /// </summary>
    private void NavButton_PointerEntered(object sender, PointerRoutedEventArgs _)
    {
      if (sender is not ToggleButton button)
        return;

      // Cancel any pending hide timer
      _previewHideTimer?.Dispose();
      _previewHideTimer = null;

      // Get panel info based on button name
      var panelInfo = GetPanelInfoForButton(button.Name);
      if (panelInfo == null)
        return;

      // Create or get preview popup
      if (_panelPreviewPopup == null)
      {
        _panelPreviewPopup = new PanelPreviewPopup();
      }

      // Create preview content
      var previewContent = CreatePreviewContent(panelInfo.Value.PanelId);

      // Show preview
      _panelPreviewPopup.Show(button, panelInfo.Value.Title, panelInfo.Value.Description, panelInfo.Value.IconGlyph, previewContent);
    }

    /// <summary>
    /// Handles pointer exited event for navigation buttons to hide panel preview.
    /// </summary>
    private void NavButton_PointerExited(object _, PointerRoutedEventArgs __)
    {
      // Delay hiding to allow moving to preview popup
      _previewHideTimer?.Dispose();
      _previewHideTimer = new System.Threading.Timer(_ =>
      {
        this.DispatcherQueue.TryEnqueue(() => _panelPreviewPopup?.Hide());
      }, null, TimeSpan.FromMilliseconds(300), System.Threading.Timeout.InfiniteTimeSpan);
    }

    /// <summary>
    /// Gets panel information for a navigation button.
    /// </summary>
    private (string PanelId, string Title, string Description, string IconGlyph)? GetPanelInfoForButton(string buttonName)
    {
      return buttonName switch
      {
        "NavStudio" => ("Studio", "Studio", "Main workspace for voice synthesis and editing. Access timeline, mixer, and all core tools.", "\uE8A5"),
        "NavProfiles" => ("Profiles", "Profiles", "Manage voice profiles and voice cloning models. Create, edit, and organize your voice library.", "\uE77B"),
        "NavLibrary" => ("Library", "Library", "Browse and organize your audio files, voice samples, and project assets.", "\uE8F1"),
        "NavEffects" => ("Effects", "Effects & Mixer", "Apply audio effects, adjust mixing parameters, and fine-tune your voice output.", "\uE8F5"),
        "NavTrain" => ("Train", "Voice Training", "Train custom voice models and improve voice cloning quality.", "\uE8F6"),
        "NavAnalyze" => ("Analyze", "Analyzer", "Analyze audio quality, waveforms, spectral analysis, and voice characteristics.", "\uE890"),
        "NavSettings" => ("Settings", "Settings", "Configure application settings, preferences, and system options.", "\uE713"),
        "NavLogs" => ("Logs", "Diagnostics", "View system logs, diagnostics, and debugging information.", "\uE8F7"),
        _ => null
      };
    }

    /// <summary>
    /// Creates preview content for a panel.
    /// </summary>
    private UIElement? CreatePreviewContent(string panelId)
    {
      var stackPanel = new StackPanel { Spacing = 8 };

      switch (panelId)
      {
        case "Profiles":
          stackPanel.Children.Add(new TextBlock { Text = "• Voice profile management", FontSize = 12 });
          stackPanel.Children.Add(new TextBlock { Text = "• Quality score tracking", FontSize = 12 });
          stackPanel.Children.Add(new TextBlock { Text = "• Profile organization", FontSize = 12 });
          break;

        case "Library":
          stackPanel.Children.Add(new TextBlock { Text = "• Audio file browser", FontSize = 12 });
          stackPanel.Children.Add(new TextBlock { Text = "• Asset organization", FontSize = 12 });
          stackPanel.Children.Add(new TextBlock { Text = "• Quick preview", FontSize = 12 });
          break;

        case "Effects":
          stackPanel.Children.Add(new TextBlock { Text = "• Audio effects chain", FontSize = 12 });
          stackPanel.Children.Add(new TextBlock { Text = "• Mixing controls", FontSize = 12 });
          stackPanel.Children.Add(new TextBlock { Text = "• Real-time processing", FontSize = 12 });
          break;

        case "Train":
          stackPanel.Children.Add(new TextBlock { Text = "• Model training interface", FontSize = 12 });
          stackPanel.Children.Add(new TextBlock { Text = "• Training progress tracking", FontSize = 12 });
          stackPanel.Children.Add(new TextBlock { Text = "• Quality metrics", FontSize = 12 });
          break;

        case "Analyze":
          stackPanel.Children.Add(new TextBlock { Text = "• Waveform visualization", FontSize = 12 });
          stackPanel.Children.Add(new TextBlock { Text = "• Spectral analysis", FontSize = 12 });
          stackPanel.Children.Add(new TextBlock { Text = "• Quality metrics", FontSize = 12 });
          break;

        case "Settings":
          stackPanel.Children.Add(new TextBlock { Text = "• Application preferences", FontSize = 12 });
          stackPanel.Children.Add(new TextBlock { Text = "• Engine configuration", FontSize = 12 });
          stackPanel.Children.Add(new TextBlock { Text = "• System settings", FontSize = 12 });
          break;

        case "Logs":
          stackPanel.Children.Add(new TextBlock { Text = "• System diagnostics", FontSize = 12 });
          stackPanel.Children.Add(new TextBlock { Text = "• Error logs", FontSize = 12 });
          stackPanel.Children.Add(new TextBlock { Text = "• Performance metrics", FontSize = 12 });
          break;

        default:
          return null;
      }

      return stackPanel;
    }

    #endregion Panel Preview on Hover (IDEA 20)

    #region Panel Docking (IDEA 14)

    /// <summary>
    /// Handles panel dock requests from PanelHost controls.
    /// </summary>
    private void PanelHost_OnPanelDockRequested(object? sender, PanelDockEventArgs e)
    {
      if (e.SourcePanelHost == null)
        return;

      // Get the target PanelHost based on target region
      Controls.PanelHost? targetHost = e.TargetRegion switch
      {
        PanelRegion.Left => FindNameOnContent("LeftPanelHost") as Controls.PanelHost,
        PanelRegion.Center => FindNameOnContent("CenterPanelHost") as Controls.PanelHost,
        PanelRegion.Right => FindNameOnContent("RightPanelHost") as Controls.PanelHost,
        PanelRegion.Bottom => FindNameOnContent("BottomPanelHost") as Controls.PanelHost,
        _ => null
      };

      if (targetHost == null || targetHost == e.SourcePanelHost)
        return;

      // Swap panel contents
      var sourceContent = e.SourcePanelHost.Content;
      var targetContent = targetHost.Content;

      // Animate the swap
      AnimatePanelDock(e.SourcePanelHost, targetHost, sourceContent, targetContent);
    }

    /// <summary>
    /// Animates panel docking with visual feedback.
    /// </summary>
    private void AnimatePanelDock(Controls.PanelHost sourceHost, Controls.PanelHost targetHost, UIElement? sourceContent, UIElement? targetContent)
    {
      // Create fade-out animation for source
      var sourceFadeOut = new Microsoft.UI.Xaml.Media.Animation.DoubleAnimation
      {
        To = 0,
        Duration = TimeSpan.FromMilliseconds(200)
      };
      Storyboard.SetTarget(sourceFadeOut, sourceHost);
      Storyboard.SetTargetProperty(sourceFadeOut, "Opacity");

      // Create fade-in animation for target
      var targetFadeIn = new Microsoft.UI.Xaml.Media.Animation.DoubleAnimation
      {
        From = 0,
        To = 1,
        Duration = TimeSpan.FromMilliseconds(200),
        BeginTime = TimeSpan.FromMilliseconds(200)
      };
      Storyboard.SetTarget(targetFadeIn, targetHost);
      Storyboard.SetTargetProperty(targetFadeIn, "Opacity");

      var storyboard = new Microsoft.UI.Xaml.Media.Animation.Storyboard();
      storyboard.Children.Add(sourceFadeOut);
      storyboard.Children.Add(targetFadeIn);

      storyboard.Completed += (_, _) =>
      {
        var sourceRegion = sourceHost.PanelRegion;
        var targetRegion = targetHost.PanelRegion;

        // Swap contents after animation
        sourceHost.Content = targetContent;
        targetHost.Content = sourceContent;

        // Update panel regions if needed
        sourceHost.PanelRegion = targetRegion;
        targetHost.PanelRegion = sourceRegion;

        // Reset opacity
        sourceHost.Opacity = 1;
        targetHost.Opacity = 1;

        // Show success toast
        var toastService = ServiceProvider.TryGetToastNotificationService();
        toastService?.ShowSuccess("Panel Docked", $"Panel moved to {targetHost.PanelRegion} region");
      };

      storyboard.Begin();
    }

    #endregion Panel Docking (IDEA 14)

    private void GlobalSearchView_NavigateRequested(object? sender, Views.SearchNavigationEventArgs e)
    {
      HideGlobalSearch();

      try
      {
        NavigateToSearchResult(e.Result);
      }
      catch (Exception ex)
      {
        var toastService = ServiceProvider.GetToastNotificationService();
        toastService?.ShowError(
            "Navigation Failed",
            $"Could not navigate to search result: {ex.Message}");
      }
    }

    /// <summary>
    /// Navigates to a search result by opening the appropriate panel and selecting the item.
    /// </summary>
    private void NavigateToSearchResult(VoiceStudio.Core.Models.SearchResultItem result)
    {
      // Use fully qualified property access to resolve ambiguity
      var panelId = (result as dynamic)?.PanelId?.ToLowerInvariant() ?? string.Empty;
      var itemId = (result as dynamic)?.Id ?? string.Empty;

      // Map panel IDs to PanelHost regions and view types
      Controls.PanelHost? targetHost = null;
      UserControl? panelView = null;

      switch (panelId)
      {
        case "profiles":
        case "profilesview":
          targetHost = FindNameOnContent("LeftPanelHost") as Controls.PanelHost;
          panelView = new ProfilesView();
          break;

        case "timeline":
        case "timelineview":
          targetHost = FindNameOnContent("CenterPanelHost") as Controls.PanelHost;
          panelView = new TimelineView();
          break;

        case "effectsmixer":
        case "effectsmixerview":
        case "effects":
          targetHost = FindNameOnContent("RightPanelHost") as Controls.PanelHost;
          panelView = new EffectsMixerView();
          break;

        case "macro":
        case "macroview":
        case "macros":
          targetHost = FindNameOnContent("BottomPanelHost") as Controls.PanelHost;
          panelView = new MacroView();
          break;

        case "analyzer":
        case "analyzerview":
          targetHost = FindNameOnContent("RightPanelHost") as Controls.PanelHost;
          panelView = new AnalyzerView();
          break;

        case "library":
        case "libraryview":
          targetHost = FindNameOnContent("LeftPanelHost") as Controls.PanelHost;
          panelView = new LibraryView();
          break;

        default:
          // Unknown panel - show error
          var toastService = ServiceProvider.GetToastNotificationService();
          var resultPanelId = (result as dynamic)?.PanelId ?? "Unknown";
          toastService?.ShowError(
              "Panel Not Found",
              $"Could not find panel: {resultPanelId}");
          return;
      }

      if (targetHost != null && panelView != null)
      {
        // Switch to the panel
        targetHost.Content = panelView;

        // Attempt to select the item in the panel
        var resultType = (result as dynamic)?.Type ?? string.Empty;
        var resultTitle = (result as dynamic)?.Title ?? "Unknown";
        TrySelectItemInPanel(panelView, itemId, resultType);

        // Show success toast
        var toastService = ServiceProvider.GetToastNotificationService();
        toastService?.ShowSuccess(
            "Navigation Complete",
            $"Navigated to {resultType}: {resultTitle}");
      }
    }

    /// <summary>
    /// Attempts to select an item in a panel by ID. Each panel should implement
    /// its own item selection logic if needed.
    /// </summary>
    private void TrySelectItemInPanel(UserControl panelView, string _, string __)
    {
      // Panel-specific item selection logic
      // Each panel can implement INavigatablePanel interface in the future for standardized navigation

      switch (panelView)
      {
        case ProfilesView profilesView:
          // ProfilesView could select a profile by ID
          // Implementation depends on ProfilesViewModel having a NavigateToItem method
          break;

        case TimelineView timelineView:
          // TimelineView could select a project or clip by ID
          break;

        case EffectsMixerView effectsMixerView:
          // EffectsMixerView could select an effect or channel by ID
          break;

        case MacroView macroView:
          // MacroView could select a macro by ID
          break;

          // Add more panel-specific navigation logic as needed
      }

      // Future: Panels can implement an interface like INavigatablePanel with NavigateToItem(itemId) method
    }

    private async void MainWindow_Activated(object sender, WindowActivatedEventArgs e)
    {
      if (IsGateCSmokeMode())
      {
        // Smoke runs must not touch WinUI state that may already be closing/closed
        // (e.g., --smoke-exit closes the window quickly). Keep this handler no-op.
        return;
      }

      // Attach keyboard handler to root content (only once).
      // Guard against COMException if the window is closing during activation.
      try
      {
        if (this.Content is UIElement root)
        {
          root.KeyDown -= MainWindow_KeyDown; // Remove first to avoid duplicates
          root.KeyDown += MainWindow_KeyDown;
        }
      }
      catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {ex.Message}", "MainWindow.MainWindow_Activated");
      }

      if (e.WindowActivationState != WindowActivationState.CodeActivated)
        return;

      // Check if we should show welcome dialog
      var localSettings = Windows.Storage.ApplicationData.Current.LocalSettings;
      var showWelcome = localSettings.Values[ShowWelcomeKey] as bool? ?? true;

      if (showWelcome)
      {
        var welcomeDialog = new WelcomeView();
        var result = await welcomeDialog.ShowAsync();

        // Save preference
        localSettings.Values[ShowWelcomeKey] = welcomeDialog.ShowOnStartup;
      }
    }

    private static bool IsGateCSmokeMode()
    {
      try
      {
        static bool IsTruthy(string? value)
        {
          if (string.IsNullOrWhiteSpace(value))
          {
            return false;
          }

          return value.Equals("1", StringComparison.OrdinalIgnoreCase)
              || value.Equals("true", StringComparison.OrdinalIgnoreCase);
        }

        if (IsTruthy(Environment.GetEnvironmentVariable("VOICE_STUDIO_SMOKE_EXIT"))
            || IsTruthy(Environment.GetEnvironmentVariable("VOICE_STUDIO_SMOKE_UI")))
        {
          return true;
        }

        var raw = Environment.CommandLine ?? string.Empty;
        if (!string.IsNullOrWhiteSpace(raw)
            && (raw.IndexOf("--smoke", StringComparison.OrdinalIgnoreCase) >= 0
                || raw.IndexOf("--ui-smoke", StringComparison.OrdinalIgnoreCase) >= 0))
        {
          return true;
        }

        foreach (var arg in Environment.GetCommandLineArgs())
        {
          if (arg.Equals("--smoke-exit", StringComparison.OrdinalIgnoreCase)
              || arg.Equals("--smoke-ui", StringComparison.OrdinalIgnoreCase)
              || arg.Equals("--ui-smoke", StringComparison.OrdinalIgnoreCase))
          {
            return true;
          }
        }

        return false;
      }
      catch
      {
        return false;
      }
    }

    private void RegisterKeyboardShortcuts()
    {
      // File operations
      _keyboardShortcutService.RegisterShortcut(
          "file.new",
          VirtualKey.N,
          VirtualKeyModifiers.Control,
          () => CreateNewProject(),
          "New Project");

      _keyboardShortcutService.RegisterShortcut(
          "file.open",
          VirtualKey.O,
          VirtualKeyModifiers.Control,
          () => OpenProject(),
          "Open Project");

      _keyboardShortcutService.RegisterShortcut(
          "file.save",
          VirtualKey.S,
          VirtualKeyModifiers.Control,
          () => SaveProject(),
          "Save Project");

      // Playback
      _keyboardShortcutService.RegisterShortcut(
          "playback.play",
          VirtualKey.Space,
          VirtualKeyModifiers.None,
          () => TogglePlayback(),
          "Play/Pause");

      _keyboardShortcutService.RegisterShortcut(
          "playback.stop",
          VirtualKey.S,
          VirtualKeyModifiers.None,
          () => StopPlayback(),
          "Stop");

      _keyboardShortcutService.RegisterShortcut(
          "playback.record",
          VirtualKey.R,
          VirtualKeyModifiers.Control,
          () => ToggleRecording(),
          "Record");

      // Edit operations
      _keyboardShortcutService.RegisterShortcut(
          "edit.undo",
          VirtualKey.Z,
          VirtualKeyModifiers.Control,
          () =>
          {
            try
            {
              var undoService = ServiceProvider.GetUndoRedoService();
              if (undoService.CanUndo)
              {
                undoService.Undo();
              }
            }
            catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {ex.Message}", "MainWindow.RegisterKeyboardShortcuts");
      }
          },
          "Undo");

      _keyboardShortcutService.RegisterShortcut(
          "edit.redo",
          VirtualKey.Y,
          VirtualKeyModifiers.Control,
          () =>
          {
            try
            {
              var undoService = ServiceProvider.GetUndoRedoService();
              if (undoService.CanRedo)
              {
                undoService.Redo();
              }
            }
            catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {ex.Message}", "MainWindow.Unknown");
      }
          },
          "Redo");

      // Navigation
      _keyboardShortcutService.RegisterShortcut(
          "nav.commandpalette",
          VirtualKey.P,
          VirtualKeyModifiers.Control,
          () => ShowCommandPalette(),
          "Command Palette");

      // Global Search (IDEA 5)
      _keyboardShortcutService.RegisterShortcut(
          "nav.globalsearch",
          VirtualKey.K,
          VirtualKeyModifiers.Control,
          () => ShowGlobalSearch(),
          "Global Search");

      // Zoom
      _keyboardShortcutService.RegisterShortcut(
          "zoom.in",
          VirtualKey.Add,
          VirtualKeyModifiers.Control,
          () => ZoomIn(),
          "Zoom In");

      _keyboardShortcutService.RegisterShortcut(
          "zoom.out",
          VirtualKey.Subtract,
          VirtualKeyModifiers.Control,
          () => ZoomOut(),
          "Zoom Out");

      _keyboardShortcutService.RegisterShortcut(
          "zoom.reset",
          VirtualKey.Number0,
          VirtualKeyModifiers.Control,
          () => ResetZoom(),
          "Reset Zoom");

      // Help
      _keyboardShortcutService.RegisterShortcut(
          "help.shortcuts",
          VirtualKey.Number0, // Temporary - '?' key mapping varies by keyboard layout
          VirtualKeyModifiers.Control,
          () =>
          {
            if (_keyboardShortcutsMenuItem != null)
            {
              KeyboardShortcutsMenuItem_Click(_keyboardShortcutsMenuItem, new RoutedEventArgs());
            }
          },
          "Keyboard Shortcuts");

      // Panel Quick-Switch (IDEA 1): Ctrl+1-9 for direct panel switching
      // Left PanelHost: Ctrl+1-3
      RegisterPanelQuickSwitchShortcut(1, PanelRegion.Left, 0, "Profiles", () => new ProfilesView());
      RegisterPanelQuickSwitchShortcut(2, PanelRegion.Left, 1, "Library", () => new LibraryView());
      RegisterPanelQuickSwitchShortcut(3, PanelRegion.Left, 2, "Training", () => new TrainingView());

      // Center PanelHost: Ctrl+4-6
      RegisterPanelQuickSwitchShortcut(4, PanelRegion.Center, 0, "Timeline", () => new TimelineView());
      RegisterPanelQuickSwitchShortcut(5, PanelRegion.Center, 1, "Voice Synthesis", () => new VoiceSynthesisView());
      RegisterPanelQuickSwitchShortcut(6, PanelRegion.Center, 2, "Text Speech Editor", () => new TextSpeechEditorView());

      // Right PanelHost: Ctrl+7-9
      RegisterPanelQuickSwitchShortcut(7, PanelRegion.Right, 0, "Effects Mixer", () => new EffectsMixerView());
      RegisterPanelQuickSwitchShortcut(8, PanelRegion.Right, 1, "Analyzer", () => new AnalyzerView());
      RegisterPanelQuickSwitchShortcut(9, PanelRegion.Right, 2, "Quality Control", () => new QualityControlView());
    }

    /// <summary>
    /// Registers a panel quick-switch shortcut (IDEA 1).
    /// </summary>
    private void RegisterPanelQuickSwitchShortcut(int number, PanelRegion region, int _, string panelName, Func<UserControl> panelFactory)
    {
      VirtualKey key = number switch
      {
        1 => VirtualKey.Number1,
        2 => VirtualKey.Number2,
        3 => VirtualKey.Number3,
        4 => VirtualKey.Number4,
        5 => VirtualKey.Number5,
        6 => VirtualKey.Number6,
        7 => VirtualKey.Number7,
        8 => VirtualKey.Number8,
        9 => VirtualKey.Number9,
        _ => VirtualKey.Number1
      };

      _keyboardShortcutService.RegisterShortcut(
          $"nav.panel.{number}",
          key,
          VirtualKeyModifiers.Control,
          () => SwitchToPanel(region, panelName, panelFactory),
          $"Switch to {panelName}");
    }

    /// <summary>
    /// Switches to a panel and shows visual feedback (IDEA 1).
    /// </summary>
    private void SwitchToPanel(PanelRegion region, string panelName, Func<UserControl> panelFactory)
    {
      // Get the target PanelHost
      Controls.PanelHost? targetHost = region switch
      {
        PanelRegion.Left => FindNameOnContent("LeftPanelHost") as Controls.PanelHost,
        PanelRegion.Center => FindNameOnContent("CenterPanelHost") as Controls.PanelHost,
        PanelRegion.Right => FindNameOnContent("RightPanelHost") as Controls.PanelHost,
        PanelRegion.Bottom => FindNameOnContent("BottomPanelHost") as Controls.PanelHost,
        _ => null
      };

      if (targetHost == null)
        return;

      // Switch panel content
      targetHost.Content = panelFactory();

      if (IsGateCSmokeMode())
      {
        // Smoke runs should avoid extra UI animations/popups that can introduce timing flake or stalls.
        return;
      }

      // Show visual indicator
      ShowPanelQuickSwitchIndicator(panelName, region, targetHost);
    }

    /// <summary>
    /// Shows the panel quick-switch visual indicator (IDEA 1).
    /// </summary>
    private void ShowPanelQuickSwitchIndicator(string panelName, PanelRegion region, Controls.PanelHost targetHost)
    {
      // Initialize popup if needed
      if (_panelQuickSwitchPopup == null)
      {
        _panelQuickSwitchIndicator = new PanelQuickSwitchIndicator();
        _panelQuickSwitchPopup = new Popup
        {
          Child = _panelQuickSwitchIndicator,
          IsLightDismissEnabled = false
        };
      }

      // Set panel info
      _panelQuickSwitchIndicator?.SetPanelInfo(panelName, region);

      // Position popup at center of target PanelHost
      var rootElement = targetHost.XamlRoot?.Content as FrameworkElement;
      if (rootElement != null)
      {
        var transform = targetHost.TransformToVisual(rootElement);
        var point = transform.TransformPoint(new Windows.Foundation.Point(0, 0));

        _panelQuickSwitchPopup.HorizontalOffset = point.X + (targetHost.ActualWidth / 2) - ((_panelQuickSwitchIndicator?.ActualWidth ?? 0) / 2);
        _panelQuickSwitchPopup.VerticalOffset = point.Y + (targetHost.ActualHeight / 2) - ((_panelQuickSwitchIndicator?.ActualHeight ?? 0) / 2);
      }

      _panelQuickSwitchPopup.XamlRoot = targetHost.XamlRoot;
      _panelQuickSwitchPopup.IsOpen = true;

      // Animate in
      if (_panelQuickSwitchIndicator != null)
      {
        var fadeIn = new Microsoft.UI.Xaml.Media.Animation.FadeInThemeAnimation();
        fadeIn.Duration = TimeSpan.FromMilliseconds(200); // VSQ.Animation.Duration.Fast * 2
        Storyboard.SetTarget(fadeIn, _panelQuickSwitchIndicator);
        var storyboard = new Storyboard();
        storyboard.Children.Add(fadeIn);
        storyboard.Begin();
      }

      // Hide after 1.5 seconds
      _quickSwitchHideTimer?.Stop();

      _quickSwitchHideTimer = new DispatcherTimer
      {
        Interval = TimeSpan.FromMilliseconds(1500) // 1.5 seconds display time
      };
      _quickSwitchHideTimer.Tick += (_, _) =>
      {
        _quickSwitchHideTimer.Stop();
        HidePanelQuickSwitchIndicator();
      };
      _quickSwitchHideTimer.Start();
    }

    /// <summary>
    /// Hides the panel quick-switch visual indicator.
    /// </summary>
    private void HidePanelQuickSwitchIndicator()
    {
      if (_panelQuickSwitchPopup?.IsOpen != true || _panelQuickSwitchIndicator == null)
        return;

      // Animate out
      var fadeOut = new Microsoft.UI.Xaml.Media.Animation.FadeOutThemeAnimation();
      fadeOut.Duration = TimeSpan.FromMilliseconds(200); // VSQ.Animation.Duration.Fast * 2
      Storyboard.SetTarget(fadeOut, _panelQuickSwitchIndicator);
      var storyboard = new Storyboard();
      storyboard.Children.Add(fadeOut);
      storyboard.Begin();

      // Close after animation
      var timer = new DispatcherTimer
      {
        Interval = TimeSpan.FromMilliseconds(200)
      };
      timer.Tick += (_, _) =>
      {
        timer.Stop();
        _panelQuickSwitchPopup.IsOpen = false;
      };
      timer.Start();
    }

    private async void CheckForUpdatesMenuItem_Click(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
    {
      try
      {
        // Create UpdateViewModel with the context and update service
        var context = ServiceProvider.GetViewModelContext();
        var updateViewModel = new ViewModels.UpdateViewModel(context, _updateService);

        // Create and show update dialog
        var updateDialog = new Views.UpdateDialog(updateViewModel);
        await updateDialog.ShowAsync();
      }
      catch (Exception ex)
      {
        // Show error if update check fails
        var errorService = ServiceProvider.GetErrorDialogService();
        await errorService.ShowErrorAsync(
            "Update Check Failed",
            $"Unable to check for updates: {ex.Message}",
            "OK");
      }
    }

    /// <summary>
    /// Toggles Mini Timeline visibility in BottomPanelHost (IDEA 6).
    /// </summary>
    private void ToggleMiniTimelineMenuItem_Click(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
    {
      _isMiniTimelineVisible = !_isMiniTimelineVisible;

      var bottomPanelHost = FindNameOnContent("BottomPanelHost") as Controls.PanelHost;
      if (bottomPanelHost != null)
      {
        if (_isMiniTimelineVisible)
        {
          // Show Mini Timeline
          bottomPanelHost.Content = new MiniTimelineView();
        }
        else
        {
          // Show Macro View
          bottomPanelHost.Content = new MacroView();
        }
      }

      UpdateMiniTimelineMenuItem();

      // Show toast notification
      var toastService = ServiceProvider.TryGetToastNotificationService();
      toastService?.ShowSuccess(
          "Panel Switched",
          _isMiniTimelineVisible ? "Mini Timeline is now visible" : "Macro View is now visible");
    }

    /// <summary>
    /// Updates the Mini Timeline menu item text based on current state (IDEA 6).
    /// </summary>
    private void UpdateMiniTimelineMenuItem()
    {
      if (_toggleMiniTimelineMenuItem != null)
      {
        _toggleMiniTimelineMenuItem.Text = _isMiniTimelineVisible
            ? "Show Macro View"
            : "Show Mini Timeline";
      }
    }

    private async void CustomizeToolbarMenuItem_Click(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
    {
      try
      {
        var dialog = new ToolbarCustomizationDialog();
        await dialog.ShowAsync();

        // Toolbar will automatically refresh via ConfigurationChanged event
      }
      catch (Exception ex)
      {
        var toastService = ServiceProvider.TryGetToastNotificationService();
        toastService?.ShowError(
            "Customization Failed",
            $"Could not open toolbar customization: {ex.Message}");
      }
    }

    private async void KeyboardShortcutsMenuItem_Click(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
    {
      try
      {
        // Show keyboard shortcuts cheat sheet (IDEA 29)
        var shortcutsView = new Views.KeyboardShortcutsView();
        var dialog = new ContentDialog
        {
          Title = "Keyboard Shortcuts",
          Content = shortcutsView,
          CloseButtonText = "Close",
          DefaultButton = ContentDialogButton.Close,
          XamlRoot = this.Content.XamlRoot,
          Width = 800,
          Height = 600
        };

        await dialog.ShowAsync();
      }
      catch (Exception ex)
      {
        // Show error if opening documentation fails
        var toastService = ServiceProvider.GetToastNotificationService();
        toastService?.ShowToast(
            Services.ToastType.Error,
            "Failed to Open Documentation",
            $"Unable to open keyboard shortcuts documentation: {ex.Message}");
      }
    }

    private void ShowCommandPalette()
    {
      try
      {
        var panelRegistry = ServiceProvider.GetPanelRegistry();
        var commandPaletteService = new CommandPaletteService(
            panelRegistry,
            new ThemeManager()
        );
        commandPaletteService.Show();
      }
      catch
      {
        // Fallback: Show simple message if CommandPaletteService fails
        // In production, this would show a proper command palette
      }
    }

    private void ShowGlobalSearch()
    {
      var globalSearchView = FindNameOnContent("GlobalSearchView") as Views.GlobalSearchView;
      var globalSearchOverlay = FindNameOnContent("GlobalSearchOverlay") as FrameworkElement;
      if (globalSearchView != null && globalSearchOverlay != null)
      {
        globalSearchOverlay.Visibility = Microsoft.UI.Xaml.Visibility.Visible;
        globalSearchView.Show();
      }
    }

    private void GlobalSearchOverlay_Tapped(object _, Microsoft.UI.Xaml.Input.TappedRoutedEventArgs e)
    {
      // Close search when clicking on overlay background
      var globalSearchOverlay = FindNameOnContent("GlobalSearchOverlay") as FrameworkElement;
      if (globalSearchOverlay != null && ReferenceEquals(e.OriginalSource, globalSearchOverlay))
      {
        HideGlobalSearch();
      }
    }

    private void HideGlobalSearch()
    {
      var globalSearchView = FindNameOnContent("GlobalSearchView") as Views.GlobalSearchView;
      var globalSearchOverlay = FindNameOnContent("GlobalSearchOverlay") as FrameworkElement;
      if (globalSearchView != null && globalSearchOverlay != null)
      {
        globalSearchView.Hide();
        globalSearchOverlay.Visibility = Microsoft.UI.Xaml.Visibility.Collapsed;
      }
    }

    private async void SaveProject()
    {
      var centerPanelHost = FindNameOnContent("CenterPanelHost") as Controls.PanelHost;
      var rightPanelHost = FindNameOnContent("RightPanelHost") as Controls.PanelHost;
      if (centerPanelHost?.Content is TimelineView timelineView && timelineView.ViewModel != null)
      {
        var viewModel = timelineView.ViewModel;
        if (viewModel.SelectedProject != null)
        {
          try
          {
            // Save mixer state if EffectsMixerView is active
            if (rightPanelHost?.Content is EffectsMixerView mixerView && mixerView.ViewModel != null && mixerView.ViewModel.SaveMixerStateCommand.CanExecute(null))
            {
              await mixerView.ViewModel.SaveMixerStateCommand.ExecuteAsync(null);
            }
          }
          catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {ex.Message}", "MainWindow.SaveProject");
      }
        }
      }
    }

    private async void CreateNewProject()
    {
      var centerPanelHost = FindNameOnContent("CenterPanelHost") as Controls.PanelHost;
      if (centerPanelHost?.Content is TimelineView timelineView && timelineView.ViewModel != null)
      {
        var viewModel = timelineView.ViewModel;
        if (viewModel.CreateProjectCommand.CanExecute(null))
        {
          await viewModel.CreateProjectCommand.ExecuteAsync(null);
        }
      }
    }

    private async void OpenProject()
    {
      var centerPanelHost = FindNameOnContent("CenterPanelHost") as Controls.PanelHost;
      if (centerPanelHost?.Content is TimelineView timelineView && timelineView.ViewModel != null)
      {
        var viewModel = timelineView.ViewModel;
        if (viewModel.LoadProjectsCommand.CanExecute(null))
        {
          await viewModel.LoadProjectsCommand.ExecuteAsync(null);
        }
      }
    }

    private async void OpenRecentProject(string projectId, string projectName)
    {
      try
      {
        var centerPanelHost2 = FindNameOnContent("CenterPanelHost") as Controls.PanelHost;
        if (centerPanelHost2?.Content is TimelineView timelineView && timelineView.ViewModel != null)
        {
          var viewModel = timelineView.ViewModel;

          // Load projects if not already loaded
          if (viewModel.Projects.Count == 0)
          {
            await viewModel.LoadProjectsCommand.ExecuteAsync(null);
          }

          // Find and select the project - handle ambiguity by checking both Project types
          var project = viewModel.Projects
              .OfType<VoiceStudio.Core.Models.Project>()
              .FirstOrDefault(p => p.Id == projectId);
          if (project != null)
          {
            viewModel.SelectedProject = project;

            // Update recent projects service
            if (_recentProjectsService != null)
            {
              await _recentProjectsService.AddRecentProjectAsync(projectId, projectName);
            }

            var toastService = ServiceProvider.GetToastNotificationService();
            toastService?.ShowToast(
                Services.ToastType.Success,
                "Project Opened",
                $"Opened project: {projectName}");
          }
          else
          {
            // Project not found - try to load it from backend
            var backendClient = ServiceProvider.GetBackendClient();
            try
            {
              var loadedProject = await backendClient.GetProjectAsync(projectId);
              if (loadedProject != null)
              {
                viewModel.Projects.Add(loadedProject);
                viewModel.SelectedProject = loadedProject;

                if (_recentProjectsService != null)
                {
                  await _recentProjectsService.AddRecentProjectAsync(projectId, projectName);
                }
              }
              else
              {
                throw new Exception("Project not found");
              }
            }
            catch
            {
              var toastService = ServiceProvider.GetToastNotificationService();
              toastService?.ShowToast(
                  Services.ToastType.Error,
                  "Project Not Found",
                  $"Could not open project: {projectName}. It may have been deleted.");

              // Remove from recent projects
              if (_recentProjectsService != null)
              {
                await _recentProjectsService.RemoveRecentProjectAsync(projectId);
              }
            }
          }
        }
      }
      catch (Exception ex)
      {
        var toastService = ServiceProvider.GetToastNotificationService();
        toastService?.ShowToast(
            Services.ToastType.Error,
            "Failed to Open Project",
            ex.Message);
      }
    }

    private async void PinRecentProject(string projectId)
    {
      try
      {
        if (_recentProjectsService != null)
        {
          await _recentProjectsService.PinProjectAsync(projectId);
          var toastService = ServiceProvider.GetToastNotificationService();
          toastService?.ShowToast(
              Services.ToastType.Success,
              "Project Pinned",
              "Project pinned to Recent Projects menu");
        }
      }
      catch (Exception ex)
      {
        var toastService = ServiceProvider.GetToastNotificationService();
        toastService?.ShowToast(
            Services.ToastType.Error,
            "Failed to Pin Project",
            ex.Message);
      }
    }

    private async void UnpinRecentProject(string projectId)
    {
      try
      {
        if (_recentProjectsService != null)
        {
          await _recentProjectsService.UnpinProjectAsync(projectId);
          var toastService = ServiceProvider.GetToastNotificationService();
          toastService?.ShowToast(
              Services.ToastType.Success,
              "Project Unpinned",
              "Project removed from pinned list");
        }
      }
      catch (Exception ex)
      {
        var toastService = ServiceProvider.GetToastNotificationService();
        toastService?.ShowToast(
            Services.ToastType.Error,
            "Failed to Unpin Project",
            ex.Message);
      }
    }

    private async void ClearRecentProjects()
    {
      try
      {
        if (_recentProjectsService != null)
        {
          await _recentProjectsService.ClearRecentProjectsAsync();
          var toastService = ServiceProvider.GetToastNotificationService();
          toastService?.ShowToast(
              Services.ToastType.Success,
              "Recent Projects Cleared",
              "All recent projects have been cleared");
        }
      }
      catch (Exception ex)
      {
        var toastService = ServiceProvider.GetToastNotificationService();
        toastService?.ShowToast(
            Services.ToastType.Error,
            "Failed to Clear Recent Projects",
            ex.Message);
      }
    }

    private void InitializeMenuBar()
    {
      var host = FindInContent<ContentControl>("MenuBarHost");
      if (host == null)
      {
        return;
      }

      var menuBar = new MenuBar
      {
        HorizontalAlignment = HorizontalAlignment.Stretch,
        VerticalAlignment = VerticalAlignment.Center
      };

      menuBar.Items.Add(BuildFileMenu());
      menuBar.Items.Add(BuildEditMenu());
      menuBar.Items.Add(BuildViewMenu());
      menuBar.Items.Add(BuildModulesMenu());
      menuBar.Items.Add(BuildPlaybackMenu());
      menuBar.Items.Add(BuildToolsMenu());
      menuBar.Items.Add(BuildAiMenu());
      menuBar.Items.Add(BuildHelpMenu());

      host.Content = menuBar;
    }

    private MenuBarItem BuildFileMenu()
    {
      var item = new MenuBarItem { Title = "File" };
      item.Items.Add(CreateMenuItem("New Project", CreateNewProject));
      item.Items.Add(CreateMenuItem("Open Project", OpenProject));
      item.Items.Add(CreateMenuItem("Save Project", SaveProject));
      item.Items.Add(new MenuFlyoutSeparator());
      if (_recentProjectsSubMenu != null)
      {
        item.Items.Add(_recentProjectsSubMenu);
        item.Items.Add(new MenuFlyoutSeparator());
      }
      item.Items.Add(CreateMenuItem("Exit", () => Close()));
      return item;
    }

    private MenuBarItem BuildEditMenu()
    {
      var item = new MenuBarItem { Title = "Edit" };
      item.Items.Add(CreateMenuItem("Undo", ExecuteUndo));
      item.Items.Add(CreateMenuItem("Redo", ExecuteRedo));
      return item;
    }

    private MenuBarItem BuildViewMenu()
    {
      var item = new MenuBarItem { Title = "View" };
      if (_toggleMiniTimelineMenuItem != null)
      {
        item.Items.Add(_toggleMiniTimelineMenuItem);
      }
      item.Items.Add(CreateMenuItem("Global Search", ShowGlobalSearch));
      return item;
    }

    private MenuBarItem BuildModulesMenu()
    {
      var item = new MenuBarItem { Title = "Modules" };
      item.Items.Add(CreateMenuItem("Studio (Timeline)", () => NavStudio_Click(this, new RoutedEventArgs())));
      item.Items.Add(CreateMenuItem("Profiles", () => NavProfiles_Click(this, new RoutedEventArgs())));
      item.Items.Add(CreateMenuItem("Library", () => NavLibrary_Click(this, new RoutedEventArgs())));
      item.Items.Add(CreateMenuItem("Effects Mixer", () => NavEffects_Click(this, new RoutedEventArgs())));
      item.Items.Add(CreateMenuItem("Training", () => NavTrain_Click(this, new RoutedEventArgs())));
      item.Items.Add(CreateMenuItem("Analyzer", () => NavAnalyze_Click(this, new RoutedEventArgs())));
      item.Items.Add(CreateMenuItem("Settings", () => NavSettings_Click(this, new RoutedEventArgs())));
      item.Items.Add(CreateMenuItem("Diagnostics", () => NavLogs_Click(this, new RoutedEventArgs())));
      return item;
    }

    private MenuBarItem BuildPlaybackMenu()
    {
      var item = new MenuBarItem { Title = "Playback" };
      item.Items.Add(CreateMenuItem("Play/Pause", TogglePlayback));
      item.Items.Add(CreateMenuItem("Stop", StopPlayback));
      item.Items.Add(CreateMenuItem("Record", ToggleRecording));
      return item;
    }

    private MenuBarItem BuildToolsMenu()
    {
      var item = new MenuBarItem { Title = "Tools" };
      if (_customizeToolbarMenuItem != null)
      {
        item.Items.Add(_customizeToolbarMenuItem);
      }
      if (_checkForUpdatesMenuItem != null)
      {
        item.Items.Add(_checkForUpdatesMenuItem);
      }
      if (_keyboardShortcutsMenuItem != null)
      {
        item.Items.Add(_keyboardShortcutsMenuItem);
      }
      return item;
    }

    private MenuBarItem BuildAiMenu()
    {
      var item = new MenuBarItem { Title = "AI" };
      item.Items.Add(CreateMenuItem(
          "AI Mixing & Mastering",
          () => SwitchToPanel(PanelRegion.Right, "AI Mixing & Mastering", () => new AIMixingMasteringView())));
      item.Items.Add(CreateMenuItem(
          "Ensemble Synthesis",
          () => SwitchToPanel(PanelRegion.Center, "Ensemble Synthesis", () => new EnsembleSynthesisView())));
      return item;
    }

    private MenuBarItem BuildHelpMenu()
    {
      var item = new MenuBarItem { Title = "Help" };
      item.Items.Add(CreateMenuItem("Documentation Folder", OpenDocumentationFolder));
      item.Items.Add(CreateMenuItem("About VoiceStudio", ShowAboutDialog));
      return item;
    }

    private MenuFlyoutItem CreateMenuItem(string text, Action action)
    {
      var item = new MenuFlyoutItem { Text = text };
      item.Click += (_, __) => action();
      return item;
    }

    private void ExecuteUndo()
    {
      try
      {
        var undoService = ServiceProvider.GetUndoRedoService();
        if (undoService.CanUndo)
        {
          undoService.Undo();
        }
      }
      catch (Exception ex)
      {
        ServiceProvider.TryGetErrorLoggingService()?.LogError(ex, "ExecuteUndo");
      }
    }

    private void ExecuteRedo()
    {
      try
      {
        var undoService = ServiceProvider.GetUndoRedoService();
        if (undoService.CanRedo)
        {
          undoService.Redo();
        }
      }
      catch (Exception ex)
      {
        ServiceProvider.TryGetErrorLoggingService()?.LogError(ex, "ExecuteRedo");
      }
    }

    private void OpenDocumentationFolder()
    {
      var repoRoot = Environment.GetEnvironmentVariable("VOICESTUDIO_REPO_ROOT");
      var docsPath = repoRoot != null
          ? Path.Combine(repoRoot, "docs")
          : Path.Combine(AppContext.BaseDirectory, "docs");
      try
      {
        if (!Directory.Exists(docsPath))
        {
          ServiceProvider.TryGetToastNotificationService()?.ShowWarning(
              $"Docs folder not found: {docsPath}",
              "Documentation");
          return;
        }

        Process.Start(new ProcessStartInfo
        {
          FileName = "explorer.exe",
          Arguments = $"\"{docsPath}\"",
          UseShellExecute = true
        });
      }
      catch (Exception ex)
      {
        ServiceProvider.TryGetErrorLoggingService()?.LogError(ex, "OpenDocumentationFolder");
        ServiceProvider.TryGetToastNotificationService()?.ShowError(
            "Unable to open documentation folder.",
            "Documentation");
      }
    }

    private async void ShowAboutDialog()
    {
      try
      {
        var version = Package.Current.Id.Version;
        var versionText = $"{version.Major}.{version.Minor}.{version.Build}.{version.Revision}";
        var dialog = new ContentDialog
        {
          Title = "VoiceStudio Quantum+",
          Content = $"Version {versionText}",
          CloseButtonText = "Close",
          XamlRoot = (Content as FrameworkElement)?.XamlRoot
        };

        await dialog.ShowAsync();
      }
      catch (Exception ex)
      {
        ServiceProvider.TryGetErrorLoggingService()?.LogError(ex, "ShowAboutDialog");
        ServiceProvider.TryGetToastNotificationService()?.ShowError(
            "Unable to show About dialog.",
            "About");
      }
    }

    private void PopulateRecentProjectsMenu()
    {
      if (_recentProjectsSubMenu == null || _recentProjectsService == null)
        return;

      _recentProjectsSubMenu.Items.Clear();

      var allProjects = _recentProjectsService.AllProjects;

      if (allProjects.Count == 0)
      {
        var emptyItem = new MenuFlyoutItem
        {
          Text = "No recent projects",
          IsEnabled = false
        };
        _recentProjectsSubMenu.Items.Add(emptyItem);
        return;
      }

      // Add pinned projects first
      var pinnedProjects = _recentProjectsService.PinnedProjects;
      if (pinnedProjects.Count > 0)
      {
        foreach (var project in pinnedProjects)
        {
          var subMenu = new MenuFlyoutSubItem
          {
            Text = $"📌 {project.Name}"
          };
          var openItem = new MenuFlyoutItem
          {
            Text = "Open",
            Tag = project.Path
          };
          openItem.Click += (_, _) => OpenRecentProject(project.Path, project.Name);
          subMenu.Items.Add(openItem);
          subMenu.Items.Add(new MenuFlyoutSeparator());

          var unpinItem = new MenuFlyoutItem
          {
            Text = "Unpin",
            Tag = project.Path
          };
          unpinItem.Click += (_, _) => UnpinRecentProject(project.Path);
          subMenu.Items.Add(unpinItem);

          _recentProjectsSubMenu!.Items.Add(subMenu);
        }

        if (_recentProjectsService.RecentProjects.Count > 0)
        {
          _recentProjectsSubMenu!.Items.Add(new MenuFlyoutSeparator());
        }
      }

      // Add recent projects
      foreach (var project in _recentProjectsService.RecentProjects)
      {
        var subMenu = new MenuFlyoutSubItem
        {
          Text = project.Name
        };
        var openItem2 = new MenuFlyoutItem
        {
          Text = "Open",
          Tag = project.Path
        };
        openItem2.Click += (_, _) => OpenRecentProject(project.Path, project.Name);
        subMenu.Items.Add(openItem2);
        subMenu.Items.Add(new MenuFlyoutSeparator());

        var pinItem = new MenuFlyoutItem
        {
          Text = "Pin",
          Tag = project.Path
        };
        pinItem.Click += (_, _) => PinRecentProject(project.Path);
        subMenu.Items.Add(pinItem);

        var removeItem = new MenuFlyoutItem
        {
          Text = "Remove from list",
          Tag = project.Path
        };
        removeItem.Click += async (_, _) =>
        {
          if (_recentProjectsService != null)
          {
            await _recentProjectsService.RemoveRecentProjectAsync(project.Path);
          }
        };
        subMenu.Items.Add(removeItem);

        _recentProjectsSubMenu!.Items.Add(subMenu);
      }

      // Add separator and clear option
      if (allProjects.Count > 0)
      {
        _recentProjectsSubMenu!.Items.Add(new MenuFlyoutSeparator());
        var clearItem = new MenuFlyoutItem
        {
          Text = "Clear Recent Projects"
        };
        clearItem.Click += (_, _) => ClearRecentProjects();
        _recentProjectsSubMenu!.Items.Add(clearItem);
      }
    }

    private async void TogglePlayback()
    {
      var centerPanelHost = FindNameOnContent("CenterPanelHost") as Controls.PanelHost;
      if (centerPanelHost?.Content is TimelineView timelineView && timelineView.ViewModel != null)
      {
        var viewModel = timelineView.ViewModel;
        if (viewModel.IsPlaying)
        {
          if (viewModel.PauseAudioCommand.CanExecute(null))
          {
            viewModel.PauseAudioCommand.Execute(null);
          }
        }
        else
        {
          if (viewModel.PlayAudioCommand.CanExecute(null))
          {
            await viewModel.PlayAudioCommand.ExecuteAsync(null);
          }
        }
      }
    }

    private void StopPlayback()
    {
      var centerPanelHost = FindNameOnContent("CenterPanelHost") as Controls.PanelHost;
      if (centerPanelHost?.Content is TimelineView timelineView && timelineView.ViewModel != null)
      {
        var viewModel = timelineView.ViewModel;
        if (viewModel.StopAudioCommand.CanExecute(null))
        {
          viewModel.StopAudioCommand.Execute(null);
        }
      }
    }

    private void ToggleRecording()
    {
      try
      {
        if (!(FindNameOnContent("RightPanelHost") is Controls.PanelHost rightPanelHost))
        {
          return;
        }

        var recordingView = rightPanelHost.Content as RecordingView;
        if (recordingView == null)
        {
          recordingView = new RecordingView();
          rightPanelHost.Content = recordingView;
        }

        var viewModel = recordingView.ViewModel;
        if (viewModel.IsRecording)
        {
          if (viewModel.StopRecordingCommand.CanExecute(null))
          {
            viewModel.StopRecordingCommand.Execute(null);
          }
        }
        else
        {
          if (viewModel.StartRecordingCommand.CanExecute(null))
          {
            viewModel.StartRecordingCommand.Execute(null);
          }
        }
      }
      catch (Exception ex)
      {
        ServiceProvider.TryGetErrorLoggingService()?.LogError(ex, "ToggleRecording");
        ServiceProvider.TryGetToastNotificationService()?.ShowError(
            "Recording toggle failed.",
            "Recording");
      }
    }

    private void ZoomIn()
    {
      var centerPanelHost = FindNameOnContent("CenterPanelHost") as Controls.PanelHost;
      if (centerPanelHost?.Content is TimelineView timelineView && timelineView.ViewModel != null)
      {
        var viewModel = timelineView.ViewModel;
        if (viewModel.ZoomInCommand.CanExecute(null))
        {
          viewModel.ZoomInCommand.Execute(null);
        }
      }
    }

    private void ZoomOut()
    {
      var centerPanelHost = FindNameOnContent("CenterPanelHost") as Controls.PanelHost;
      if (centerPanelHost?.Content is TimelineView timelineView && timelineView.ViewModel != null)
      {
        var viewModel = timelineView.ViewModel;
        if (viewModel.ZoomOutCommand.CanExecute(null))
        {
          viewModel.ZoomOutCommand.Execute(null);
        }
      }
    }

    private void ResetZoom()
    {
      var centerPanelHost = FindNameOnContent("CenterPanelHost") as Controls.PanelHost;
      if (centerPanelHost?.Content is TimelineView timelineView && timelineView.ViewModel != null)
      {
        var viewModel = timelineView.ViewModel;
        viewModel.TimelineZoom = 1.0;
      }
    }

    /// <summary>
    /// Loads workspace layout from PanelStateService and restores panel arrangement.
    /// </summary>
    private void LoadWorkspaceLayout()
    {
      if (_panelStateService == null)
        return;

      try
      {
        var layout = _panelStateService.GetCurrentLayout();
        // Layout will be used by RestorePanelsFromLayout
      }
      catch (Exception ex)
      {
        System.Diagnostics.Debug.WriteLine($"Failed to load workspace layout: {ex.Message}");
      }
    }

    /// <summary>
    /// Restores panels from saved workspace layout.
    /// Returns true if panels were restored, false if using defaults.
    /// </summary>
    private bool RestorePanelsFromLayout()
    {
      if (_panelStateService == null)
        return false;

      try
      {
        var layout = _panelStateService.GetCurrentLayout();

        // For now, always use defaults as panel registry is not yet implemented
        // Planned feature: When panel registry is implemented, restore panels from layout.Regions
        return false;
      }
      catch (Exception ex)
      {
        System.Diagnostics.Debug.WriteLine($"Failed to restore panels from layout: {ex.Message}");
        return false;
      }
    }

    /// <summary>
    /// Saves current workspace layout including all panel states.
    /// </summary>
    private void SaveWorkspaceLayout()
    {
      if (_panelStateService == null)
        return;

      try
      {
        // Save state for each panel host
        var leftPanelHost = FindNameOnContent("LeftPanelHost") as Controls.PanelHost;
        var centerPanelHost = FindNameOnContent("CenterPanelHost") as Controls.PanelHost;
        var rightPanelHost = FindNameOnContent("RightPanelHost") as Controls.PanelHost;
        var bottomPanelHost = FindNameOnContent("BottomPanelHost") as Controls.PanelHost;
        leftPanelHost?.SaveRegionState();
        centerPanelHost?.SaveRegionState();
        rightPanelHost?.SaveRegionState();
        bottomPanelHost?.SaveRegionState();
      }
      catch (Exception ex)
      {
        System.Diagnostics.Debug.WriteLine($"Failed to save workspace layout: {ex.Message}");
      }
    }

    /// <summary>
    /// Handles workspace profile changes.
    /// </summary>
    private void OnWorkspaceProfileChanged(object? sender, WorkspaceProfileChangedEventArgs e)
    {
      try
      {
        // Reload layout and restore panels
        LoadWorkspaceLayout();
        RestorePanelsFromLayout();
      }
      catch (Exception ex)
      {
        System.Diagnostics.Debug.WriteLine($"Failed to handle workspace profile change: {ex.Message}");
      }
    }

    private void MainWindow_Closed(object sender, WindowEventArgs e)
    {
      // Save workspace layout before closing
      SaveWorkspaceLayout();
      Cleanup();
    }

    private void MainWindow_KeyDown(object sender, KeyRoutedEventArgs e)
    {
      var modifiers = VirtualKeyModifiers.None;
      if (InputHelper.IsControlPressed())
        modifiers |= VirtualKeyModifiers.Control;
      if (InputHelper.IsShiftPressed())
        modifiers |= VirtualKeyModifiers.Shift;
      var altState = Microsoft.UI.Input.InputKeyboardSource.GetKeyStateForCurrentThread(VirtualKey.Menu);
      if ((altState & Windows.UI.Core.CoreVirtualKeyStates.Down) == Windows.UI.Core.CoreVirtualKeyStates.Down)
        modifiers |= VirtualKeyModifiers.Menu;

      if (_keyboardShortcutService.TryHandleKeyDown(e.Key, modifiers))
      {
        e.Handled = true;
      }
    }

    private void Cleanup()
    {
      if (_disposed)
        return;

      // Dispose clock timer
      _clockTimer?.Dispose();
      _clockTimer = null;

      // Dispose preview timer
      _previewHideTimer?.Dispose();
      _previewHideTimer = null;

      // Save workspace layout before cleanup
      SaveWorkspaceLayout();

      // Unsubscribe from events
      if (this.Content is UIElement root)
      {
        root.KeyDown -= MainWindow_KeyDown;
      }
      this.Activated -= MainWindow_Activated;
      this.Closed -= MainWindow_Closed;

      if (_panelStateService != null)
      {
        _panelStateService.WorkspaceProfileChanged -= OnWorkspaceProfileChanged;
      }

      _disposed = true;
    }

    ~MainWindow()
    {
      Cleanup();
    }
  }
}