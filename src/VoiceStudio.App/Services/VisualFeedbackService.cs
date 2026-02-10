// Phase 5.4: Visual Feedback and Animation
// Task 5.4.1-5.4.5: Comprehensive visual feedback system

using System;
using System.Collections.Generic;
using System.Numerics;
using System.Threading.Tasks;
using Microsoft.UI;
using Microsoft.UI.Composition;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Hosting;
using Microsoft.UI.Xaml.Media;
using Windows.UI;

namespace VoiceStudio.App.Services;

/// <summary>
/// Visual feedback types for user actions.
/// </summary>
public enum FeedbackType
{
    Success,
    Error,
    Warning,
    Info,
    Progress
}

/// <summary>
/// Configuration for visual feedback animations.
/// </summary>
public class VisualFeedbackConfig
{
    public bool EnableAnimations { get; set; } = true;
    public bool EnableHapticFeedback { get; set; } = true;
    public bool EnableSoundFeedback { get; set; } = false;
    public TimeSpan DefaultDuration { get; set; } = TimeSpan.FromMilliseconds(300);
    public TimeSpan ToastDuration { get; set; } = TimeSpan.FromSeconds(3);
}

/// <summary>
/// Phase 5.4: Comprehensive visual feedback service for UI interactions.
/// Provides consistent feedback animations, toasts, and visual cues.
/// </summary>
public class VisualFeedbackService
{
    private readonly VisualFeedbackConfig _config = new();
    private readonly AccessibilityService? _accessibilityService;
    private Compositor? _compositor;
    private readonly Queue<ToastRequest> _toastQueue = new();
    private bool _isShowingToast;

    public VisualFeedbackConfig Config => _config;

    public VisualFeedbackService(AccessibilityService? accessibilityService = null)
    {
        _accessibilityService = accessibilityService;
    }

    /// <summary>
    /// Initialize the visual feedback service with a root element.
    /// </summary>
    public void Initialize(UIElement rootElement)
    {
        var visual = ElementCompositionPreview.GetElementVisual(rootElement);
        _compositor = visual.Compositor;
    }

    #region Ripple Effects

    /// <summary>
    /// Create a ripple effect at the click position.
    /// </summary>
    public void CreateRipple(UIElement element, Windows.Foundation.Point clickPosition)
    {
        if (!ShouldAnimate() || _compositor == null)
            return;

        var visual = ElementCompositionPreview.GetElementVisual(element);
        var container = visual.Compositor.CreateContainerVisual();
        var rippleVisual = _compositor.CreateSpriteVisual();

        // Create circular ripple
        var brush = _compositor.CreateColorBrush(Color.FromArgb(50, 255, 255, 255));
        rippleVisual.Brush = brush;
        rippleVisual.Size = new Vector2(20, 20);
        rippleVisual.Offset = new Vector3((float)clickPosition.X - 10, (float)clickPosition.Y - 10, 0);

        container.Children.InsertAtTop(rippleVisual);
        ElementCompositionPreview.SetElementChildVisual(element, container);

        // Animate scale and fade
        var scaleAnimation = _compositor.CreateVector3KeyFrameAnimation();
        scaleAnimation.InsertKeyFrame(0, new Vector3(1, 1, 1));
        scaleAnimation.InsertKeyFrame(1, new Vector3(8, 8, 1));
        scaleAnimation.Duration = TimeSpan.FromMilliseconds(400);

        var fadeAnimation = _compositor.CreateScalarKeyFrameAnimation();
        fadeAnimation.InsertKeyFrame(0, 1);
        fadeAnimation.InsertKeyFrame(1, 0);
        fadeAnimation.Duration = TimeSpan.FromMilliseconds(400);

        rippleVisual.StartAnimation("Scale", scaleAnimation);
        rippleVisual.StartAnimation("Opacity", fadeAnimation);

        // Clean up after animation
        Task.Delay(450).ContinueWith(_ =>
        {
            element.DispatcherQueue.TryEnqueue(() =>
            {
                ElementCompositionPreview.SetElementChildVisual(element, null);
            });
        });
    }

    #endregion

    #region Button Feedback

    /// <summary>
    /// Apply press feedback to a button.
    /// </summary>
    public void ApplyPressEffect(UIElement element)
    {
        if (!ShouldAnimate() || _compositor == null)
            return;

        var visual = ElementCompositionPreview.GetElementVisual(element);
        SetCenterPoint(element, visual);

        var animation = _compositor.CreateVector3KeyFrameAnimation();
        animation.InsertKeyFrame(0, new Vector3(1, 1, 1));
        animation.InsertKeyFrame(1, new Vector3(0.95f, 0.95f, 1));
        animation.Duration = TimeSpan.FromMilliseconds(100);

        visual.StartAnimation("Scale", animation);
    }

