// Copyright (c) VoiceStudio. All rights reserved.
// Licensed under the MIT License.

using System;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.App.Services.IPC
{
    /// <summary>
    /// HTTP message handler that adds HMAC signatures to outgoing requests.
    /// Implements Phase 6.1.3 request signing for secure IPC.
    /// 
    /// This handler is designed to be part of the HttpClient pipeline,
    /// typically chained with CorrelationIdHandler.
    /// </summary>
    public class HmacSigningHandler : DelegatingHandler
    {
        private readonly IRequestSigner _signer;

        /// <summary>
        /// Create a new HmacSigningHandler with the specified signer.
        /// </summary>
        /// <param name="signer">Request signer instance</param>
        public HmacSigningHandler(IRequestSigner signer) : base(new HttpClientHandler())
        {
            _signer = signer ?? throw new ArgumentNullException(nameof(signer));
        }

        /// <summary>
        /// Create a new HmacSigningHandler with the specified signer and inner handler.
        /// </summary>
        /// <param name="signer">Request signer instance</param>
        /// <param name="innerHandler">Inner HTTP handler</param>
        public HmacSigningHandler(IRequestSigner signer, HttpMessageHandler innerHandler) : base(innerHandler)
        {
            _signer = signer ?? throw new ArgumentNullException(nameof(signer));
        }

        /// <inheritdoc/>
        protected override async Task<HttpResponseMessage> SendAsync(
            HttpRequestMessage request,
            CancellationToken cancellationToken)
        {
            // Sign the request before sending
            await _signer.SignHttpRequestAsync(request).ConfigureAwait(false);

            // Continue with the request
            return await base.SendAsync(request, cancellationToken).ConfigureAwait(false);
        }
    }
}
