// Phase 5.4: Animation System
// Task 5.4.3: Loading and progress animations

using System;
using System.Numerics;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.UI.Composition;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Hosting;
using Microsoft.UI.Xaml.Shapes;

namespace VoiceStudio.App.Features.Animations;

/// <summary>
/// Loading animation types.
/// </summary>
public enum LoadingAnimationType
{
    Spinner,
    Dots,
    Pulse,
    Wave,
    Progress,
}

/// <summary>
/// Loading animation controller.
/// </summary>
public class LoadingAnimationController
{
    private readonly UIElement _element;
    private readonly Compositor _compositor;
    private CompositionAnimation? _animation;
    private CancellationTokenSource? _cts;

    public LoadingAnimationController(UIElement element)
    {
        _element = element;
        var visual = ElementCompositionPreview.GetElementVisual(element);
        _compositor = visual.Compositor;
    }

    /// <summary>
    /// Start a spinner animation.
    /// </summary>
    public void StartSpinner()
    {
        var visual = ElementCompositionPreview.GetElementVisual(_element);
        
        // Set center point for rotation
        var frameworkElement = _element as FrameworkElement;
        visual.CenterPoint = new Vector3(
            (float)(frameworkElement?.ActualWidth ?? 0) / 2,
            (float)(frameworkElement?.ActualHeight ?? 0) / 2,
            0);
        
        var animation = _compositor.CreateScalarKeyFrameAnimation();
        animation.InsertKeyFrame(0, 0);
        animation.InsertKeyFrame(1, 360, _compositor.CreateLinearEasingFunction());
        animation.Duration = TimeSpan.FromSeconds(1);
        animation.IterationBehavior = AnimationIterationBehavior.Forever;
        
        visual.StartAnimation("RotationAngleInDegrees", animation);
        _animation = animation;
    }

    /// <summary>
    /// Start a pulsing animation.
    /// </summary>
    public void StartPulse()
    {
        var visual = ElementCompositionPreview.GetElementVisual(_element);
        
        var pulseElement = _element as FrameworkElement;
        visual.CenterPoint = new Vector3(
            (float)(pulseElement?.ActualWidth ?? 0) / 2,
            (float)(pulseElement?.ActualHeight ?? 0) / 2,
            0);
        
        var animation = _compositor.CreateVector3KeyFrameAnimation();
        animation.InsertKeyFrame(0, new Vector3(1, 1, 1));
        animation.InsertKeyFrame(0.5f, new Vector3(1.2f, 1.2f, 1));
        animation.InsertKeyFrame(1, new Vector3(1, 1, 1));
        animation.Duration = TimeSpan.FromSeconds(1);
        animation.IterationBehavior = AnimationIterationBehavior.Forever;
        
        visual.StartAnimation("Scale", animation);
        _animation = animation;
    }

    /// <summary>
    /// Start a dot wave animation.
    /// </summary>
    public async Task StartDotsAsync(Panel container, int dotCount = 3)
    {
        _cts = new CancellationTokenSource();
        
        var dots = new UIElement[dotCount];
        
        for (int i = 0; i < dotCount; i++)
        {
            var dot = new Ellipse
            {
                Width = 10,
                Height = 10,
                Fill = new Microsoft.UI.Xaml.Media.SolidColorBrush(
                    Microsoft.UI.Colors.White),
                Margin = new Thickness(5, 0, 5, 0),
            };
            
            container.Children.Add(dot);
            dots[i] = dot;
        }
        
        // Animate dots
        while (!_cts.Token.IsCancellationRequested)
        {
            for (int i = 0; i < dotCount; i++)
            {
                AnimateDot(dots[i], i * 100);
            }
            
            try
            {
                await Task.Delay(1000, _cts.Token);
            }
            catch (OperationCanceledException)
            {
                break;
            }
        }
        
        // Clean up
        container.Children.Clear();
    }

