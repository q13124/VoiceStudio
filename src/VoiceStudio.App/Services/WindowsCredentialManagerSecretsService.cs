using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Secrets service implementation using Windows Credential Manager for production.
  /// </summary>
  public class WindowsCredentialManagerSecretsService : ISecretsService
  {
    private const string ServiceName = "VoiceStudio";
    private readonly Dictionary<string, string> _cache = new();

    // Windows Credential Manager P/Invoke declarations
    [DllImport("advapi32.dll", EntryPoint = "CredReadW", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool CredRead(string target, int type, int reservedFlag, out IntPtr credentialPtr);

    [DllImport("advapi32.dll", EntryPoint = "CredWriteW", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool CredWrite(ref Credential credential, int flags);

    [DllImport("advapi32.dll", EntryPoint = "CredDeleteW", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool CredDelete(string target, int type, int reservedFlag);

    [DllImport("advapi32.dll", SetLastError = true)]
    private static extern void CredFree(IntPtr buffer);

    private const int CRED_TYPE_GENERIC = 1;
    private const int CRED_PERSIST_LOCAL_MACHINE = 2;

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private struct Credential
    {
      public int Flags;
      public int Type;
      public string TargetName;
      public string Comment;
      public System.Runtime.InteropServices.ComTypes.FILETIME LastWritten;
      public int CredentialBlobSize;
      public IntPtr CredentialBlob;
      public int Persist;
      public int AttributeCount;
      public IntPtr Attributes;
      public string TargetAlias;
      public string UserName;
    }

    public Task<string?> GetSecretAsync(string key, string? defaultValue = null, CancellationToken cancellationToken = default)
    {
      cancellationToken.ThrowIfCancellationRequested();

      if (string.IsNullOrWhiteSpace(key))
        return Task.FromResult(defaultValue);

      // Check cache first
      if (_cache.TryGetValue(key, out var cachedValue))
        return Task.FromResult<string?>(cachedValue);

      // Try environment variable first (highest priority)
      var envKey = key.ToUpperInvariant().Replace("-", "_");
      var envValue = Environment.GetEnvironmentVariable(envKey) ?? Environment.GetEnvironmentVariable(key);
      if (!string.IsNullOrEmpty(envValue))
      {
        _cache[key] = envValue;
        return Task.FromResult<string?>(envValue);
      }

      // Try Windows Credential Manager
      var credentialTarget = $"{ServiceName}:{key}";
      if (CredRead(credentialTarget, CRED_TYPE_GENERIC, 0, out var credentialPtr))
      {
        try
        {
          var credential = Marshal.PtrToStructure<Credential>(credentialPtr);
          if (credential.CredentialBlobSize > 0 && credential.CredentialBlob != IntPtr.Zero)
          {
            var secretBytes = new byte[credential.CredentialBlobSize];
            Marshal.Copy(credential.CredentialBlob, secretBytes, 0, credential.CredentialBlobSize);
            var secretValue = Encoding.UTF8.GetString(secretBytes);
            _cache[key] = secretValue;
            return Task.FromResult<string?>(secretValue);
          }
        }
        finally
        {
          CredFree(credentialPtr);
        }
      }

      // Return default value
      return Task.FromResult(defaultValue);
    }

    public Task<bool> SetSecretAsync(string key, string value, CancellationToken cancellationToken = default)
    {
      cancellationToken.ThrowIfCancellationRequested();

      if (string.IsNullOrWhiteSpace(key))
        return Task.FromResult(false);

      // Update cache
      _cache[key] = value;

      // Store in Windows Credential Manager
      var credentialTarget = $"{ServiceName}:{key}";
      var secretBytes = Encoding.UTF8.GetBytes(value);

      var credential = new Credential
      {
        Type = CRED_TYPE_GENERIC,
        TargetName = credentialTarget,
        CredentialBlobSize = secretBytes.Length,
        CredentialBlob = Marshal.AllocCoTaskMem(secretBytes.Length),
        Persist = CRED_PERSIST_LOCAL_MACHINE,
        UserName = Environment.UserName
      };

      try
      {
        Marshal.Copy(secretBytes, 0, credential.CredentialBlob, secretBytes.Length);
        var result = CredWrite(ref credential, 0);
        return Task.FromResult(result);
      }
      catch
      {
        return Task.FromResult(false);
      }
      finally
      {
        if (credential.CredentialBlob != IntPtr.Zero)
        {
          Marshal.FreeCoTaskMem(credential.CredentialBlob);
        }
      }
    }

    public Task<bool> DeleteSecretAsync(string key, CancellationToken cancellationToken = default)
    {
      cancellationToken.ThrowIfCancellationRequested();

      if (string.IsNullOrWhiteSpace(key))
        return Task.FromResult(false);

      // Remove from cache
      _cache.Remove(key);

      // Delete from Windows Credential Manager
      var credentialTarget = $"{ServiceName}:{key}";
      var result = CredDelete(credentialTarget, CRED_TYPE_GENERIC, 0);
      return Task.FromResult(result);
    }

    public Task<IReadOnlyList<string>> ListSecretsAsync(CancellationToken cancellationToken = default)
    {
      cancellationToken.ThrowIfCancellationRequested();

      // Note: Windows Credential Manager doesn't support enumeration
      // We can only return cached keys
      return Task.FromResult((IReadOnlyList<string>)_cache.Keys.ToList().AsReadOnly());
    }

    public Task<bool> SecretExistsAsync(string key, CancellationToken cancellationToken = default)
    {
      cancellationToken.ThrowIfCancellationRequested();

      if (string.IsNullOrWhiteSpace(key))
        return Task.FromResult(false);

      // Check cache
      if (_cache.ContainsKey(key))
        return Task.FromResult(true);

      // Check environment variable
      var envKey = key.ToUpperInvariant().Replace("-", "_");
      if (!string.IsNullOrEmpty(Environment.GetEnvironmentVariable(envKey)) ||
          !string.IsNullOrEmpty(Environment.GetEnvironmentVariable(key)))
      {
        return Task.FromResult(true);
      }

      // Check Windows Credential Manager
      var credentialTarget = $"{ServiceName}:{key}";
      if (CredRead(credentialTarget, CRED_TYPE_GENERIC, 0, out var credentialPtr))
      {
        CredFree(credentialPtr);
        return Task.FromResult(true);
      }

      return Task.FromResult(false);
    }
  }
}
