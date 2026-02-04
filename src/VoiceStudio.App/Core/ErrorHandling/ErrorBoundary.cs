// Copyright (c) VoiceStudio. All rights reserved.
// Licensed under the MIT License.

using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using VoiceStudio.App.Logging;

namespace VoiceStudio.App.Core.ErrorHandling
{
    /// <summary>
    /// Centralized error handling that makes logging the default path.
    /// Replaces empty catch blocks with logged, tracked error handling.
    /// </summary>
    public static class ErrorBoundary
    {
        /// <summary>
        /// Executes an action with automatic error logging on failure.
        /// </summary>
        /// <typeparam name="T">The return type of the action.</typeparam>
        /// <param name="action">The action to execute.</param>
        /// <param name="fallback">The fallback value to return on failure.</param>
        /// <param name="context">Optional context for the error message.</param>
        /// <param name="caller">Automatically captured caller method name.</param>
        /// <returns>The result of the action, or the fallback value on failure.</returns>
        public static T Execute<T>(
            Func<T> action,
            T fallback,
            string? context = null,
            [CallerMemberName] string caller = "")
        {
            try
            {
                return action();
            }
            catch (Exception ex)
            {
                var message = string.IsNullOrEmpty(context)
                    ? $"{caller} failed: {ex.Message}"
                    : $"{caller} failed ({context}): {ex.Message}";

                ErrorLogger.LogWarning(message, "ErrorBoundary",
                    new Dictionary<string, object>
                    {
                        ["exception_type"] = ex.GetType().Name,
                        ["caller"] = caller,
                        ["context"] = context ?? string.Empty
                    });

                return fallback;
            }
        }

        /// <summary>
        /// Executes an async action with automatic error logging on failure.
        /// </summary>
        /// <typeparam name="T">The return type of the action.</typeparam>
        /// <param name="action">The async action to execute.</param>
        /// <param name="fallback">The fallback value to return on failure.</param>
        /// <param name="context">Optional context for the error message.</param>
        /// <param name="caller">Automatically captured caller method name.</param>
        /// <returns>The result of the action, or the fallback value on failure.</returns>
        public static async Task<T> ExecuteAsync<T>(
            Func<Task<T>> action,
            T fallback,
            string? context = null,
            [CallerMemberName] string caller = "")
        {
            try
            {
                return await action();
            }
            catch (Exception ex)
            {
                var message = string.IsNullOrEmpty(context)
                    ? $"{caller} failed: {ex.Message}"
                    : $"{caller} failed ({context}): {ex.Message}";

                ErrorLogger.LogWarning(message, "ErrorBoundary",
                    new Dictionary<string, object>
                    {
                        ["exception_type"] = ex.GetType().Name,
                        ["caller"] = caller,
                        ["context"] = context ?? string.Empty
                    });

                return fallback;
            }
        }

        /// <summary>
        /// Executes a void action with automatic error logging on failure.
        /// </summary>
        /// <param name="action">The action to execute.</param>
        /// <param name="context">Optional context for the error message.</param>
        /// <param name="caller">Automatically captured caller method name.</param>
        /// <returns>True if the action succeeded, false otherwise.</returns>
        public static bool TryExecute(
            Action action,
            string? context = null,
            [CallerMemberName] string caller = "")
        {
            try
            {
                action();
                return true;
            }
            catch (Exception ex)
            {
                var message = string.IsNullOrEmpty(context)
                    ? $"{caller} failed: {ex.Message}"
                    : $"{caller} failed ({context}): {ex.Message}";

                ErrorLogger.LogWarning(message, "ErrorBoundary",
                    new Dictionary<string, object>
                    {
                        ["exception_type"] = ex.GetType().Name,
                        ["caller"] = caller,
                        ["context"] = context ?? string.Empty
                    });

                return false;
            }
        }

        /// <summary>
        /// Executes an async void action with automatic error logging on failure.
        /// </summary>
        /// <param name="action">The async action to execute.</param>
        /// <param name="context">Optional context for the error message.</param>
        /// <param name="caller">Automatically captured caller method name.</param>
        /// <returns>True if the action succeeded, false otherwise.</returns>
        public static async Task<bool> TryExecuteAsync(
            Func<Task> action,
            string? context = null,
            [CallerMemberName] string caller = "")
        {
            try
            {
                await action();
                return true;
            }
            catch (Exception ex)
            {
                var message = string.IsNullOrEmpty(context)
                    ? $"{caller} failed: {ex.Message}"
                    : $"{caller} failed ({context}): {ex.Message}";

                ErrorLogger.LogWarning(message, "ErrorBoundary",
                    new Dictionary<string, object>
                    {
                        ["exception_type"] = ex.GetType().Name,
                        ["caller"] = caller,
                        ["context"] = context ?? string.Empty
                    });

                return false;
            }
        }

        /// <summary>
        /// Wraps an action that may throw and converts it to a Result type.
        /// Useful for callers who want to inspect the error without throwing.
        /// </summary>
        /// <typeparam name="T">The return type of the action.</typeparam>
        /// <param name="action">The action to execute.</param>
        /// <param name="context">Optional context for the error message.</param>
        /// <param name="caller">Automatically captured caller method name.</param>
        /// <returns>A Result containing either the value or the exception.</returns>
        public static Result<T> Capture<T>(
            Func<T> action,
            string? context = null,
            [CallerMemberName] string caller = "")
        {
            try
            {
                return Result<T>.Success(action());
            }
            catch (Exception ex)
            {
                var message = string.IsNullOrEmpty(context)
                    ? $"{caller} failed: {ex.Message}"
                    : $"{caller} failed ({context}): {ex.Message}";

                ErrorLogger.LogWarning(message, "ErrorBoundary",
                    new Dictionary<string, object>
                    {
                        ["exception_type"] = ex.GetType().Name,
                        ["caller"] = caller,
                        ["context"] = context ?? string.Empty
                    });

                return Result<T>.Failure(ex);
            }
        }
    }

    /// <summary>
    /// Represents the result of an operation that may fail.
    /// </summary>
    /// <typeparam name="T">The type of the value.</typeparam>
    public readonly struct Result<T>
    {
        public bool IsSuccess { get; }
        public T? Value { get; }
        public Exception? Error { get; }

        private Result(bool isSuccess, T? value, Exception? error)
        {
            IsSuccess = isSuccess;
            Value = value;
            Error = error;
        }

        public static Result<T> Success(T value) => new(true, value, null);
        public static Result<T> Failure(Exception error) => new(false, default, error);

        public T GetValueOrDefault(T defaultValue) => IsSuccess ? Value! : defaultValue;

        public void Match(Action<T> onSuccess, Action<Exception> onFailure)
        {
            if (IsSuccess)
                onSuccess(Value!);
            else
                onFailure(Error!);
        }
    }
}
