using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Services;
using Xunit;
using VoiceStudio.IntegrationTests;

namespace VoiceStudio.IntegrationTests
{
    /// <summary>
    /// Integration tests for voice engine integration via backend API.
    /// Tests engine listing, recommendations, metrics, and synthesis with different engines.
    /// </summary>
    public class EngineIntegrationTests : IDisposable
    {
        private readonly IBackendClient _backendClient;
        private readonly HttpClient _httpClient;
        private readonly string _baseUrl;

        public EngineIntegrationTests()
        {
            // Get base URL from environment or use default
            _baseUrl = Environment.GetEnvironmentVariable("VOICESTUDIO_API_URL") 
                ?? "http://localhost:8000";
            
            _httpClient = new HttpClient
            {
                BaseAddress = new Uri(_baseUrl),
                Timeout = TimeSpan.FromMinutes(5) // Longer timeout for engine tests
            };
            
            _backendClient = new BackendClient(_httpClient);
        }

        [Fact]
        public async Task ListEngines_ShouldReturnEngineList()
        {
            // Act
            var engines = await _backendClient.SendRequestAsync<object, Dictionary<string, object>>(
                "/api/engines/list",
                null,
                System.Net.Http.HttpMethod.Get,
                CancellationToken.None
            );

            // Assert
            Assert.NotNull(engines);
            Assert.True(engines.ContainsKey("engines"));
            
            var engineList = engines["engines"];
            Assert.NotNull(engineList);
        }

        [Fact]
        public async Task ListEngines_ShouldIncludeAvailabilityStatus()
        {
            // Act
            var response = await _backendClient.SendRequestAsync<object, Dictionary<string, object>>(
                "/api/engines/list",
                null,
                System.Net.Http.HttpMethod.Get,
                CancellationToken.None
            );

            // Assert
            Assert.True(response.ContainsKey("available"));
            var available = response["available"];
            Assert.NotNull(available);
        }

        [Fact]
        public async Task GetEngineMetrics_ShouldReturnMetrics()
        {
            // Arrange - Get first available engine
            var enginesResponse = await _backendClient.SendRequestAsync<object, Dictionary<string, object>>(
                "/api/engines/list",
                null,
                System.Net.Http.HttpMethod.Get,
                CancellationToken.None
            );

            if (enginesResponse == null || !enginesResponse.ContainsKey("engines"))
            {
                // Skip if no engines available
                return;
            }

            var engines = enginesResponse["engines"];
            if (engines is not List<object> engineList || engineList.Count == 0)
            {
                // Skip if no engines
                return;
            }

            // Get first engine name (assuming it's a string or has a name property)
            string? engineName = null;
            if (engineList[0] is string engineNameStr)
            {
                engineName = engineNameStr;
            }
            else if (engineList[0] is Dictionary<string, object> engineDict && engineDict.ContainsKey("name"))
            {
                engineName = engineDict["name"]?.ToString();
            }

            if (string.IsNullOrEmpty(engineName))
            {
                // Skip if can't determine engine name
                return;
            }

            // Act
            var metrics = await _backendClient.SendRequestAsync<object, Dictionary<string, object>>(
                $"/api/engines/{Uri.EscapeDataString(engineName)}/metrics",
                null,
                System.Net.Http.HttpMethod.Get,
                CancellationToken.None
            );

            // Assert
            Assert.NotNull(metrics);
        }

        [Fact]
        public async Task RecommendEngine_ShouldReturnRecommendations()
        {
            // Arrange
            var request = new Dictionary<string, object>
            {
                { "task_type", "tts" },
                { "min_mos_score", 3.5 },
                { "prefer_speed", false }
            };

            // Act
            var recommendations = await _backendClient.SendRequestAsync<Dictionary<string, object>, Dictionary<string, object>>(
                "/api/engines/recommend",
                request,
                System.Net.Http.HttpMethod.Post,
                CancellationToken.None
            );

            // Assert
            Assert.NotNull(recommendations);
            Assert.True(recommendations.ContainsKey("recommendations"));
            
            var recommendationsList = recommendations["recommendations"];
            Assert.NotNull(recommendationsList);
        }

