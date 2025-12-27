using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml;
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Panels;
using VoiceStudio.App.Services;
using System;
using System.Collections.Generic;
using System.Linq;
using VoiceStudio.App.Views.Panels;
using Microsoft.UI.Xaml.Controls.Primitives;
using System.Windows.Input;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Media.Animation;
using Windows.ApplicationModel.DataTransfer;

namespace VoiceStudio.App.Controls
{
    public sealed partial class PanelHost : UserControl
    {
        private PanelStateService? _panelStateService;
        private string? _previousPanelId;
        private PanelRegion _region = PanelRegion.Center;
        private DragDropVisualFeedbackService? _dragDropService;
        private PanelRegion? _currentDropZone;
        private bool _isDragging = false;

        public static new readonly DependencyProperty ContentProperty =
            DependencyProperty.Register(nameof(Content), typeof(UIElement), typeof(PanelHost), 
                new PropertyMetadata(null, OnContentChanged));

        public static readonly DependencyProperty PanelRegionProperty =
            DependencyProperty.Register(
                nameof(PanelRegion),
                typeof(PanelRegion),
                typeof(PanelHost),
                new PropertyMetadata(PanelRegion.Center, OnPanelRegionChanged));

        public static readonly DependencyProperty IsLoadingProperty =
            DependencyProperty.Register(
                nameof(IsLoading),
                typeof(bool),
                typeof(PanelHost),
                new PropertyMetadata(false));

        public static readonly DependencyProperty LoadingMessageProperty =
            DependencyProperty.Register(
                nameof(LoadingMessage),
                typeof(string),
                typeof(PanelHost),
                new PropertyMetadata("Loading..."));

        public static readonly DependencyProperty IsCollapsedProperty =
            DependencyProperty.Register(
                nameof(IsCollapsed),
                typeof(bool),
                typeof(PanelHost),
                new PropertyMetadata(false, OnIsCollapsedChanged));

        public static readonly DependencyProperty PanelTitleProperty =
            DependencyProperty.Register(
                nameof(PanelTitle),
                typeof(string),
                typeof(PanelHost),
                new PropertyMetadata("Panel", OnPanelTitleChanged));

        public static readonly DependencyProperty PanelIconProperty =
            DependencyProperty.Register(
                nameof(PanelIcon),
                typeof(string),
                typeof(PanelHost),
                new PropertyMetadata("📋", OnPanelIconChanged));

        public static readonly DependencyProperty QualityMetricsProperty =
            DependencyProperty.Register(
                nameof(QualityMetrics),
                typeof(QualityMetrics),
                typeof(PanelHost),
                new PropertyMetadata(null));

        public static readonly DependencyProperty ShowQualityBadgeProperty =
            DependencyProperty.Register(
                nameof(ShowQualityBadge),
                typeof(bool),
                typeof(PanelHost),
                new PropertyMetadata(false));

        public new UIElement Content
        {
            get => (UIElement)GetValue(ContentProperty);
            set => SetValue(ContentProperty, value);
        }

        public bool IsLoading
        {
            get => (bool)GetValue(IsLoadingProperty);
            set => SetValue(IsLoadingProperty, value);
        }

        public string LoadingMessage
        {
            get => (string)GetValue(LoadingMessageProperty);
            set => SetValue(LoadingMessageProperty, value);
        }

        public bool IsCollapsed
        {
            get => (bool)GetValue(IsCollapsedProperty);
            set => SetValue(IsCollapsedProperty, value);
        }

        public string PanelTitle
        {
            get => (string)GetValue(PanelTitleProperty);
            set => SetValue(PanelTitleProperty, value);
        }

        public string PanelIcon
        {
            get => (string)GetValue(PanelIconProperty);
            set => SetValue(PanelIconProperty, value);
        }

        public QualityMetrics? QualityMetrics
        {
            get => (QualityMetrics?)GetValue(QualityMetricsProperty);
            set => SetValue(QualityMetricsProperty, value);
        }

        public bool ShowQualityBadge
        {
            get => (bool)GetValue(ShowQualityBadgeProperty);
            set => SetValue(ShowQualityBadgeProperty, value);
        }

        // XAML compiler stability: avoid bool->Visibility x:Bind.
        public Visibility QualityBadgeVisibility => ShowQualityBadge ? Visibility.Visible : Visibility.Collapsed;

