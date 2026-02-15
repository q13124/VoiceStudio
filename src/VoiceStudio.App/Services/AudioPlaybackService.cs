using System;
using System.IO;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Logging;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Audio playback service using NAudio/WASAPI for high-quality audio output.
  /// Supports WAV, MP3, FLAC formats and real-time streaming.
  /// </summary>
  /// <remarks>
  /// DEPRECATED (Audit M-4): Use <see cref="AudioPlayerService"/> (IAudioPlayerService) instead.
  /// AudioPlayerService is the canonical playback service with preview support, seek, and
  /// position tracking. This class has zero consumers and is retained only for backward
  /// compatibility during the transition period. Will be removed in v1.2.
  /// </remarks>
  [System.Obsolete("Use AudioPlayerService (IAudioPlayerService) instead. See Audit M-4.")]
  public class AudioPlaybackService : IAudioPlaybackService, IDisposable
  {
    private NAudio.Wave.WaveOutEvent? _waveOut;
    private NAudio.Wave.AudioFileReader? _audioFileReader;
    private NAudio.Wave.WaveStream? _waveStream;
    private System.Threading.Timer? _positionTimer;
    private bool _disposed;
    private double _volume = 1.0;
    private bool _isPlaying;
    private bool _isPaused;
    private readonly HttpClient _httpClient = new();
    private readonly object _lockObject = new();

    public bool IsPlaying
    {
      get { lock (_lockObject) { return _isPlaying; } }
      private set { lock (_lockObject) { _isPlaying = value; } }
    }

    public double Position => _audioFileReader?.CurrentTime.TotalSeconds ?? 0.0;

    public double Duration => _audioFileReader?.TotalTime.TotalSeconds ?? 0.0;

    public double Volume
    {
      get => _volume;
      set
      {
        _volume = Math.Max(0.0, Math.Min(1.0, value));
        if (_audioFileReader != null)
        {
          _audioFileReader.Volume = (float)_volume;
        }
      }
    }

    public event EventHandler? PlaybackStarted;
    public event EventHandler? PlaybackStopped;
    public event EventHandler<double>? PositionChanged;

    public async Task PlayFileAsync(string filePath, CancellationToken cancellationToken = default)
    {
      if (!File.Exists(filePath))
        throw new FileNotFoundException($"Audio file not found: {filePath}");

      await Task.Run(() =>
      {
        try
        {
          lock (_lockObject)
          {
            // Stop any current playback
            StopInternal();

            // Create audio file reader (NAudio handles WAV, MP3, FLAC automatically)
            _audioFileReader = new NAudio.Wave.AudioFileReader(filePath);
            _audioFileReader.Volume = (float)_volume;

            // Create wave out device
            _waveOut = new NAudio.Wave.WaveOutEvent();
            _waveOut.Init(_audioFileReader);
            _waveOut.PlaybackStopped += WaveOut_PlaybackStopped;

            // Start playback
            _waveOut.Play();
            _isPlaying = true;
            _isPaused = false;

            // Start position tracking timer
            StartPositionTimer();

            PlaybackStarted?.Invoke(this, EventArgs.Empty);
          }
        }
        catch (Exception ex)
        {
          throw new InvalidOperationException($"Failed to play audio file: {ex.Message}", ex);
        }
      }, cancellationToken);
    }

    public async Task PlayStreamAsync(Stream audioStream, string format = "wav", CancellationToken cancellationToken = default)
    {
      if (audioStream == null)
        throw new ArgumentNullException(nameof(audioStream));

      await Task.Run(() =>
      {
        try
        {
          lock (_lockObject)
          {
            // Stop any current playback
            StopInternal();

            // Copy stream to memory for seeking support
            var memoryStream = new MemoryStream();
            audioStream.CopyTo(memoryStream);
            memoryStream.Position = 0;

            // Create appropriate wave stream based on format
            NAudio.Wave.WaveStream baseStream = format.ToLowerInvariant() switch
            {
              "wav" => new NAudio.Wave.WaveFileReader(memoryStream),
              "mp3" => new NAudio.Wave.Mp3FileReader(memoryStream),
              // Note: FLAC support requires NAudio.Lame or other FLAC decoder
              // For now, treat FLAC as unsupported
              "flac" => throw new NotSupportedException("FLAC format requires additional NAudio extensions. Please convert to WAV or MP3."),
              _ => throw new NotSupportedException($"Audio format '{format}' is not supported. Supported formats: WAV, MP3")
            };

            // Wrap with volume control using WaveChannel32 (converts to 32-bit float internally)
            _waveStream = new NAudio.Wave.WaveChannel32(baseStream)
            {
              Volume = (float)_volume
            };

            // Store baseStream reference for position/duration tracking
            // WaveFileReader and Mp3FileReader have TotalTime and CurrentTime properties
            // We'll use reflection or cast to access these
            _audioFileReader = baseStream as NAudio.Wave.AudioFileReader;
            if (_audioFileReader == null)
            {
              // For format-specific readers, create a temporary file for AudioFileReader
              // This allows us to use the same position tracking interface
              // Note: This is a workaround - in production, we might want a better solution
              var tempPath = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString() + "." + format);
              File.WriteAllBytes(tempPath, memoryStream.ToArray());
              _audioFileReader = new NAudio.Wave.AudioFileReader(tempPath);
              _audioFileReader.Volume = (float)_volume;

              // Use the AudioFileReader's stream instead
              _waveStream?.Dispose();
              _waveStream = null;
              baseStream?.Dispose();
            }
            else
            {
              _audioFileReader.Volume = (float)_volume;
            }

            // Create wave out device
            _waveOut = new NAudio.Wave.WaveOutEvent();
            _waveOut.Init(_waveStream ?? _audioFileReader);
            _waveOut.PlaybackStopped += WaveOut_PlaybackStopped;

            // Start playback
            _waveOut.Play();
            _isPlaying = true;
            _isPaused = false;

            // Start position tracking timer
            StartPositionTimer();

            PlaybackStarted?.Invoke(this, EventArgs.Empty);
          }
        }
        catch (Exception ex)
        {
          throw new InvalidOperationException($"Failed to play audio stream: {ex.Message}", ex);
        }
      }, cancellationToken);
    }

    public async Task PlayUrlAsync(string audioUrl, CancellationToken cancellationToken = default)
    {
      if (string.IsNullOrWhiteSpace(audioUrl))
        throw new ArgumentException("Audio URL cannot be null or empty", nameof(audioUrl));

      try
      {
        // Download audio from URL
        var response = await _httpClient.GetAsync(audioUrl, cancellationToken);
        response.EnsureSuccessStatusCode();

        // Determine format from URL or content type
        var format = "wav";
        var contentType = response.Content.Headers.ContentType?.MediaType;
        if (contentType != null)
        {
          format = contentType switch
          {
            "audio/wav" or "audio/wave" or "audio/x-wav" => "wav",
            "audio/mpeg" or "audio/mp3" => "mp3",
            "audio/flac" or "audio/x-flac" => "flac",
            _ => Path.GetExtension(audioUrl).TrimStart('.').ToLowerInvariant() switch
            {
              "mp3" => "mp3",
              "flac" => "flac",
              _ => "wav"
            }
          };
        }
        else
        {
          var extension = Path.GetExtension(audioUrl).TrimStart('.').ToLowerInvariant();
          if (!string.IsNullOrEmpty(extension))
            format = extension;
        }

        // Play from stream
        await using var stream = await response.Content.ReadAsStreamAsync(cancellationToken);
        await PlayStreamAsync(stream, format, cancellationToken);
      }
      catch (HttpRequestException ex)
      {
        throw new InvalidOperationException($"Failed to download audio from URL: {ex.Message}", ex);
      }
    }

    public void Pause()
    {
      lock (_lockObject)
      {
        if (_waveOut != null && _isPlaying && !_isPaused)
        {
          _waveOut.Pause();
          _isPaused = true;
        }
      }
    }

    public void Resume()
    {
      lock (_lockObject)
      {
        if (_waveOut != null && _isPaused)
        {
          // NAudio WaveOutEvent doesn't have Resume() - call Play() to resume
          _waveOut.Play();
          _isPaused = false;
        }
      }
    }

    public void Stop()
    {
      lock (_lockObject)
      {
        StopInternal();
        PlaybackStopped?.Invoke(this, EventArgs.Empty);
      }
    }

    private void StopInternal()
    {
      // Stop position timer
      _positionTimer?.Dispose();
      _positionTimer = null;

      // Stop and dispose audio components
      try
      {
        // Unsubscribe from event before disposing to prevent callbacks on disposed object
        if (_waveOut != null)
        {
          _waveOut.PlaybackStopped -= WaveOut_PlaybackStopped;
        }
        
        _waveOut?.Stop();
        _waveOut?.Dispose();
        _audioFileReader?.Dispose();
        _waveStream?.Dispose();
      }
      catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {ex.Message}", "AudioPlaybackService.StopInternal");
      }

      _waveOut = null;
      _audioFileReader = null;
      _waveStream = null;
      _isPlaying = false;
      _isPaused = false;
    }

    public void Seek(double position)
    {
      lock (_lockObject)
      {
        if (_audioFileReader != null && position >= 0 && position <= Duration)
        {
          _audioFileReader.CurrentTime = TimeSpan.FromSeconds(position);
          PositionChanged?.Invoke(this, Position);
        }
      }
    }

    private void StartPositionTimer()
    {
      _positionTimer?.Dispose();
      _positionTimer = new System.Threading.Timer(
          _ =>
          {
            if (_isPlaying && _audioFileReader != null)
            {
              PositionChanged?.Invoke(this, Position);
            }
          },
          null,
          TimeSpan.Zero,
          TimeSpan.FromMilliseconds(100) // Update every 100ms
      );
    }

    private void WaveOut_PlaybackStopped(object? sender, NAudio.Wave.StoppedEventArgs e)
    {
      lock (_lockObject)
      {
        _isPlaying = false;
        _isPaused = false;
        _positionTimer?.Dispose();
        _positionTimer = null;
        PlaybackStopped?.Invoke(this, EventArgs.Empty);
      }
    }

    public void Dispose()
    {
      if (!_disposed)
      {
        Stop();
        _httpClient?.Dispose();
        _positionTimer?.Dispose();
        _disposed = true;
      }
    }
  }
}