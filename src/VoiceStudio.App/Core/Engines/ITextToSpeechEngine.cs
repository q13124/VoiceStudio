using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Models;

namespace VoiceStudio.Core.Engines
{
    /// <summary>
    /// Interface for Text-to-Speech engines.
    /// </summary>
    public interface ITextToSpeechEngine : IEngine
    {
        /// <summary>
        /// Gets available voice profiles for this engine.
        /// </summary>
        Task<IEnumerable<VoiceProfile>> GetVoicesAsync(CancellationToken cancellationToken = default);

        /// <summary>
        /// Synthesizes speech from text.
        /// </summary>
        /// <param name="request">The synthesis parameters.</param>
        /// <param name="cancellationToken">Cancellation token.</param>
        /// <returns>The generated audio clip.</returns>
        Task<AudioClip> SynthesizeAsync(VoiceSynthesisRequest request, CancellationToken cancellationToken = default);
    }
}
