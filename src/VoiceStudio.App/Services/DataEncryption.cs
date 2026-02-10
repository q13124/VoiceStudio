// Task 2.4.1: At-rest encryption for sensitive data
// Provides AES-256-GCM encryption for local data protection

using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Logging;

namespace VoiceStudio.App.Services;

/// <summary>
/// Encrypted data container with all required metadata.
/// </summary>
public record EncryptedData
{
    public byte[] Ciphertext { get; init; } = Array.Empty<byte>();
    public byte[] Nonce { get; init; } = Array.Empty<byte>();
    public byte[] Tag { get; init; } = Array.Empty<byte>();
    public byte[] Salt { get; init; } = Array.Empty<byte>();
    
    /// <summary>
    /// Serialize to bytes for storage.
    /// </summary>
    public byte[] ToBytes()
    {
        using var ms = new MemoryStream();
        using var writer = new BinaryWriter(ms);
        
        writer.Write((byte)Salt.Length);
        writer.Write(Salt);
        writer.Write((byte)Nonce.Length);
        writer.Write(Nonce);
        writer.Write((byte)Tag.Length);
        writer.Write(Tag);
        writer.Write(Ciphertext.Length);
        writer.Write(Ciphertext);
        
        return ms.ToArray();
    }
    
    /// <summary>
    /// Deserialize from bytes.
    /// </summary>
    public static EncryptedData FromBytes(byte[] data)
    {
        using var ms = new MemoryStream(data);
        using var reader = new BinaryReader(ms);
        
        var saltLen = reader.ReadByte();
        var salt = reader.ReadBytes(saltLen);
        
        var nonceLen = reader.ReadByte();
        var nonce = reader.ReadBytes(nonceLen);
        
        var tagLen = reader.ReadByte();
        var tag = reader.ReadBytes(tagLen);
        
        var ciphertextLen = reader.ReadInt32();
        var ciphertext = reader.ReadBytes(ciphertextLen);
        
        return new EncryptedData
        {
            Salt = salt,
            Nonce = nonce,
            Tag = tag,
            Ciphertext = ciphertext
        };
    }
    
    /// <summary>
    /// Convert to Base64 string for text storage.
    /// </summary>
    public string ToBase64() => Convert.ToBase64String(ToBytes());
    
    /// <summary>
    /// Parse from Base64 string.
    /// </summary>
    public static EncryptedData FromBase64(string base64) => 
        FromBytes(Convert.FromBase64String(base64));
}

/// <summary>
/// AES-256-GCM encryption service for sensitive data.
/// </summary>
public class DataEncryptionService : IDisposable
{
    private const int SaltSize = 32;
    private const int NonceSize = 12; // AES-GCM standard
    private const int TagSize = 16;
    private const int KeySize = 32; // 256 bits
    private const int Iterations = 100000;
    
    private readonly ILogger<DataEncryptionService>? _logger;
    private readonly byte[] _masterKey;
    private bool _disposed;
    
    /// <summary>
    /// Initialize with a master key.
    /// </summary>
    public DataEncryptionService(byte[]? masterKey = null, ILogger<DataEncryptionService>? logger = null)
    {
        _logger = logger;
        _masterKey = masterKey ?? GetOrCreateMasterKey();
    }
    
    private static byte[] GetOrCreateMasterKey()
    {
        // Try to get from environment
        var keyEnv = Environment.GetEnvironmentVariable("VOICESTUDIO_ENCRYPTION_KEY");
        if (!string.IsNullOrEmpty(keyEnv))
        {
            return Convert.FromBase64String(keyEnv);
        }
        
        // Generate a new key (for development only)
        var key = new byte[KeySize];
        RandomNumberGenerator.Fill(key);
        return key;
    }
    
    /// <summary>
    /// Derive an encryption key from master key and salt.
    /// </summary>
    private byte[] DeriveKey(byte[] salt)
    {
        using var pbkdf2 = new Rfc2898DeriveBytes(
            _masterKey,
            salt,
            Iterations,
            HashAlgorithmName.SHA256);
        return pbkdf2.GetBytes(KeySize);
    }
    
