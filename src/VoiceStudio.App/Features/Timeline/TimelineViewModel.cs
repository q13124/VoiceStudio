// Phase 5: Timeline Component
// Task 5.11: Professional audio timeline

using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Windows.Input;

namespace VoiceStudio.App.Features.Timeline;

/// <summary>
/// Timeline track types.
/// </summary>
public enum TrackType
{
    Audio,
    Voice,
    Music,
    SoundFX,
    Video,
    Subtitle,
}

/// <summary>
/// A clip on the timeline.
/// </summary>
public class TimelineClip : INotifyPropertyChanged
{
    private double _startTime;
    private double _duration;
    private double _volume = 1.0;
    private bool _isMuted;
    private bool _isSelected;

    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string Name { get; set; } = "";
    public string SourcePath { get; set; } = "";
    public TrackType TrackType { get; set; }
    
    public double StartTime
    {
        get => _startTime;
        set { _startTime = value; OnPropertyChanged(); }
    }
    
    public double Duration
    {
        get => _duration;
        set { _duration = value; OnPropertyChanged(); OnPropertyChanged(nameof(EndTime)); }
    }
    
    public double EndTime => StartTime + Duration;
    
    public double Volume
    {
        get => _volume;
        set { _volume = Math.Clamp(value, 0, 2); OnPropertyChanged(); }
    }
    
    public bool IsMuted
    {
        get => _isMuted;
        set { _isMuted = value; OnPropertyChanged(); }
    }
    
    public bool IsSelected
    {
        get => _isSelected;
        set { _isSelected = value; OnPropertyChanged(); }
    }
    
    // Audio properties
    public double FadeInDuration { get; set; }
    public double FadeOutDuration { get; set; }
    public double TrimStart { get; set; }
    public double TrimEnd { get; set; }
    
    public event PropertyChangedEventHandler? PropertyChanged;
    
    protected void OnPropertyChanged([CallerMemberName] string? name = null) =>
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
}

/// <summary>
/// A track on the timeline.
/// </summary>
public class TimelineTrack : INotifyPropertyChanged
{
    private bool _isExpanded = true;
    private bool _isMuted;
    private bool _isSolo;
    private double _volume = 1.0;

    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string Name { get; set; } = "";
    public TrackType Type { get; set; }
    public double Height { get; set; } = 80;
    public ObservableCollection<TimelineClip> Clips { get; } = new();
    
    public bool IsExpanded
    {
        get => _isExpanded;
        set { _isExpanded = value; OnPropertyChanged(); }
    }
    
    public bool IsMuted
    {
        get => _isMuted;
        set { _isMuted = value; OnPropertyChanged(); }
    }
    
    public bool IsSolo
    {
        get => _isSolo;
        set { _isSolo = value; OnPropertyChanged(); }
    }
    
    public double Volume
    {
        get => _volume;
        set { _volume = Math.Clamp(value, 0, 2); OnPropertyChanged(); }
    }
    
    public event PropertyChangedEventHandler? PropertyChanged;
    
    protected void OnPropertyChanged([CallerMemberName] string? name = null) =>
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
}

/// <summary>
/// ViewModel for the timeline component.
/// </summary>
public class TimelineViewModel : INotifyPropertyChanged
{
    private double _currentTime;
    private double _totalDuration = 60;
    private double _zoom = 1.0;
    private double _scrollPosition;
    private bool _isPlaying;
    private bool _isLooping;
    private double _selectionStart;
    private double _selectionEnd;
    private bool _snapEnabled = true;
    private double _snapInterval = 0.1;

    public TimelineViewModel()
    {
        Tracks = new ObservableCollection<TimelineTrack>();
        SelectedClips = new ObservableCollection<TimelineClip>();
        
        // Commands
        PlayCommand = new RelayCommand(() => Play());
        PauseCommand = new RelayCommand(() => Pause());
        StopCommand = new RelayCommand(() => Stop());
        AddTrackCommand = new RelayCommand<TrackType>(AddTrack);
        DeleteSelectedCommand = new RelayCommand(DeleteSelected);
        SplitAtPlayheadCommand = new RelayCommand(SplitAtPlayhead);
    }

