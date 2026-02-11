using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Gateways;

namespace VoiceStudio.App.Services.Gateways
{
  /// <summary>
  /// Gateway implementation for engine discovery, configuration, and status operations.
  /// </summary>
  public sealed class EngineGateway : IEngineGateway
  {
    private readonly IBackendTransport _transport;

    public EngineGateway(IBackendTransport transport)
    {
      _transport = transport ?? throw new ArgumentNullException(nameof(transport));
    }

    public async Task<GatewayResult<IReadOnlyList<EngineInfo>>> GetAllAsync(
        CancellationToken cancellationToken = default)
    {
      return await _transport.GetAsync<IReadOnlyList<EngineInfo>>(
          "/api/engines",
          cancellationToken);
    }

    public async Task<GatewayResult<EngineDetail>> GetByIdAsync(
        string engineId,
        CancellationToken cancellationToken = default)
    {
      return await _transport.GetAsync<EngineDetail>(
          $"/api/engines/{Uri.EscapeDataString(engineId)}",
          cancellationToken);
    }

    public async Task<GatewayResult<EngineParameterSchema>> GetSchemaAsync(
        string engineId,
        CancellationToken cancellationToken = default)
    {
      return await _transport.GetAsync<EngineParameterSchema>(
          $"/api/engines/{Uri.EscapeDataString(engineId)}/schema",
          cancellationToken);
    }

    public async Task<GatewayResult<VoiceStudio.Core.Gateways.EngineStatus>> GetStatusAsync(
        string engineId,
        CancellationToken cancellationToken = default)
    {
      return await _transport.GetAsync<VoiceStudio.Core.Gateways.EngineStatus>(
          $"/api/engines/{Uri.EscapeDataString(engineId)}/status",
          cancellationToken);
    }

    public async Task<GatewayResult<bool>> SetActiveAsync(
        string engineId,
        CancellationToken cancellationToken = default)
    {
      return await _transport.PostAsync(
          $"/api/engines/{Uri.EscapeDataString(engineId)}/activate",
          new { },
          cancellationToken);
    }

    public async Task<GatewayResult<EngineInfo?>> GetActiveAsync(
        CancellationToken cancellationToken = default)
    {
      return await _transport.GetAsync<EngineInfo?>(
          "/api/engines/active",
          cancellationToken);
    }

    public async Task<GatewayResult<bool>> InitializeAsync(
        string engineId,
        CancellationToken cancellationToken = default)
    {
      return await _transport.PostAsync(
          $"/api/engines/{Uri.EscapeDataString(engineId)}/initialize",
          new { },
          cancellationToken);
    }
  }
}
