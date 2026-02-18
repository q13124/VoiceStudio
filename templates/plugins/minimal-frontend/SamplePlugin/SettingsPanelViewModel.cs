using System;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using VoiceStudio.Core.Services;

namespace {{CLASS_NAME}}Plugin;

/// <summary>
/// ViewModel for the Settings Panel.
/// 
/// Implements INotifyPropertyChanged for WPF/WinUI binding.
/// Handles all UI logic and backend communication.
/// </summary>
public class SettingsPanelViewModel : INotifyPropertyChanged
{
    private IBackendClient _backend;
    private string _message = "Hello from {{DISPLAY_NAME}}!";

    /// <summary>Message property with two-way binding support</summary>
    public string Message
    {
        get => _message;
        set => SetProperty(ref _message, value);
    }

    /// <summary>
    /// Set the backend client for API calls.
    /// </summary>
    internal void SetBackendClient(IBackendClient backend)
    {
        _backend = backend;
    }

    /// <summary>
    /// Save current state (called when panel deactivates).
    /// Override to persist settings.
    /// </summary>
    internal async Task SaveStateAsync()
    {
        // Example: Save Message to backend
        // await _backend?.PostAsync("/api/plugin/{{PLUGIN_NAME}}/message",
        //     new { message = Message });
        
        await Task.CompletedTask;
    }

    /// <summary>
    /// Standard implementation of SetProperty for INotifyPropertyChanged.
    /// Notifies UI when property changes.
    /// </summary>
    protected void SetProperty<T>(
        ref T field,
        T value,
        [CallerMemberName] string propertyName = "")
    {
        if (!Equals(field, value))
        {
            field = value;
            OnPropertyChanged(propertyName);
        }
    }

    /// <summary>
    /// Raise PropertyChanged event when property changes.
    /// </summary>
    protected void OnPropertyChanged([CallerMemberName] string propertyName = "")
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }

    public event PropertyChangedEventHandler PropertyChanged;
}