    public ObservableCollection<TimelineTrack> Tracks { get; }
    public ObservableCollection<TimelineClip> SelectedClips { get; }

    public double CurrentTime
    {
        get => _currentTime;
        set
        {
            _currentTime = Math.Clamp(value, 0, TotalDuration);
            OnPropertyChanged();
            OnPropertyChanged(nameof(CurrentTimeFormatted));
        }
    }

    public string CurrentTimeFormatted =>
        TimeSpan.FromSeconds(CurrentTime).ToString(@"mm\:ss\.fff");

    public double TotalDuration
    {
        get => _totalDuration;
        set { _totalDuration = value; OnPropertyChanged(); }
    }

    public double Zoom
    {
        get => _zoom;
        set
        {
            _zoom = Math.Clamp(value, 0.1, 10);
            OnPropertyChanged();
            OnPropertyChanged(nameof(PixelsPerSecond));
        }
    }

    public double PixelsPerSecond => 100 * Zoom;

    public double ScrollPosition
    {
        get => _scrollPosition;
        set { _scrollPosition = value; OnPropertyChanged(); }
    }

    public bool IsPlaying
    {
        get => _isPlaying;
        set { _isPlaying = value; OnPropertyChanged(); }
    }

    public bool IsLooping
    {
        get => _isLooping;
        set { _isLooping = value; OnPropertyChanged(); }
    }

    public double SelectionStart
    {
        get => _selectionStart;
        set { _selectionStart = value; OnPropertyChanged(); }
    }

    public double SelectionEnd
    {
        get => _selectionEnd;
        set { _selectionEnd = value; OnPropertyChanged(); }
    }

    public bool SnapEnabled
    {
        get => _snapEnabled;
        set { _snapEnabled = value; OnPropertyChanged(); }
    }

    public double SnapInterval
    {
        get => _snapInterval;
        set { _snapInterval = value; OnPropertyChanged(); }
    }

    // Commands
    public ICommand PlayCommand { get; }
    public ICommand PauseCommand { get; }
    public ICommand StopCommand { get; }
    public ICommand AddTrackCommand { get; }
    public ICommand DeleteSelectedCommand { get; }
    public ICommand SplitAtPlayheadCommand { get; }

    public void Play()
    {
        IsPlaying = true;
    }

    public void Pause()
    {
        IsPlaying = false;
    }

    public void Stop()
    {
        IsPlaying = false;
        CurrentTime = 0;
    }

    public void AddTrack(TrackType type)
    {
        var track = new TimelineTrack
        {
            Name = $"{type} {Tracks.Count + 1}",
            Type = type,
        };
        
        Tracks.Add(track);
    }

    public void AddClip(string trackId, TimelineClip clip)
    {
        foreach (var track in Tracks)
        {
            if (track.Id == trackId)
            {
                if (SnapEnabled)
                {
                    clip.StartTime = SnapTime(clip.StartTime);
                }
                
                track.Clips.Add(clip);
                UpdateTotalDuration();
                break;
            }
        }
    }

    public void MoveClip(TimelineClip clip, double newStartTime, string? newTrackId = null)
    {
        if (SnapEnabled)
        {
            newStartTime = SnapTime(newStartTime);
        }
        
        clip.StartTime = Math.Max(0, newStartTime);
        
        if (newTrackId != null)
        {
            // Move to different track
            foreach (var track in Tracks)
            {
                if (track.Clips.Contains(clip))
                {
                    track.Clips.Remove(clip);
                    break;
                }
            }
            
            foreach (var track in Tracks)
            {
                if (track.Id == newTrackId)
                {
                    track.Clips.Add(clip);
                    break;
                }
            }
        }
        
        UpdateTotalDuration();
    }

