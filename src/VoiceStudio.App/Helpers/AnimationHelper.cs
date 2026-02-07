using System;
using System.Numerics;
using Microsoft.UI.Composition;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Hosting;

namespace VoiceStudio.App.Helpers;

/// <summary>
/// Helper class for Fluent Design animations and visual effects.
/// 
/// Phase 11.2: Micro-animations
/// Implements connected animations, spring physics, and contextual transitions.
/// </summary>
public static class AnimationHelper
{
    private static readonly TimeSpan DefaultDuration = TimeSpan.FromMilliseconds(300);
    private static readonly TimeSpan FastDuration = TimeSpan.FromMilliseconds(150);
    private static readonly TimeSpan SlowDuration = TimeSpan.FromMilliseconds(500);

    #region Fade Animations

    /// <summary>
    /// Fade in an element with optional offset.
    /// </summary>
    public static void FadeIn(UIElement element, TimeSpan? duration = null, Vector3? startOffset = null)
    {
        var compositor = ElementCompositionPreview.GetElementVisual(element).Compositor;
        var visual = ElementCompositionPreview.GetElementVisual(element);

        duration ??= DefaultDuration;
        startOffset ??= new Vector3(0, 20, 0);

        // Create fade animation
        var fadeAnimation = compositor.CreateScalarKeyFrameAnimation();
        fadeAnimation.InsertKeyFrame(0f, 0f);
        fadeAnimation.InsertKeyFrame(1f, 1f, compositor.CreateCubicBezierEasingFunction(new Vector2(0.1f, 0.9f), new Vector2(0.2f, 1f)));
        fadeAnimation.Duration = duration.Value;

        // Create offset animation
        var offsetAnimation = compositor.CreateVector3KeyFrameAnimation();
        offsetAnimation.InsertKeyFrame(0f, startOffset.Value);
        offsetAnimation.InsertKeyFrame(1f, Vector3.Zero, compositor.CreateCubicBezierEasingFunction(new Vector2(0.1f, 0.9f), new Vector2(0.2f, 1f)));
        offsetAnimation.Duration = duration.Value;

        // Start animations
        visual.StartAnimation("Opacity", fadeAnimation);
        visual.StartAnimation("Offset", offsetAnimation);
    }

    /// <summary>
    /// Fade out an element with optional offset.
    /// </summary>
    public static void FadeOut(UIElement element, TimeSpan? duration = null, Vector3? endOffset = null)
    {
        var compositor = ElementCompositionPreview.GetElementVisual(element).Compositor;
        var visual = ElementCompositionPreview.GetElementVisual(element);

        duration ??= DefaultDuration;
        endOffset ??= new Vector3(0, -20, 0);

        var fadeAnimation = compositor.CreateScalarKeyFrameAnimation();
        fadeAnimation.InsertKeyFrame(0f, 1f);
        fadeAnimation.InsertKeyFrame(1f, 0f, compositor.CreateCubicBezierEasingFunction(new Vector2(0.1f, 0.9f), new Vector2(0.2f, 1f)));
        fadeAnimation.Duration = duration.Value;

        var offsetAnimation = compositor.CreateVector3KeyFrameAnimation();
        offsetAnimation.InsertKeyFrame(0f, Vector3.Zero);
        offsetAnimation.InsertKeyFrame(1f, endOffset.Value, compositor.CreateCubicBezierEasingFunction(new Vector2(0.1f, 0.9f), new Vector2(0.2f, 1f)));
        offsetAnimation.Duration = duration.Value;

        visual.StartAnimation("Opacity", fadeAnimation);
        visual.StartAnimation("Offset", offsetAnimation);
    }

    #endregion

    #region Scale Animations

    /// <summary>
    /// Scale up animation for emphasis.
    /// </summary>
    public static void ScaleUp(UIElement element, float targetScale = 1.05f, TimeSpan? duration = null)
    {
        var compositor = ElementCompositionPreview.GetElementVisual(element).Compositor;
        var visual = ElementCompositionPreview.GetElementVisual(element);

        duration ??= FastDuration;

        // Set center point for scaling
        visual.CenterPoint = new Vector3((float)(element as FrameworkElement)?.ActualWidth / 2 ?? 0,
                                         (float)(element as FrameworkElement)?.ActualHeight / 2 ?? 0, 0);

        var scaleAnimation = compositor.CreateVector3KeyFrameAnimation();
        scaleAnimation.InsertKeyFrame(0f, Vector3.One);
        scaleAnimation.InsertKeyFrame(1f, new Vector3(targetScale, targetScale, 1f), 
            compositor.CreateCubicBezierEasingFunction(new Vector2(0.1f, 0.9f), new Vector2(0.2f, 1f)));
        scaleAnimation.Duration = duration.Value;

        visual.StartAnimation("Scale", scaleAnimation);
    }