    /// <summary>
    /// Apply release feedback to a button.
    /// </summary>
    public void ApplyReleaseEffect(UIElement element)
    {
        if (!ShouldAnimate() || _compositor == null)
            return;

        var visual = ElementCompositionPreview.GetElementVisual(element);

        var animation = _compositor.CreateSpringVector3Animation();
        animation.FinalValue = new Vector3(1, 1, 1);
        animation.DampingRatio = 0.5f;
        animation.Period = TimeSpan.FromMilliseconds(50);

        visual.StartAnimation("Scale", animation);
    }

    /// <summary>
    /// Apply hover effect to an element.
    /// </summary>
    public void ApplyHoverEffect(UIElement element, bool isHovering)
    {
        if (!ShouldAnimate() || _compositor == null)
            return;

        var visual = ElementCompositionPreview.GetElementVisual(element);
        SetCenterPoint(element, visual);

        var scale = isHovering ? new Vector3(1.02f, 1.02f, 1) : new Vector3(1, 1, 1);

        var animation = _compositor.CreateVector3KeyFrameAnimation();
        animation.InsertKeyFrame(1, scale);
        animation.Duration = TimeSpan.FromMilliseconds(150);

        visual.StartAnimation("Scale", animation);
    }

    #endregion

    #region Status Feedback

    /// <summary>
    /// Show success feedback with animation.
    /// </summary>
    public async Task ShowSuccessAsync(UIElement element, string? message = null)
    {
        await ShowStatusFeedbackAsync(element, FeedbackType.Success, message);
    }

    /// <summary>
    /// Show error feedback with shake animation.
    /// </summary>
    public async Task ShowErrorAsync(UIElement element, string? message = null)
    {
        await ShowStatusFeedbackAsync(element, FeedbackType.Error, message);

        // Add shake animation for errors
        if (ShouldAnimate() && _compositor != null)
        {
            var visual = ElementCompositionPreview.GetElementVisual(element);

            var shakeAnimation = _compositor.CreateVector3KeyFrameAnimation();
            shakeAnimation.InsertKeyFrame(0, new Vector3(0, 0, 0));
            shakeAnimation.InsertKeyFrame(0.2f, new Vector3(-10, 0, 0));
            shakeAnimation.InsertKeyFrame(0.4f, new Vector3(10, 0, 0));
            shakeAnimation.InsertKeyFrame(0.6f, new Vector3(-10, 0, 0));
            shakeAnimation.InsertKeyFrame(0.8f, new Vector3(10, 0, 0));
            shakeAnimation.InsertKeyFrame(1, new Vector3(0, 0, 0));
            shakeAnimation.Duration = TimeSpan.FromMilliseconds(400);

            visual.StartAnimation("Offset", shakeAnimation);
        }
    }

    /// <summary>
    /// Show warning feedback.
    /// </summary>
    public async Task ShowWarningAsync(UIElement element, string? message = null)
    {
        await ShowStatusFeedbackAsync(element, FeedbackType.Warning, message);
    }

    private async Task ShowStatusFeedbackAsync(UIElement element, FeedbackType type, string? message)
    {
        // Announce to screen readers
        if (message != null && _accessibilityService != null)
        {
            switch (type)
            {
                case FeedbackType.Success:
                    _accessibilityService.AnnounceSuccess(message);
                    break;
                case FeedbackType.Error:
                    _accessibilityService.AnnounceError(message);
                    break;
                default:
                    _accessibilityService.AnnounceStatus(message);
                    break;
            }
        }

        // Visual feedback pulse
        if (ShouldAnimate() && _compositor != null)
        {
            var visual = ElementCompositionPreview.GetElementVisual(element);
            SetCenterPoint(element, visual);

            var pulseAnimation = _compositor.CreateVector3KeyFrameAnimation();
            pulseAnimation.InsertKeyFrame(0, new Vector3(1, 1, 1));
            pulseAnimation.InsertKeyFrame(0.5f, new Vector3(1.05f, 1.05f, 1));
            pulseAnimation.InsertKeyFrame(1, new Vector3(1, 1, 1));
            pulseAnimation.Duration = TimeSpan.FromMilliseconds(300);

            visual.StartAnimation("Scale", pulseAnimation);
        }

        await Task.CompletedTask;
    }

    #endregion

    #region Toast Notifications