    /// <summary>
    /// Encrypt plaintext bytes.
    /// </summary>
    public EncryptedData Encrypt(byte[] plaintext)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        
        var salt = new byte[SaltSize];
        var nonce = new byte[NonceSize];
        RandomNumberGenerator.Fill(salt);
        RandomNumberGenerator.Fill(nonce);
        
        var key = DeriveKey(salt);
        
        var ciphertext = new byte[plaintext.Length];
        var tag = new byte[TagSize];
        
        using var aes = new AesGcm(key, TagSize);
        aes.Encrypt(nonce, plaintext, ciphertext, tag);
        
        _logger?.LogDebug("Encrypted {Bytes} bytes of data", plaintext.Length);
        
        return new EncryptedData
        {
            Ciphertext = ciphertext,
            Nonce = nonce,
            Tag = tag,
            Salt = salt
        };
    }
    
    /// <summary>
    /// Encrypt a string.
    /// </summary>
    public EncryptedData Encrypt(string plaintext)
    {
        return Encrypt(Encoding.UTF8.GetBytes(plaintext));
    }
    
    /// <summary>
    /// Encrypt an object as JSON.
    /// </summary>
    public EncryptedData EncryptObject<T>(T obj)
    {
        var json = JsonSerializer.Serialize(obj);
        return Encrypt(json);
    }
    
    /// <summary>
    /// Decrypt to bytes.
    /// </summary>
    public byte[] Decrypt(EncryptedData encrypted)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        
        var key = DeriveKey(encrypted.Salt);
        var plaintext = new byte[encrypted.Ciphertext.Length];
        
        using var aes = new AesGcm(key, TagSize);
        aes.Decrypt(encrypted.Nonce, encrypted.Ciphertext, encrypted.Tag, plaintext);
        
        _logger?.LogDebug("Decrypted {Bytes} bytes of data", plaintext.Length);
        
        return plaintext;
    }
    
    /// <summary>
    /// Decrypt to string.
    /// </summary>
    public string DecryptToString(EncryptedData encrypted)
    {
        return Encoding.UTF8.GetString(Decrypt(encrypted));
    }
    
    /// <summary>
    /// Decrypt to object.
    /// </summary>
    public T? DecryptObject<T>(EncryptedData encrypted)
    {
        var json = DecryptToString(encrypted);
        return JsonSerializer.Deserialize<T>(json);
    }
    
    /// <summary>
    /// Encrypt a file.
    /// </summary>
    public async Task EncryptFileAsync(string inputPath, string outputPath, CancellationToken ct = default)
    {
        var plaintext = await File.ReadAllBytesAsync(inputPath, ct);
        var encrypted = Encrypt(plaintext);
        await File.WriteAllBytesAsync(outputPath, encrypted.ToBytes(), ct);
        _logger?.LogInformation("Encrypted file: {Input} -> {Output}", inputPath, outputPath);
    }
    
    /// <summary>
    /// Decrypt a file.
    /// </summary>
    public async Task DecryptFileAsync(string inputPath, string outputPath, CancellationToken ct = default)
    {
        var encryptedBytes = await File.ReadAllBytesAsync(inputPath, ct);
        var encrypted = EncryptedData.FromBytes(encryptedBytes);
        var plaintext = Decrypt(encrypted);
        await File.WriteAllBytesAsync(outputPath, plaintext, ct);
        _logger?.LogInformation("Decrypted file: {Input} -> {Output}", inputPath, outputPath);
    }
    
    /// <summary>
    /// Generate a secure random key encoded as Base64.
    /// </summary>
    public static string GenerateKey()
    {
        var key = new byte[KeySize];
        RandomNumberGenerator.Fill(key);
        return Convert.ToBase64String(key);
    }
    
    public void Dispose()
    {
        if (!_disposed)
        {
            // Clear master key from memory
            Array.Clear(_masterKey, 0, _masterKey.Length);
            _disposed = true;
        }
        GC.SuppressFinalize(this);
    }
}