    private void AnimateDot(UIElement dot, int delayMs)
    {
        var visual = ElementCompositionPreview.GetElementVisual(dot);
        
        visual.CenterPoint = new Vector3(5, 5, 0);
        
        var animation = _compositor.CreateVector3KeyFrameAnimation();
        animation.InsertKeyFrame(0, new Vector3(1, 1, 1));
        animation.InsertKeyFrame(0.5f, new Vector3(1.5f, 1.5f, 1));
        animation.InsertKeyFrame(1, new Vector3(1, 1, 1));
        animation.Duration = TimeSpan.FromMilliseconds(600);
        animation.DelayTime = TimeSpan.FromMilliseconds(delayMs);
        
        visual.StartAnimation("Scale", animation);
    }

    /// <summary>
    /// Stop the current animation.
    /// </summary>
    public void Stop()
    {
        _cts?.Cancel();
        
        var visual = ElementCompositionPreview.GetElementVisual(_element);
        visual.StopAnimation("RotationAngleInDegrees");
        visual.StopAnimation("Scale");
        visual.RotationAngleInDegrees = 0;
        visual.Scale = Vector3.One;
    }
}

/// <summary>
/// Progress animation with percentage.
/// </summary>
public class ProgressAnimationController
{
    private readonly UIElement _progressElement;
    private readonly Compositor _compositor;
    private double _currentProgress;

    public ProgressAnimationController(UIElement progressElement)
    {
        _progressElement = progressElement;
        var visual = ElementCompositionPreview.GetElementVisual(progressElement);
        _compositor = visual.Compositor;
    }

    /// <summary>
    /// Animate progress to a value.
    /// </summary>
    public void AnimateTo(double progress, TimeSpan duration)
    {
        progress = Math.Clamp(progress, 0, 100);
        
        if (_progressElement is ProgressBar progressBar)
        {
            AnimateProgressBar(progressBar, progress, duration);
        }
        else if (_progressElement is FrameworkElement element)
        {
            AnimateScaleProgress(element, progress / 100.0, duration);
        }
        
        _currentProgress = progress;
    }

    private void AnimateProgressBar(ProgressBar progressBar, double toValue, TimeSpan duration)
    {
        var visual = ElementCompositionPreview.GetElementVisual(progressBar);
        
        // Animate the value property using Storyboard
        var storyboard = new Microsoft.UI.Xaml.Media.Animation.Storyboard();
        var animation = new Microsoft.UI.Xaml.Media.Animation.DoubleAnimation
        {
            From = progressBar.Value,
            To = toValue,
            Duration = new Duration(duration),
            EasingFunction = new Microsoft.UI.Xaml.Media.Animation.QuadraticEase
            {
                EasingMode = Microsoft.UI.Xaml.Media.Animation.EasingMode.EaseOut,
            },
        };
        
        Microsoft.UI.Xaml.Media.Animation.Storyboard.SetTarget(animation, progressBar);
        Microsoft.UI.Xaml.Media.Animation.Storyboard.SetTargetProperty(animation, "Value");
        
        storyboard.Children.Add(animation);
        storyboard.Begin();
    }

    private void AnimateScaleProgress(FrameworkElement element, double scale, TimeSpan duration)
    {
        var visual = ElementCompositionPreview.GetElementVisual(element);
        
        var animation = _compositor.CreateScalarKeyFrameAnimation();
        animation.InsertKeyFrame(0, (float)(_currentProgress / 100.0));
        animation.InsertKeyFrame(1, (float)scale);
        animation.Duration = duration;
        
        visual.StartAnimation("Scale.X", animation);
    }

    /// <summary>
    /// Pulse the progress indicator.
    /// </summary>
    public void Pulse()
    {
        var visual = ElementCompositionPreview.GetElementVisual(_progressElement);
        
        var animation = _compositor.CreateScalarKeyFrameAnimation();
        animation.InsertKeyFrame(0, 1);
        animation.InsertKeyFrame(0.5f, 1.05f);
        animation.InsertKeyFrame(1, 1);
        animation.Duration = TimeSpan.FromMilliseconds(300);
        
        visual.StartAnimation("Scale.Y", animation);
    }
}
