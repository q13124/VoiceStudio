using System;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using VoiceStudio.App.Utilities;
using VoiceStudio.Core.Exceptions;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Implementation of IErrorDialogService for displaying user-friendly error dialogs.
    /// </summary>
    public class ErrorDialogService : IErrorDialogService
    {
        private readonly IErrorLoggingService? _errorLoggingService;

        public ErrorDialogService(IErrorLoggingService? errorLoggingService = null)
        {
            _errorLoggingService = errorLoggingService;
        }

        public async Task ShowErrorAsync(Exception exception, string? title = null, string? context = null)
        {
            if (exception == null)
                return;

            // Log the error
            _errorLoggingService?.LogError(exception, context ?? string.Empty);

            var userMessage = ErrorHandler.GetUserFriendlyMessage(exception);
            var recoverySuggestion = ErrorHandler.GetRecoverySuggestion(exception);
            var dialogTitle = title ?? GetErrorTitle(exception);

            await ShowErrorDialogAsync(dialogTitle, userMessage, recoverySuggestion, exception);
        }

        public async Task ShowErrorAsync(string message, string? title = null, string? recoverySuggestion = null)
        {
            if (string.IsNullOrWhiteSpace(message))
                return;

            _errorLoggingService?.LogWarning(message, "User Error");

            await ShowErrorDialogAsync(title ?? "Error", message, recoverySuggestion);
        }

        public async Task ShowWarningAsync(string message, string? title = null)
        {
            if (string.IsNullOrWhiteSpace(message))
                return;

            _errorLoggingService?.LogWarning(message);

            var dialog = new ContentDialog
            {
                Title = title ?? "Warning",
                Content = message,
                PrimaryButtonText = "OK",
                XamlRoot = GetXamlRoot()
            };

            await dialog.ShowAsync();
        }

        public async Task ShowInfoAsync(string message, string? title = null)
        {
            if (string.IsNullOrWhiteSpace(message))
                return;

            var dialog = new ContentDialog
            {
                Title = title ?? "Information",
                Content = message,
                PrimaryButtonText = "OK",
                XamlRoot = GetXamlRoot()
            };

            await dialog.ShowAsync();
        }

        private async Task ShowErrorDialogAsync(string title, string message, string? recoverySuggestion, Exception? exception = null)
        {
            var stackPanel = new StackPanel { Spacing = 12 };

            // Error icon and message
            var headerPanel = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 12 };
            
            var errorIcon = new TextBlock
            {
                Text = "⚠️",
                FontSize = 24,
                VerticalAlignment = VerticalAlignment.Top,
                Margin = new Microsoft.UI.Xaml.Thickness(0, 0, 0, 0)
            };
            headerPanel.Children.Add(errorIcon);

            var messageText = new TextBlock
            {
                Text = message,
                TextWrapping = Microsoft.UI.Xaml.TextWrapping.Wrap,
                FontSize = 14,
                Foreground = Application.Current.Resources["VSQ.Text.PrimaryBrush"] as Microsoft.UI.Xaml.Media.Brush ?? new Microsoft.UI.Xaml.Media.SolidColorBrush(Microsoft.UI.Colors.White),
                VerticalAlignment = VerticalAlignment.Center
            };
            headerPanel.Children.Add(messageText);
            stackPanel.Children.Add(headerPanel);

            // Recovery suggestion with styled container
            if (!string.IsNullOrWhiteSpace(recoverySuggestion))
            {
                var warnBrush = Application.Current.Resources["VSQ.Warn.Brush"] as Microsoft.UI.Xaml.Media.SolidColorBrush;
                var warnColor = warnBrush?.Color ?? Microsoft.UI.ColorHelper.FromArgb(255, 255, 181, 64);
                
                var suggestionContainer = new Border
                {
                    Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(Microsoft.UI.ColorHelper.FromArgb(30, warnColor.R, warnColor.G, warnColor.B)),
                    BorderBrush = new Microsoft.UI.Xaml.Media.SolidColorBrush(Microsoft.UI.ColorHelper.FromArgb(100, warnColor.R, warnColor.G, warnColor.B)),
                    BorderThickness = new Microsoft.UI.Xaml.Thickness(1),
                    CornerRadius = new Microsoft.UI.Xaml.CornerRadius(4),
                    Padding = new Microsoft.UI.Xaml.Thickness(12, 8, 12, 8),
                    Margin = new Microsoft.UI.Xaml.Thickness(0, 8, 0, 0)
                };

                var suggestionStack = new StackPanel { Spacing = 4 };
                
                var suggestionHeader = new TextBlock
                {
                    Text = "💡 Suggestion:",
                    FontWeight = Microsoft.UI.Text.FontWeights.SemiBold,
                    FontSize = 12,
                    Foreground = warnBrush ?? new Microsoft.UI.Xaml.Media.SolidColorBrush(warnColor)
                };
                suggestionStack.Children.Add(suggestionHeader);

                var suggestionText = new TextBlock
                {
                    Text = recoverySuggestion,
                    TextWrapping = Microsoft.UI.Xaml.TextWrapping.Wrap,
                    FontSize = 12,
                    Foreground = Application.Current.Resources["VSQ.Text.PrimaryBrush"] as Microsoft.UI.Xaml.Media.Brush ?? new Microsoft.UI.Xaml.Media.SolidColorBrush(Microsoft.UI.ColorHelper.FromArgb(230, 255, 255, 255)),
                    LineHeight = 18
                };
                suggestionStack.Children.Add(suggestionText);

                suggestionContainer.Child = suggestionStack;
                stackPanel.Children.Add(suggestionContainer);
            }

            var dialog = new ContentDialog
            {
                Title = title,
                Content = stackPanel,
                PrimaryButtonText = "OK",
                XamlRoot = GetXamlRoot(),
                DefaultButton = ContentDialogButton.Primary
            };

            // Add retry button for transient errors
            if (exception != null && ErrorHandler.IsTransientError(exception))
            {
                dialog.SecondaryButtonText = "Retry";
            }

            var result = await dialog.ShowAsync();
            
            // Return retry indication if secondary button was clicked
            if (result == ContentDialogResult.Secondary && exception != null)
            {
                // Note: This is a simple implementation. In a real scenario, you might want
                // to return a value or use a callback to handle retry logic.
            }
        }

        private string GetErrorTitle(Exception exception)
        {
            return exception switch
            {
                BackendUnavailableException => "Connection Error",
                BackendTimeoutException => "Timeout Error",
                BackendAuthenticationException => "Authentication Error",
                BackendNotFoundException => "Not Found",
                BackendValidationException => "Validation Error",
                BackendServerException => "Server Error",
                BackendDeserializationException => "Data Processing Error",
                BackendException => "Backend Error",
                _ => "Error"
            };
        }

        private XamlRoot? GetXamlRoot()
        {
            // Try to get the XamlRoot from the main window
            if (App.MainWindowInstance != null)
            {
                return App.MainWindowInstance.Content?.XamlRoot;
            }
            return null;
        }
    }
}

