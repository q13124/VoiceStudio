using System;
using CommunityToolkit.Mvvm.Messaging;
using VoiceStudio.Core.Messaging;

namespace VoiceStudio.App.Services.Messaging
{
  /// <summary>
  /// Application messenger implementation using WeakReferenceMessenger.
  /// Provides decoupled communication between ViewModels and services.
  /// </summary>
  public sealed class AppMessenger : IAppMessenger
  {
    private readonly IMessenger _messenger;

    /// <summary>
    /// Gets the default instance of the app messenger.
    /// </summary>
    public static IAppMessenger Default { get; } = new AppMessenger(WeakReferenceMessenger.Default);

    /// <summary>
    /// Creates a new instance with the default WeakReferenceMessenger.
    /// </summary>
    public AppMessenger() : this(WeakReferenceMessenger.Default)
    {
    }

    /// <summary>
    /// Creates a new instance with a custom messenger (for testing).
    /// </summary>
    /// <param name="messenger">The messenger instance to use.</param>
    public AppMessenger(IMessenger messenger)
    {
      _messenger = messenger ?? throw new ArgumentNullException(nameof(messenger));
    }

    /// <inheritdoc />
    public void Register<TMessage>(object recipient, Action<TMessage> handler)
        where TMessage : class
    {
      if (recipient == null) throw new ArgumentNullException(nameof(recipient));
      if (handler == null) throw new ArgumentNullException(nameof(handler));

      _messenger.Register<TMessage>(recipient, (r, m) => handler(m));
    }

    /// <inheritdoc />
    public void Register<TMessage, TToken>(object recipient, TToken token, Action<TMessage> handler)
        where TMessage : class
        where TToken : IEquatable<TToken>
    {
      if (recipient == null) throw new ArgumentNullException(nameof(recipient));
      if (token == null) throw new ArgumentNullException(nameof(token));
      if (handler == null) throw new ArgumentNullException(nameof(handler));

      _messenger.Register<TMessage, TToken>(recipient, token, (r, m) => handler(m));
    }

    /// <inheritdoc />
    public void UnregisterAll(object recipient)
    {
      if (recipient == null) throw new ArgumentNullException(nameof(recipient));

      _messenger.UnregisterAll(recipient);
    }

    /// <inheritdoc />
    public void Unregister<TMessage>(object recipient)
        where TMessage : class
    {
      if (recipient == null) throw new ArgumentNullException(nameof(recipient));

      _messenger.Unregister<TMessage>(recipient);
    }

    /// <inheritdoc />
    public void Unregister<TMessage, TToken>(object recipient, TToken token)
        where TMessage : class
        where TToken : IEquatable<TToken>
    {
      if (recipient == null) throw new ArgumentNullException(nameof(recipient));
      if (token == null) throw new ArgumentNullException(nameof(token));

      _messenger.Unregister<TMessage, TToken>(recipient, token);
    }

    /// <inheritdoc />
    public void Send<TMessage>(TMessage message)
        where TMessage : class
    {
      if (message == null) throw new ArgumentNullException(nameof(message));

      _messenger.Send(message);
    }

    /// <inheritdoc />
    public void Send<TMessage, TToken>(TMessage message, TToken token)
        where TMessage : class
        where TToken : IEquatable<TToken>
    {
      if (message == null) throw new ArgumentNullException(nameof(message));
      if (token == null) throw new ArgumentNullException(nameof(token));

      _messenger.Send(message, token);
    }

    /// <inheritdoc />
    public bool IsRegistered<TMessage>(object recipient)
        where TMessage : class
    {
      if (recipient == null) throw new ArgumentNullException(nameof(recipient));

      return _messenger.IsRegistered<TMessage>(recipient);
    }

    /// <inheritdoc />
    public void Reset()
    {
      _messenger.Reset();
    }
  }
}