    /// <summary>
    /// Scale down animation (return to normal).
    /// </summary>
    public static void ScaleDown(UIElement element, TimeSpan? duration = null)
    {
        var compositor = ElementCompositionPreview.GetElementVisual(element).Compositor;
        var visual = ElementCompositionPreview.GetElementVisual(element);

        duration ??= FastDuration;

        var scaleAnimation = compositor.CreateVector3KeyFrameAnimation();
        scaleAnimation.InsertKeyFrame(0f, visual.Scale);
        scaleAnimation.InsertKeyFrame(1f, Vector3.One, 
            compositor.CreateCubicBezierEasingFunction(new Vector2(0.1f, 0.9f), new Vector2(0.2f, 1f)));
        scaleAnimation.Duration = duration.Value;

        visual.StartAnimation("Scale", scaleAnimation);
    }

    /// <summary>
    /// Spring-based scale animation for bouncy effect.
    /// </summary>
    public static void SpringScale(UIElement element, float targetScale = 1.1f)
    {
        var compositor = ElementCompositionPreview.GetElementVisual(element).Compositor;
        var visual = ElementCompositionPreview.GetElementVisual(element);

        visual.CenterPoint = new Vector3((float)(element as FrameworkElement)?.ActualWidth / 2 ?? 0,
                                         (float)(element as FrameworkElement)?.ActualHeight / 2 ?? 0, 0);

        var springAnimation = compositor.CreateSpringVector3Animation();
        springAnimation.FinalValue = new Vector3(targetScale, targetScale, 1f);
        springAnimation.DampingRatio = 0.6f;
        springAnimation.Period = TimeSpan.FromMilliseconds(50);
        springAnimation.StopBehavior = AnimationStopBehavior.SetToFinalValue;

        visual.StartAnimation("Scale", springAnimation);
    }

    #endregion

    #region Slide Animations

    /// <summary>
    /// Slide in from direction.
    /// </summary>
    public static void SlideIn(UIElement element, SlideDirection direction, TimeSpan? duration = null)
    {
        var compositor = ElementCompositionPreview.GetElementVisual(element).Compositor;
        var visual = ElementCompositionPreview.GetElementVisual(element);

        duration ??= DefaultDuration;

        var startOffset = GetSlideOffset(element, direction, -1);

        var offsetAnimation = compositor.CreateVector3KeyFrameAnimation();
        offsetAnimation.InsertKeyFrame(0f, startOffset);
        offsetAnimation.InsertKeyFrame(1f, Vector3.Zero, 
            compositor.CreateCubicBezierEasingFunction(new Vector2(0.1f, 0.9f), new Vector2(0.2f, 1f)));
        offsetAnimation.Duration = duration.Value;

        var fadeAnimation = compositor.CreateScalarKeyFrameAnimation();
        fadeAnimation.InsertKeyFrame(0f, 0f);
        fadeAnimation.InsertKeyFrame(1f, 1f);
        fadeAnimation.Duration = duration.Value;

        visual.StartAnimation("Offset", offsetAnimation);
        visual.StartAnimation("Opacity", fadeAnimation);
    }

    /// <summary>
    /// Slide out in direction.
    /// </summary>
    public static void SlideOut(UIElement element, SlideDirection direction, TimeSpan? duration = null)
    {
        var compositor = ElementCompositionPreview.GetElementVisual(element).Compositor;
        var visual = ElementCompositionPreview.GetElementVisual(element);

        duration ??= DefaultDuration;

        var endOffset = GetSlideOffset(element, direction, 1);

        var offsetAnimation = compositor.CreateVector3KeyFrameAnimation();
        offsetAnimation.InsertKeyFrame(0f, Vector3.Zero);
        offsetAnimation.InsertKeyFrame(1f, endOffset, 
            compositor.CreateCubicBezierEasingFunction(new Vector2(0.1f, 0.9f), new Vector2(0.2f, 1f)));
        offsetAnimation.Duration = duration.Value;

        var fadeAnimation = compositor.CreateScalarKeyFrameAnimation();
        fadeAnimation.InsertKeyFrame(0f, 1f);
        fadeAnimation.InsertKeyFrame(1f, 0f);
        fadeAnimation.Duration = duration.Value;

        visual.StartAnimation("Offset", offsetAnimation);
        visual.StartAnimation("Opacity", fadeAnimation);
    }

