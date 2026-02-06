// Copyright (c) VoiceStudio. All rights reserved.
// Licensed under the MIT License.

using System;
using System.Net.Http;
using System.Threading.Tasks;

namespace VoiceStudio.App.Services.IPC
{
    /// <summary>
    /// Interface for HMAC-based request signing for IPC security.
    /// Implements Phase 6.1.3 request signing for UI-to-backend communication.
    /// </summary>
    public interface IRequestSigner
    {
        /// <summary>
        /// Sign a request and generate an HMAC signature.
        /// </summary>
        /// <param name="method">HTTP method (GET, POST, etc.)</param>
        /// <param name="path">Request path (e.g., /api/v1/voices)</param>
        /// <param name="body">Request body (empty string for bodyless requests)</param>
        /// <param name="timestamp">ISO 8601 timestamp for replay attack prevention</param>
        /// <returns>Base64-encoded HMAC-SHA256 signature</returns>
        string SignRequest(string method, string path, string body, string timestamp);

        /// <summary>
        /// Sign an HTTP request message by adding signature headers.
        /// </summary>
        /// <param name="request">HTTP request to sign</param>
        /// <returns>Task that completes when signing is done</returns>
        Task SignHttpRequestAsync(HttpRequestMessage request);

        /// <summary>
        /// Verify a signature against the expected payload.
        /// Used primarily for testing purposes on the C# side.
        /// </summary>
        /// <param name="signature">The signature to verify</param>
        /// <param name="method">HTTP method</param>
        /// <param name="path">Request path</param>
        /// <param name="body">Request body</param>
        /// <param name="timestamp">Timestamp used for signing</param>
        /// <returns>True if signature is valid</returns>
        bool VerifySignature(string signature, string method, string path, string body, string timestamp);

        /// <summary>
        /// Generate a timestamp for signing.
        /// </summary>
        /// <returns>ISO 8601 formatted timestamp</returns>
        string GenerateTimestamp();
    }
}
