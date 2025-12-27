using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Windows.Storage;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Secrets service implementation using encrypted dev vault file for development.
    /// </summary>
    public class DevVaultSecretsService : ISecretsService
    {
        private const string VaultFileName = "dev_vault.json";
        private const string VaultKeyFileName = "dev_vault.key";
        private readonly Dictionary<string, string> _cache = new();
        private readonly string _vaultPath;
        private readonly string _vaultKeyPath;
        private byte[]? _encryptionKey;

        public DevVaultSecretsService()
        {
            var localFolder = ApplicationData.Current.LocalFolder.Path;
            _vaultPath = Path.Combine(localFolder, VaultFileName);
            _vaultKeyPath = Path.Combine(localFolder, VaultKeyFileName);
        }

        private async Task<byte[]> GetOrCreateEncryptionKeyAsync()
        {
            if (_encryptionKey != null)
                return _encryptionKey;

            // Try to load existing key
            if (File.Exists(_vaultKeyPath))
            {
                var keyBytes = await File.ReadAllBytesAsync(_vaultKeyPath);
                if (keyBytes.Length == 32) // AES-256 key size
                {
                    _encryptionKey = keyBytes;
                    return _encryptionKey;
                }
            }

            // Generate new key
            using var rng = RandomNumberGenerator.Create();
            _encryptionKey = new byte[32];
            rng.GetBytes(_encryptionKey);

            // Save key
            await File.WriteAllBytesAsync(_vaultKeyPath, _encryptionKey);

            return _encryptionKey;
        }

        private async Task<Dictionary<string, string>> LoadVaultAsync()
        {
            if (!File.Exists(_vaultPath))
                return new Dictionary<string, string>();

            try
            {
                var encryptedData = await File.ReadAllBytesAsync(_vaultPath);
                var key = await GetOrCreateEncryptionKeyAsync();

                // Decrypt
                using var aes = Aes.Create();
                aes.Key = key;
                aes.Mode = CipherMode.CBC;
                aes.Padding = PaddingMode.PKCS7;

                // Extract IV (first 16 bytes)
                var iv = new byte[16];
                Array.Copy(encryptedData, 0, iv, 0, 16);
                aes.IV = iv;

                // Decrypt the rest
                var cipherText = new byte[encryptedData.Length - 16];
                Array.Copy(encryptedData, 16, cipherText, 0, cipherText.Length);

                using var decryptor = aes.CreateDecryptor();
                var plainText = decryptor.TransformFinalBlock(cipherText, 0, cipherText.Length);

                var json = Encoding.UTF8.GetString(plainText);
                var vault = JsonSerializer.Deserialize<Dictionary<string, string>>(json);
                return vault ?? new Dictionary<string, string>();
            }
            catch
            {
                return new Dictionary<string, string>();
            }
        }

        private async Task SaveVaultAsync(Dictionary<string, string> vault)
        {
            try
            {
                var json = JsonSerializer.Serialize(vault);
                var plainText = Encoding.UTF8.GetBytes(json);
                var key = await GetOrCreateEncryptionKeyAsync();

                // Encrypt
                using var aes = Aes.Create();
                aes.Key = key;
                aes.Mode = CipherMode.CBC;
                aes.Padding = PaddingMode.PKCS7;
                aes.GenerateIV();

                using var encryptor = aes.CreateEncryptor();
                var cipherText = encryptor.TransformFinalBlock(plainText, 0, plainText.Length);

                // Prepend IV
                var encryptedData = new byte[16 + cipherText.Length];
                Array.Copy(aes.IV, 0, encryptedData, 0, 16);
                Array.Copy(cipherText, 0, encryptedData, 16, cipherText.Length);

                await File.WriteAllBytesAsync(_vaultPath, encryptedData);
            }
            catch
            {
                // If saving fails, continue without persistence
            }
        }

        public async Task<string?> GetSecretAsync(string key, string? defaultValue = null, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(key))
                return defaultValue;

            // Check cache first
            if (_cache.TryGetValue(key, out var cachedValue))
                return cachedValue;

            // Try environment variable first (highest priority)
            var envKey = key.ToUpperInvariant().Replace("-", "_");
            var envValue = Environment.GetEnvironmentVariable(envKey) ?? Environment.GetEnvironmentVariable(key);
            if (!string.IsNullOrEmpty(envValue))
            {
                _cache[key] = envValue;
                return envValue;
            }

            // Try dev vault
            var vault = await LoadVaultAsync();
            if (vault.TryGetValue(key, out var vaultValue))
            {
                _cache[key] = vaultValue;
                return vaultValue;
            }

            // Return default value
            return defaultValue;
        }

        public async Task<bool> SetSecretAsync(string key, string value, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(key))
                return false;

            // Update cache
            _cache[key] = value;

            // Store in dev vault
            var vault = await LoadVaultAsync();
            vault[key] = value;
            await SaveVaultAsync(vault);

            return true;
        }

        public async Task<bool> DeleteSecretAsync(string key, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(key))
                return false;

            // Remove from cache
            _cache.Remove(key);

            // Remove from dev vault
            var vault = await LoadVaultAsync();
            if (vault.Remove(key))
            {
                await SaveVaultAsync(vault);
                return true;
            }

            return false;
        }

        public async Task<IReadOnlyList<string>> ListSecretsAsync(CancellationToken cancellationToken = default)
        {
            var vault = await LoadVaultAsync();
            return vault.Keys.ToList().AsReadOnly();
        }

        public async Task<bool> SecretExistsAsync(string key, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(key))
                return false;

            // Check cache
            if (_cache.ContainsKey(key))
                return true;

            // Check environment variable
            var envKey = key.ToUpperInvariant().Replace("-", "_");
            if (!string.IsNullOrEmpty(Environment.GetEnvironmentVariable(envKey)) ||
                !string.IsNullOrEmpty(Environment.GetEnvironmentVariable(key)))
            {
                return true;
            }

            // Check dev vault
            var vault = await LoadVaultAsync();
            return vault.ContainsKey(key);
        }
    }
}
