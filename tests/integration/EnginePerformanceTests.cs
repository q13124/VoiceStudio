using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Services;
using Xunit;

namespace VoiceStudio.IntegrationTests
{
    /// <summary>
    /// Performance benchmarks for engine integration via backend API.
    /// Measures response times, throughput, and resource usage.
    /// </summary>
    public class EnginePerformanceTests : IDisposable
    {
        private readonly IBackendClient _backendClient;
        private readonly HttpClient _httpClient;
        private readonly string _baseUrl;

        public EnginePerformanceTests()
        {
            _baseUrl = Environment.GetEnvironmentVariable("VOICESTUDIO_API_URL") 
                ?? "http://localhost:8000";
            
            _httpClient = new HttpClient
            {
                BaseAddress = new Uri(_baseUrl),
                Timeout = TimeSpan.FromMinutes(10) // Longer timeout for performance tests
            };
            
            _backendClient = new BackendClient(_httpClient);
        }

        [Fact]
        public async Task ListEngines_ShouldRespondWithinThreshold()
        {
            // Arrange
            var stopwatch = Stopwatch.StartNew();

            // Act
            var engines = await _backendClient.SendRequestAsync<object, Dictionary<string, object>>(
                "/api/engines/list",
                null,
                System.Net.Http.HttpMethod.Get,
                CancellationToken.None
            );

            stopwatch.Stop();

            // Assert
            Assert.NotNull(engines);
            
            // Should respond within 2 seconds (accounting for network latency)
            Assert.True(stopwatch.ElapsedMilliseconds < 2000, 
                $"Response took {stopwatch.ElapsedMilliseconds}ms, expected < 2000ms");
        }

        [Fact]
        public async Task ListEngines_CachedResponse_ShouldBeFaster()
        {
            // Arrange - First request (cache miss)
            var stopwatch1 = Stopwatch.StartNew();
            await _backendClient.SendRequestAsync<object, Dictionary<string, object>>(
                "/api/engines/list",
                null,
                System.Net.Http.HttpMethod.Get,
                CancellationToken.None
            );
            stopwatch1.Stop();

            // Act - Second request (cache hit)
            var stopwatch2 = Stopwatch.StartNew();
            await _backendClient.SendRequestAsync<object, Dictionary<string, object>>(
                "/api/engines/list",
                null,
                System.Net.Http.HttpMethod.Get,
                CancellationToken.None
            );
            stopwatch2.Stop();

            // Assert - Cached response should be significantly faster
            stopwatch2.ElapsedMilliseconds.Should().BeLessThan(stopwatch1.ElapsedMilliseconds);
            stopwatch2.ElapsedMilliseconds.Should().BeLessThan(100); // Cached should be < 100ms
        }

        [Fact]
        public async Task RecommendEngine_ShouldRespondWithinThreshold()
        {
            // Arrange
            var request = TestFixtures.CreateEngineRecommendationRequest(
                taskType: "tts",
                minMosScore: 3.0
            );

            var stopwatch = Stopwatch.StartNew();

            // Act
            var recommendations = await _backendClient.SendRequestAsync<Dictionary<string, object>, Dictionary<string, object>>(
                "/api/engines/recommend",
                request,
                System.Net.Http.HttpMethod.Post,
                CancellationToken.None
            );

            stopwatch.Stop();

            // Assert
            Assert.NotNull(recommendations);
            
            // Should respond within 5 seconds (engine evaluation may take time)
            Assert.True(stopwatch.ElapsedMilliseconds < 5000,
                $"Response took {stopwatch.ElapsedMilliseconds}ms, expected < 5000ms");
        }

        [Fact]
        public async Task GetEngineMetrics_ShouldRespondWithinThreshold()
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
                return; // Skip if no engines
            }

            var engines = enginesResponse["engines"];
            if (engines is not List<object> engineList || engineList.Count == 0)
            {
                return; // Skip if no engines
            }

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
                return; // Skip if can't determine engine name
            }

            var stopwatch = Stopwatch.StartNew();

            // Act
            var metrics = await _backendClient.SendRequestAsync<object, Dictionary<string, object>>(
                $"/api/engines/{Uri.EscapeDataString(engineName)}/metrics",
                null,
                System.Net.Http.HttpMethod.Get,
                CancellationToken.None
            );

            stopwatch.Stop();

            // Assert
            metrics.Should().NotBeNull();
            
            // Should respond within 2 seconds
            stopwatch.ElapsedMilliseconds.Should().BeLessThan(2000);
        }

        [Fact]
        public async Task SynthesizeVoice_PerformanceBenchmark()
        {
            // Arrange - Create test profile
            var profileRequest = TestFixtures.CreateTestProfileRequest("Performance Test Profile");
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

            var synthesisRequest = TestFixtures.CreateSynthesisRequest(profileId, TestFixtures.TestTexts.Short);

            try
            {
                var stopwatch = Stopwatch.StartNew();

                // Act
                var response = await _backendClient.SendRequestAsync<Dictionary<string, object>, Dictionary<string, object>>(
                    "/api/voice/synthesize",
                    synthesisRequest,
                    System.Net.Http.HttpMethod.Post,
                    CancellationToken.None
                );

                stopwatch.Stop();

                // Assert
                Assert.NotNull(response);
                Assert.True(response.ContainsKey("audio_id"));
                
                // Synthesis should complete within reasonable time (30 seconds for short text)
                Assert.True(stopwatch.ElapsedMilliseconds < 30000,
                    $"Synthesis took {stopwatch.ElapsedMilliseconds}ms, expected < 30000ms");
                
                // Log performance metrics
                var processingTime = response.ContainsKey("processing_time") 
                    ? response["processing_time"]?.ToString() 
                    : "N/A";
                
                // Performance assertion: Short text synthesis should be reasonably fast
                // Actual time depends on engine, but should be under 30 seconds
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
        public async Task ConcurrentEngineListRequests_ShouldHandleLoad()
        {
            // Arrange
            const int concurrentRequests = 10;
            var tasks = new List<Task<Dictionary<string, object>?>>();

            // Act
            var stopwatch = Stopwatch.StartNew();
            
            for (int i = 0; i < concurrentRequests; i++)
            {
                tasks.Add(_backendClient.SendRequestAsync<object, Dictionary<string, object>>(
                    "/api/engines/list",
                    null,
                    System.Net.Http.HttpMethod.Get,
                    CancellationToken.None
                ));
            }

            var results = await Task.WhenAll(tasks);
            stopwatch.Stop();

            // Assert
            Assert.All(results, r => Assert.NotNull(r)); // All should not be null
            Assert.All(results, r => Assert.True(r.ContainsKey("engines"))); // All should have engines
            
            // All requests should complete within reasonable time (5 seconds for 10 concurrent)
            Assert.True(stopwatch.ElapsedMilliseconds < 5000,
                $"Concurrent requests took {stopwatch.ElapsedMilliseconds}ms, expected < 5000ms");
        }

        public void Dispose()
        {
            _httpClient?.Dispose();
        }
    }
}
