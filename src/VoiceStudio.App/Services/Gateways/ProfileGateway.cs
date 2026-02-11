using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Gateways;

namespace VoiceStudio.App.Services.Gateways
{
  /// <summary>
  /// Gateway implementation for voice profile CRUD operations.
  /// </summary>
  public sealed class ProfileGateway : IProfileGateway
  {
    private readonly IBackendTransport _transport;

    public ProfileGateway(IBackendTransport transport)
    {
      _transport = transport ?? throw new ArgumentNullException(nameof(transport));
    }

    public async Task<GatewayResult<IReadOnlyList<ProfileInfo>>> GetAllAsync(
        CancellationToken cancellationToken = default)
    {
      return await _transport.GetAsync<IReadOnlyList<ProfileInfo>>(
          "/api/profiles",
          cancellationToken);
    }

    public async Task<GatewayResult<ProfileDetail>> GetByIdAsync(
        string profileId,
        CancellationToken cancellationToken = default)
    {
      return await _transport.GetAsync<ProfileDetail>(
          $"/api/profiles/{Uri.EscapeDataString(profileId)}",
          cancellationToken);
    }

    public async Task<GatewayResult<ProfileDetail>> CreateAsync(
        ProfileCreateRequest request,
        CancellationToken cancellationToken = default)
    {
      return await _transport.PostAsync<ProfileCreateRequest, ProfileDetail>(
          "/api/profiles",
          request,
          cancellationToken);
    }

    public async Task<GatewayResult<ProfileDetail>> UpdateAsync(
        string profileId,
        ProfileUpdateRequest request,
        CancellationToken cancellationToken = default)
    {
      return await _transport.PutAsync<ProfileUpdateRequest, ProfileDetail>(
          $"/api/profiles/{Uri.EscapeDataString(profileId)}",
          request,
          cancellationToken);
    }

    public async Task<GatewayResult<bool>> DeleteAsync(
        string profileId,
        CancellationToken cancellationToken = default)
    {
      return await _transport.DeleteAsync(
          $"/api/profiles/{Uri.EscapeDataString(profileId)}",
          cancellationToken);
    }

    public async Task<GatewayResult<bool>> ExportAsync(
        string profileId,
        Stream outputStream,
        CancellationToken cancellationToken = default)
    {
      return await _transport.DownloadAsync(
          $"/api/profiles/{Uri.EscapeDataString(profileId)}/export",
          outputStream,
          cancellationToken: cancellationToken);
    }

    public async Task<GatewayResult<ProfileDetail>> ImportAsync(
        Stream inputStream,
        string fileName,
        CancellationToken cancellationToken = default)
    {
      return await _transport.UploadAsync<ProfileDetail>(
          "/api/profiles/import",
          inputStream,
          fileName,
          cancellationToken: cancellationToken);
    }

    public async Task<GatewayResult<ProfileDetail?>> GetDefaultAsync(
        CancellationToken cancellationToken = default)
    {
      return await _transport.GetAsync<ProfileDetail?>(
          "/api/profiles/default",
          cancellationToken);
    }

    public async Task<GatewayResult<bool>> SetDefaultAsync(
        string profileId,
        CancellationToken cancellationToken = default)
    {
      return await _transport.PostAsync(
          $"/api/profiles/{Uri.EscapeDataString(profileId)}/set-default",
          new { },
          cancellationToken);
    }
  }
}
