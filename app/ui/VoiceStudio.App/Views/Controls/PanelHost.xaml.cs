using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls.Primitives;
using VoiceStudio.App.Services;
using System;

namespace VoiceStudio.App.Views.Controls
{
    public sealed partial class PanelHost : UserControl
    {
        public static readonly DependencyProperty TitleProperty =
            DependencyProperty.Register(nameof(Title), typeof(string), typeof(PanelHost), 
                new PropertyMetadata("Panel", OnTitleChanged));

        public static readonly DependencyProperty IconGlyphProperty =
            DependencyProperty.Register(nameof(IconGlyph), typeof(string), typeof(PanelHost), 
                new PropertyMetadata("\uE700", OnIconChanged));

        public static readonly DependencyProperty IsCollapsedProperty =
            DependencyProperty.Register(nameof(IsCollapsed), typeof(bool), typeof(PanelHost), 
                new PropertyMetadata(false, OnCollapsedChanged));

        private static WindowHostService? _windowHostService;
        private static readonly object _serviceLock = new object();

        public string Title
        {
            get => (string)GetValue(TitleProperty);
            set => SetValue(TitleProperty, value);
        }

        public string IconGlyph
        {
            get => (string)GetValue(IconGlyphProperty);
            set => SetValue(IconGlyphProperty, value);
        }

        public bool IsCollapsed
        {
            get => (bool)GetValue(IsCollapsedProperty);
            set => SetValue(IsCollapsedProperty, value);
        }

        public PanelHost()
        {
            this.InitializeComponent();
            PopOutButton.Click += OnPopOutClick;
            CollapseButton.Click += OnCollapseClick;
            OptionsButton.Click += OnOptionsClick;
        }

        private static WindowHostService GetWindowHostService()
        {
            if (_windowHostService == null)
            {
                lock (_serviceLock)
                {
                    if (_windowHostService == null)
                    {
                        _windowHostService = new WindowHostService();
                    }
                }
            }
            return _windowHostService;
        }

        private static void OnTitleChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is PanelHost host && e.NewValue is string title)
            {
                host.PanelTitle.Text = title;
            }
        }

        private static void OnIconChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is PanelHost host && e.NewValue is string glyph)
            {
                host.PanelIcon.Glyph = glyph;
            }
        }

        private static void OnCollapsedChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is PanelHost host)
            {
                // Toggle visibility of content area
                var contentBorder = host.FindName("ContentBorder") as FrameworkElement;
                if (contentBorder != null)
                {
                    contentBorder.Visibility = host.IsCollapsed ? Visibility.Collapsed : Visibility.Visible;
                }
            }
        }

        private void OnPopOutClick(object sender, RoutedEventArgs e)
        {
            try
            {
                var windowHostService = GetWindowHostService();
                var panelId = $"PanelHost_{Title}_{GetHashCode()}";
                
                // Check if already floating
                if (windowHostService.IsFloating(panelId))
                {
                    // Close floating window and return to docked state
                    windowHostService.CloseFloatingWindow(panelId);
                    return;
                }

                // Get the content to pop out - find ContentPresenter within ContentBorder
                var contentBorder = FindName("ContentBorder") as Microsoft.UI.Xaml.Controls.Border;
                if (contentBorder == null)
                {
                    return;
                }

                // Find ContentPresenter in the Border's visual tree
                UIElement? panelContent = null;
                if (contentBorder.Child is Microsoft.UI.Xaml.Controls.ContentPresenter contentPresenter)
                {
                    panelContent = contentPresenter.Content as UIElement;
                }
                else if (contentBorder.Child is UIElement directContent)
                {
                    panelContent = directContent;
                }

                if (panelContent == null)
                {
                    var errorDialog = new ContentDialog
                    {
                        Title = "No Content",
                        Content = "This panel has no content to display in a floating window.",
                        CloseButtonText = "OK",
                        XamlRoot = this.XamlRoot
                    };
                    _ = errorDialog.ShowAsync();
                    return;
                }

                // Create floating window with panel content
                var floatingContent = new Microsoft.UI.Xaml.Controls.Border
                {
                    CornerRadius = contentBorder.CornerRadius,
                    Background = contentBorder.Background,
                    BorderBrush = contentBorder.BorderBrush,
                    BorderThickness = contentBorder.BorderThickness,
                    Padding = contentBorder.Padding,
                    Child = panelContent
                };

                windowHostService.CreateFloatingWindow(
                    panelId: panelId,
                    title: Title,
                    content: floatingContent,
                    width: 800,
                    height: 600
                );
            }
            catch (Exception ex)
            {
                // Show error if floating window creation fails
                var dialog = new ContentDialog
                {
                    Title = "Error",
                    Content = $"Failed to create floating window: {ex.Message}",
                    CloseButtonText = "OK",
                    XamlRoot = this.XamlRoot
                };
                _ = dialog.ShowAsync();
            }
        }

        private void OnCollapseClick(object sender, RoutedEventArgs e)
        {
            IsCollapsed = !IsCollapsed;
        }

        private void OnOptionsClick(object sender, RoutedEventArgs e)
        {
            // Stub: Open options flyout
            var flyout = new MenuFlyout();
            flyout.Items.Add(new MenuFlyoutItem { Text = "Settings" });
            flyout.Items.Add(new MenuFlyoutItem { Text = "Reset Layout" });
            flyout.ShowAt(OptionsButton);
        }
    }
}

