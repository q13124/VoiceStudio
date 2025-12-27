using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Collaboration indicator control showing active users.
    /// Implements IDEA 25: Real-Time Collaboration Indicators.
    /// </summary>
    public sealed class CollaborationIndicator : UserControl
    {
        private CollaborationService? _collaborationService;

        public CollaborationIndicator()
        {
            // NOTE: XAML-backed implementation removed to avoid XamlCompiler.exe crashes.
            Content = new TextBlock
            {
                Text = "Collaboration indicator temporarily disabled (XAML compiler stability)",
                TextWrapping = TextWrapping.Wrap,
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center,
                Opacity = 0.7
            };

            Loaded += CollaborationIndicator_Loaded;
        }

        private void CollaborationIndicator_Loaded(object sender, RoutedEventArgs e)
        {
            _collaborationService = Services.ServiceProvider.TryGetCollaborationService();
            if (_collaborationService != null)
            {
                _collaborationService.UserJoined += CollaborationService_UserJoined;
                _collaborationService.UserLeft += CollaborationService_UserLeft;
                UpdateUserList();
            }
        }

        private void CollaborationService_UserJoined(object? sender, ActiveUserEventArgs e)
        {
            this.DispatcherQueue.TryEnqueue(() => UpdateUserList());
        }

        private void CollaborationService_UserLeft(object? sender, ActiveUserEventArgs e)
        {
            this.DispatcherQueue.TryEnqueue(() => UpdateUserList());
        }

        private void UpdateUserList()
        {
            if (_collaborationService == null)
                return;
            // UI elements are not currently rendered (placeholder only).
        }
    }
}

