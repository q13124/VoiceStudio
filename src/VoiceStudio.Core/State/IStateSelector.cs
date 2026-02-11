using System;

namespace VoiceStudio.Core.State
{
  /// <summary>
  /// Typed interface for state selectors.
  /// </summary>
  /// <typeparam name="T">The type of the derived value.</typeparam>
  public interface IStateSelector<T>
  {
    /// <summary>
    /// Gets the current value.
    /// </summary>
    T Value { get; }

    /// <summary>
    /// Occurs when the value changes.
    /// </summary>
    event EventHandler<T>? ValueChanged;
  }
}
