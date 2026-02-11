using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using VoiceStudio.App.Tests.Mocks;
using VoiceStudio.Core.Gateways;
using VoiceStudio.Core.Messaging;
using VoiceStudio.Core.State;

namespace VoiceStudio.App.Tests.Integration
{
  /// <summary>
  /// Base class for command integration tests.
  /// </summary>
  public abstract class CommandTestBase : IDisposable
  {
    protected TestFixture Fixture { get; private set; } = null!;
    protected MockBackendTransport Transport => Fixture.MockTransport;
    protected MockVoiceGateway VoiceGateway => Fixture.MockVoiceGateway;
    protected MockProfileGateway ProfileGateway => Fixture.MockProfileGateway;
    protected MockJobGateway JobGateway => Fixture.MockJobGateway;
    protected MockEngineGateway EngineGateway => Fixture.MockEngineGateway;
    protected MockAudioGateway AudioGateway => Fixture.MockAudioGateway;
    protected MockProjectGateway ProjectGateway => Fixture.MockProjectGateway;
    protected MockTimelineGateway TimelineGateway => Fixture.MockTimelineGateway;
    protected MockAppMessenger Messenger => Fixture.MockMessenger;
    protected IAppStateStore StateStore => Fixture.StateStore;

    private bool _disposed;

    /// <summary>
    /// Initializes the test fixture before each test.
    /// </summary>
    [TestInitialize]
    public virtual void TestInitialize()
    {
      Fixture = CreateFixture();
    }

    /// <summary>
    /// Cleans up the test fixture after each test.
    /// </summary>
    [TestCleanup]
    public virtual void TestCleanup()
    {
      Dispose();
    }

    /// <summary>
    /// Creates the test fixture. Override to customize services.
    /// </summary>
    protected virtual TestFixture CreateFixture()
    {
      return new TestFixture();
    }

    /// <summary>
    /// Gets a service from the test container.
    /// </summary>
    protected T GetService<T>() where T : notnull
    {
      return Fixture.GetService<T>();
    }

    /// <summary>
    /// Asserts that a specific message type was sent.
    /// </summary>
    protected void AssertMessageSent<T>() where T : class
    {
      var messages = Messenger.GetSentMessages<T>();
      Assert.IsTrue(
          System.Linq.Enumerable.Any(messages),
          $"Expected message of type {typeof(T).Name} to be sent, but it was not.");
    }

    /// <summary>
    /// Asserts that a specific message type was sent with a predicate.
    /// </summary>
    protected void AssertMessageSent<T>(Func<T, bool> predicate) where T : class
    {
      var messages = Messenger.GetSentMessages<T>();
      Assert.IsTrue(
          System.Linq.Enumerable.Any(messages, predicate),
          $"Expected message of type {typeof(T).Name} matching predicate to be sent, but it was not.");
    }

    /// <summary>
    /// Asserts that no messages of a specific type were sent.
    /// </summary>
    protected void AssertNoMessageSent<T>() where T : class
    {
      var messages = Messenger.GetSentMessages<T>();
      Assert.IsFalse(
          System.Linq.Enumerable.Any(messages),
          $"Expected no message of type {typeof(T).Name} to be sent, but {System.Linq.Enumerable.Count(messages)} were sent.");
    }

    /// <summary>
    /// Asserts that the state store contains expected state.
    /// </summary>
    protected void AssertState<T>(Func<AppState, T> selector, Func<T, bool> predicate, string message = "")
    {
      var value = StateStore.Select(selector);
      Assert.IsTrue(predicate(value), message);
    }

    /// <summary>
    /// Asserts that a gateway result is successful.
    /// </summary>
    protected void AssertSuccess<T>(GatewayResult<T> result)
    {
      Assert.IsTrue(result.Success, $"Expected success but got error: {result.Error?.Message}");
    }

    /// <summary>
    /// Asserts that a gateway result is a failure with specific error code.
    /// </summary>
    protected void AssertFailure<T>(GatewayResult<T> result, string? expectedCode = null)
    {
      Assert.IsFalse(result.Success, "Expected failure but got success");
      if (expectedCode != null)
      {
        Assert.AreEqual(expectedCode, result.Error?.Code, $"Expected error code '{expectedCode}' but got '{result.Error?.Code}'");
      }
    }

    /// <summary>
    /// Waits for a condition to become true.
    /// </summary>
    protected async Task WaitForAsync(Func<bool> condition, TimeSpan? timeout = null, TimeSpan? pollInterval = null)
    {
      var actualTimeout = timeout ?? TimeSpan.FromSeconds(5);
      var actualPollInterval = pollInterval ?? TimeSpan.FromMilliseconds(50);

      using var cts = new CancellationTokenSource(actualTimeout);

      while (!condition() && !cts.IsCancellationRequested)
      {
        await Task.Delay(actualPollInterval, cts.Token);
      }

      Assert.IsTrue(condition(), "Condition did not become true within timeout");
    }

    /// <summary>
    /// Waits for a message of a specific type to be sent.
    /// </summary>
    protected async Task<T> WaitForMessageAsync<T>(TimeSpan? timeout = null) where T : class
    {
      var actualTimeout = timeout ?? TimeSpan.FromSeconds(5);
      var startCount = System.Linq.Enumerable.Count(Messenger.GetSentMessages<T>());

      using var cts = new CancellationTokenSource(actualTimeout);

      while (!cts.IsCancellationRequested)
      {
        var messages = Messenger.GetSentMessages<T>();
        var newMessages = System.Linq.Enumerable.Skip(messages, startCount);

        if (System.Linq.Enumerable.Any(newMessages))
          return System.Linq.Enumerable.First(newMessages);

        await Task.Delay(TimeSpan.FromMilliseconds(50), cts.Token);
      }

      throw new TimeoutException($"No message of type {typeof(T).Name} was sent within timeout");
    }

    /// <summary>
    /// Disposes test resources.
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
          Fixture?.Dispose();
        }
        _disposed = true;
      }
    }
  }
}
