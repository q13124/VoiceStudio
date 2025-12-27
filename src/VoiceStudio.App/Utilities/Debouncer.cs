using System;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.App.Utilities
{
    /// <summary>
    /// Utility class for debouncing expensive operations.
    /// Delays execution until a specified time has passed since the last invocation.
    /// </summary>
    public class Debouncer
    {
        private readonly TimeSpan _delay;
        private readonly Action? _action;
        private readonly Func<Task>? _asyncAction;
        private CancellationTokenSource? _cancellationTokenSource;
        private readonly object _lock = new object();

        /// <summary>
        /// Creates a debouncer for synchronous actions.
        /// </summary>
        /// <param name="action">The action to debounce</param>
        /// <param name="delay">The delay in milliseconds</param>
        public Debouncer(Action action, int delayMs)
        {
            _action = action ?? throw new ArgumentNullException(nameof(action));
            _delay = TimeSpan.FromMilliseconds(delayMs);
        }

        /// <summary>
        /// Creates a debouncer for asynchronous actions.
        /// </summary>
        /// <param name="asyncAction">The async action to debounce</param>
        /// <param name="delay">The delay in milliseconds</param>
        public Debouncer(Func<Task> asyncAction, int delayMs)
        {
            _asyncAction = asyncAction ?? throw new ArgumentNullException(nameof(asyncAction));
            _delay = TimeSpan.FromMilliseconds(delayMs);
        }

        /// <summary>
        /// Invokes the debounced action. Cancels any pending invocation and schedules a new one.
        /// </summary>
        public void Invoke()
        {
            lock (_lock)
            {
                _cancellationTokenSource?.Cancel();
                _cancellationTokenSource?.Dispose();
                _cancellationTokenSource = new CancellationTokenSource();

                var token = _cancellationTokenSource.Token;

                if (_action != null)
                {
                    _ = Task.Run(async () =>
                    {
                        try
                        {
                            await Task.Delay(_delay, token);
                            if (!token.IsCancellationRequested)
                            {
                                _action();
                            }
                        }
                        catch (OperationCanceledException)
                        {
                            // Expected when debouncing
                        }
                    }, token);
                }
                else if (_asyncAction != null)
                {
                    _ = Task.Run(async () =>
                    {
                        try
                        {
                            await Task.Delay(_delay, token);
                            if (!token.IsCancellationRequested)
                            {
                                await _asyncAction();
                            }
                        }
                        catch (OperationCanceledException)
                        {
                            // Expected when debouncing
                        }
                    }, token);
                }
            }
        }

        /// <summary>
        /// Cancels any pending invocation.
        /// </summary>
        public void Cancel()
        {
            lock (_lock)
            {
                _cancellationTokenSource?.Cancel();
                _cancellationTokenSource?.Dispose();
                _cancellationTokenSource = null;
            }
        }

        /// <summary>
        /// Disposes the debouncer and cancels any pending invocation.
        /// </summary>
        public void Dispose()
        {
            Cancel();
        }
    }
}
