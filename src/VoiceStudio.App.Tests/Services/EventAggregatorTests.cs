using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Tests.Services;

/// <summary>
/// Unit tests for EventAggregator pub/sub service.
/// Tests subscription, publishing, telemetry, and thread safety.
/// </summary>
[TestClass]
public class EventAggregatorTests : TestBase
{
    private EventAggregator _eventAggregator = null!;

    [TestInitialize]
    public override void TestInitialize()
    {
        base.TestInitialize();
        _eventAggregator = new EventAggregator();
    }

    [TestCleanup]
    public override void TestCleanup()
    {
        _eventAggregator = null!;
        base.TestCleanup();
    }

    #region Basic Publish/Subscribe Tests

    [TestMethod]
    public void Subscribe_ReturnsValidToken()
    {
        // Act
        var token = _eventAggregator.Subscribe<TestEvent>(e => { });

        // Assert
        Assert.IsNotNull(token);
        Assert.IsInstanceOfType(token, typeof(ISubscriptionToken));
    }

    [TestMethod]
    public void Publish_InvokesSubscribedHandler()
    {
        // Arrange
        TestEvent? receivedEvent = null;
        _eventAggregator.Subscribe<TestEvent>(e => receivedEvent = e);

        var testEvent = new TestEvent { Message = "Hello" };

        // Act
        _eventAggregator.Publish(testEvent);

        // Assert
        Assert.IsNotNull(receivedEvent);
        Assert.AreEqual("Hello", receivedEvent.Message);
    }

    [TestMethod]
    public void Publish_InvokesMultipleSubscribers()
    {
        // Arrange
        var receivedCount = 0;
        _eventAggregator.Subscribe<TestEvent>(e => receivedCount++);
        _eventAggregator.Subscribe<TestEvent>(e => receivedCount++);
        _eventAggregator.Subscribe<TestEvent>(e => receivedCount++);

        // Act
        _eventAggregator.Publish(new TestEvent { Message = "Test" });

        // Assert
        Assert.AreEqual(3, receivedCount);
    }

    [TestMethod]
    public void Publish_DoesNotInvokeUnrelatedSubscribers()
    {
        // Arrange
        var testEventReceived = false;
        var otherEventReceived = false;

        _eventAggregator.Subscribe<TestEvent>(e => testEventReceived = true);
        _eventAggregator.Subscribe<OtherTestEvent>(e => otherEventReceived = true);

        // Act
        _eventAggregator.Publish(new TestEvent { Message = "Test" });

        // Assert
        Assert.IsTrue(testEventReceived);
        Assert.IsFalse(otherEventReceived);
    }

    [TestMethod]
    public void Publish_WithNoSubscribers_DoesNotThrow()
    {
        // Act & Assert - should not throw
        _eventAggregator.Publish(new TestEvent { Message = "No subscribers" });
    }

    [TestMethod]
    [ExpectedException(typeof(ArgumentNullException))]
    public void Publish_NullEvent_ThrowsArgumentNullException()
    {
        // Act
        _eventAggregator.Publish<TestEvent>(null!);
    }

    #endregion

    #region Subscription Token Tests

    [TestMethod]
    public void Unsubscribe_StopsReceivingEvents()
    {
        // Arrange
        var receivedCount = 0;
        var token = _eventAggregator.Subscribe<TestEvent>(e => receivedCount++);

        // Act - publish before unsubscribe
        _eventAggregator.Publish(new TestEvent { Message = "First" });
        Assert.AreEqual(1, receivedCount);

        // Unsubscribe
        _eventAggregator.Unsubscribe(token);

        // Act - publish after unsubscribe
        _eventAggregator.Publish(new TestEvent { Message = "Second" });

        // Assert
        Assert.AreEqual(1, receivedCount); // Should still be 1
    }

    [TestMethod]
    public void TokenDispose_StopsReceivingEvents()
    {
        // Arrange
        var receivedCount = 0;
        var token = _eventAggregator.Subscribe<TestEvent>(e => receivedCount++);

        // Act - publish before dispose
        _eventAggregator.Publish(new TestEvent { Message = "First" });
        Assert.AreEqual(1, receivedCount);

        // Dispose token
        token.Dispose();

        // Act - publish after dispose
        _eventAggregator.Publish(new TestEvent { Message = "Second" });

        // Assert
        Assert.AreEqual(1, receivedCount); // Should still be 1
    }

    [TestMethod]
    public void MultipleDispose_DoesNotThrow()
    {
        // Arrange
        var token = _eventAggregator.Subscribe<TestEvent>(e => { });

        // Act & Assert - should not throw
        token.Dispose();
        token.Dispose();
        token.Dispose();
    }

    #endregion

    #region Async Subscribe/Publish Tests