    public void SelectClip(TimelineClip clip, bool addToSelection = false)
    {
        if (!addToSelection)
        {
            foreach (var selected in SelectedClips)
            {
                selected.IsSelected = false;
            }
            SelectedClips.Clear();
        }
        
        clip.IsSelected = true;
        SelectedClips.Add(clip);
    }

    public void ClearSelection()
    {
        foreach (var clip in SelectedClips)
        {
            clip.IsSelected = false;
        }
        SelectedClips.Clear();
    }

    public void DeleteSelected()
    {
        foreach (var clip in SelectedClips)
        {
            foreach (var track in Tracks)
            {
                if (track.Clips.Contains(clip))
                {
                    track.Clips.Remove(clip);
                    break;
                }
            }
        }
        
        SelectedClips.Clear();
        UpdateTotalDuration();
    }

    public void SplitAtPlayhead()
    {
        foreach (var clip in SelectedClips)
        {
            if (CurrentTime > clip.StartTime && CurrentTime < clip.EndTime)
            {
                var splitPoint = CurrentTime - clip.StartTime;
                
                var newClip = new TimelineClip
                {
                    Name = $"{clip.Name} (split)",
                    SourcePath = clip.SourcePath,
                    TrackType = clip.TrackType,
                    StartTime = CurrentTime,
                    Duration = clip.Duration - splitPoint,
                    Volume = clip.Volume,
                    TrimStart = clip.TrimStart + splitPoint,
                };
                
                clip.Duration = splitPoint;
                
                foreach (var track in Tracks)
                {
                    if (track.Clips.Contains(clip))
                    {
                        track.Clips.Add(newClip);
                        break;
                    }
                }
            }
        }
    }

    public void ZoomIn()
    {
        Zoom *= 1.2;
    }

    public void ZoomOut()
    {
        Zoom /= 1.2;
    }

    public void ZoomToFit()
    {
        // Calculate zoom to fit all content
        if (TotalDuration > 0)
        {
            // Would need container width
            Zoom = 1.0;
        }
    }

    private double SnapTime(double time)
    {
        if (!SnapEnabled || SnapInterval <= 0)
        {
            return time;
        }
        
        return Math.Round(time / SnapInterval) * SnapInterval;
    }

    private void UpdateTotalDuration()
    {
        double maxEnd = 0;
        
        foreach (var track in Tracks)
        {
            foreach (var clip in track.Clips)
            {
                if (clip.EndTime > maxEnd)
                {
                    maxEnd = clip.EndTime;
                }
            }
        }
        
        TotalDuration = Math.Max(60, maxEnd + 10);
    }

    public event PropertyChangedEventHandler? PropertyChanged;
    
    protected void OnPropertyChanged([CallerMemberName] string? name = null) =>
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
}

/// <summary>
/// Relay command with parameter.
/// </summary>
public class RelayCommand<T> : ICommand
{
    private readonly Action<T> _execute;
    private readonly Func<T, bool>? _canExecute;

    public RelayCommand(Action<T> execute, Func<T, bool>? canExecute = null)
    {
        _execute = execute;
        _canExecute = canExecute;
    }

    public event EventHandler? CanExecuteChanged;

    public bool CanExecute(object? parameter) =>
        _canExecute?.Invoke((T)parameter!) ?? true;

    public void Execute(object? parameter) =>
        _execute((T)parameter!);
}

/// <summary>
/// Simple relay command.
/// </summary>
public class RelayCommand : ICommand
{
    private readonly Action _execute;
    private readonly Func<bool>? _canExecute;

    public RelayCommand(Action execute, Func<bool>? canExecute = null)
    {
        _execute = execute;
        _canExecute = canExecute;
    }

    public event EventHandler? CanExecuteChanged;

    public bool CanExecute(object? parameter) => _canExecute?.Invoke() ?? true;
    public void Execute(object? parameter) => _execute();
}