    private static Vector3 GetSlideOffset(UIElement element, SlideDirection direction, int multiplier)
    {
        var fe = element as FrameworkElement;
        float width = (float)(fe?.ActualWidth ?? 100);
        float height = (float)(fe?.ActualHeight ?? 100);
        float slideDistance = 50f; // Default slide distance

        return direction switch
        {
            SlideDirection.Left => new Vector3(slideDistance * multiplier, 0, 0),
            SlideDirection.Right => new Vector3(-slideDistance * multiplier, 0, 0),
            SlideDirection.Up => new Vector3(0, slideDistance * multiplier, 0),
            SlideDirection.Down => new Vector3(0, -slideDistance * multiplier, 0),
            _ => Vector3.Zero
        };
    }

    #endregion

    #region Rotation Animations

    /// <summary>
    /// Rotate element.
    /// </summary>
    public static void Rotate(UIElement element, float targetDegrees, TimeSpan? duration = null)
    {
        var compositor = ElementCompositionPreview.GetElementVisual(element).Compositor;
        var visual = ElementCompositionPreview.GetElementVisual(element);

        duration ??= DefaultDuration;

        visual.CenterPoint = new Vector3((float)(element as FrameworkElement)?.ActualWidth / 2 ?? 0,
                                         (float)(element as FrameworkElement)?.ActualHeight / 2 ?? 0, 0);

        var rotationAnimation = compositor.CreateScalarKeyFrameAnimation();
        rotationAnimation.InsertKeyFrame(0f, visual.RotationAngleInDegrees);
        rotationAnimation.InsertKeyFrame(1f, targetDegrees, 
            compositor.CreateCubicBezierEasingFunction(new Vector2(0.1f, 0.9f), new Vector2(0.2f, 1f)));
        rotationAnimation.Duration = duration.Value;

        visual.StartAnimation("RotationAngleInDegrees", rotationAnimation);
    }

    /// <summary>
    /// Continuous spin animation (e.g., for loading indicators).
    /// </summary>
    public static void StartSpinning(UIElement element, TimeSpan? cycleDuration = null)
    {
        var compositor = ElementCompositionPreview.GetElementVisual(element).Compositor;
        var visual = ElementCompositionPreview.GetElementVisual(element);

        cycleDuration ??= TimeSpan.FromSeconds(1);

        visual.CenterPoint = new Vector3((float)(element as FrameworkElement)?.ActualWidth / 2 ?? 0,
                                         (float)(element as FrameworkElement)?.ActualHeight / 2 ?? 0, 0);

        var rotationAnimation = compositor.CreateScalarKeyFrameAnimation();
        rotationAnimation.InsertKeyFrame(0f, 0f);
        rotationAnimation.InsertKeyFrame(1f, 360f, compositor.CreateLinearEasingFunction());
        rotationAnimation.Duration = cycleDuration.Value;
        rotationAnimation.IterationBehavior = AnimationIterationBehavior.Forever;

        visual.StartAnimation("RotationAngleInDegrees", rotationAnimation);
    }

    /// <summary>
    /// Stop spinning animation.
    /// </summary>
    public static void StopSpinning(UIElement element)
    {
        var visual = ElementCompositionPreview.GetElementVisual(element);
        visual.StopAnimation("RotationAngleInDegrees");
        visual.RotationAngleInDegrees = 0;
    }

    #endregion

    #region Staggered Animations

    /// <summary>
    /// Animate a list of elements with staggered timing.
    /// </summary>
    public static void StaggeredFadeIn(UIElement[] elements, TimeSpan staggerDelay, TimeSpan? itemDuration = null)
    {
        itemDuration ??= DefaultDuration;

        for (int i = 0; i < elements.Length; i++)
        {
            var element = elements[i];
            var delay = TimeSpan.FromMilliseconds(staggerDelay.TotalMilliseconds * i);

            var compositor = ElementCompositionPreview.GetElementVisual(element).Compositor;
            var visual = ElementCompositionPreview.GetElementVisual(element);

            visual.Opacity = 0;

            var fadeAnimation = compositor.CreateScalarKeyFrameAnimation();
            fadeAnimation.InsertKeyFrame(0f, 0f);
            fadeAnimation.InsertKeyFrame(1f, 1f, compositor.CreateCubicBezierEasingFunction(new Vector2(0.1f, 0.9f), new Vector2(0.2f, 1f)));
            fadeAnimation.Duration = itemDuration.Value;
            fadeAnimation.DelayTime = delay;

            var offsetAnimation = compositor.CreateVector3KeyFrameAnimation();
            offsetAnimation.InsertKeyFrame(0f, new Vector3(0, 30, 0));
            offsetAnimation.InsertKeyFrame(1f, Vector3.Zero, compositor.CreateCubicBezierEasingFunction(new Vector2(0.1f, 0.9f), new Vector2(0.2f, 1f)));
            offsetAnimation.Duration = itemDuration.Value;
            offsetAnimation.DelayTime = delay;

            visual.StartAnimation("Opacity", fadeAnimation);
            visual.StartAnimation("Offset", offsetAnimation);
        }
    }

