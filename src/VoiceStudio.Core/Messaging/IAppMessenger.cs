using System;

namespace VoiceStudio.Core.Messaging
{
  /// <summary>
  /// Abstraction for application-wide messaging using weak references.
  /// Enables decoupled communication between ViewModels and services.
  /// </summary>
  public interface IAppMessenger
  {
    /// <summary>
    /// Registers a recipient for a message type.
    /// </summary>
    /// <typeparam name="TMessage">The message type to register for.</typeparam>
    /// <param name="recipient">The recipient object.</param>
    /// <param name="handler">The message handler.</param>
    void Register<TMessage>(object recipient, Action<TMessage> handler)
        where TMessage : class;

    /// <summary>
    /// Registers a recipient for a message type with a specific token.
    /// </summary>
    /// <typeparam name="TMessage">The message type to register for.</typeparam>
    /// <typeparam name="TToken">The token type.</typeparam>
    /// <param name="recipient">The recipient object.</param>
    /// <param name="token">The token to filter messages.</param>
    /// <param name="handler">The message handler.</param>
    void Register<TMessage, TToken>(object recipient, TToken token, Action<TMessage> handler)
        where TMessage : class
        where TToken : IEquatable<TToken>;

    /// <summary>
    /// Unregisters a recipient from all message types.
    /// </summary>
    /// <param name="recipient">The recipient to unregister.</param>
    void UnregisterAll(object recipient);

    /// <summary>
    /// Unregisters a recipient from a specific message type.
    /// </summary>
    /// <typeparam name="TMessage">The message type to unregister from.</typeparam>
    /// <param name="recipient">The recipient to unregister.</param>
    void Unregister<TMessage>(object recipient)
        where TMessage : class;

    /// <summary>
    /// Unregisters a recipient from a specific message type and token.
    /// </summary>
    /// <typeparam name="TMessage">The message type to unregister from.</typeparam>
    /// <typeparam name="TToken">The token type.</typeparam>
    /// <param name="recipient">The recipient to unregister.</param>
    /// <param name="token">The token that was used for registration.</param>
    void Unregister<TMessage, TToken>(object recipient, TToken token)
        where TMessage : class
        where TToken : IEquatable<TToken>;

    /// <summary>
    /// Sends a message to all registered recipients.
    /// </summary>
    /// <typeparam name="TMessage">The message type.</typeparam>
    /// <param name="message">The message to send.</param>
    void Send<TMessage>(TMessage message)
        where TMessage : class;

    /// <summary>
    /// Sends a message to all registered recipients with a specific token.
    /// </summary>
    /// <typeparam name="TMessage">The message type.</typeparam>
    /// <typeparam name="TToken">The token type.</typeparam>
    /// <param name="message">The message to send.</param>
    /// <param name="token">The token to filter recipients.</param>
    void Send<TMessage, TToken>(TMessage message, TToken token)
        where TMessage : class
        where TToken : IEquatable<TToken>;

    /// <summary>
    /// Checks if a recipient is registered for a specific message type.
    /// </summary>
    /// <typeparam name="TMessage">The message type.</typeparam>
    /// <param name="recipient">The recipient to check.</param>
    /// <returns>True if the recipient is registered.</returns>
    bool IsRegistered<TMessage>(object recipient)
        where TMessage : class;

    /// <summary>
    /// Resets the messenger, unregistering all recipients.
    /// </summary>
    void Reset();
  }
}