    /// <summary>
    /// Show a toast notification.
    /// </summary>
    public void ShowToast(string title, string message, FeedbackType type = FeedbackType.Info)
    {
        _toastQueue.Enqueue(new ToastRequest { Title = title, Message = message, Type = type });

        if (!_isShowingToast)
        {
            _ = ProcessToastQueueAsync();
        }
    }

    private async Task ProcessToastQueueAsync()
    {
        _isShowingToast = true;

        while (_toastQueue.Count > 0)
        {
            var request = _toastQueue.Dequeue();

            // For now, just announce - actual toast UI would be implemented in the app layer
            _accessibilityService?.AnnounceStatus($"{request.Title}: {request.Message}");

            await Task.Delay(_config.ToastDuration);
        }

        _isShowingToast = false;
    }

    private class ToastRequest
    {
        public string Title { get; set; } = "";
        public string Message { get; set; } = "";
        public FeedbackType Type { get; set; }
    }

    #endregion

    #region Skeleton Loading

    /// <summary>
    /// Create a skeleton loading placeholder.
    /// </summary>
    public Border CreateSkeletonElement(double width, double height)
    {
        var skeleton = new Border
        {
            Width = width,
            Height = height,
            CornerRadius = new CornerRadius(4),
            Background = new SolidColorBrush(Color.FromArgb(30, 128, 128, 128))
        };

        if (ShouldAnimate() && _compositor != null)
        {
            StartSkeletonAnimation(skeleton);
        }

        return skeleton;
    }

    /// <summary>
    /// Start skeleton shimmer animation.
    /// </summary>
    public void StartSkeletonAnimation(UIElement element)
    {
        if (_compositor == null)
            return;

        var visual = ElementCompositionPreview.GetElementVisual(element);

        var animation = _compositor.CreateScalarKeyFrameAnimation();
        animation.InsertKeyFrame(0, 0.3f);
        animation.InsertKeyFrame(0.5f, 0.6f);
        animation.InsertKeyFrame(1, 0.3f);
        animation.Duration = TimeSpan.FromMilliseconds(1500);
        animation.IterationBehavior = AnimationIterationBehavior.Forever;

        visual.StartAnimation("Opacity", animation);
    }

    /// <summary>
    /// Stop skeleton animation and fade in real content.
    /// </summary>
    public async Task ReplaceSkeletonAsync(UIElement skeleton, UIElement realContent)
    {
        if (!ShouldAnimate() || _compositor == null)
        {
            skeleton.Visibility = Visibility.Collapsed;
            realContent.Visibility = Visibility.Visible;
            return;
        }

        // Fade out skeleton
        var skeletonVisual = ElementCompositionPreview.GetElementVisual(skeleton);
        skeletonVisual.StopAnimation("Opacity");

        var fadeOutAnimation = _compositor.CreateScalarKeyFrameAnimation();
        fadeOutAnimation.InsertKeyFrame(1, 0);
        fadeOutAnimation.Duration = TimeSpan.FromMilliseconds(200);
        skeletonVisual.StartAnimation("Opacity", fadeOutAnimation);

        await Task.Delay(200);
        skeleton.Visibility = Visibility.Collapsed;

        // Fade in real content
        realContent.Visibility = Visibility.Visible;
        var contentVisual = ElementCompositionPreview.GetElementVisual(realContent);
        contentVisual.Opacity = 0;

        var fadeInAnimation = _compositor.CreateScalarKeyFrameAnimation();
        fadeInAnimation.InsertKeyFrame(0, 0);
        fadeInAnimation.InsertKeyFrame(1, 1);
        fadeInAnimation.Duration = TimeSpan.FromMilliseconds(300);
        contentVisual.StartAnimation("Opacity", fadeInAnimation);
    }

    #endregion

    #region Transition Animations

