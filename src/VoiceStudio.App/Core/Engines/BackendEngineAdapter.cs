using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Engines;
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services.Engines
{
  /// <summary>
  /// Adapter that bridges the local IEngine interface to the remote Python backend.
  /// </summary>
  public class BackendEngineAdapter : ITextToSpeechEngine, ITranscriptionEngine
  {
    private readonly IBackendClient _backendClient;
    private readonly string _engineId;
    private readonly EngineCapabilities _capabilities;

    public string Id => _engineId;
    public string Name { get; private set; }
    public string Version { get; private set; } = "1.0";
    public EngineCapabilities Capabilities => _capabilities;

    public BackendEngineAdapter(IBackendClient backendClient, string engineId, string name, EngineCapabilities capabilities)
    {
      _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));
      _engineId = engineId ?? throw new ArgumentNullException(nameof(engineId));
      Name = name ?? engineId;
      _capabilities = capabilities;
    }

    public async Task InitializeAsync(CancellationToken cancellationToken = default)
    {
      // Call backend to start/warmup the engine
      // POST /api/engines/{id}/start
      await _backendClient.SendRequestAsync<object, object>(
          $"/api/engines/{_engineId}/start",
          null,
          HttpMethod.Post,
          cancellationToken);
    }

    public async Task ShutdownAsync(CancellationToken cancellationToken = default)
    {
      // POST /api/engines/{id}/stop
      await _backendClient.SendRequestAsync<object, object>(
          $"/api/engines/{_engineId}/stop",
          null,
          HttpMethod.Post,
          cancellationToken);
    }

    public async Task<bool> IsAvailableAsync(CancellationToken cancellationToken = default)
    {
      try
      {
        // GET /api/engines/{id}/status
        // Assuming status endpoint returns a JSON with "state" or similar
        var status = await _backendClient.SendRequestAsync<object, Dictionary<string, object>>(
            $"/api/engines/{_engineId}/status",
            null,
            HttpMethod.Get,
            cancellationToken);

        if (status != null && status.TryGetValue("state", out var stateObj))
        {
          var state = stateObj.ToString()?.ToLowerInvariant();
          return state == "healthy" || state == "running" || state == "idle";
        }
        return false;
      }
      catch
      {
        return false;
      }
    }

        // ITextToSpeechEngine implementation
        public async Task<IEnumerable<VoiceProfile>> GetVoicesAsync(CancellationToken cancellationToken = default)
        {
            if (!Capabilities.HasFlag(EngineCapabilities.TextToSpeech))
                throw new NotSupportedException($"Engine {_engineId} does not support TTS.");

            // GET /api/engines/{id}/voices
            return await _backendClient.SendRequestAsync<object, List<VoiceProfile>>(
                $"/api/engines/{_engineId}/voices",
                null,
                HttpMethod.Get,
                cancellationToken) ?? new List<VoiceProfile>();
        }

    public async Task<AudioClip> SynthesizeAsync(VoiceSynthesisRequest request, CancellationToken cancellationToken = default)
    {
      if (!Capabilities.HasFlag(EngineCapabilities.TextToSpeech))
        throw new NotSupportedException($"Engine {_engineId} does not support TTS.");

      request.Engine = _engineId;

      // POST /api/voice/synthesize
      // The backend returns VoiceSynthesisResponse, we need to map to AudioClip
      var response = await _backendClient.SendRequestAsync<VoiceSynthesisRequest, VoiceSynthesisResponse>(
          "/api/voice/synthesize",
          request,
          HttpMethod.Post,
          cancellationToken);

      if (response == null)
        throw new Exception("Synthesis returned null response.");

      return new AudioClip
      {
        Id = Guid.NewGuid().ToString(),
        Name = $"Synthesis - {DateTime.Now:HH:mm:ss}",
        AudioId = response.AudioId,
        AudioUrl = response.AudioUrl,
        Duration = TimeSpan.FromSeconds(response.Duration),
        Engine = _engineId,
        QualityScore = response.QualityScore
      };
    }

    // ITranscriptionEngine implementation
    public async Task<TranscriptionResponse> TranscribeAsync(string audioClipId, string? language = null, CancellationToken cancellationToken = default)
    {
      if (!Capabilities.HasFlag(EngineCapabilities.Transcription))
        throw new NotSupportedException($"Engine {_engineId} does not support Transcription.");

      var request = new TranscriptionRequest
      {
        AudioId = audioClipId,
        Engine = _engineId,
        Language = language
      };

      // POST /api/transcribe
      var response = await _backendClient.SendRequestAsync<TranscriptionRequest, TranscriptionResponse>(
          "/api/transcribe",
          request,
          HttpMethod.Post,
          cancellationToken);

      return response ?? throw new Exception("Transcription returned null response.");
    }
  }
}
