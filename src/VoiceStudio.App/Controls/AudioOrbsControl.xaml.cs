using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Shapes;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Controls
{
  /// <summary>
  /// AudioOrbs visualization control using Path-based rendering.
  /// Displays frequency magnitudes in a circular/orbital pattern.
  /// </summary>
  public sealed partial class AudioOrbsControl : UserControl
  {
    private Canvas? _orbsCanvas;

    public static readonly DependencyProperty DataProperty =
        DependencyProperty.Register(
            nameof(Data),
            typeof(AudioOrbsData),
            typeof(AudioOrbsControl),
            new PropertyMetadata(null, OnDataChanged));

    public AudioOrbsControl()
    {
      InitializeComponent();
      this.SizeChanged += AudioOrbsControl_SizeChanged;
      this.Loaded += (_, _) => InitializeControls();
    }

    private static void OnDataChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
      if (d is AudioOrbsControl control)
      {
        control.UpdateOrbs();
      }
    }

    private void AudioOrbsControl_SizeChanged(object _, SizeChangedEventArgs e)
    {
      UpdateOrbs();
    }

    public AudioOrbsData? Data
    {
      get => (AudioOrbsData?)GetValue(DataProperty);
      set => SetValue(DataProperty, value);
    }

    private void UpdateOrbs()
    {
      if (_orbsCanvas == null || Data == null || Data.Magnitudes == null || Data.Magnitudes.Count == 0)
      {
        if (_orbsCanvas != null)
          _orbsCanvas.Children.Clear();
        return;
      }

      _orbsCanvas.Children.Clear();

      var actualWidth = ActualWidth > 0 ? ActualWidth : 400;
      var actualHeight = ActualHeight > 0 ? ActualHeight : 400;
      var centerX = actualWidth / 2.0;
      var centerY = actualHeight / 2.0;
      var maxRadius = Math.Min(actualWidth, actualHeight) / 2.5;

      var orbCount = Math.Min(Data.OrbCount, Data.Magnitudes.Count);
      var magnitudeCount = Data.Magnitudes.Count;

      // Draw concentric circles (orbs) for each frequency band
      for (int i = 0; i < orbCount; i++)
      {
        var magnitudeIndex = (int)((double)i / orbCount * magnitudeCount);
        if (magnitudeIndex >= Data.Magnitudes.Count)
          break;

        var magnitude = Data.Magnitudes[magnitudeIndex];
        var normalizedMagnitude = Math.Clamp(magnitude, 0.0f, 1.0f);

        // Calculate radius for this orb (distributed across available radius)
        var baseRadius = (i + 1.0) / orbCount * maxRadius;
        var radius = baseRadius * normalizedMagnitude;

        // Create orb as ellipse
        var orb = new Ellipse
        {
          Width = radius * 2,
          Height = radius * 2,
          StrokeThickness = 2
        };

        // Color based on magnitude (blue to red gradient)
        var color = MagnitudeToColor(normalizedMagnitude);
        orb.Stroke = new SolidColorBrush(color);
        orb.Fill = new SolidColorBrush(color) { Opacity = 0.2 };

        Canvas.SetLeft(orb, centerX - radius);
        Canvas.SetTop(orb, centerY - radius);

        _orbsCanvas.Children.Add(orb);
      }

      // Draw center point
      var center = new Ellipse
      {
        Width = 8,
        Height = 8,
        Fill = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 255, 255, 255))
      };
      Canvas.SetLeft(center, centerX - 4);
      Canvas.SetTop(center, centerY - 4);
      _orbsCanvas.Children.Add(center);
    }

    private Windows.UI.Color MagnitudeToColor(float normalized)
    {
      // Color gradient: blue (low) -> cyan -> yellow -> red (high)
      byte r, g, b;
      if (normalized < 0.33f)
      {
        var t = normalized / 0.33f;
        r = 0;
        g = (byte)(t * 255);
        b = 255;
      }
      else if (normalized < 0.66f)
      {
        var t = (normalized - 0.33f) / 0.33f;
        r = 0;
        g = 255;
        b = (byte)(255 * (1 - t));
      }
      else
      {
        var t = (normalized - 0.66f) / 0.34f;
        r = (byte)(t * 255);
        g = (byte)(255 * (1 - t));
        b = 0;
      }

      return Windows.UI.Color.FromArgb(255, r, g, b);
    }

    private void InitializeControls()
    {
      if (Content is Grid grid)
      {
        _orbsCanvas = grid.FindName("OrbsCanvas") as Canvas;
        if (_orbsCanvas != null)
        {
          UpdateOrbs();
        }
      }
    }

    protected override void OnApplyTemplate()
    {
      base.OnApplyTemplate();
      InitializeControls();
    }
  }
}