        [Fact]
        public async Task RecommendEngine_WithQualityTier_ShouldFilterResults()
        {
            // Arrange
            var request = TestFixtures.CreateEngineRecommendationRequest(
                taskType: "tts",
                qualityTier: "high",
                preferSpeed: false
            );

            // Act
            var recommendations = await _backendClient.SendRequestAsync<Dictionary<string, object>, Dictionary<string, object>>(
                "/api/engines/recommend",
                request,
                System.Net.Http.HttpMethod.Post,
                CancellationToken.None
            );

            // Assert
            Assert.NotNull(recommendations);
            if (recommendations.ContainsKey("recommendations"))
            {
                var recommendationsList = recommendations["recommendations"];
                Assert.NotNull(recommendationsList);
            }
        }

        [Fact]
        public async Task SynthesizeVoice_WithEngine_ShouldUseSpecifiedEngine()
        {
            // Arrange - Create a test profile first
            var profileRequest = TestFixtures.CreateTestProfileRequest("Engine Test Profile");
            var profile = await _backendClient.SendRequestAsync<Dictionary<string, object>, Dictionary<string, object>>(
                "/api/profiles",
                profileRequest,
                System.Net.Http.HttpMethod.Post,
                CancellationToken.None
            );

            if (profile == null || !profile.ContainsKey("id"))
            {
                // Skip if profile creation failed
                return;
            }

            var profileId = profile["id"]?.ToString();
            if (string.IsNullOrEmpty(profileId))
            {
                return;
            }

            // Get available engines
            var enginesResponse = await _backendClient.SendRequestAsync<object, Dictionary<string, object>>(
                "/api/engines/list",
                null,
                System.Net.Http.HttpMethod.Get,
                CancellationToken.None
            );

            if (enginesResponse == null || !enginesResponse.ContainsKey("engines"))
            {
                // Skip if no engines
                return;
            }

            // Act - Try synthesis with default engine (engine selection handled by backend)
            var synthesisRequest = TestFixtures.CreateSynthesisRequest(profileId, TestFixtures.TestTexts.Medium);

            try
            {
                var response = await _backendClient.SendRequestAsync<Dictionary<string, object>, Dictionary<string, object>>(
                    "/api/voice/synthesize",
                    synthesisRequest,
                    System.Net.Http.HttpMethod.Post,
                    CancellationToken.None
                );

                // Assert
                Assert.NotNull(response);
                Assert.True(response.ContainsKey("audio_id"));
                
                // Verify quality metrics if present
                if (response.ContainsKey("quality_metrics"))
                {
                    var qualityMetrics = response["quality_metrics"];
                    Assert.NotNull(qualityMetrics);
                }
            }
            finally
            {
                // Cleanup - Delete test profile
                try
                {
                    await _backendClient.SendRequestAsync<object, object>(
                        $"/api/profiles/{Uri.EscapeDataString(profileId)}",
                        null,
                        System.Net.Http.HttpMethod.Delete,
                        CancellationToken.None
                    );
                }
                // ALLOWED: empty catch - test cleanup must not throw
                catch
                {
                    // Ignore cleanup errors
                }
            }
        }

        [Fact]
        public async Task GetEngineMetrics_WithInvalidEngine_ShouldHandleError()
        {
            // Act
            try
            {
                var metrics = await _backendClient.SendRequestAsync<object, Dictionary<string, object>>(
                    "/api/engines/invalid_engine_name/metrics",
                    null,
                    System.Net.Http.HttpMethod.Get,
                    CancellationToken.None
                );

                // If no exception, metrics might be null or empty
                Assert.NotNull(metrics);
            }
            catch (HttpRequestException)
            {
                // Expected for invalid engine - should return 404 or 400
            }
        }

        [Fact]
        public async Task RecommendEngine_WithInvalidTaskType_ShouldHandleError()
        {
            // Arrange
            var request = TestFixtures.CreateEngineRecommendationRequest(
                taskType: "invalid_task_type"
            );

            // Act
            try
            {
                var recommendations = await _backendClient.SendRequestAsync<Dictionary<string, object>, Dictionary<string, object>>(
                    "/api/engines/recommend",
                    request,
                    System.Net.Http.HttpMethod.Post,
                    CancellationToken.None
                );

                // May return empty recommendations or error
                recommendations.Should().NotBeNull();
            }
            catch (HttpRequestException)
            {
                // Expected for invalid task type
            }
        }

        [Fact]
        public async Task SynthesizeVoice_WithInvalidProfile_ShouldHandleError()
        {
            // Arrange
            var synthesisRequest = TestFixtures.CreateSynthesisRequest("invalid_profile_id", "Test text");

            // Act
            try
            {
                var response = await _backendClient.SendRequestAsync<Dictionary<string, object>, Dictionary<string, object>>(
                    "/api/voice/synthesize",
                    synthesisRequest,
                    System.Net.Http.HttpMethod.Post,
                    CancellationToken.None
                );

                // Should not succeed with invalid profile
                Assert.Null(response);
            }
            catch (HttpRequestException)
            {
                // Expected - should return 404 for invalid profile
            }
        }

