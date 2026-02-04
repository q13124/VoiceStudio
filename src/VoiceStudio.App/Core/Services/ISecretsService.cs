using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Services
{
  /// <summary>
  /// Service for managing secrets securely using Windows Credential Manager (production) or dev vault (development).
  /// </summary>
  public interface ISecretsService
  {
    /// <summary>
    /// Gets a secret value by key.
    /// Priority: 1. Environment variable, 2. Credential Manager/Dev Vault, 3. Default value
    /// </summary>
    /// <param name="key">The secret key.</param>
    /// <param name="defaultValue">Optional default value if not found.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The secret value, or default value if not found.</returns>
    Task<string?> GetSecretAsync(string key, string? defaultValue = null, CancellationToken cancellationToken = default);

    /// <summary>
    /// Sets a secret value.
    /// </summary>
    /// <param name="key">The secret key.</param>
    /// <param name="value">The secret value.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>True if successful, false otherwise.</returns>
    Task<bool> SetSecretAsync(string key, string value, CancellationToken cancellationToken = default);

    /// <summary>
    /// Deletes a secret by key.
    /// </summary>
    /// <param name="key">The secret key.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>True if successful, false otherwise.</returns>
    Task<bool> DeleteSecretAsync(string key, CancellationToken cancellationToken = default);

    /// <summary>
    /// Lists all secret keys (Credential Manager/Dev Vault only, env vars not enumerable).
    /// </summary>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>List of secret keys.</returns>
    Task<IReadOnlyList<string>> ListSecretsAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Checks if a secret exists.
    /// </summary>
    /// <param name="key">The secret key.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>True if secret exists, false otherwise.</returns>
    Task<bool> SecretExistsAsync(string key, CancellationToken cancellationToken = default);
  }
}