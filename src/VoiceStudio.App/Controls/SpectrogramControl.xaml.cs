using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media.Imaging;
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices.WindowsRuntime;

namespace VoiceStudio.App.Controls
{
  /// <summary>
  /// Spectrogram visualization control that renders a compact heatmap from FFT frames.
  /// </summary>
  public sealed partial class SpectrogramControl : UserControl
  {
    private const int MaxRenderWidth = 1024;
    private const int MaxRenderHeight = 512;
    private const int MinRenderWidth = 64;
    private const int MinRenderHeight = 64;
    private WriteableBitmap? _bitmap;
    private double _durationSeconds;

    public SpectrogramControl()
    {
      InitializeComponent();
      SizeChanged += SpectrogramControl_SizeChanged;
    }

    public static readonly DependencyProperty FramesProperty =
        DependencyProperty.Register(
            nameof(Frames),
            typeof(IEnumerable),
            typeof(SpectrogramControl),
            new PropertyMetadata(null, OnFramesChanged));

    public static readonly DependencyProperty ZoomLevelProperty =
        DependencyProperty.Register(
            nameof(ZoomLevel),
            typeof(double),
            typeof(SpectrogramControl),
            new PropertyMetadata(1.0, OnZoomChanged));

    public static readonly DependencyProperty PlaybackPositionProperty =
        DependencyProperty.Register(
            nameof(PlaybackPosition),
            typeof(double),
            typeof(SpectrogramControl),
            new PropertyMetadata(-1.0, OnPlaybackPositionChanged));

    public IEnumerable? Frames
    {
      get => (IEnumerable?)GetValue(FramesProperty);
      set => SetValue(FramesProperty, value);
    }

    public double ZoomLevel
    {
      get => (double)GetValue(ZoomLevelProperty);
      set => SetValue(ZoomLevelProperty, value);
    }

    public double PlaybackPosition
    {
      get => (double)GetValue(PlaybackPositionProperty);
      set => SetValue(PlaybackPositionProperty, value);
    }

    private static void OnFramesChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
      if (d is SpectrogramControl control)
      {
        control.UpdateSpectrogram();
      }
    }