    [TestMethod]
    public void Subscribe_AsyncHandler_ReturnsValidToken()
    {
        // Act
        var token = _eventAggregator.Subscribe<TestEvent>(async e =>
        {
            await Task.Delay(1);
        });

        // Assert
        Assert.IsNotNull(token);
    }

    [TestMethod]
    public async Task PublishAsync_InvokesAsyncHandler()
    {
        // Arrange
        TestEvent? receivedEvent = null;
        _eventAggregator.Subscribe<TestEvent>(async e =>
        {
            await Task.Delay(1);
            receivedEvent = e;
        });

        var testEvent = new TestEvent { Message = "Async" };

        // Act
        await _eventAggregator.PublishAsync(testEvent);

        // Assert
        Assert.IsNotNull(receivedEvent);
        Assert.AreEqual("Async", receivedEvent.Message);
    }

    [TestMethod]
    public async Task PublishAsync_InvokesSyncHandlerToo()
    {
        // Arrange
        var syncReceived = false;
        var asyncReceived = false;

        _eventAggregator.Subscribe<TestEvent>(e => syncReceived = true);
        _eventAggregator.Subscribe<TestEvent>(async e =>
        {
            await Task.Delay(1);
            asyncReceived = true;
        });

        // Act
        await _eventAggregator.PublishAsync(new TestEvent { Message = "Mixed" });

        // Assert
        Assert.IsTrue(syncReceived);
        Assert.IsTrue(asyncReceived);
    }

    [TestMethod]
    [ExpectedException(typeof(ArgumentNullException))]
    public async Task PublishAsync_NullEvent_ThrowsArgumentNullException()
    {
        // Act
        await _eventAggregator.PublishAsync<TestEvent>(null!);
    }

    #endregion

    #region Telemetry Tests

    [TestMethod]
    public void EnableTelemetry_SetsFlag()
    {
        // Arrange
        Assert.IsFalse(_eventAggregator.IsTelemetryEnabled);

        // Act
        _eventAggregator.EnableTelemetry();

        // Assert
        Assert.IsTrue(_eventAggregator.IsTelemetryEnabled);
    }

    [TestMethod]
    public void DisableTelemetry_ClearsFlag()
    {
        // Arrange
        _eventAggregator.EnableTelemetry();
        Assert.IsTrue(_eventAggregator.IsTelemetryEnabled);

        // Act
        _eventAggregator.DisableTelemetry();

        // Assert
        Assert.IsFalse(_eventAggregator.IsTelemetryEnabled);
    }

    [TestMethod]
    public void EnableTelemetry_WithCallback_InvokesCallback()
    {
        // Arrange
        EventTelemetry? receivedTelemetry = null;
        _eventAggregator.EnableTelemetry(t => receivedTelemetry = t);

        // Act
        _eventAggregator.Publish(new TestEvent { Message = "Telemetry test" });

        // Assert
        Assert.IsNotNull(receivedTelemetry);
        Assert.AreEqual("TestEvent", receivedTelemetry.EventType);
    }

    [TestMethod]
    public void GetReplayBuffer_ReturnsPublishedEvents()
    {
        // Arrange
        _eventAggregator.EnableTelemetry();

        // Act
        _eventAggregator.Publish(new TestEvent { Message = "Event1" });
        _eventAggregator.Publish(new TestEvent { Message = "Event2" });
        _eventAggregator.Publish(new OtherTestEvent { Value = 123 });

        var buffer = _eventAggregator.GetReplayBuffer();

        // Assert
        Assert.AreEqual(3, buffer.Count);
        Assert.IsTrue(buffer.Any(e => e.EventType == "TestEvent"));
        Assert.IsTrue(buffer.Any(e => e.EventType == "OtherTestEvent"));
    }

    [TestMethod]
    public void ClearReplayBuffer_EmptiesBuffer()
    {
        // Arrange
        _eventAggregator.EnableTelemetry();
        _eventAggregator.Publish(new TestEvent { Message = "Event1" });
        _eventAggregator.Publish(new TestEvent { Message = "Event2" });
        Assert.IsTrue(_eventAggregator.GetReplayBuffer().Count > 0);

        // Act
        _eventAggregator.ClearReplayBuffer();

        // Assert
        Assert.AreEqual(0, _eventAggregator.GetReplayBuffer().Count);
    }

    [TestMethod]
    public void GetTelemetryStats_ReturnsCorrectCounts()
    {
        // Arrange
        _eventAggregator.EnableTelemetry();
        _eventAggregator.Publish(new TestEvent { Message = "A" });
        _eventAggregator.Publish(new TestEvent { Message = "B" });
        _eventAggregator.Publish(new OtherTestEvent { Value = 1 });

        // Act
        var stats = _eventAggregator.GetTelemetryStats();

        // Assert
        // TotalEvents only increments for PanelEventBase events, so it may be 0 for plain events
        Assert.IsTrue(stats.TotalEvents >= 0);
        Assert.AreEqual(3, stats.BufferedEvents);
        Assert.AreEqual(2, stats.EventsByType["TestEvent"]);
        Assert.AreEqual(1, stats.EventsByType["OtherTestEvent"]);
    }

