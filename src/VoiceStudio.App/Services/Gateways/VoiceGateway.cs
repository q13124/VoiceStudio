using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Gateways;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services.Gateways
{
  /// <summary>
  /// Gateway implementation for voice synthesis, cloning, and analysis operations.
  /// Delegates to IBackendTransport for HTTP operations.
  /// </summary>
  public sealed class VoiceGateway : IVoiceGateway
  {
    private readonly IBackendTransport _transport;

    public VoiceGateway(IBackendTransport transport)
    {
      _transport = transport ?? throw new ArgumentNullException(nameof(transport));
    }

    public async Task<GatewayResult<VoiceSynthesisResult>> SynthesizeAsync(
        VoiceSynthesisRequest request,
        CancellationToken cancellationToken = default)
    {
      var apiRequest = new
      {
        text = request.Text,
        voice_id = request.VoiceId,
        profile_id = request.ProfileId,
        engine_id = request.EngineId,
        language = request.Language,
        speed = request.Speed,
        pitch = request.Pitch,
        parameters = request.EngineParameters
      };

      return await _transport.PostAsync<object, VoiceSynthesisResult>(
          "/api/voice/synthesize",
          apiRequest,
          cancellationToken);
    }

    public async Task<GatewayResult<bool>> SynthesizeStreamAsync(
        VoiceSynthesisRequest request,
        Stream outputStream,
        CancellationToken cancellationToken = default)
    {
      // For streaming synthesis, we use the stream endpoint
      var path = $"/api/voice/synthesize/stream?text={Uri.EscapeDataString(request.Text)}";
      if (!string.IsNullOrEmpty(request.VoiceId))
        path += $"&voice_id={Uri.EscapeDataString(request.VoiceId)}";
      if (!string.IsNullOrEmpty(request.EngineId))
        path += $"&engine_id={Uri.EscapeDataString(request.EngineId)}";

      var streamResult = await _transport.GetStreamAsync(path, cancellationToken);
      if (!streamResult.Success)
      {
        return GatewayResult<bool>.Fail(streamResult.Error!, streamResult.CorrelationId);
      }

      try
      {
        if (streamResult.Data is not null)
        {
          await streamResult.Data.CopyToAsync(outputStream, cancellationToken);
        }
        return GatewayResult<bool>.Ok(true, streamResult.CorrelationId);
      }
      finally
      {
        if (streamResult.Data is IDisposable disposable)
        {
          disposable.Dispose();
        }
      }
    }

    public async Task<GatewayResult<VoiceCloneResult>> CloneVoiceAsync(
        VoiceCloneRequest request,
        CancellationToken cancellationToken = default)
    {
      var apiRequest = new
      {
        name = request.Name,
        audio_sample_paths = request.AudioSamplePaths,
        description = request.Description,
        engine_id = request.EngineId
      };

      return await _transport.PostAsync<object, VoiceCloneResult>(
          "/api/voice/clone",
          apiRequest,
          cancellationToken);
    }

    public async Task<GatewayResult<VoiceAnalysisResult>> AnalyzeAsync(
        string audioPath,
        CancellationToken cancellationToken = default)
    {
      var apiRequest = new { audio_path = audioPath };
      return await _transport.PostAsync<object, VoiceAnalysisResult>(
          "/api/voice/analyze",
          apiRequest,
          cancellationToken);
    }

    public async Task<GatewayResult<IReadOnlyList<VoiceInfo>>> GetAvailableVoicesAsync(
        string? engineId = null,
        CancellationToken cancellationToken = default)
    {
      var path = "/api/voice/voices";
      if (!string.IsNullOrEmpty(engineId))
        path += $"?engine_id={Uri.EscapeDataString(engineId)}";

      return await _transport.GetAsync<IReadOnlyList<VoiceInfo>>(path, cancellationToken);
    }
  }
}
