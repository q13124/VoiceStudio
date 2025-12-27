using System;
using System.Collections.Generic;
using VoiceStudio.Core.Models;

namespace VoiceStudio.IntegrationTests
{
    /// <summary>
    /// Test fixtures and helper methods for engine integration tests.
    /// </summary>
    public static class TestFixtures
    {
        /// <summary>
        /// Creates a test voice profile request.
        /// </summary>
        public static Dictionary<string, object> CreateTestProfileRequest(string? name = null)
        {
            return new Dictionary<string, object>
            {
                { "name", name ?? $"Test Profile {Guid.NewGuid():N}" },
                { "language", "en" },
                { "tags", new List<string> { "test", "integration" } }
            };
        }

        /// <summary>
        /// Creates a test voice synthesis request.
        /// </summary>
        public static Dictionary<string, object> CreateSynthesisRequest(string profileId, string? text = null, string? engine = null)
        {
            var request = new Dictionary<string, object>
            {
                { "text", text ?? "Hello, this is a test of voice synthesis with the engine integration test suite." },
                { "voice_profile_id", profileId },
                { "language", "en" },
                { "speed", 1.0 },
                { "pitch", 0.0 }
            };

            if (!string.IsNullOrEmpty(engine))
            {
                request["engine"] = engine;
            }

            return request;
        }

        /// <summary>
        /// Creates an engine recommendation request.
        /// </summary>
        public static Dictionary<string, object> CreateEngineRecommendationRequest(
            string taskType = "tts",
            double? minMosScore = null,
            double? minSimilarity = null,
            double? minNaturalness = null,
            bool preferSpeed = false,
            string? qualityTier = null)
        {
            var request = new Dictionary<string, object>
            {
                { "task_type", taskType },
                { "prefer_speed", preferSpeed }
            };

            if (minMosScore.HasValue)
            {
                request["min_mos_score"] = minMosScore.Value;
            }

            if (minSimilarity.HasValue)
            {
                request["min_similarity"] = minSimilarity.Value;
            }

            if (minNaturalness.HasValue)
            {
                request["min_naturalness"] = minNaturalness.Value;
            }

            if (!string.IsNullOrEmpty(qualityTier))
            {
                request["quality_tier"] = qualityTier;
            }

            return request;
        }

        /// <summary>
        /// Test audio data for engine testing (sine wave).
        /// </summary>
        public static byte[] GenerateTestAudio(int durationSeconds = 1, int sampleRate = 22050)
        {
            var samples = durationSeconds * sampleRate;
            var audio = new float[samples];
            var frequency = 440.0; // A4 note

            for (int i = 0; i < samples; i++)
            {
                audio[i] = (float)(0.5 * Math.Sin(2 * Math.PI * frequency * i / sampleRate));
            }

            // Convert to 16-bit PCM
            var bytes = new byte[samples * 2];
            for (int i = 0; i < samples; i++)
            {
                var sample = (short)(audio[i] * short.MaxValue);
                bytes[i * 2] = (byte)(sample & 0xFF);
                bytes[i * 2 + 1] = (byte)((sample >> 8) & 0xFF);
            }

            return bytes;
        }

        /// <summary>
        /// Common test text samples for synthesis testing.
        /// </summary>
        public static class TestTexts
        {
            public static string Short => "Hello, world!";
            public static string Medium => "This is a medium-length test sentence for voice synthesis testing.";
            public static string Long => "This is a longer test passage designed to evaluate voice synthesis quality across multiple sentences. It includes various punctuation marks, such as commas, periods, and question marks? The text also tests the engine's ability to handle different sentence structures and natural language patterns.";
            public static string Numbers => "The number 42 is the answer. Pi is approximately 3.14159.";
            public static string SpecialChars => "Hello! How are you? I'm doing well. Let's test: quotes, dashes—and more.";
        }
    }
}
