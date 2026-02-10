// Phase 5: Synthesis UI
// Task 5.16: Main synthesis interface
// Gap Analysis Fix: Refactored to use CommunityToolkit.Mvvm patterns

using System;
using System.Collections.ObjectModel;
using System.Threading;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.App.Features.VoiceProfile;

namespace VoiceStudio.App.Features.Synthesis;

/// <summary>
/// Synthesis engine info.
/// </summary>
public class EngineInfo
{
    public string Id { get; set; } = "";
    public string Name { get; set; } = "";
    public string Description { get; set; } = "";
    public bool IsAvailable { get; set; }
    public bool RequiresGPU { get; set; }
}

/// <summary>
/// Synthesis parameters.
/// Gap Analysis Fix: Uses CommunityToolkit.Mvvm ObservableObject.
/// </summary>
public partial class SynthesisParameters : ObservableObject
{
    private double _speed = 1.0;
    private double _pitch = 1.0;
    private double _volume = 1.0;
    private double _stability = 0.5;
    private double _similarity = 0.75;
    private double _style = 0.0;

    public double Speed
    {
        get => _speed;
        set => SetProperty(ref _speed, Math.Clamp(value, 0.25, 4.0));
    }

    public double Pitch
    {
        get => _pitch;
        set => SetProperty(ref _pitch, Math.Clamp(value, 0.5, 2.0));
    }

    public double Volume
    {
        get => _volume;
        set => SetProperty(ref _volume, Math.Clamp(value, 0, 2.0));
    }

    public double Stability
    {
        get => _stability;
        set => SetProperty(ref _stability, Math.Clamp(value, 0, 1.0));
    }

    public double Similarity
    {
        get => _similarity;
        set => SetProperty(ref _similarity, Math.Clamp(value, 0, 1.0));
    }

    public double Style
    {
        get => _style;
        set => SetProperty(ref _style, Math.Clamp(value, 0, 1.0));
    }
}

/// <summary>
/// Synthesis result.
/// </summary>
public class SynthesisResult
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string Text { get; set; } = "";
    public string AudioPath { get; set; } = "";
    public TimeSpan Duration { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    public string Engine { get; set; } = "";
    public string Voice { get; set; } = "";
}

/// <summary>
/// ViewModel for the synthesis interface.
/// Gap Analysis Fix: Uses CommunityToolkit.Mvvm ObservableObject and RelayCommand.
/// </summary>
public partial class SynthesisViewModel : ObservableObject
{
    private string _inputText = "";
    private EngineInfo? _selectedEngine;
    private VoiceProfileData? _selectedVoice;
    private bool _isSynthesizing;
    private double _progress;
    private string _statusMessage = "Ready";
    private SynthesisResult? _currentResult;
    private bool _isPlaying;
    private CancellationTokenSource? _synthesizeCts;

    public SynthesisViewModel()
    {
        Parameters = new SynthesisParameters();
        AvailableEngines = new ObservableCollection<EngineInfo>();
        AvailableVoices = new ObservableCollection<VoiceProfileData>();
        History = new ObservableCollection<SynthesisResult>();
        
        SynthesizeCommand = new AsyncRelayCommand(SynthesizeAsync, CanSynthesize);
        CancelCommand = new RelayCommand(CancelSynthesis, () => IsSynthesizing);
        PlayCommand = new AsyncRelayCommand(PlayAsync, CanPlay);
        PauseCommand = new RelayCommand(Pause);
        SaveCommand = new AsyncRelayCommand(SaveAsync, CanSave);
        ClearHistoryCommand = new RelayCommand(ClearHistory);
    }

    // Input
    public string InputText
    {
        get => _inputText;
        set
        {
            if (SetProperty(ref _inputText, value))
            {
                OnPropertyChanged(nameof(CharacterCount));
                OnPropertyChanged(nameof(WordCount));
                OnPropertyChanged(nameof(EstimatedDuration));
            }
        }
    }

    public int CharacterCount => InputText.Length;
    public int WordCount => string.IsNullOrWhiteSpace(InputText)
        ? 0
        : InputText.Split(Array.Empty<char>(), StringSplitOptions.RemoveEmptyEntries).Length;
    
    public TimeSpan EstimatedDuration => TimeSpan.FromSeconds(WordCount * 0.5 / Parameters.Speed);

    // Engine and voice selection
    public ObservableCollection<EngineInfo> AvailableEngines { get; }
    public ObservableCollection<VoiceProfileData> AvailableVoices { get; }

    public EngineInfo? SelectedEngine
    {
        get => _selectedEngine;
        set
        {
            if (SetProperty(ref _selectedEngine, value))
            {
                // Reload voices for engine
                _ = LoadVoicesAsync();
            }
        }
    }

    public VoiceProfileData? SelectedVoice
    {
        get => _selectedVoice;
        set => SetProperty(ref _selectedVoice, value);
    }

