using System;
using Microsoft.UI.Xaml.Controls;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;

namespace {{CLASS_NAME}}Plugin;

/// <summary>
/// Settings panel for {{DISPLAY_NAME}} plugin.
/// 
/// Demonstrates MVVM pattern with ViewModel binding and
/// implementation of ILifecyclePanelView for lifecycle control.
/// </summary>
public sealed partial class SettingsPanel : UserControl, ILifecyclePanelView
{
    private SettingsPanelViewModel _viewModel;
    private IBackendClient _backend;

    /// <summary>Unique panel identifier</summary>
    public string PanelId => "{{PLUGIN_NAME}}_settings";

    /// <summary>Display name shown in UI</summary>
    public string DisplayName => "{{DISPLAY_NAME}} Settings";

    /// <summary>Where in the UI this panel should appear</summary>
    public PanelRegion Region => PanelRegion.Right;

    public SettingsPanel()
    {
        InitializeComponent();
        
        // Create and bind ViewModel
        _viewModel = new SettingsPanelViewModel();
        DataContext = _viewModel;
    }

    /// <summary>
    /// Called when the panel becomes visible/active.
    /// Use for loading data, starting timers, subscribing to events.
    /// </summary>
    public async System.Threading.Tasks.Task OnActivatedAsync(
        System.Threading.CancellationToken cancellationToken = default)
    {
        // Panel is now visible - refresh data if needed
        await RefreshAsync(cancellationToken);
    }

    /// <summary>
    /// Called when the panel becomes hidden/inactive.
    /// Use for stopping timers, unsubscribing, cleaning up resources.
    /// </summary>
    public async System.Threading.Tasks.Task OnDeactivatedAsync(
        System.Threading.CancellationToken cancellationToken = default)
    {
        // Panel is now hidden - save state if needed
        await _viewModel.SaveStateAsync();
    }

    /// <summary>
    /// Called to refresh the panel's data on demand.
    /// </summary>
    public async System.Threading.Tasks.Task RefreshAsync(
        System.Threading.CancellationToken cancellationToken = default)
    {
        // Refresh UI data from backend if needed
        if (_backend != null)
        {
            // Example: await RefreshFromBackendAsync();
        }
    }

    /// <summary>
    /// Set the backend client for API calls.
    /// Called by the plugin during Initialize.
    /// </summary>
    internal void SetBackendClient(IBackendClient backend)
    {
        _backend = backend;
        _viewModel.SetBackendClient(backend);
    }
}