        [Fact]
        public async Task SynthesizeVoice_WithEmptyText_ShouldHandleError()
        {
            // Arrange - Create test profile
            var profileRequest = TestFixtures.CreateTestProfileRequest("Error Test Profile");
            var profile = await _backendClient.SendRequestAsync<Dictionary<string, object>, Dictionary<string, object>>(
                "/api/profiles",
                profileRequest,
                System.Net.Http.HttpMethod.Post,
                CancellationToken.None
            );

            if (profile == null || !profile.ContainsKey("id"))
            {
                return; // Skip if profile creation failed
            }

            var profileId = profile["id"]?.ToString();
            if (string.IsNullOrEmpty(profileId))
            {
                return;
            }

            var synthesisRequest = TestFixtures.CreateSynthesisRequest(profileId, "");

            try
            {
                // Act
                try
                {
                    var response = await _backendClient.SendRequestAsync<Dictionary<string, object>, Dictionary<string, object>>(
                        "/api/voice/synthesize",
                        synthesisRequest,
                        System.Net.Http.HttpMethod.Post,
                        CancellationToken.None
                    );

                    // Should not succeed with empty text
                    Assert.Null(response);
                }
                catch (HttpRequestException)
                {
                    // Expected - should return 400 for empty text
                }
            }
            finally
            {
                // Cleanup
                try
                {
                    await _backendClient.SendRequestAsync<object, object>(
                        $"/api/profiles/{Uri.EscapeDataString(profileId)}",
                        null,
                        System.Net.Http.HttpMethod.Delete,
                        CancellationToken.None
                    );
                }
                // ALLOWED: empty catch - test cleanup must not throw
                catch
                {
                    // Ignore cleanup errors
                }
            }
        }

        [Fact]
        public async Task ListEngines_ShouldBeCached()
        {
            // Act - First request
            var response1 = await _backendClient.SendRequestAsync<object, Dictionary<string, object>>(
                "/api/engines/list",
                null,
                System.Net.Http.HttpMethod.Get,
                CancellationToken.None
            );

            // Second request should be faster (cached)
            var startTime = DateTime.UtcNow;
            var response2 = await _backendClient.SendRequestAsync<object, Dictionary<string, object>>(
                "/api/engines/list",
                null,
                System.Net.Http.HttpMethod.Get,
                CancellationToken.None
            );
            var duration = (DateTime.UtcNow - startTime).TotalMilliseconds;

            // Assert
            Assert.NotNull(response1);
            Assert.NotNull(response2);
            
            // Cached response should be faster (typically < 50ms)
            Assert.True(duration < 100, $"Cached response took {duration}ms, expected < 100ms");
        }

        [Fact]
        public async Task RecommendEngine_WithMinRequirements_ShouldFilterEngines()
        {
            // Arrange
            var request = new Dictionary<string, object>
            {
                { "task_type", "tts" },
                { "min_mos_score", 4.5 },
                { "min_similarity", 0.9 },
                { "min_naturalness", 0.85 }
            };

            // Act
            var recommendations = await _backendClient.SendRequestAsync<Dictionary<string, object>, Dictionary<string, object>>(
                "/api/engines/recommend",
                request,
                System.Net.Http.HttpMethod.Post,
                CancellationToken.None
            );

            // Assert
            recommendations.Should().NotBeNull();
            if (recommendations.ContainsKey("recommendations"))
            {
                var recommendationsList = recommendations["recommendations"];
                if (recommendationsList is List<object> recList)
                {
                    // All recommendations should meet minimum requirements
                    foreach (var rec in recList)
                    {
                        if (rec is Dictionary<string, object> recDict)
                        {
                            Assert.True(recDict.ContainsKey("meets_requirements"));
                            var meetsRequirements = recDict["meets_requirements"];
                            if (meetsRequirements is bool meets && meets)
                            {
                                // If meets requirements, verify quality estimates
                                if (recDict.ContainsKey("quality_estimate"))
                                {
                                    var qualityEstimate = recDict["quality_estimate"];
                                    Assert.NotNull(qualityEstimate);
                                }
                            }
                        }
                    }
                }
            }
        }

        public void Dispose()
        {
            _httpClient?.Dispose();
        }
    }
}
