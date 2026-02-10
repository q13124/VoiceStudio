// Phase 5: Status Bar Component
// Task 5.13: Professional status bar

using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace VoiceStudio.App.Features.StatusBar;

/// <summary>
/// Status bar item types.
/// </summary>
public enum StatusItemType
{
    Text,
    Progress,
    Icon,
    Button,
}

/// <summary>
/// Status bar item.
/// </summary>
public class StatusItem : INotifyPropertyChanged
{
    private string _text = "";
    private string _icon = "";
    private double _progress;
    private bool _isVisible = true;
    private bool _isClickable;

    public string Id { get; set; } = "";
    public StatusItemType Type { get; set; }
    public int Order { get; set; }
    
    public string Text
    {
        get => _text;
        set { _text = value; OnPropertyChanged(); }
    }
    
    public string Icon
    {
        get => _icon;
        set { _icon = value; OnPropertyChanged(); }
    }
    
    public double Progress
    {
        get => _progress;
        set { _progress = value; OnPropertyChanged(); }
    }
    
    public bool IsVisible
    {
        get => _isVisible;
        set { _isVisible = value; OnPropertyChanged(); }
    }
    
    public bool IsClickable
    {
        get => _isClickable;
        set { _isClickable = value; OnPropertyChanged(); }
    }
    
    public Action? ClickAction { get; set; }
    
    public event PropertyChangedEventHandler? PropertyChanged;
    
    protected void OnPropertyChanged([CallerMemberName] string? name = null) =>
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
}

/// <summary>
/// ViewModel for the status bar.
/// </summary>
public class StatusBarViewModel : INotifyPropertyChanged
{
    private string _mainStatus = "Ready";
    private bool _isProcessing;
    private double _processingProgress;
    private string _engineStatus = "";
    private string _audioStatus = "";
    private bool _isBackendConnected;

    public StatusBarViewModel()
    {
        LeftItems = new ObservableCollection<StatusItem>();
        RightItems = new ObservableCollection<StatusItem>();
        
        // Default items
        LeftItems.Add(new StatusItem
        {
            Id = "main_status",
            Type = StatusItemType.Text,
            Text = "Ready",
            Order = 0,
        });
        
        RightItems.Add(new StatusItem
        {
            Id = "engine",
            Type = StatusItemType.Text,
            Icon = "\uE950",
            Text = "Engine: None",
            Order = 100,
        });
        
        RightItems.Add(new StatusItem
        {
            Id = "audio",
            Type = StatusItemType.Text,
            Icon = "\uE767",
            Text = "44.1 kHz",
            Order = 200,
        });
        
        RightItems.Add(new StatusItem
        {
            Id = "backend",
            Type = StatusItemType.Icon,
            Icon = "\uEB51",
            Text = "Backend",
            IsClickable = true,
            Order = 300,
        });
    }

    public ObservableCollection<StatusItem> LeftItems { get; }
    public ObservableCollection<StatusItem> RightItems { get; }

    public string MainStatus
    {
        get => _mainStatus;
        set
        {
            _mainStatus = value;
            OnPropertyChanged();
            UpdateItem("main_status", i => i.Text = value);
        }
    }

    public bool IsProcessing
    {
        get => _isProcessing;
        set { _isProcessing = value; OnPropertyChanged(); }
    }

    public double ProcessingProgress
    {
        get => _processingProgress;
        set { _processingProgress = value; OnPropertyChanged(); }
    }

    public string EngineStatus
    {
        get => _engineStatus;
        set
        {
            _engineStatus = value;
            OnPropertyChanged();
            UpdateItem("engine", i => i.Text = $"Engine: {value}");
        }
    }

    public string AudioStatus
    {
        get => _audioStatus;
        set
        {
            _audioStatus = value;
            OnPropertyChanged();
            UpdateItem("audio", i => i.Text = value);
        }
    }

    public bool IsBackendConnected
    {
        get => _isBackendConnected;
        set
        {
            _isBackendConnected = value;
            OnPropertyChanged();
            UpdateItem("backend", i =>
            {
                i.Icon = value ? "\uEB52" : "\uEB51";
                i.Text = value ? "Connected" : "Disconnected";
            });
        }
    }

    /// <summary>
    /// Show a temporary status message.
    /// </summary>
    public void ShowTemporaryStatus(string message, int durationMs = 3000)
    {
        var previous = MainStatus;
        MainStatus = message;
        
        // Restore after duration
        var timer = new System.Threading.Timer(_ =>
        {
            MainStatus = previous;
        }, null, durationMs, System.Threading.Timeout.Infinite);
    }

    /// <summary>
    /// Start showing progress.
    /// </summary>
    public void StartProgress(string message)
    {
        MainStatus = message;
        IsProcessing = true;
        ProcessingProgress = 0;
    }

    /// <summary>
    /// Update progress.
    /// </summary>
    public void UpdateProgress(double progress, string? message = null)
    {
        ProcessingProgress = progress;
        if (message != null)
        {
            MainStatus = message;
        }
    }

    /// <summary>
    /// Complete progress.
    /// </summary>
    public void CompleteProgress(string? message = null)
    {
        IsProcessing = false;
        ProcessingProgress = 0;
        MainStatus = message ?? "Ready";
    }

    /// <summary>
    /// Add a custom status item.
    /// </summary>
    public void AddItem(StatusItem item, bool rightSide = true)
    {
        var collection = rightSide ? RightItems : LeftItems;
        collection.Add(item);
    }

    /// <summary>
    /// Remove a status item.
    /// </summary>
    public void RemoveItem(string itemId)
    {
        foreach (var item in LeftItems)
        {
            if (item.Id == itemId)
            {
                LeftItems.Remove(item);
                return;
            }
        }
        
        foreach (var item in RightItems)
        {
            if (item.Id == itemId)
            {
                RightItems.Remove(item);
                return;
            }
        }
    }

    private void UpdateItem(string id, Action<StatusItem> update)
    {
        foreach (var item in LeftItems)
        {
            if (item.Id == id)
            {
                update(item);
                return;
            }
        }
        
        foreach (var item in RightItems)
        {
            if (item.Id == id)
            {
                update(item);
                return;
            }
        }
    }

    public event PropertyChangedEventHandler? PropertyChanged;
    
    protected void OnPropertyChanged([CallerMemberName] string? name = null) =>
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
}
