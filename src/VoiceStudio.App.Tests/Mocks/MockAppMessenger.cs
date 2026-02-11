using System;
using System.Collections.Generic;
using VoiceStudio.Core.Messaging;

namespace VoiceStudio.App.Tests.Mocks
{
  /// <summary>
  /// Mock implementation of <see cref="IAppMessenger"/> for testing.
  /// </summary>
  public class MockAppMessenger : IAppMessenger
  {
    private readonly Dictionary<Type, List<(object Recipient, Delegate Handler)>> _handlers = new();
    private readonly Dictionary<(Type, object), List<(object Recipient, Delegate Handler)>> _tokenHandlers = new();
    private readonly List<object> _sentMessages = new();

    /// <summary>
    /// Gets all messages that have been sent.
    /// </summary>
    public IReadOnlyList<object> SentMessages => _sentMessages;

    /// <summary>
    /// Gets messages of a specific type that have been sent.
    /// </summary>
    public IEnumerable<T> GetSentMessages<T>() where T : class
    {
      foreach (var msg in _sentMessages)
      {
        if (msg is T typedMsg)
          yield return typedMsg;
      }
    }

    /// <summary>
    /// Clears all sent messages.
    /// </summary>
    public void ClearSentMessages()
    {
      _sentMessages.Clear();
    }

    /// <inheritdoc />
    public void Register<TMessage>(object recipient, Action<TMessage> handler)
        where TMessage : class
    {
      var type = typeof(TMessage);
      if (!_handlers.ContainsKey(type))
        _handlers[type] = new List<(object, Delegate)>();

      _handlers[type].Add((recipient, handler));
    }

    /// <inheritdoc />
    public void Register<TMessage, TToken>(object recipient, TToken token, Action<TMessage> handler)
        where TMessage : class
        where TToken : IEquatable<TToken>
    {
      var key = (typeof(TMessage), (object)token!);
      if (!_tokenHandlers.ContainsKey(key))
        _tokenHandlers[key] = new List<(object, Delegate)>();

      _tokenHandlers[key].Add((recipient, handler));
    }

    /// <inheritdoc />
    public void UnregisterAll(object recipient)
    {
      foreach (var handlers in _handlers.Values)
      {
        handlers.RemoveAll(h => h.Recipient == recipient);
      }

      foreach (var handlers in _tokenHandlers.Values)
      {
        handlers.RemoveAll(h => h.Recipient == recipient);
      }
    }

    /// <inheritdoc />
    public void Unregister<TMessage>(object recipient)
        where TMessage : class
    {
      var type = typeof(TMessage);
      if (_handlers.TryGetValue(type, out var handlers))
      {
        handlers.RemoveAll(h => h.Recipient == recipient);
      }
    }

    /// <inheritdoc />
    public void Unregister<TMessage, TToken>(object recipient, TToken token)
        where TMessage : class
        where TToken : IEquatable<TToken>
    {
      var key = (typeof(TMessage), (object)token!);
      if (_tokenHandlers.TryGetValue(key, out var handlers))
      {
        handlers.RemoveAll(h => h.Recipient == recipient);
      }
    }

    /// <inheritdoc />
    public void Send<TMessage>(TMessage message)
        where TMessage : class
    {
      _sentMessages.Add(message);

      var type = typeof(TMessage);
      if (_handlers.TryGetValue(type, out var handlers))
      {
        foreach (var (_, handler) in handlers)
        {
          ((Action<TMessage>)handler)(message);
        }
      }
    }

    /// <inheritdoc />
    public void Send<TMessage, TToken>(TMessage message, TToken token)
        where TMessage : class
        where TToken : IEquatable<TToken>
    {
      _sentMessages.Add(message);

      var key = (typeof(TMessage), (object)token!);
      if (_tokenHandlers.TryGetValue(key, out var handlers))
      {
        foreach (var (_, handler) in handlers)
        {
          ((Action<TMessage>)handler)(message);
        }
      }
    }

    /// <inheritdoc />
    public bool IsRegistered<TMessage>(object recipient)
        where TMessage : class
    {
      var type = typeof(TMessage);
      if (_handlers.TryGetValue(type, out var handlers))
      {
        return handlers.Exists(h => h.Recipient == recipient);
      }
      return false;
    }

    /// <inheritdoc />
    public void Reset()
    {
      _handlers.Clear();
      _tokenHandlers.Clear();
      _sentMessages.Clear();
    }
  }
}
