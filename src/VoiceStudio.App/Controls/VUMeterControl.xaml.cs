using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Shapes;

namespace VoiceStudio.App.Controls
{
  /// <summary>
  /// VU meter visualization control using native rendering.
  /// Displays peak and RMS audio levels as vertical bars.
  /// </summary>
  public sealed partial class VUMeterControl : UserControl
  {
    private Rectangle? _peakBar;
    private Rectangle? _rmsBar;

    public static readonly DependencyProperty PeakLevelProperty =
        DependencyProperty.Register(
            nameof(PeakLevel),
            typeof(double),
            typeof(VUMeterControl),
            new PropertyMetadata(0.0, OnLevelChanged));

    public static readonly DependencyProperty RmsLevelProperty =
        DependencyProperty.Register(
            nameof(RmsLevel),
            typeof(double),
            typeof(VUMeterControl),
            new PropertyMetadata(0.0, OnLevelChanged));

    public VUMeterControl()
    {
      InitializeComponent();
      this.SizeChanged += VUMeterControl_SizeChanged;
      this.Loaded += (_, _) => InitializeControls();
    }

    private static void OnLevelChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
      if (d is VUMeterControl control)
      {
        control.UpdateMeters();
      }
    }

    private void VUMeterControl_SizeChanged(object _, SizeChangedEventArgs e)
    {
      UpdateMeters();
    }

    public double PeakLevel
    {
      get => (double)GetValue(PeakLevelProperty);
      set => SetValue(PeakLevelProperty, value);
    }

    public double RmsLevel
    {
      get => (double)GetValue(RmsLevelProperty);
      set => SetValue(RmsLevelProperty, value);
    }

    private void UpdateMeters()
    {
      if (_peakBar == null || _rmsBar == null)
        return;

      var actualWidth = ActualWidth > 0 ? ActualWidth : 100;
      var actualHeight = ActualHeight > 0 ? ActualHeight : 200;

      // Clamp levels to 0-1 range (assuming normalized input)
      var peak = Math.Clamp(PeakLevel, 0.0, 1.0);
      var rms = Math.Clamp(RmsLevel, 0.0, 1.0);

      var barWidth = (actualWidth / 2.0) - 10;
      var maxHeight = actualHeight - 20;

      // Update peak bar (left side, red)
      _peakBar.Width = barWidth;
      _peakBar.Height = maxHeight * peak;
      Canvas.SetLeft(_peakBar, 5);
      Canvas.SetTop(_peakBar, actualHeight - 10 - _peakBar.Height);

      // Update RMS bar (right side, green)
      _rmsBar.Width = barWidth;
      _rmsBar.Height = maxHeight * rms;
      Canvas.SetLeft(_rmsBar, (actualWidth / 2.0) + 5);
      Canvas.SetTop(_rmsBar, actualHeight - 10 - _rmsBar.Height);

      // Update colors based on levels
      if (peak > 0.9)
        _peakBar.Fill = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 255, 0, 0)); // Red
      else if (peak > 0.7)
        _peakBar.Fill = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 255, 165, 0)); // Orange
      else
        _peakBar.Fill = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 0, 255, 0)); // Green

      if (rms > 0.9)
        _rmsBar.Fill = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 255, 0, 0)); // Red
      else if (rms > 0.7)
        _rmsBar.Fill = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 255, 165, 0)); // Orange
      else
        _rmsBar.Fill = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 0, 255, 0)); // Green
    }

    private void InitializeControls()
    {
      if (Content is Grid grid)
      {
        var canvas = grid.FindName("MeterCanvas") as Canvas;
        if (canvas != null)
        {
          _peakBar = canvas.FindName("PeakBar") as Rectangle;
          _rmsBar = canvas.FindName("RmsBar") as Rectangle;

          if (_peakBar != null && _rmsBar != null)
          {
            UpdateMeters();
          }
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