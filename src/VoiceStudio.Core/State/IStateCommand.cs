namespace VoiceStudio.Core.State
{
  /// <summary>
  /// Base interface for state commands.
  /// Commands encapsulate a state mutation operation.
  /// </summary>
  public interface IStateCommand
  {
    /// <summary>
    /// Gets the name of the command for debugging/telemetry.
    /// </summary>
    string Name { get; }

    /// <summary>
    /// Executes the command, returning the new state.
    /// </summary>
    /// <param name="state">The current state.</param>
    /// <returns>The new state after executing the command.</returns>
    AppState Execute(AppState state);
  }

  /// <summary>
  /// Interface for undoable state commands.
  /// Commands that implement this interface can be undone.
  /// </summary>
  public interface IUndoableCommand : IStateCommand
  {
    /// <summary>
    /// Undoes the command, returning the previous state.
    /// </summary>
    /// <param name="state">The current state.</param>
    /// <returns>The state after undoing the command.</returns>
    AppState Undo(AppState state);

    /// <summary>
    /// Gets a value indicating whether this command can be merged with another command.
    /// Used for combining rapid successive changes into a single undo operation.
    /// </summary>
    bool CanMerge { get; }

    /// <summary>
    /// Merges this command with another command of the same type.
    /// </summary>
    /// <param name="other">The other command to merge with.</param>
    /// <returns>A merged command, or null if merge is not possible.</returns>
    IUndoableCommand? Merge(IUndoableCommand other);
  }

  /// <summary>
  /// Abstract base class for undoable commands with built-in state snapshot.
  /// </summary>
  public abstract class UndoableCommandBase : IUndoableCommand
  {
    private AppState? _previousState;

    /// <inheritdoc />
    public abstract string Name { get; }

    /// <inheritdoc />
    public virtual bool CanMerge => false;

    /// <inheritdoc />
    public AppState Execute(AppState state)
    {
      _previousState = state;
      return ExecuteCore(state);
    }

    /// <inheritdoc />
    public AppState Undo(AppState state)
    {
      // Return the snapshotted previous state if available
      return _previousState ?? UndoCore(state);
    }

    /// <inheritdoc />
    public virtual IUndoableCommand? Merge(IUndoableCommand other) => null;

    /// <summary>
    /// Core execution logic to be implemented by derived classes.
    /// </summary>
    protected abstract AppState ExecuteCore(AppState state);

    /// <summary>
    /// Core undo logic. Default returns previous snapshot.
    /// Override for commands that need custom undo logic.
    /// </summary>
    protected virtual AppState UndoCore(AppState state) => state;
  }
}
