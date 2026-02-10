// Phase 5.4: Animation System
// Task 5.4.1-5.4.5: Smooth, accessible animations

using System;
using System.Numerics;
using System.Threading.Tasks;
using Microsoft.UI.Composition;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Hosting;
using Microsoft.UI.Xaml.Media.Animation;

namespace VoiceStudio.App.Features.Animations;

/// <summary>
/// Animation configuration.
/// </summary>
public class AnimationConfig
{
    public bool EnableAnimations { get; set; } = true;
    public double SpeedMultiplier { get; set; } = 1.0;
    public bool UseHardwareAcceleration { get; set; } = true;
}

/// <summary>
/// Easing functions for animations.
/// </summary>
public enum EasingType
{
    Linear,
    EaseIn,
    EaseOut,
    EaseInOut,
    Spring,
    Bounce,
}

/// <summary>
/// Service for managing UI animations.
/// </summary>
public class AnimationService
{
    private readonly AnimationConfig _config = new();
    private Compositor? _compositor;
    private bool _reduceMotion;

    public AnimationConfig Config => _config;

    /// <summary>
    /// Initialize animation service.
    /// </summary>
    public void Initialize(UIElement rootElement)
    {
        var visual = ElementCompositionPreview.GetElementVisual(rootElement);
        _compositor = visual.Compositor;
        
        // Check system settings for reduced motion
        var uiSettings = new Windows.UI.ViewManagement.UISettings();
        _reduceMotion = !uiSettings.AnimationsEnabled;
    }

    /// <summary>
    /// Check if animations should be used.
    /// </summary>
    public bool ShouldAnimate => _config.EnableAnimations && !_reduceMotion;

    /// <summary>
    /// Get adjusted duration based on settings.
    /// </summary>
    public TimeSpan GetDuration(TimeSpan baseDuration)
    {
        if (!ShouldAnimate)
        {
            return TimeSpan.Zero;
        }
        
        return TimeSpan.FromMilliseconds(baseDuration.TotalMilliseconds / _config.SpeedMultiplier);
    }

    /// <summary>
    /// Fade in an element.
    /// </summary>
    public async Task FadeInAsync(UIElement element, TimeSpan duration)
    {
        if (!ShouldAnimate || _compositor == null)
        {
            element.Opacity = 1;
            return;
        }
        
        var visual = ElementCompositionPreview.GetElementVisual(element);
        visual.Opacity = 0;
        
        var animation = _compositor.CreateScalarKeyFrameAnimation();
        animation.InsertKeyFrame(0, 0);
        animation.InsertKeyFrame(1, 1, GetEasingFunction(EasingType.EaseOut));
        animation.Duration = GetDuration(duration);
        
        visual.StartAnimation("Opacity", animation);
        
        await Task.Delay(GetDuration(duration));
    }

    /// <summary>
    /// Fade out an element.
    /// </summary>
    public async Task FadeOutAsync(UIElement element, TimeSpan duration)
    {
        if (!ShouldAnimate || _compositor == null)
        {
            element.Opacity = 0;
            return;
        }
        
        var visual = ElementCompositionPreview.GetElementVisual(element);
        
        var animation = _compositor.CreateScalarKeyFrameAnimation();
        animation.InsertKeyFrame(0, 1);
        animation.InsertKeyFrame(1, 0, GetEasingFunction(EasingType.EaseOut));
        animation.Duration = GetDuration(duration);
        
        visual.StartAnimation("Opacity", animation);
        
        await Task.Delay(GetDuration(duration));
    }

    /// <summary>
    /// Slide in from a direction.
    /// </summary>
    public async Task SlideInAsync(
        UIElement element,
        SlideDirection direction,
        TimeSpan duration,
        double distance = 50)
    {
        if (!ShouldAnimate || _compositor == null)
        {
            return;
        }
        
        var visual = ElementCompositionPreview.GetElementVisual(element);
        
        var offset = direction switch
        {
            SlideDirection.Left => new Vector3((float)-distance, 0, 0),
            SlideDirection.Right => new Vector3((float)distance, 0, 0),
            SlideDirection.Up => new Vector3(0, (float)-distance, 0),
            SlideDirection.Down => new Vector3(0, (float)distance, 0),
            _ => Vector3.Zero,
        };
        
        visual.Offset = offset;
        visual.Opacity = 0;
        
        // Offset animation
        var offsetAnimation = _compositor.CreateVector3KeyFrameAnimation();
        offsetAnimation.InsertKeyFrame(0, offset);
        offsetAnimation.InsertKeyFrame(1, Vector3.Zero, GetEasingFunction(EasingType.EaseOut));
        offsetAnimation.Duration = GetDuration(duration);
        
        // Opacity animation
        var opacityAnimation = _compositor.CreateScalarKeyFrameAnimation();
        opacityAnimation.InsertKeyFrame(0, 0);
        opacityAnimation.InsertKeyFrame(1, 1);
        opacityAnimation.Duration = GetDuration(duration);
        
        visual.StartAnimation("Offset", offsetAnimation);
        visual.StartAnimation("Opacity", opacityAnimation);
        
        await Task.Delay(GetDuration(duration));
    }

