using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.App.Core.Commands
{
    /// <summary>
    /// Base interface for all command handlers.
    /// </summary>
    public interface ICommandHandler
    {
        /// <summary>
        /// Determines whether the command can execute with the given parameter.
        /// </summary>
        /// <param name="parameter">Optional command parameter.</param>
        /// <returns>True if the command can execute, false otherwise.</returns>
        bool CanExecute(object? parameter);
    }

    /// <summary>
    /// Interface for synchronous command handlers.
    /// </summary>
    public interface ISyncCommandHandler : ICommandHandler
    {
        /// <summary>
        /// Executes the command synchronously.
        /// </summary>
        /// <param name="parameter">Optional command parameter.</param>
        void Execute(object? parameter);
    }

    /// <summary>
    /// Interface for asynchronous command handlers.
    /// </summary>
    public interface IAsyncCommandHandler : ICommandHandler
    {
        /// <summary>
        /// Executes the command asynchronously.
        /// </summary>
        /// <param name="parameter">Optional command parameter.</param>
        /// <param name="cancellationToken">Cancellation token.</param>
        /// <returns>A task representing the asynchronous operation.</returns>
        Task ExecuteAsync(object? parameter, CancellationToken cancellationToken = default);
    }

    /// <summary>
    /// Typed interface for synchronous command handlers with strongly-typed parameters.
    /// </summary>
    /// <typeparam name="TParameter">The type of the command parameter.</typeparam>
    public interface ISyncCommandHandler<in TParameter> : ICommandHandler
    {
        /// <summary>
        /// Determines whether the command can execute with the given parameter.
        /// </summary>
        bool CanExecute(TParameter? parameter);

        /// <summary>
        /// Executes the command synchronously with the typed parameter.
        /// </summary>
        void Execute(TParameter? parameter);

        // Explicit interface implementation for untyped version
        bool ICommandHandler.CanExecute(object? parameter) => CanExecute((TParameter?)parameter);
    }

    /// <summary>
    /// Typed interface for asynchronous command handlers with strongly-typed parameters.
    /// </summary>
    /// <typeparam name="TParameter">The type of the command parameter.</typeparam>
    public interface IAsyncCommandHandler<in TParameter> : ICommandHandler
    {
        /// <summary>
        /// Determines whether the command can execute with the given parameter.
        /// </summary>
        bool CanExecute(TParameter? parameter);

        /// <summary>
        /// Executes the command asynchronously with the typed parameter.
        /// </summary>
        Task ExecuteAsync(TParameter? parameter, CancellationToken cancellationToken = default);

        // Explicit interface implementation for untyped version
        bool ICommandHandler.CanExecute(object? parameter) => CanExecute((TParameter?)parameter);
    }
}