    #endregion

    #region Implicit Animations

    /// <summary>
    /// Enable implicit animations for smooth property changes.
    /// </summary>
    public static void EnableImplicitAnimations(UIElement element)
    {
        var compositor = ElementCompositionPreview.GetElementVisual(element).Compositor;
        var visual = ElementCompositionPreview.GetElementVisual(element);

        var implicitAnimations = compositor.CreateImplicitAnimationCollection();

        // Offset animation
        var offsetAnimation = compositor.CreateVector3KeyFrameAnimation();
        offsetAnimation.InsertExpressionKeyFrame(1f, "this.FinalValue");
        offsetAnimation.Duration = DefaultDuration;
        offsetAnimation.Target = "Offset";
        implicitAnimations["Offset"] = offsetAnimation;

        // Scale animation
        var scaleAnimation = compositor.CreateVector3KeyFrameAnimation();
        scaleAnimation.InsertExpressionKeyFrame(1f, "this.FinalValue");
        scaleAnimation.Duration = DefaultDuration;
        scaleAnimation.Target = "Scale";
        implicitAnimations["Scale"] = scaleAnimation;

        // Opacity animation
        var opacityAnimation = compositor.CreateScalarKeyFrameAnimation();
        opacityAnimation.InsertExpressionKeyFrame(1f, "this.FinalValue");
        opacityAnimation.Duration = DefaultDuration;
        opacityAnimation.Target = "Opacity";
        implicitAnimations["Opacity"] = opacityAnimation;

        visual.ImplicitAnimations = implicitAnimations;
    }

    /// <summary>
    /// Disable implicit animations.
    /// </summary>
    public static void DisableImplicitAnimations(UIElement element)
    {
        var visual = ElementCompositionPreview.GetElementVisual(element);
        visual.ImplicitAnimations = null;
    }

    #endregion

    #region Expression Animations

    /// <summary>
    /// Create parallax effect based on scroll position.
    /// </summary>
    public static void CreateParallaxEffect(UIElement element, ScrollViewer scrollViewer, float parallaxFactor = 0.5f)
    {
        var compositor = ElementCompositionPreview.GetElementVisual(element).Compositor;
        var visual = ElementCompositionPreview.GetElementVisual(element);

        var scrollerPropertySet = ElementCompositionPreview.GetScrollViewerManipulationPropertySet(scrollViewer);

        var parallaxExpression = compositor.CreateExpressionAnimation(
            $"Vector3(0, -scroller.Translation.Y * {parallaxFactor}, 0)");
        parallaxExpression.SetReferenceParameter("scroller", scrollerPropertySet);

        visual.StartAnimation("Offset", parallaxExpression);
    }

    #endregion

    #region Utility Methods

    /// <summary>
    /// Reset all transforms on an element.
    /// </summary>
    public static void ResetTransforms(UIElement element)
    {
        var visual = ElementCompositionPreview.GetElementVisual(element);
        visual.Offset = Vector3.Zero;
        visual.Scale = Vector3.One;
        visual.Opacity = 1f;
        visual.RotationAngleInDegrees = 0;
    }

    /// <summary>
    /// Stop all animations on an element.
    /// </summary>
    public static void StopAllAnimations(UIElement element)
    {
        var visual = ElementCompositionPreview.GetElementVisual(element);
        visual.StopAnimation("Offset");
        visual.StopAnimation("Scale");
        visual.StopAnimation("Opacity");
        visual.StopAnimation("RotationAngleInDegrees");
    }

    #endregion
}

/// <summary>
/// Direction for slide animations.
/// </summary>
public enum SlideDirection
{
    Left,
    Right,
    Up,
    Down
}