        public PanelRegion PanelRegion
        {
            get => (PanelRegion)GetValue(PanelRegionProperty);
            set => SetValue(PanelRegionProperty, value);
        }

        public PanelHost()
        {
            this.InitializeComponent();
            _panelStateService = ServiceProvider.GetPanelStateService();
            _dragDropService = ServiceProvider.TryGetDragDropVisualFeedbackService();
            
            // Wire up resize handles to resize this PanelHost (defensive null checks)
            var rightHandle = this.FindName("RightResizeHandle") as PanelResizeHandle;
            if (rightHandle != null)
            {
                rightHandle.TargetElement = this;
            }
            var bottomHandle = this.FindName("BottomResizeHandle") as PanelResizeHandle;
            if (bottomHandle != null)
            {
                bottomHandle.TargetElement = this;
            }

            // Enable drop on the entire PanelHost for docking
            this.AllowDrop = true;
        }

        private static void OnContentChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is PanelHost host)
            {
                // Dispose previous ViewModel if it implements IDisposable
                host.DisposePreviousViewModel(e.OldValue as UIElement);

                // Save previous panel state before changing content
                host.SaveCurrentPanelState();

                // Restore new panel state
                host.RestorePanelState(e.NewValue as UIElement);

                // Update context-sensitive action bar (IDEA 2)
                host.UpdateActionBar(e.NewValue as UIElement);
            }
        }

        private static void OnPanelRegionChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is PanelHost host)
            {
                host._region = (PanelRegion)e.NewValue;
            }
        }

        private static void OnIsCollapsedChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is PanelHost host)
            {
                var panelBody = host.FindName("PanelBody") as FrameworkElement;
                if (panelBody != null)
                {
                    panelBody.Visibility = (bool)e.NewValue ? Visibility.Collapsed : Visibility.Visible;
                }
            }
        }

        private static void OnPanelTitleChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is PanelHost host)
            {
                var titleTextBlock = host.FindName("PanelTitleTextBlock") as TextBlock;
                if (titleTextBlock != null)
                {
                    titleTextBlock.Text = e.NewValue?.ToString() ?? "Panel";
                }
            }
        }

        private static void OnPanelIconChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is PanelHost host)
            {
                var iconTextBlock = host.FindName("PanelIconTextBlock") as TextBlock;
                if (iconTextBlock != null)
                {
                    iconTextBlock.Text = e.NewValue?.ToString() ?? "📋";
                }
            }
        }

        private void CollapseButton_Click(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
        {
            IsCollapsed = !IsCollapsed;
        }

        /// <summary>
        /// Saves the current panel state before switching panels.
        /// </summary>
        private void SaveCurrentPanelState()
        {
            if (_panelStateService == null || Content == null || string.IsNullOrEmpty(_previousPanelId))
                return;

            try
            {
                // Try to get ViewModel from content to save panel-specific state
                string? panelId = null;
                VoiceStudio.Core.Models.PanelState? panelState = null;

                // Get panel ID from ViewModel if it implements IPanelView
                if (GetPanelIdFromContent(Content, out panelId) && !string.IsNullOrEmpty(panelId))
                {
                    panelState = new VoiceStudio.Core.Models.PanelState
                    {
                        PanelId = panelId
                    };

                    // If ViewModel implements state persistence, get custom state
                    // For now, just save basic state (can be extended later)
                    _panelStateService.SavePanelState(_region, panelId, panelState);
                }
            }
            catch (Exception ex)
            {
                // Don't break panel switching if state saving fails
                System.Diagnostics.Debug.WriteLine($"Failed to save panel state: {ex.Message}");
            }
        }

        /// <summary>
        /// Restores panel state when a panel is loaded.
        /// </summary>
        private void RestorePanelState(UIElement? newContent)
        {
            if (_panelStateService == null || newContent == null)
                return;

            try
            {
                // Get panel ID from content
                if (!GetPanelIdFromContent(newContent, out string? panelId) || string.IsNullOrEmpty(panelId))
                    return;

                _previousPanelId = panelId;

                // Get saved state for this panel
                var savedState = _panelStateService.GetPanelState(_region, panelId);
                if (savedState == null)
                    return;

                // Restore panel-specific state if ViewModel supports it
                // For now, basic restoration (can be extended with IPanelStatePersistable interface)
                System.Diagnostics.Debug.WriteLine($"Restoring state for panel: {panelId}");
            }
            catch (Exception ex)
            {
                // Don't break panel loading if state restoration fails
                System.Diagnostics.Debug.WriteLine($"Failed to restore panel state: {ex.Message}");
            }
        }

        /// <summary>
        /// Gets panel ID from content by checking if it has a ViewModel implementing IPanelView.
        /// </summary>
        private bool GetPanelIdFromContent(UIElement content, out string? panelId)
        {
            panelId = null;

            // Try to get ViewModel from UserControl's DataContext
            if (content is UserControl userControl)
            {
                var viewModel = userControl.DataContext;
                if (viewModel is IPanelView panelView)
                {
                    panelId = panelView.PanelId;
                    return true;
                }
            }

            // Try to get from FrameworkElement's DataContext
            if (content is FrameworkElement frameworkElement)
            {
                var viewModel = frameworkElement.DataContext;
                if (viewModel is IPanelView panelView)
                {
                    panelId = panelView.PanelId;
                    return true;
                }
            }

            return false;
        }

        /// <summary>
        /// Disposes the ViewModel from the previous content if it implements IDisposable.
        /// This ensures proper cleanup when switching panels.
        /// </summary>
        private void DisposePreviousViewModel(UIElement? oldContent)
        {
            if (oldContent == null)
                return;

            try
            {
                // Try to get ViewModel from UserControl's DataContext
                if (oldContent is UserControl userControl)
                {
                    var viewModel = userControl.DataContext;
                    if (viewModel is IDisposable disposable)
                    {
                        disposable.Dispose();
                        return;
                    }
                }

                // Try to get from FrameworkElement's DataContext
                if (oldContent is FrameworkElement frameworkElement)
                {
                    var viewModel = frameworkElement.DataContext;
                    if (viewModel is IDisposable disposable)
                    {
                        disposable.Dispose();
                    }
                }
            }
            catch (Exception ex)
            {
                // Don't break panel switching if disposal fails
                System.Diagnostics.Debug.WriteLine($"Failed to dispose previous ViewModel: {ex.Message}");
            }
        }

        /// <summary>
        /// Saves region state (active panel, opened panels).
        /// Called by MainWindow when saving workspace layout.
        /// </summary>
        public void SaveRegionState()
        {
            if (_panelStateService == null)
                return;

            try
            {
                string activePanelId = string.Empty;
                var openedPanels = new List<string>();

                // Get active panel ID
                if (Content != null && GetPanelIdFromContent(Content, out string? panelId))
                {
                    activePanelId = panelId ?? string.Empty;
                    openedPanels.Add(activePanelId);
                }

                _panelStateService.SaveRegionState(_region, activePanelId, openedPanels);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to save region state: {ex.Message}");
            }
        }

        /// <summary>
        /// Updates the context-sensitive action bar based on the current panel content.
        /// Implements IDEA 2: Context-Sensitive Action Bar in PanelHost Headers.
        /// </summary>
        private void UpdateActionBar(UIElement? content)
        {
            if (ActionBar == null)
                return;

            // Clear existing actions
            ActionBar.Children.Clear();

            if (content == null)
            {
                ActionBar.Visibility = Visibility.Collapsed;
                return;
            }

            // Try to get ViewModel from content
            IPanelActionable? actionable = null;

            if (content is UserControl userControl)
            {
                actionable = userControl.DataContext as IPanelActionable;
            }
            else if (content is FrameworkElement frameworkElement)
            {
                actionable = frameworkElement.DataContext as IPanelActionable;
            }

            if (actionable == null)
            {
                ActionBar.Visibility = Visibility.Collapsed;
                return;
            }

            // Get header actions from panel
            var actions = actionable.GetHeaderActions()?.ToList() ?? new List<PanelHeaderAction>();

            if (actions.Count == 0)
            {
                ActionBar.Visibility = Visibility.Collapsed;
                return;
            }

            // Limit to 4 actions to maintain compactness
            var actionsToShow = actions.Where(a => a.IsVisible).Take(4).ToList();

            if (actionsToShow.Count == 0)
            {
                ActionBar.Visibility = Visibility.Collapsed;
                return;
            }

            // Create AppBarButtons for each action
            foreach (var action in actionsToShow)
            {
                var button = new AppBarButton
                {
                    Label = action.Name,
                    IsEnabled = action.IsEnabled,
                    Command = action.Command,
                    Width = 32,
                    Height = 32
                };
                if (!string.IsNullOrEmpty(action.Tooltip))
                {
                    ToolTipService.SetToolTip(button, action.Tooltip);
                }

                // Set icon - try FontIcon first, fallback to SymbolIcon or TextBlock
                if (action.Icon.Length == 1 && char.IsSymbol(action.Icon[0]))
                {
                    // Single character symbol - use FontIcon
                    button.Icon = new FontIcon { Glyph = action.Icon };
                }
                else if (action.Icon.StartsWith("&#x") || action.Icon.StartsWith("\\u"))
                {
                    // Unicode escape sequence
                    button.Icon = new FontIcon { Glyph = action.Icon };
                }
                else
                {
                    // Emoji or text - use TextBlock as icon
                    var textBlock = new TextBlock
                    {
                        Text = action.Icon,
                        FontSize = 16,
                        HorizontalAlignment = HorizontalAlignment.Center,
                        VerticalAlignment = VerticalAlignment.Center
                    };
                    button.Content = textBlock;
                }

                AutomationProperties.SetName(button, action.Name);
                if (!string.IsNullOrEmpty(action.KeyboardShortcut))
                {
                    AutomationProperties.SetHelpText(button, $"Keyboard shortcut: {action.KeyboardShortcut}");
                }

                ActionBar.Children.Add(button);
            }

            ActionBar.Visibility = Visibility.Visible;
        }

        #region Panel Docking Visual Feedback (IDEA 14)

        /// <summary>
        /// Handles the start of a drag operation from the panel header.
        /// </summary>
        private void HeaderGrid_DragStarting(UIElement sender, DragStartingEventArgs args)
        {
            _isDragging = true;
            
            // Set drag data
            args.Data.SetText(PanelTitleTextBlock?.Text ?? "Panel");
            args.Data.Properties.Add("PanelHost", this);
            args.Data.Properties.Add("PanelRegion", _region);
            args.Data.Properties.Add("PanelId", GetPanelIdFromContent(Content, out string? panelId) ? panelId : string.Empty);
            
            // Create drag preview
            if (_dragDropService != null)
            {
                var preview = _dragDropService.CreateDragPreview(HeaderBorder, PanelTitleTextBlock?.Text ?? "Panel");
                args.DragUI.SetContentFromDataPackage();
            }

            // Show drop zones in MainWindow (this will be handled by MainWindow)
            ShowDropZones();
        }

        /// <summary>
        /// Handles drag over events to show visual feedback.
        /// </summary>
        private void HeaderGrid_DragOver(object sender, DragEventArgs e)
        {
            if (!_isDragging)
                return;

            e.AcceptedOperation = DataPackageOperation.Move;
            e.DragUIOverride.IsGlyphVisible = false;
            e.DragUIOverride.Caption = "Dock Panel";

            // Determine which drop zone the cursor is over
            var position = e.GetPosition(RootGrid);
            var dropZone = GetDropZoneFromPosition(position.X, position.Y);
            
            if (dropZone != _currentDropZone)
            {
                _currentDropZone = dropZone;
                UpdateDropZoneVisuals(dropZone);
            }
        }

        /// <summary>
        /// Handles drop events to dock the panel.
        /// </summary>
        private void HeaderGrid_Drop(object sender, DragEventArgs e)
        {
            if (!_isDragging)
                return;

            var targetRegion = _currentDropZone;
            if (targetRegion.HasValue && targetRegion.Value != _region)
            {
                // Trigger panel docking event (MainWindow will handle the actual docking)
                OnPanelDockRequested?.Invoke(this, new PanelDockEventArgs
                {
                    SourcePanelHost = this,
                    SourceRegion = _region,
                    TargetRegion = targetRegion.Value
                });
            }

            HideDropZones();
            _isDragging = false;
            _currentDropZone = null;
        }

        /// <summary>
        /// Handles drag leave events to clean up visual feedback.
        /// </summary>
        private void HeaderGrid_DragLeave(object sender, DragEventArgs e)
        {
            HideDropZones();
            _currentDropZone = null;
        }

        /// <summary>
        /// Determines which drop zone the cursor position is over.
        /// </summary>
        private PanelRegion? GetDropZoneFromPosition(double x, double y)
        {
            var rootGrid = this.FindName("RootGrid") as FrameworkElement;
            if (rootGrid == null)
                return null;

            var width = rootGrid.ActualWidth;
            var height = rootGrid.ActualHeight;

            if (width == 0 || height == 0)
                return null;

            var leftThreshold = width * 0.2;  // Left 20%
            var rightThreshold = width * 0.8; // Right 20%
            var bottomThreshold = height * 0.85; // Bottom 15%

            // Check bottom first (smaller area)
            if (y > bottomThreshold)
            {
                return PanelRegion.Bottom;
            }
            // Check left
            else if (x < leftThreshold)
            {
                return PanelRegion.Left;
            }
            // Check right
            else if (x > rightThreshold)
            {
                return PanelRegion.Right;
            }
            // Default to center
            else
            {
                return PanelRegion.Center;
            }
        }

        /// <summary>
        /// Shows drop zone indicators.
        /// </summary>
        private void ShowDropZones()
        {
            if (DropZoneOverlay == null)
                return;

            DropZoneOverlay.Visibility = Visibility.Visible;
            
            // Show drag shadow on source panel
            if (DragShadow != null)
            {
                DragShadow.Visibility = Visibility.Visible;
                var shadowFade = new DoubleAnimation
                {
                    To = 0.5,
                    Duration = TimeSpan.FromMilliseconds(200)
                };
                Storyboard.SetTarget(shadowFade, DragShadow);
                Storyboard.SetTargetProperty(shadowFade, "Opacity");
                var shadowStoryboard = new Storyboard();
                shadowStoryboard.Children.Add(shadowFade);
                shadowStoryboard.Begin();
            }
            
            // Reduce opacity of source panel to show it's being dragged
            var sourceFade = new DoubleAnimation
            {
                To = 0.6,
                Duration = TimeSpan.FromMilliseconds(200)
            };
            Storyboard.SetTarget(sourceFade, RootGrid);
            Storyboard.SetTargetProperty(sourceFade, "Opacity");
            var sourceStoryboard = new Storyboard();
            sourceStoryboard.Children.Add(sourceFade);
            sourceStoryboard.Begin();
            
            // Animate drop zones in
            AnimateDropZone(LeftDropZone, 0);
            AnimateDropZone(CenterDropZone, 50);
            AnimateDropZone(RightDropZone, 100);
            AnimateDropZone(BottomDropZone, 150);
        }

        /// <summary>
        /// Hides drop zone indicators.
        /// </summary>
        private void HideDropZones()
        {
            if (DropZoneOverlay == null)
                return;

            // Animate drop zones out
            AnimateDropZoneOut(LeftDropZone);
            AnimateDropZoneOut(CenterDropZone);
            AnimateDropZoneOut(RightDropZone);
            AnimateDropZoneOut(BottomDropZone);

            // Hide drag shadow
            if (DragShadow != null)
            {
                var shadowFadeOut = new DoubleAnimation
                {
                    To = 0,
                    Duration = TimeSpan.FromMilliseconds(200)
                };
                Storyboard.SetTarget(shadowFadeOut, DragShadow);
                Storyboard.SetTargetProperty(shadowFadeOut, "Opacity");
                var shadowStoryboard = new Storyboard();
                shadowStoryboard.Children.Add(shadowFadeOut);
                shadowStoryboard.Completed += (s, e) =>
                {
                    if (DragShadow != null)
                        DragShadow.Visibility = Visibility.Collapsed;
                };
                shadowStoryboard.Begin();
            }

            // Restore source panel opacity
            var sourceFadeIn = new DoubleAnimation
            {
                To = 1.0,
                Duration = TimeSpan.FromMilliseconds(200)
            };
            Storyboard.SetTarget(sourceFadeIn, RootGrid);
            Storyboard.SetTargetProperty(sourceFadeIn, "Opacity");
            var sourceStoryboard = new Storyboard();
            sourceStoryboard.Children.Add(sourceFadeIn);
            sourceStoryboard.Begin();

            // Hide overlay after animation
            var hideStoryboard = new Storyboard();
            var fadeOut = new DoubleAnimation
            {
                To = 0,
                Duration = TimeSpan.FromMilliseconds(200)
            };
            Storyboard.SetTarget(fadeOut, DropZoneOverlay);
            Storyboard.SetTargetProperty(fadeOut, "Opacity");
            hideStoryboard.Children.Add(fadeOut);
            hideStoryboard.Completed += (s, e) =>
            {
                if (DropZoneOverlay != null)
                    DropZoneOverlay.Visibility = Visibility.Collapsed;
            };
            hideStoryboard.Begin();
        }

        /// <summary>
        /// Updates visual feedback for the current drop zone.
        /// </summary>
        private void UpdateDropZoneVisuals(PanelRegion? dropZone)
        {
            // Reset all drop zones
            var leftDropZone = this.FindName("LeftDropZone") as Border;
            var centerDropZone = this.FindName("CenterDropZone") as Border;
            var rightDropZone = this.FindName("RightDropZone") as Border;
            var bottomDropZone = this.FindName("BottomDropZone") as Border;
            ResetDropZone(leftDropZone);
            ResetDropZone(centerDropZone);
            ResetDropZone(rightDropZone);
            ResetDropZone(bottomDropZone);

            // Highlight the active drop zone
            Border? activeZone = dropZone switch
            {
                PanelRegion.Left => leftDropZone,
                PanelRegion.Center => centerDropZone,
                PanelRegion.Right => rightDropZone,
                PanelRegion.Bottom => bottomDropZone,
                _ => null
            };

            if (activeZone != null)
            {
                HighlightDropZone(activeZone);
                if (dropZone.HasValue)
                {
                    ShowDockPreview(dropZone.Value);
                }
            }
            else
            {
                HideDockPreview();
            }
        }

        /// <summary>
        /// Animates a drop zone in.
        /// </summary>
        private void AnimateDropZone(Border? zone, int delayMs)
        {
            if (zone == null)
                return;

            var storyboard = new Storyboard();
            
            // Fade in
            var fadeIn = new DoubleAnimation
            {
                From = 0,
                To = 0.8,
                Duration = TimeSpan.FromMilliseconds(300),
                BeginTime = TimeSpan.FromMilliseconds(delayMs)
            };
            Storyboard.SetTarget(fadeIn, zone);
            Storyboard.SetTargetProperty(fadeIn, "Opacity");
            storyboard.Children.Add(fadeIn);

            // Scale in
            var scaleTransform = new Microsoft.UI.Xaml.Media.ScaleTransform();
            zone.RenderTransform = scaleTransform;
            var scaleX = new DoubleAnimation
            {
                From = 0.8,
                To = 1.0,
                Duration = TimeSpan.FromMilliseconds(300),
                BeginTime = TimeSpan.FromMilliseconds(delayMs)
            };
            Storyboard.SetTarget(scaleX, scaleTransform);
            Storyboard.SetTargetProperty(scaleX, "ScaleX");
            storyboard.Children.Add(scaleX);

            var scaleY = new DoubleAnimation
            {
                From = 0.8,
                To = 1.0,
                Duration = TimeSpan.FromMilliseconds(300),
                BeginTime = TimeSpan.FromMilliseconds(delayMs)
            };
            Storyboard.SetTarget(scaleY, scaleTransform);
            Storyboard.SetTargetProperty(scaleY, "ScaleY");
            storyboard.Children.Add(scaleY);

            storyboard.Begin();
        }

        /// <summary>
        /// Animates a drop zone out.
        /// </summary>
        private void AnimateDropZoneOut(Border? zone)
        {
            if (zone == null)
                return;

            var storyboard = new Storyboard();
            var fadeOut = new DoubleAnimation
            {
                To = 0,
                Duration = TimeSpan.FromMilliseconds(200)
            };
            Storyboard.SetTarget(fadeOut, zone);
            Storyboard.SetTargetProperty(fadeOut, "Opacity");
            storyboard.Children.Add(fadeOut);
            storyboard.Begin();
        }

        /// <summary>
        /// Highlights a drop zone.
        /// </summary>
        private void HighlightDropZone(Border zone)
        {
            var storyboard = new Storyboard();
            
            // Increase opacity
            var fadeIn = new DoubleAnimation
            {
                To = 1.0,
                Duration = TimeSpan.FromMilliseconds(150)
            };
            Storyboard.SetTarget(fadeIn, zone);
            Storyboard.SetTargetProperty(fadeIn, "Opacity");
            storyboard.Children.Add(fadeIn);

            // Pulse border
            var borderAnimation = new DoubleAnimation
            {
                To = 5,
                Duration = TimeSpan.FromMilliseconds(150)
            };
            Storyboard.SetTarget(borderAnimation, zone);
            Storyboard.SetTargetProperty(borderAnimation, "(Border.BorderThickness)");
            storyboard.Children.Add(borderAnimation);

            storyboard.Begin();
        }

        /// <summary>
        /// Resets a drop zone to default state.
        /// </summary>
        private void ResetDropZone(Border? zone)
        {
            if (zone == null)
                return;

            zone.Opacity = 0.3;
            zone.BorderThickness = new Thickness(3);
        }

        /// <summary>
        /// Shows dock preview indicator.
        /// </summary>
        private void ShowDockPreview(PanelRegion region)
        {
            if (DockPreviewIndicator == null || DockPreviewText == null)
                return;

            var (regionName, icon) = region switch
            {
                PanelRegion.Left => ("Left", "◀"),
                PanelRegion.Center => ("Center", "⬌"),
                PanelRegion.Right => ("Right", "▶"),
                PanelRegion.Bottom => ("Bottom", "▼"),
                _ => ("Here", "⚓")
            };

            // Update icon if DockPreviewIcon exists (search within DockPreviewIndicator)
            var dockPreviewIcon = DockPreviewIndicator.FindName("DockPreviewIcon") as TextBlock;
            if (dockPreviewIcon == null && DockPreviewIndicator is FrameworkElement fe)
            {
                // Try finding it in the visual tree
                dockPreviewIcon = FindVisualChild<TextBlock>(fe, "DockPreviewIcon");
            }
            if (dockPreviewIcon != null)
            {
                dockPreviewIcon.Text = icon;
            }

            DockPreviewText.Text = $"Dock to {regionName}";
            DockPreviewIndicator.Visibility = Visibility.Visible;

            var storyboard = new Storyboard();
            var fadeIn = new DoubleAnimation
            {
                To = 0.9,
                Duration = TimeSpan.FromMilliseconds(200)
            };
            Storyboard.SetTarget(fadeIn, DockPreviewIndicator);
            Storyboard.SetTargetProperty(fadeIn, "Opacity");
            storyboard.Children.Add(fadeIn);
            storyboard.Begin();
        }

        /// <summary>
        /// Helper method to find a visual child by name.
        /// </summary>
        private static T? FindVisualChild<T>(DependencyObject parent, string childName) where T : DependencyObject
        {
            for (int i = 0; i < Microsoft.UI.Xaml.Media.VisualTreeHelper.GetChildrenCount(parent); i++)
            {
                var child = Microsoft.UI.Xaml.Media.VisualTreeHelper.GetChild(parent, i);
                if (child is T t && child is FrameworkElement fe && fe.Name == childName)
                {
                    return t;
                }
                var childOfChild = FindVisualChild<T>(child, childName);
                if (childOfChild != null)
                {
                    return childOfChild;
                }
            }
            return null;
        }

        /// <summary>
        /// Hides dock preview indicator.
        /// </summary>
        private void HideDockPreview()
        {
            if (DockPreviewIndicator == null)
                return;

            var storyboard = new Storyboard();
            var fadeOut = new DoubleAnimation
            {
                To = 0,
                Duration = TimeSpan.FromMilliseconds(150)
            };
            Storyboard.SetTarget(fadeOut, DockPreviewIndicator);
            Storyboard.SetTargetProperty(fadeOut, "Opacity");
            storyboard.Children.Add(fadeOut);
            storyboard.Completed += (s, e) =>
            {
                if (DockPreviewIndicator != null)
                    DockPreviewIndicator.Visibility = Visibility.Collapsed;
            };
            storyboard.Begin();
        }

        /// <summary>
        /// Event raised when a panel dock is requested.
        /// </summary>
        public event EventHandler<PanelDockEventArgs>? OnPanelDockRequested;

        #endregion
    }

    /// <summary>
    /// Event arguments for panel docking.
    /// </summary>
    public class PanelDockEventArgs : EventArgs
    {
        public PanelHost SourcePanelHost { get; set; } = null!;
        public PanelRegion SourceRegion { get; set; }
        public PanelRegion TargetRegion { get; set; }
    }
}

