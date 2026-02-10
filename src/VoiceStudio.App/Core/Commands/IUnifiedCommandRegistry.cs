using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Input;

namespace VoiceStudio.App.Core.Commands
{
    /// <summary>
    /// Unified command registry that centralizes all application commands.
    /// Provides command registration, execution, status tracking, and integration
    /// with keyboard shortcuts.
    /// </summary>
    public interface IUnifiedCommandRegistry
    {
        #region Registration

        /// <summary>
        /// Registers a synchronous command handler.
        /// </summary>
        /// <param name="descriptor">Command metadata.</param>
        /// <param name="handler">The command handler.</param>
        void Register(CommandDescriptor descriptor, ISyncCommandHandler handler);

        /// <summary>
        /// Registers an asynchronous command handler.
        /// </summary>
        /// <param name="descriptor">Command metadata.</param>
        /// <param name="handler">The command handler.</param>
        void Register(CommandDescriptor descriptor, IAsyncCommandHandler handler);

        /// <summary>
        /// Registers a command with a simple action delegate.
        /// </summary>
        /// <param name="descriptor">Command metadata.</param>
        /// <param name="execute">The action to execute.</param>
        /// <param name="canExecute">Optional predicate to determine if command can execute.</param>
        void Register(CommandDescriptor descriptor, Action<object?> execute, Func<object?, bool>? canExecute = null);

        /// <summary>
        /// Registers a command with an async action delegate.
        /// </summary>
        /// <param name="descriptor">Command metadata.</param>
        /// <param name="executeAsync">The async action to execute.</param>
        /// <param name="canExecute">Optional predicate to determine if command can execute.</param>
        void Register(CommandDescriptor descriptor, Func<object?, CancellationToken, Task> executeAsync, Func<object?, bool>? canExecute = null);

        /// <summary>
        /// Unregisters a command by ID.
        /// </summary>
        /// <param name="commandId">The command ID to unregister.</param>
        /// <returns>True if the command was found and removed.</returns>
        bool Unregister(string commandId);

        #endregion

        #region Execution

        /// <summary>
        /// Executes a command by ID.
        /// </summary>
        /// <param name="commandId">The command ID.</param>
        /// <param name="parameter">Optional parameter to pass to the command.</param>
        /// <param name="cancellationToken">Cancellation token.</param>
        /// <returns>A task representing the command execution.</returns>
        Task ExecuteAsync(string commandId, object? parameter = null, CancellationToken cancellationToken = default);

        /// <summary>
        /// Determines if a command can execute.
        /// </summary>
        /// <param name="commandId">The command ID.</param>
        /// <param name="parameter">Optional parameter to evaluate.</param>
        /// <returns>True if the command can execute.</returns>
        bool CanExecute(string commandId, object? parameter = null);

        /// <summary>
        /// Gets an ICommand wrapper for a registered command.
        /// Useful for XAML binding.
        /// </summary>
        /// <param name="commandId">The command ID.</param>
        /// <returns>An ICommand wrapper, or null if not found.</returns>
        ICommand? GetCommand(string commandId);

        #endregion

        #region Discovery

        /// <summary>
        /// Gets the descriptor for a command.
        /// </summary>
        /// <param name="commandId">The command ID.</param>
        /// <returns>The command descriptor, or null if not found.</returns>
        CommandDescriptor? GetDescriptor(string commandId);

        /// <summary>
        /// Gets all registered commands.
        /// </summary>
        /// <returns>A read-only list of all command descriptors.</returns>
        IReadOnlyList<CommandDescriptor> GetAllCommands();

        /// <summary>
        /// Gets commands filtered by category.
        /// </summary>
        /// <param name="category">The category to filter by.</param>
        /// <returns>Commands in the specified category.</returns>
        IReadOnlyList<CommandDescriptor> GetCommandsByCategory(string category);

        /// <summary>
        /// Gets all available categories.
        /// </summary>
        /// <returns>A list of category names.</returns>
        IReadOnlyList<string> GetCategories();

        /// <summary>
        /// Checks if a command is registered.
        /// </summary>
        /// <param name="commandId">The command ID.</param>
        /// <returns>True if the command is registered.</returns>
        bool IsRegistered(string commandId);

        #endregion

        #region Status Tracking

        /// <summary>
        /// Gets the runtime state for a command.
        /// </summary>
        /// <param name="commandId">The command ID.</param>
        /// <returns>The runtime state, or null if not found.</returns>
        CommandRuntimeState? GetState(string commandId);

        /// <summary>
        /// Gets the current status of a command.
        /// </summary>
        /// <param name="commandId">The command ID.</param>
        /// <returns>The command status.</returns>
        CommandStatus GetStatus(string commandId);

        /// <summary>
        /// Gets a health report of all commands.
        /// </summary>
        /// <returns>A dictionary mapping command IDs to their status.</returns>
        IReadOnlyDictionary<string, CommandStatus> GetHealthReport();

        /// <summary>
        /// Gets the count of commands by status.
        /// </summary>
        /// <returns>A dictionary mapping status to count.</returns>
        IReadOnlyDictionary<CommandStatus, int> GetStatusCounts();

        #endregion

        #region Events

        /// <summary>
        /// Raised when a command executes successfully.
        /// </summary>
        event EventHandler<CommandExecutedEventArgs>? CommandExecuted;

        /// <summary>
        /// Raised when a command execution fails.
        /// </summary>
        event EventHandler<CommandFailedEventArgs>? CommandFailed;

        /// <summary>
        /// Raised when a command is registered.
        /// </summary>
        event EventHandler<CommandDescriptor>? CommandRegistered;

        /// <summary>
        /// Raised when a command is unregistered.
        /// </summary>
        event EventHandler<string>? CommandUnregistered;

        #endregion
    }
}
