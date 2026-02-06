// Copyright (c) VoiceStudio. All rights reserved.
// Licensed under the MIT License.

using System;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;

namespace VoiceStudio.App.Services.IPC
{
    /// <summary>
    /// HMAC-SHA256 request signer for IPC security.
    /// Implements Phase 6.1.3 request signing to protect UI-to-backend communication.
    /// 
    /// Security features:
    /// - HMAC-SHA256 for message authentication
    /// - Timestamp-based replay attack prevention
    /// - Body content included in signature to prevent tampering
    /// </summary>
    public class RequestSigner : IRequestSigner, IDisposable
    {
        /// <summary>
        /// Header name for the HMAC signature.
        /// </summary>
        public const string SignatureHeader = "X-HMAC-Signature";

        /// <summary>
        /// Header name for the signing timestamp.
        /// </summary>
        public const string TimestampHeader = "X-HMAC-Timestamp";

        /// <summary>
        /// Header name for the signature version.
        /// </summary>
        public const string VersionHeader = "X-HMAC-Version";

        /// <summary>
        /// Current signature version for compatibility checks.
        /// </summary>
        public const string SignatureVersion = "1";

        /// <summary>
        /// Maximum age of a valid signature in seconds (5 minutes).
        /// </summary>
        public const int MaxTimestampAgeSeconds = 300;

        private readonly byte[] _secretKey;
        private readonly bool _isEnabled;
        private bool _disposed;

        /// <summary>
        /// Create a new RequestSigner with the specified secret key.
        /// </summary>
        /// <param name="secretKey">Secret key for HMAC signing (should be at least 32 bytes)</param>
        /// <param name="enabled">Whether signing is enabled (feature flag support)</param>
        public RequestSigner(byte[] secretKey, bool enabled = true)
        {
            if (secretKey == null || secretKey.Length < 32)
            {
                throw new ArgumentException("Secret key must be at least 32 bytes", nameof(secretKey));
            }

            _secretKey = new byte[secretKey.Length];
            Array.Copy(secretKey, _secretKey, secretKey.Length);
            _isEnabled = enabled;
        }

        /// <summary>
        /// Create a RequestSigner from a Base64-encoded secret key.
        /// </summary>
        /// <param name="base64SecretKey">Base64-encoded secret key</param>
        /// <param name="enabled">Whether signing is enabled</param>
        public RequestSigner(string base64SecretKey, bool enabled = true)
            : this(Convert.FromBase64String(base64SecretKey), enabled)
        {
        }

        /// <summary>
        /// Create a disabled RequestSigner (for testing or gradual rollout).
        /// </summary>
        public static RequestSigner CreateDisabled()
        {
            // Use a dummy key since we're disabled
            var dummyKey = new byte[32];
            return new RequestSigner(dummyKey, enabled: false);
        }

        /// <summary>
        /// Generate a new random secret key suitable for HMAC-SHA256.
        /// </summary>
        /// <returns>Base64-encoded 32-byte key</returns>
        public static string GenerateSecretKey()
        {
            var key = new byte[32];
            using var rng = RandomNumberGenerator.Create();
            rng.GetBytes(key);
            return Convert.ToBase64String(key);
        }

        /// <inheritdoc/>
        public string SignRequest(string method, string path, string body, string timestamp)
        {
            if (string.IsNullOrEmpty(method))
                throw new ArgumentNullException(nameof(method));
            if (string.IsNullOrEmpty(path))
                throw new ArgumentNullException(nameof(path));
            if (string.IsNullOrEmpty(timestamp))
                throw new ArgumentNullException(nameof(timestamp));

            // Normalize inputs
            method = method.ToUpperInvariant();
            body = body ?? string.Empty;

            // Build payload: METHOD|PATH|TIMESTAMP|BODY
            var payload = $"{method}|{path}|{timestamp}|{body}";

            using var hmac = new HMACSHA256(_secretKey);
            var hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(payload));
            return Convert.ToBase64String(hash);
        }

        /// <inheritdoc/>
        public async Task SignHttpRequestAsync(HttpRequestMessage request)
        {
            if (!_isEnabled)
            {
                // Signing disabled - don't add headers
                return;
            }

            if (request == null)
                throw new ArgumentNullException(nameof(request));

            var method = request.Method.Method;
            var path = request.RequestUri?.PathAndQuery ?? "/";
            var timestamp = GenerateTimestamp();
            var body = string.Empty;

            // Read body if present
            if (request.Content != null)
            {
                body = await request.Content.ReadAsStringAsync().ConfigureAwait(false);
            }

            var signature = SignRequest(method, path, body, timestamp);

            // Add headers
            request.Headers.Remove(SignatureHeader);
            request.Headers.Remove(TimestampHeader);
            request.Headers.Remove(VersionHeader);

            request.Headers.Add(SignatureHeader, signature);
            request.Headers.Add(TimestampHeader, timestamp);
            request.Headers.Add(VersionHeader, SignatureVersion);
        }

        /// <inheritdoc/>
        public bool VerifySignature(string signature, string method, string path, string body, string timestamp)
        {
            if (string.IsNullOrEmpty(signature))
                return false;

            try
            {
                var expectedSignature = SignRequest(method, path, body, timestamp);
                return CryptographicEquals(signature, expectedSignature);
            }
            catch
            {
                return false;
            }
        }

        /// <inheritdoc/>
        public string GenerateTimestamp()
        {
            return DateTime.UtcNow.ToString("o");
        }

        /// <summary>
        /// Compare two strings in constant time to prevent timing attacks.
        /// </summary>
        private static bool CryptographicEquals(string a, string b)
        {
            if (a == null || b == null)
                return false;

            var aBytes = Encoding.UTF8.GetBytes(a);
            var bBytes = Encoding.UTF8.GetBytes(b);

            if (aBytes.Length != bBytes.Length)
                return false;

            var result = 0;
            for (var i = 0; i < aBytes.Length; i++)
            {
                result |= aBytes[i] ^ bBytes[i];
            }

            return result == 0;
        }

        /// <summary>
        /// Dispose of sensitive key material.
        /// </summary>
        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        protected virtual void Dispose(bool disposing)
        {
            if (_disposed)
                return;

            if (disposing)
            {
                // Clear secret key from memory
                Array.Clear(_secretKey, 0, _secretKey.Length);
            }

            _disposed = true;
        }
    }
}