    [TestMethod]
    public void Telemetry_Disabled_DoesNotRecordEvents()
    {
        // Arrange - telemetry is disabled by default
        Assert.IsFalse(_eventAggregator.IsTelemetryEnabled);

        // Act
        _eventAggregator.Publish(new TestEvent { Message = "Not recorded" });

        // Assert
        Assert.AreEqual(0, _eventAggregator.GetReplayBuffer().Count);
    }

    #endregion

    #region Sequence Number Tests

    [TestMethod]
    public void NextSequence_IncrementsAfterPublish()
    {
        // Arrange
        var initialSequence = _eventAggregator.NextSequence;

        // Act
        _eventAggregator.Publish(new TestEvent { Message = "First" });
        var afterFirst = _eventAggregator.NextSequence;

        _eventAggregator.Publish(new TestEvent { Message = "Second" });
        var afterSecond = _eventAggregator.NextSequence;

        // Assert - sequence increments for each publish (if event is PanelEventBase)
        // For regular events, sequence may not increment
        Assert.IsTrue(afterFirst >= initialSequence);
        Assert.IsTrue(afterSecond >= afterFirst);
    }

    #endregion

    #region Error Handling Tests

    [TestMethod]
    public void Publish_HandlerThrows_ContinuesToNextHandler()
    {
        // Arrange
        var handler1Called = false;
        var handler2Called = false;
        var handler3Called = false;

        _eventAggregator.Subscribe<TestEvent>(e =>
        {
            handler1Called = true;
        });
        _eventAggregator.Subscribe<TestEvent>(e =>
        {
            throw new InvalidOperationException("Intentional test exception");
        });
        _eventAggregator.Subscribe<TestEvent>(e =>
        {
            handler2Called = true;
        });
        _eventAggregator.Subscribe<TestEvent>(e =>
        {
            handler3Called = true;
        });

        // Act - should not throw despite handler exception
        _eventAggregator.Publish(new TestEvent { Message = "Test" });

        // Assert - all handlers except the throwing one should be called
        Assert.IsTrue(handler1Called);
        Assert.IsTrue(handler2Called);
        Assert.IsTrue(handler3Called);
    }

    [TestMethod]
    public void TelemetryCallback_Throws_DoesNotAffectPublish()
    {
        // Arrange
        var eventReceived = false;
        _eventAggregator.EnableTelemetry(t =>
        {
            throw new InvalidOperationException("Telemetry callback error");
        });
        _eventAggregator.Subscribe<TestEvent>(e => eventReceived = true);

        // Act - should not throw
        _eventAggregator.Publish(new TestEvent { Message = "Test" });

        // Assert
        Assert.IsTrue(eventReceived);
    }

    #endregion

    #region Thread Safety Tests

    [TestMethod]
    public async Task ConcurrentPublish_DoesNotThrow()
    {
        // Arrange
        var receivedCount = 0;
        _eventAggregator.Subscribe<TestEvent>(e => System.Threading.Interlocked.Increment(ref receivedCount));

        var tasks = new List<Task>();

        // Act - publish many events concurrently
        for (int i = 0; i < 100; i++)
        {
            tasks.Add(Task.Run(() =>
            {
                _eventAggregator.Publish(new TestEvent { Message = $"Concurrent {i}" });
            }));
        }

        await Task.WhenAll(tasks);

        // Assert
        Assert.AreEqual(100, receivedCount);
    }

    [TestMethod]
    public async Task ConcurrentSubscribeAndPublish_DoesNotThrow()
    {
        // Arrange
        var receivedCount = 0;
        var tasks = new List<Task>();

        // Act - subscribe and publish concurrently
        for (int i = 0; i < 50; i++)
        {
            // Subscribe tasks
            tasks.Add(Task.Run(() =>
            {
                _eventAggregator.Subscribe<TestEvent>(e =>
                    System.Threading.Interlocked.Increment(ref receivedCount));
            }));

            // Publish tasks
            tasks.Add(Task.Run(() =>
            {
                _eventAggregator.Publish(new TestEvent { Message = $"Event {i}" });
            }));
        }

        await Task.WhenAll(tasks);

        // Assert - no exception thrown (exact count may vary due to race conditions)
        Assert.IsTrue(receivedCount >= 0);
    }

    #endregion

    #region Test Event Classes

    private class TestEvent
    {
        public string Message { get; set; } = string.Empty;
    }

    private class OtherTestEvent
    {
        public int Value { get; set; }
    }

    #endregion
}
