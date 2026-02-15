using System;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Services
{
  /// <summary>
  /// Interface for event aggregator service providing pub/sub pattern for cross-panel synchronization.
  /// </summary>
  /// <remarks>
  /// Backend-Frontend Integration Plan - Phase 4: Cross-panel synchronization
  /// This enables decoupled communication between ViewModels without direct dependencies.
  /// </remarks>
  public interface IEventAggregator
  {
    /// <summary>
    /// Publishes an event to all subscribers.
    /// </summary>
    /// <typeparam name="TEvent">The type of event to publish.</typeparam>
    /// <param name="eventMessage">The event message to publish.</param>
    void Publish<TEvent>(TEvent eventMessage) where TEvent : class;

    /// <summary>
    /// Publishes an event asynchronously to all subscribers.
    /// </summary>
    /// <typeparam name="TEvent">The type of event to publish.</typeparam>
    /// <param name="eventMessage">The event message to publish.</param>
    /// <returns>A task representing the asynchronous operation.</returns>
    Task PublishAsync<TEvent>(TEvent eventMessage) where TEvent : class;

    /// <summary>
    /// Subscribes to an event type.
    /// </summary>
    /// <typeparam name="TEvent">The type of event to subscribe to.</typeparam>
    /// <param name="handler">The action to invoke when the event is published.</param>
    /// <returns>A subscription token that can be used to unsubscribe.</returns>
    ISubscriptionToken Subscribe<TEvent>(Action<TEvent> handler) where TEvent : class;

    /// <summary>
    /// Subscribes to an event type with an async handler.
    /// </summary>
    /// <typeparam name="TEvent">The type of event to subscribe to.</typeparam>
    /// <param name="handler">The async function to invoke when the event is published.</param>
    /// <returns>A subscription token that can be used to unsubscribe.</returns>
    ISubscriptionToken Subscribe<TEvent>(Func<TEvent, Task> handler) where TEvent : class;

    /// <summary>
    /// Unsubscribes using a subscription token.
    /// </summary>
    /// <param name="token">The subscription token returned from Subscribe.</param>
    void Unsubscribe(ISubscriptionToken token);

    /// <summary>
    /// Unsubscribes all handlers for a specific subscriber object.
    /// </summary>
    /// <param name="subscriber">The subscriber object to unsubscribe.</param>
    void UnsubscribeAll(object subscriber);
  }

  /// <summary>
  /// Token representing a subscription to an event.
  /// </summary>
  public interface ISubscriptionToken : IDisposable
  {
    /// <summary>
    /// Gets whether the subscription is still active.
    /// </summary>
    bool IsActive { get; }

    /// <summary>
    /// Gets the type of event this subscription is for.
    /// </summary>
    Type EventType { get; }
  }
}