    private static void OnZoomChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
      if (d is SpectrogramControl control)
      {
        control.UpdateSpectrogram();
      }
    }

    private static void OnPlaybackPositionChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
      if (d is SpectrogramControl control)
      {
        control.UpdatePlaybackPosition();
      }
    }

    private void SpectrogramControl_SizeChanged(object _, SizeChangedEventArgs e)
    {
      UpdateSpectrogram();
      UpdatePlaybackPosition();
    }

    private void UpdateSpectrogram()
    {
      var frames = ExtractFrames(Frames);
      if (frames.Count == 0)
      {
        SpectrogramImage.Source = null;
        EmptyStateText.Visibility = Visibility.Visible;
        if (PlaybackLine != null)
        {
          PlaybackLine.Visibility = Visibility.Collapsed;
        }
        return;
      }

      EmptyStateText.Visibility = Visibility.Collapsed;

      var frameCount = frames.Count;
      var binCount = frames.Max(frame => frame.Magnitudes.Count);
      if (frameCount == 0 || binCount == 0)
      {
        SpectrogramImage.Source = null;
        EmptyStateText.Visibility = Visibility.Visible;
        return;
      }

      var targetWidth = (int)Math.Clamp(frameCount, MinRenderWidth, MaxRenderWidth);
      var targetHeight = (int)Math.Clamp(binCount, MinRenderHeight, MaxRenderHeight);

      var zoom = Math.Max(0.1, ZoomLevel);
      var framesToShow = Math.Max(1, (int)(frameCount / zoom));
      const int frameStart = 0;
      var frameEnd = Math.Min(frameCount, frameStart + framesToShow);

      var maxValue = frames.Max(frame => frame.MaxValue);
      if (maxValue <= 0)
      {
        maxValue = 1;
      }

      _bitmap = new WriteableBitmap(targetWidth, targetHeight);
      var pixels = new byte[targetWidth * targetHeight * 4];
      var frameStep = (double)(frameEnd - frameStart) / targetWidth;
      var binStep = (double)binCount / targetHeight;

      for (int y = 0; y < targetHeight; y++)
      {
        var binIndex = binCount - 1 - Math.Min(binCount - 1, (int)(y * binStep));
        var rowOffset = y * targetWidth * 4;
        for (int x = 0; x < targetWidth; x++)
        {
          var frameIndex = frameStart + Math.Min(frameEnd - frameStart - 1, (int)(x * frameStep));
          var magnitudes = frames[frameIndex].Magnitudes;
          var value = binIndex < magnitudes.Count ? magnitudes[binIndex] : 0f;
          var normalized = Math.Clamp(value / maxValue, 0f, 1f);
          var color = GetHeatmapColor(normalized);
          var pixelOffset = rowOffset + (x * 4);
          pixels[pixelOffset] = color.B;
          pixels[pixelOffset + 1] = color.G;
          pixels[pixelOffset + 2] = color.R;
          pixels[pixelOffset + 3] = color.A;
        }
      }

      using (var stream = _bitmap.PixelBuffer.AsStream())
      {
        stream.Write(pixels, 0, pixels.Length);
      }

      SpectrogramImage.Source = _bitmap;

      _durationSeconds = frames.Max(frame => frame.TimeSeconds);
      UpdatePlaybackPosition();
    }

    private void UpdatePlaybackPosition()
    {
      if (PlaybackLine == null || SpectrogramImage.Source == null || PlaybackPosition < 0)
      {
        if (PlaybackLine != null)
        {
          PlaybackLine.Visibility = Visibility.Collapsed;
        }
        return;
      }

      var width = ActualWidth > 0 ? ActualWidth : _bitmap?.PixelWidth ?? 0;
      if (width <= 0)
      {
        PlaybackLine.Visibility = Visibility.Collapsed;
        return;
      }

      var position = PlaybackPosition;
      if (_durationSeconds > 0 && position > 1.0)
      {
        position /= _durationSeconds;
      }

      position = Math.Clamp(position, 0.0, 1.0);
      var x = position * width;

      PlaybackLine.X1 = x;
      PlaybackLine.Y1 = 0;
      PlaybackLine.X2 = x;
      PlaybackLine.Y2 = ActualHeight > 0 ? ActualHeight : _bitmap?.PixelHeight ?? 0;
      PlaybackLine.Visibility = Visibility.Visible;
    }

    private static List<FrameData> ExtractFrames(IEnumerable? frameSource)
    {
      var result = new List<FrameData>();
      if (frameSource == null)
      {
        return result;
      }

      foreach (var frame in frameSource)
      {
        if (frame == null)
        {
          continue;
        }

        var magnitudes = ExtractMagnitudes(frame);
        if (magnitudes.Count == 0)
        {
          continue;
        }

        var timeSeconds = ExtractTimeSeconds(frame);
        var maxValue = magnitudes.Max();
        result.Add(new FrameData(timeSeconds, magnitudes, maxValue));
      }

      return result;
    }

    private static List<float> ExtractMagnitudes(object frame)
    {
      var magnitudes = ExtractList(frame, "Magnitudes");
      if (magnitudes.Count == 0)
      {
        magnitudes = ExtractList(frame, "Frequencies");
      }
      return magnitudes;
    }

    private static List<float> ExtractList(object frame, string propertyName)
    {
      var property = frame.GetType().GetProperty(propertyName);
      if (property == null)
      {
        return new List<float>();
      }

      var value = property.GetValue(frame);
      if (value == null)
      {
        return new List<float>();
      }

      if (value is IList<float> floatList)
      {
        return floatList.ToList();
      }

      if (value is IList<double> doubleList)
      {
        return doubleList.Select(v => (float)v).ToList();
      }

      if (value is IEnumerable<float> floatEnumerable)
      {
        return floatEnumerable.ToList();
      }

      if (value is IEnumerable<double> doubleEnumerable)
      {
        return doubleEnumerable.Select(v => (float)v).ToList();
      }

      if (value is IEnumerable enumerable)
      {
        var list = new List<float>();
        foreach (var item in enumerable)
        {
          if (item is float f)
          {
            list.Add(f);
          }
          else if (item is double d)
          {
            list.Add((float)d);
          }
          else if (item != null && float.TryParse(item.ToString(), out var parsed))
          {
            list.Add(parsed);
          }
        }
        return list;
      }

      return new List<float>();
    }

    private static double ExtractTimeSeconds(object frame)
    {
      var property = frame.GetType().GetProperty("Time");
      if (property == null)
      {
        return 0;
      }

      var value = property.GetValue(frame);
      if (value is double doubleValue)
      {
        return doubleValue;
      }

      if (value is float floatValue)
      {
        return floatValue;
      }

      if (value != null && double.TryParse(value.ToString(), out var parsed))
      {
        return parsed;
      }

      return 0;
    }

    private static Windows.UI.Color GetHeatmapColor(float value)
    {
      value = Math.Clamp(value, 0f, 1f);
      byte r;
      byte g;
      byte b;

      if (value <= 0.25f)
      {
        var t = value / 0.25f;
        r = 0;
        g = (byte)(t * 64);
        b = (byte)(128 + (t * 127));
      }
      else if (value <= 0.5f)
      {
        var t = (value - 0.25f) / 0.25f;
        r = 0;
        g = (byte)(64 + (t * 191));
        b = (byte)(255 - (t * 127));
      }
      else if (value <= 0.75f)
      {
        var t = (value - 0.5f) / 0.25f;
        r = (byte)(t * 255);
        g = (byte)(255 - (t * 64));
        b = (byte)(128 - (t * 128));
      }
      else
      {
        var t = (value - 0.75f) / 0.25f;
        r = 255;
        g = (byte)(191 - (t * 191));
        b = 0;
      }

      return Windows.UI.Color.FromArgb(255, r, g, b);
    }
  }

  /// <summary>
  /// Represents a single frame of spectrogram data.
  /// </summary>
  public class SpectrogramFrame
  {
    public double Time { get; set; }
    public List<float> Frequencies { get; set; } = new();
  }

  internal sealed record FrameData(double TimeSeconds, List<float> Magnitudes, float MaxValue);
}