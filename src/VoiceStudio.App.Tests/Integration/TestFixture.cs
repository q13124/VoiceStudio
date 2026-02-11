using System;
using System.Collections.Generic;
using Microsoft.Extensions.DependencyInjection;
using VoiceStudio.App.Services.Messaging;
using VoiceStudio.App.Tests.Mocks;
using VoiceStudio.Core.Gateways;
using VoiceStudio.Core.Messaging;
using VoiceStudio.Core.State;
using VoiceStudio.App.Services.State;

namespace VoiceStudio.App.Tests.Integration
{
  /// <summary>
  /// Test fixture providing a configured service provider with mocks for integration tests.
  /// </summary>
  public class TestFixture : IDisposable
  {
    private readonly ServiceProvider _serviceProvider;
    private bool _disposed;

    /// <summary>
    /// Gets the service provider.
    /// </summary>
    public IServiceProvider Services => _serviceProvider;

    /// <summary>
    /// Gets the mock backend transport.
    /// </summary>
    public MockBackendTransport MockTransport { get; }

    /// <summary>
    /// Gets the mock voice gateway.
    /// </summary>
    public MockVoiceGateway MockVoiceGateway { get; }

    /// <summary>
    /// Gets the mock profile gateway.
    /// </summary>
    public MockProfileGateway MockProfileGateway { get; }

    /// <summary>
    /// Gets the mock job gateway.
    /// </summary>
    public MockJobGateway MockJobGateway { get; }

    /// <summary>
    /// Gets the mock engine gateway.
    /// </summary>
    public MockEngineGateway MockEngineGateway { get; }

    /// <summary>
    /// Gets the mock audio gateway.
    /// </summary>
    public MockAudioGateway MockAudioGateway { get; }

    /// <summary>
    /// Gets the mock project gateway.
    /// </summary>
    public MockProjectGateway MockProjectGateway { get; }

    /// <summary>
    /// Gets the mock timeline gateway.
    /// </summary>
    public MockTimelineGateway MockTimelineGateway { get; }

    /// <summary>
    /// Gets the mock app messenger.
    /// </summary>
    public MockAppMessenger MockMessenger { get; }

    /// <summary>
    /// Gets the app state store.
    /// </summary>
    public AppStateStore StateStore { get; }

    /// <summary>
    /// Creates a new test fixture with default configuration.
    /// </summary>
    public TestFixture() : this(_ => { })
    {
    }

    /// <summary>
    /// Creates a new test fixture with custom service configuration.
    /// </summary>
    /// <param name="configureServices">Action to configure additional services.</param>
    public TestFixture(Action<IServiceCollection> configureServices)
    {
      // Create mocks
      MockTransport = new MockBackendTransport();
      MockVoiceGateway = new MockVoiceGateway();
      MockProfileGateway = new MockProfileGateway();
      MockJobGateway = new MockJobGateway();
      MockEngineGateway = new MockEngineGateway();
      MockAudioGateway = new MockAudioGateway();
      MockProjectGateway = new MockProjectGateway();
      MockTimelineGateway = new MockTimelineGateway();
      MockMessenger = new MockAppMessenger();
      StateStore = new AppStateStore();

      // Configure services
      var services = new ServiceCollection();

      // Logging not needed for tests

      // Add mocks as singletons
      services.AddSingleton<IBackendTransport>(MockTransport);
      services.AddSingleton<IVoiceGateway>(MockVoiceGateway);
      services.AddSingleton<IProfileGateway>(MockProfileGateway);
      services.AddSingleton<IJobGateway>(MockJobGateway);
      services.AddSingleton<IEngineGateway>(MockEngineGateway);
      services.AddSingleton<IAudioGateway>(MockAudioGateway);
      services.AddSingleton<IProjectGateway>(MockProjectGateway);
      services.AddSingleton<ITimelineGateway>(MockTimelineGateway);
      services.AddSingleton<IAppMessenger>(MockMessenger);
      services.AddSingleton<IAppStateStore>(StateStore);
      services.AddSingleton(StateStore);

      // Allow custom configuration
      configureServices(services);

      _serviceProvider = services.BuildServiceProvider();
    }

    /// <summary>
    /// Gets a service from the container.
    /// </summary>
    public T GetService<T>() where T : notnull
    {
      return _serviceProvider.GetRequiredService<T>();
    }

    /// <summary>
    /// Gets a service from the container, or null if not registered.
    /// </summary>
    public T? GetOptionalService<T>() where T : class
    {
      return _serviceProvider.GetService<T>();
    }

    /// <summary>
    /// Resets all mocks to their initial state.
    /// </summary>
    public void Reset()
    {
      MockTransport.ClearRequests();
      MockTransport.SimulatedError = null!;
      MockTransport.SimulatedLatency = TimeSpan.Zero;
      MockTransport.IsConnected = true;

      MockVoiceGateway.SynthesisRequests.Clear();
      MockVoiceGateway.CloneRequests.Clear();

      MockMessenger.Reset();
    }

    /// <summary>
    /// Disposes the fixture and its resources.
    /// </summary>
    public void Dispose()
    {
      Dispose(true);
      GC.SuppressFinalize(this);
    }

    protected virtual void Dispose(bool disposing)
    {
      if (!_disposed)
      {
        if (disposing)
        {
          _serviceProvider.Dispose();
          StateStore.Dispose();
        }
        _disposed = true;
      }
    }
  }
}
