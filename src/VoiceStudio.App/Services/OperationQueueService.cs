using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using VoiceStudio.Core.Exceptions;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Represents a queued operation.
    /// </summary>
    public class QueuedOperation
    {
        public string Id { get; set; } = Guid.NewGuid().ToString();
        public string Name { get; set; } = string.Empty;
        public Func<Task> Operation { get; set; } = null!;
        public DateTime QueuedAt { get; set; } = DateTime.UtcNow;
        public int RetryCount { get; set; } = 0;
        public int MaxRetries { get; set; } = 3;
        public object? State { get; set; }
    }

    /// <summary>
    /// Service for queuing operations when offline and executing them when connection is restored.
    /// </summary>
    public class OperationQueueService
    {
        private readonly List<QueuedOperation> _queue = new();
        private readonly object _lock = new();
        private bool _isProcessing = false;

        public event EventHandler<int>? QueueCountChanged;
        public event EventHandler<QueuedOperation>? OperationQueued;
        public event EventHandler<QueuedOperation>? OperationExecuted;
        public event EventHandler<QueuedOperation>? OperationFailed;

        /// <summary>
        /// Gets the current queue count.
        /// </summary>
        public int QueueCount
        {
            get
            {
                lock (_lock)
                {
                    return _queue.Count;
                }
            }
        }

        /// <summary>
        /// Gets all queued operations.
        /// </summary>
        public IReadOnlyList<QueuedOperation> GetQueuedOperations()
        {
            lock (_lock)
            {
                return _queue.ToList().AsReadOnly();
            }
        }

        /// <summary>
        /// Queues an operation to be executed when connection is restored.
        /// </summary>
        public string QueueOperation(string name, Func<Task> operation, object? state = null, int maxRetries = 3)
        {
            var queuedOp = new QueuedOperation
            {
                Name = name,
                Operation = operation,
                State = state,
                MaxRetries = maxRetries
            };

            lock (_lock)
            {
                _queue.Add(queuedOp);
            }

            OperationQueued?.Invoke(this, queuedOp);
            QueueCountChanged?.Invoke(this, QueueCount);

            return queuedOp.Id;
        }

        /// <summary>
        /// Removes an operation from the queue.
        /// </summary>
        public bool RemoveOperation(string operationId)
        {
            lock (_lock)
            {
                var op = _queue.FirstOrDefault(o => o.Id == operationId);
                if (op != null)
                {
                    _queue.Remove(op);
                    QueueCountChanged?.Invoke(this, QueueCount);
                    return true;
                }
            }
            return false;
        }

        /// <summary>
        /// Clears all queued operations.
        /// </summary>
        public void ClearQueue()
        {
            lock (_lock)
            {
                _queue.Clear();
            }
            QueueCountChanged?.Invoke(this, QueueCount);
        }

        /// <summary>
        /// Processes all queued operations (called when connection is restored).
        /// </summary>
        public async Task ProcessQueueAsync()
        {
            if (_isProcessing)
                return;

            _isProcessing = true;

            try
            {
                List<QueuedOperation> operationsToProcess;
                lock (_lock)
                {
                    operationsToProcess = _queue.ToList();
                }

                foreach (var operation in operationsToProcess)
                {
                    try
                    {
                        await operation.Operation();
                        
                        lock (_lock)
                        {
                            _queue.Remove(operation);
                        }

                        OperationExecuted?.Invoke(this, operation);
                        QueueCountChanged?.Invoke(this, QueueCount);
                    }
                    catch (Exception ex)
                    {
                        operation.RetryCount++;

                        // Check if we should retry
                        if (operation.RetryCount >= operation.MaxRetries || !IsTransientError(ex))
                        {
                            // Remove from queue if max retries reached or not retryable
                            lock (_lock)
                            {
                                _queue.Remove(operation);
                            }

                            OperationFailed?.Invoke(this, operation);
                            QueueCountChanged?.Invoke(this, QueueCount);
                        }
                        // Otherwise, keep in queue for next attempt
                    }
                }
            }
            finally
            {
                _isProcessing = false;
            }
        }

        private static bool IsTransientError(Exception ex)
        {
            return ex switch
            {
                BackendUnavailableException => true,
                BackendTimeoutException => true,
                BackendServerException bex when bex.StatusCode >= 500 => true,
                System.Net.Http.HttpRequestException => true,
                TaskCanceledException => true,
                TimeoutException => true,
                _ => false
            };
        }
    }
}