    /// <summary>
    /// Scale animation.
    /// </summary>
    public async Task ScaleAsync(
        UIElement element,
        Vector3 fromScale,
        Vector3 toScale,
        TimeSpan duration)
    {
        if (!ShouldAnimate || _compositor == null)
        {
            return;
        }
        
        var visual = ElementCompositionPreview.GetElementVisual(element);
        
        var animation = _compositor.CreateVector3KeyFrameAnimation();
        animation.InsertKeyFrame(0, fromScale);
        animation.InsertKeyFrame(1, toScale, GetEasingFunction(EasingType.EaseOut));
        animation.Duration = GetDuration(duration);
        
        visual.StartAnimation("Scale", animation);
        
        await Task.Delay(GetDuration(duration));
    }

    /// <summary>
    /// Spring animation for natural movement.
    /// </summary>
    public void SpringTo(UIElement element, string propertyName, float toValue)
    {
        if (!ShouldAnimate || _compositor == null)
        {
            return;
        }
        
        var visual = ElementCompositionPreview.GetElementVisual(element);
        
        var animation = _compositor.CreateSpringScalarAnimation();
        animation.FinalValue = toValue;
        animation.DampingRatio = 0.6f;
        animation.Period = TimeSpan.FromMilliseconds(50);
        
        visual.StartAnimation(propertyName, animation);
    }

    /// <summary>
    /// Create a connected animation.
    /// </summary>
    public ConnectedAnimation? PrepareConnectedAnimation(
        UIElement element,
        string key)
    {
        if (!ShouldAnimate)
        {
            return null;
        }
        
        var service = ConnectedAnimationService.GetForCurrentView();
        return service.PrepareToAnimate(key, element);
    }

    /// <summary>
    /// Play a connected animation.
    /// </summary>
    public async Task<bool> TryStartConnectedAnimationAsync(
        UIElement element,
        string key)
    {
        if (!ShouldAnimate)
        {
            return false;
        }
        
        var service = ConnectedAnimationService.GetForCurrentView();
        var animation = service.GetAnimation(key);
        
        if (animation != null)
        {
            animation.TryStart(element);
            await Task.Delay(TimeSpan.FromMilliseconds(300));
            return true;
        }
        
        return false;
    }

    /// <summary>
    /// Create an implicit animation for property changes.
    /// </summary>
    public void SetImplicitAnimation(
        UIElement element,
        string propertyName,
        TimeSpan duration)
    {
        if (!ShouldAnimate || _compositor == null)
        {
            return;
        }
        
        var visual = ElementCompositionPreview.GetElementVisual(element);
        
        var animation = propertyName switch
        {
            "Opacity" => CreateScalarAnimation(duration),
            "Offset" => CreateVector3Animation(duration),
            "Scale" => CreateVector3Animation(duration),
            _ => null,
        };
        
        if (animation != null)
        {
            var animations = _compositor.CreateImplicitAnimationCollection();
            animations[propertyName] = animation;
            visual.ImplicitAnimations = animations;
        }
    }

    private CompositionAnimation CreateScalarAnimation(TimeSpan duration)
    {
        var animation = _compositor!.CreateScalarKeyFrameAnimation();
        animation.InsertExpressionKeyFrame(1, "this.FinalValue");
        animation.Duration = GetDuration(duration);
        animation.Target = "Opacity";
        return animation;
    }

    private CompositionAnimation CreateVector3Animation(TimeSpan duration)
    {
        var animation = _compositor!.CreateVector3KeyFrameAnimation();
        animation.InsertExpressionKeyFrame(1, "this.FinalValue");
        animation.Duration = GetDuration(duration);
        return animation;
    }

    private CompositionEasingFunction GetEasingFunction(EasingType type)
    {
        return type switch
        {
            EasingType.Linear => _compositor!.CreateLinearEasingFunction(),
            EasingType.EaseIn => _compositor!.CreateCubicBezierEasingFunction(
                new Vector2(0.42f, 0), new Vector2(1, 1)),
            EasingType.EaseOut => _compositor!.CreateCubicBezierEasingFunction(
                new Vector2(0, 0), new Vector2(0.58f, 1)),
            EasingType.EaseInOut => _compositor!.CreateCubicBezierEasingFunction(
                new Vector2(0.42f, 0), new Vector2(0.58f, 1)),
            _ => _compositor!.CreateLinearEasingFunction(),
        };
    }
}

/// <summary>
/// Slide direction.
/// </summary>
public enum SlideDirection
{
    Left,
    Right,
    Up,
    Down,
}