    // Parameters
    public SynthesisParameters Parameters { get; }

    // State
    public bool IsSynthesizing
    {
        get => _isSynthesizing;
        set => SetProperty(ref _isSynthesizing, value);
    }

    public double Progress
    {
        get => _progress;
        set => SetProperty(ref _progress, value);
    }

    public string StatusMessage
    {
        get => _statusMessage;
        set => SetProperty(ref _statusMessage, value);
    }

    public SynthesisResult? CurrentResult
    {
        get => _currentResult;
        set => SetProperty(ref _currentResult, value);
    }

    public bool IsPlaying
    {
        get => _isPlaying;
        set => SetProperty(ref _isPlaying, value);
    }

    // History
    public ObservableCollection<SynthesisResult> History { get; }

    // Commands (using CommunityToolkit.Mvvm.Input)
    public IAsyncRelayCommand SynthesizeCommand { get; }
    public IRelayCommand CancelCommand { get; }
    public IAsyncRelayCommand PlayCommand { get; }
    public IRelayCommand PauseCommand { get; }
    public IAsyncRelayCommand SaveCommand { get; }
    public IRelayCommand ClearHistoryCommand { get; }

    public async Task InitializeAsync()
    {
        await LoadEnginesAsync();
        await LoadVoicesAsync();
    }

    private async Task LoadEnginesAsync()
    {
        AvailableEngines.Clear();
        
        AvailableEngines.Add(new EngineInfo
        {
            Id = "xtts",
            Name = "XTTS v2",
            Description = "Coqui XTTS for high-quality voice cloning",
            IsAvailable = true,
            RequiresGPU = true,
        });
        
        AvailableEngines.Add(new EngineInfo
        {
            Id = "piper",
            Name = "Piper TTS",
            Description = "Fast, lightweight TTS engine",
            IsAvailable = true,
            RequiresGPU = false,
        });
        
        SelectedEngine = AvailableEngines[0];
        
        await Task.CompletedTask;
    }

    private async Task LoadVoicesAsync()
    {
        AvailableVoices.Clear();
        
        AvailableVoices.Add(new VoiceProfileData
        {
            Name = "Default English",
            Engine = SelectedEngine?.Id ?? "",
            Language = "en",
        });
        
        SelectedVoice = AvailableVoices[0];
        
        await Task.CompletedTask;
    }

    private bool CanSynthesize() =>
        !string.IsNullOrWhiteSpace(InputText) &&
        SelectedEngine != null &&
        SelectedVoice != null &&
        !IsSynthesizing;

    private async Task SynthesizeAsync()
    {
        if (!CanSynthesize())
        {
            return;
        }
        
        IsSynthesizing = true;
        Progress = 0;
        StatusMessage = "Synthesizing...";
        
        _synthesizeCts = new CancellationTokenSource();
        
        try
        {
            // Simulate synthesis
            for (int i = 0; i <= 100; i += 10)
            {
                _synthesizeCts.Token.ThrowIfCancellationRequested();
                Progress = i;
                await Task.Delay(200, _synthesizeCts.Token);
            }
            
            var result = new SynthesisResult
            {
                Text = InputText,
                AudioPath = $"temp/synthesis_{DateTime.Now:yyyyMMdd_HHmmss}.wav",
                Duration = EstimatedDuration,
                Engine = SelectedEngine!.Id,
                Voice = SelectedVoice!.Name,
            };
            
            CurrentResult = result;
            History.Insert(0, result);
            
            StatusMessage = "Synthesis complete";
        }
        catch (OperationCanceledException)
        {
            StatusMessage = "Synthesis cancelled";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Error: {ex.Message}";
        }
        finally
        {
            IsSynthesizing = false;
            Progress = 0;
            _synthesizeCts = null;
        }
    }

    private void CancelSynthesis()
    {
        _synthesizeCts?.Cancel();
    }

    private bool CanPlay() => CurrentResult != null && !IsSynthesizing;

    private async Task PlayAsync()
    {
        if (CurrentResult == null)
        {
            return;
        }
        
        IsPlaying = true;
        StatusMessage = "Playing...";
        
        // Simulate playback
        await Task.Delay((int)CurrentResult.Duration.TotalMilliseconds);
        
        IsPlaying = false;
        StatusMessage = "Ready";
    }

    private void Pause()
    {
        IsPlaying = false;
    }

    private bool CanSave() => CurrentResult != null;

    private async Task SaveAsync()
    {
        if (CurrentResult == null)
        {
            return;
        }
        
        // Save audio file
        StatusMessage = "Saved";
        
        await Task.CompletedTask;
    }

    private void ClearHistory()
    {
        History.Clear();
    }
}
// Gap Analysis Fix: Removed file-scoped RelayCommand classes - using CommunityToolkit.Mvvm.Input instead
