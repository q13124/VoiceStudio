using System;
using System.Net.Http;
using VoiceStudio.Core.Services;
using VoiceStudio.Core.Services.Generated;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Adapter that wraps the generated NSwag client while preserving the existing BackendClient behavior.
  /// This ensures contract alignment with OpenAPI and keeps backward compatibility for existing consumers.
  /// </summary>
  public class BackendClientAdapter : BackendClient, IDisposable
  {
    public Client GeneratedClient { get; }

    public BackendClientAdapter(BackendClientConfig config, IErrorLoggingService? errorLoggingService = null)
        : base(config)
    {
      // Create an HttpClient for the generated client using the same base URL and timeout.
      var httpClient = new HttpClient
      {
        BaseAddress = new Uri(config.BaseUrl),
        Timeout = config.RequestTimeout
      };

      GeneratedClient = new Client(config.BaseUrl, httpClient);

      // Optional: log initialization
      errorLoggingService?.LogInfo("BackendClientAdapter initialized with generated client", "BackendClientAdapter");
    }

    public new void Dispose()
    {
      base.Dispose();
      (GeneratedClient as IDisposable)?.Dispose();
    }
  }
}