    /// <summary>
    /// Animate a page transition.
    /// </summary>
    public async Task AnimatePageTransitionAsync(UIElement outgoingPage, UIElement incomingPage, bool slideRight = true)
    {
        if (!ShouldAnimate() || _compositor == null)
        {
            outgoingPage.Visibility = Visibility.Collapsed;
            incomingPage.Visibility = Visibility.Visible;
            return;
        }

        var direction = slideRight ? 1 : -1;
        var outgoingVisual = ElementCompositionPreview.GetElementVisual(outgoingPage);
        var incomingVisual = ElementCompositionPreview.GetElementVisual(incomingPage);

        incomingPage.Visibility = Visibility.Visible;
        incomingVisual.Offset = new Vector3(300 * direction, 0, 0);
        incomingVisual.Opacity = 0;

        // Outgoing animation
        var outOffset = _compositor.CreateVector3KeyFrameAnimation();
        outOffset.InsertKeyFrame(1, new Vector3(-300 * direction, 0, 0));
        outOffset.Duration = _config.DefaultDuration;

        var outOpacity = _compositor.CreateScalarKeyFrameAnimation();
        outOpacity.InsertKeyFrame(1, 0);
        outOpacity.Duration = _config.DefaultDuration;

        // Incoming animation
        var inOffset = _compositor.CreateVector3KeyFrameAnimation();
        inOffset.InsertKeyFrame(1, Vector3.Zero);
        inOffset.Duration = _config.DefaultDuration;

        var inOpacity = _compositor.CreateScalarKeyFrameAnimation();
        inOpacity.InsertKeyFrame(1, 1);
        inOpacity.Duration = _config.DefaultDuration;

        outgoingVisual.StartAnimation("Offset", outOffset);
        outgoingVisual.StartAnimation("Opacity", outOpacity);
        incomingVisual.StartAnimation("Offset", inOffset);
        incomingVisual.StartAnimation("Opacity", inOpacity);

        await Task.Delay(_config.DefaultDuration);
        outgoingPage.Visibility = Visibility.Collapsed;
        outgoingVisual.Offset = Vector3.Zero;
        outgoingVisual.Opacity = 1;
    }

    /// <summary>
    /// Animate a panel expand/collapse.
    /// </summary>
    public void AnimatePanelExpand(UIElement panel, bool isExpanding)
    {
        if (!ShouldAnimate() || _compositor == null)
            return;

        var visual = ElementCompositionPreview.GetElementVisual(panel);

        if (isExpanding)
        {
            visual.Opacity = 0;
            visual.Scale = new Vector3(0.95f, 0.95f, 1);

            var scaleAnimation = _compositor.CreateSpringVector3Animation();
            scaleAnimation.FinalValue = new Vector3(1, 1, 1);
            scaleAnimation.DampingRatio = 0.7f;
            scaleAnimation.Period = TimeSpan.FromMilliseconds(50);

            var fadeAnimation = _compositor.CreateScalarKeyFrameAnimation();
            fadeAnimation.InsertKeyFrame(1, 1);
            fadeAnimation.Duration = TimeSpan.FromMilliseconds(200);

            visual.StartAnimation("Scale", scaleAnimation);
            visual.StartAnimation("Opacity", fadeAnimation);
        }
        else
        {
            var scaleAnimation = _compositor.CreateVector3KeyFrameAnimation();
            scaleAnimation.InsertKeyFrame(1, new Vector3(0.95f, 0.95f, 1));
            scaleAnimation.Duration = TimeSpan.FromMilliseconds(150);

            var fadeAnimation = _compositor.CreateScalarKeyFrameAnimation();
            fadeAnimation.InsertKeyFrame(1, 0);
            fadeAnimation.Duration = TimeSpan.FromMilliseconds(150);

            visual.StartAnimation("Scale", scaleAnimation);
            visual.StartAnimation("Opacity", fadeAnimation);
        }
    }

    #endregion

    #region Helper Methods

    private bool ShouldAnimate()
    {
        if (!_config.EnableAnimations)
            return false;

        if (_accessibilityService?.IsReducedMotionEnabled == true)
            return false;

        return true;
    }

    private static void SetCenterPoint(UIElement element, Visual visual)
    {
        if (element is FrameworkElement fe)
        {
            visual.CenterPoint = new Vector3(
                (float)(fe.ActualWidth / 2),
                (float)(fe.ActualHeight / 2),
                0);
        }
    }

    #endregion
}

/// <summary>
/// Extension methods for common visual feedback patterns.
/// </summary>
public static class VisualFeedbackExtensions
{
    /// <summary>
    /// Apply standard button feedback behavior.
    /// </summary>
    public static void EnableFeedback(this Button button, VisualFeedbackService feedbackService)
    {
        button.PointerPressed += (s, e) => feedbackService.ApplyPressEffect(button);
        button.PointerReleased += (s, e) => feedbackService.ApplyReleaseEffect(button);
        button.PointerEntered += (s, e) => feedbackService.ApplyHoverEffect(button, true);
        button.PointerExited += (s, e) => feedbackService.ApplyHoverEffect(button, false);
    }

    /// <summary>
    /// Create a ripple effect on click.
    /// </summary>
    public static void EnableRippleEffect(this UIElement element, VisualFeedbackService feedbackService)
    {
        element.PointerPressed += (s, e) =>
        {
            var position = e.GetCurrentPoint(element).Position;
            feedbackService.CreateRipple(element, position);
        };
    }
}
