// Task 2.4.3: Secure credential storage using Windows DPAPI
// Provides secure storage for API keys, tokens, and sensitive settings

using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Logging;
using Windows.Security.Credentials;

namespace VoiceStudio.App.Services;

/// <summary>
/// Secure storage for sensitive data using Windows Credential Manager and DPAPI.
/// </summary>
public class SecureStorageService
{
    private const string ResourceName = "VoiceStudio";
    private const string EncryptedStorePath = "data/secure";
    
    private readonly ILogger<SecureStorageService>? _logger;
    private readonly string _storagePath;
    
    public SecureStorageService(ILogger<SecureStorageService>? logger = null, string? customPath = null)
    {
        _logger = logger;
        _storagePath = customPath ?? Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "VoiceStudio",
            EncryptedStorePath);
        
        Directory.CreateDirectory(_storagePath);
    }
    
    #region Windows Credential Manager (for API keys/tokens)
    
    /// <summary>
    /// Store a credential in Windows Credential Manager.
    /// </summary>
    public bool StoreCredential(string key, string value)
    {
        try
        {
            var vault = new PasswordVault();
            
            // Remove existing if present
            try
            {
                var existing = vault.Retrieve(ResourceName, key);
                vault.Remove(existing);
            }
            // ALLOWED: empty catch - credential doesn't exist is expected when storing new
            catch (Exception)
            {
            }
            
            vault.Add(new PasswordCredential(ResourceName, key, value));
            _logger?.LogDebug("Stored credential: {Key}", key);
            return true;
        }
        catch (Exception ex)
        {
            _logger?.LogError(ex, "Failed to store credential: {Key}", key);
            return false;
        }
    }
    
    /// <summary>
    /// Retrieve a credential from Windows Credential Manager.
    /// </summary>
    public string? GetCredential(string key)
    {
        try
        {
            var vault = new PasswordVault();
            var credential = vault.Retrieve(ResourceName, key);
            credential.RetrievePassword();
            return credential.Password;
        }
        catch (Exception)
        {
            return null;
        }
    }
    
    /// <summary>
    /// Remove a credential from Windows Credential Manager.
    /// </summary>
    public bool RemoveCredential(string key)
    {
        try
        {
            var vault = new PasswordVault();
            var credential = vault.Retrieve(ResourceName, key);
            vault.Remove(credential);
            _logger?.LogDebug("Removed credential: {Key}", key);
            return true;
        }
        catch (Exception)
        {
            return false;
        }
    }
    
    /// <summary>
    /// List all stored credential keys.
    /// </summary>
    public IEnumerable<string> ListCredentials()
    {
        try
        {
            var vault = new PasswordVault();
            return vault.FindAllByResource(ResourceName)
                       .Select(c => c.UserName)
                       .ToList();
        }
        catch (Exception)
        {
            return Enumerable.Empty<string>();
        }
    }
    
    #endregion
    
    #region DPAPI Protected Storage (for larger data)
    
    /// <summary>
    /// Store data protected with DPAPI (user scope).
    /// </summary>
    public async Task<bool> StoreProtectedAsync(string key, byte[] data, CancellationToken ct = default)
    {
        try
        {
            var protectedData = ProtectedData.Protect(
                data,
                GetEntropy(key),
                DataProtectionScope.CurrentUser);
            
            var filePath = GetStoragePath(key);
            await File.WriteAllBytesAsync(filePath, protectedData, ct);
            
            _logger?.LogDebug("Stored protected data: {Key}", key);
            return true;
        }
        catch (Exception ex)
        {
            _logger?.LogError(ex, "Failed to store protected data: {Key}", key);
            return false;
        }
    }
    
    /// <summary>
    /// Store a string protected with DPAPI.
    /// </summary>
    public Task<bool> StoreProtectedAsync(string key, string value, CancellationToken ct = default)
    {
        return StoreProtectedAsync(key, Encoding.UTF8.GetBytes(value), ct);
    }
    
    /// <summary>
    /// Store an object as JSON protected with DPAPI.
    /// </summary>
    public Task<bool> StoreProtectedObjectAsync<T>(string key, T obj, CancellationToken ct = default)
    {
        var json = JsonSerializer.Serialize(obj);
        return StoreProtectedAsync(key, json, ct);
    }
    
    /// <summary>
    /// Retrieve DPAPI protected data.
    /// </summary>
    public async Task<byte[]?> GetProtectedAsync(string key, CancellationToken ct = default)
    {
        try
        {
            var filePath = GetStoragePath(key);
            if (!File.Exists(filePath))
                return null;
            
            var protectedData = await File.ReadAllBytesAsync(filePath, ct);
            
            return ProtectedData.Unprotect(
                protectedData,
                GetEntropy(key),
                DataProtectionScope.CurrentUser);
        }
        catch (Exception ex)
        {
            _logger?.LogError(ex, "Failed to retrieve protected data: {Key}", key);
            return null;
        }
    }
    
    /// <summary>
    /// Retrieve DPAPI protected string.
    /// </summary>
    public async Task<string?> GetProtectedStringAsync(string key, CancellationToken ct = default)
    {
        var data = await GetProtectedAsync(key, ct);
        return data == null ? null : Encoding.UTF8.GetString(data);
    }
    
    /// <summary>
    /// Retrieve DPAPI protected object.
    /// </summary>
    public async Task<T?> GetProtectedObjectAsync<T>(string key, CancellationToken ct = default)
    {
        var json = await GetProtectedStringAsync(key, ct);
        return json == null ? default : JsonSerializer.Deserialize<T>(json);
    }
    
    /// <summary>
    /// Remove protected data.
    /// </summary>
    public bool RemoveProtected(string key)
    {
        try
        {
            var filePath = GetStoragePath(key);
            if (File.Exists(filePath))
            {
                File.Delete(filePath);
                _logger?.LogDebug("Removed protected data: {Key}", key);
                return true;
            }
            return false;
        }
        catch (Exception ex)
        {
            _logger?.LogError(ex, "Failed to remove protected data: {Key}", key);
            return false;
        }
    }
    
    #endregion
    
    #region Helper Methods
    
    private string GetStoragePath(string key)
    {
        // Sanitize key for filename
        var safeName = string.Join("_", key.Split(Path.GetInvalidFileNameChars()));
        return Path.Combine(_storagePath, $"{safeName}.protected");
    }
    
    private static byte[] GetEntropy(string key)
    {
        // Use key-specific entropy for additional security
        using var sha = SHA256.Create();
        return sha.ComputeHash(Encoding.UTF8.GetBytes($"VoiceStudio:{key}"));
    }
    
    /// <summary>
    /// Securely wipe sensitive data from memory.
    /// </summary>
    public static void SecureWipe(byte[] data)
    {
        if (data != null)
        {
            Array.Clear(data, 0, data.Length);
        }
    }
    
    /// <summary>
    /// Check if DPAPI is available.
    /// </summary>
    public static bool IsDpapiAvailable()
    {
        try
        {
            var testData = Encoding.UTF8.GetBytes("test");
            var encrypted = ProtectedData.Protect(testData, null, DataProtectionScope.CurrentUser);
            var decrypted = ProtectedData.Unprotect(encrypted, null, DataProtectionScope.CurrentUser);
            return testData.SequenceEqual(decrypted);
        }
        catch
        {
            return false;
        }
    }
    
    #endregion
}

/// <summary>
/// Extension methods for secure storage integration.
/// </summary>
public static class SecureStorageExtensions
{
    /// <summary>
    /// Store an API key securely.
    /// </summary>
    public static bool StoreApiKey(this SecureStorageService storage, string provider, string apiKey)
    {
        return storage.StoreCredential($"apikey:{provider}", apiKey);
    }
    
    /// <summary>
    /// Get a stored API key.
    /// </summary>
    public static string? GetApiKey(this SecureStorageService storage, string provider)
    {
        return storage.GetCredential($"apikey:{provider}");
    }
    
    /// <summary>
    /// Store an OAuth token securely.
    /// </summary>
    public static async Task<bool> StoreOAuthTokenAsync(
        this SecureStorageService storage,
        string provider,
        object token,
        CancellationToken ct = default)
    {
        return await storage.StoreProtectedObjectAsync($"oauth:{provider}", token, ct);
    }
    
    /// <summary>
    /// Get a stored OAuth token.
    /// </summary>
    public static async Task<T?> GetOAuthTokenAsync<T>(
        this SecureStorageService storage,
        string provider,
        CancellationToken ct = default)
    {
        return await storage.GetProtectedObjectAsync<T>($"oauth:{provider}", ct);
    }
}
