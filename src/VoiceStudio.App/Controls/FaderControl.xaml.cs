using Microsoft.UI.Input;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using System;
using Windows.Foundation;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Custom vertical fader control for mixer channels.
    /// Supports volume control from -∞ dB to +12 dB (0.0 to 1.0 normalized).
    /// </summary>
    public sealed partial class FaderControl : UserControl
    {
        public static readonly DependencyProperty VolumeProperty =
            DependencyProperty.Register(
                nameof(Volume),
                typeof(double),
                typeof(FaderControl),
                new PropertyMetadata(1.0, OnVolumeChanged));

        private bool _isDragging = false;
        private double _dragStartY = 0.0;
        private double _dragStartVolume = 0.0;

        // Volume range: -∞ dB to +6 dB (matches EffectsMixerViewModel)
        // Volume 0.0 = -∞ dB (silence), 1.0 = 0 dB (unity), 2.0 = +6 dB
        private const double MIN_DB = -96.0; // Practical minimum (effectively silence)
        private const double MAX_DB = 6.0;
        private const double MAX_VOLUME = 2.0; // Maximum volume value (matches MixerChannel)

        public FaderControl()
        {
            this.InitializeComponent();
            UpdateFaderPosition();
        }

        /// <summary>
        /// Volume in range (0.0 to 2.0).
        /// 0.0 = -∞ dB (silence), 1.0 = 0 dB (unity), 2.0 = +6 dB
        /// </summary>
        public double Volume
        {
            get => (double)GetValue(VolumeProperty);
            set => SetValue(VolumeProperty, Math.Max(0.0, Math.Min(MAX_VOLUME, value)));
        }

        private static void OnVolumeChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is FaderControl control)
            {
                control.UpdateFaderPosition();
                control.UpdateValueDisplay();
                control.VolumeChanged?.Invoke(control, control.Volume);
            }
        }

        /// <summary>
        /// Volume in decibels (-∞ to +6 dB).
        /// </summary>
        public double VolumeDb
        {
            get => VolumeToDb(Volume);
            set
            {
                Volume = DbToVolume(value);
                UpdateFaderPosition();
                UpdateValueDisplay();
                VolumeChanged?.Invoke(this, Volume);
            }
        }

        /// <summary>
        /// Event raised when volume changes.
        /// </summary>
        public event EventHandler<double>? VolumeChanged;

        /// <summary>
        /// Convert volume (0.0-2.0) to dB.
        /// 0.0 = -∞ dB, 1.0 = 0 dB, 2.0 = +6 dB
        /// </summary>
        private double VolumeToDb(double volume)
        {
            if (volume <= 0.0)
                return MIN_DB;
            if (volume >= MAX_VOLUME)
                return MAX_DB;
            
            // Linear mapping: 0.0-1.0 maps to MIN_DB to 0dB, 1.0-2.0 maps to 0dB to MAX_DB
            if (volume <= 1.0)
            {
                // 0.0-1.0 -> MIN_DB to 0dB
                return (volume / 1.0) * (0.0 - MIN_DB) + MIN_DB;
            }
            else
            {
                // 1.0-2.0 -> 0dB to MAX_DB
                var t = (volume - 1.0) / (MAX_VOLUME - 1.0);
                return t * (MAX_DB - 0.0) + 0.0;
            }
        }

        /// <summary>
        /// Convert dB to volume (0.0-2.0).
        /// </summary>
        private double DbToVolume(double db)
        {
            if (db <= MIN_DB)
                return 0.0;
            if (db >= MAX_DB)
                return MAX_VOLUME;
            
            // Inverse of VolumeToDb
            if (db <= 0.0)
            {
                // MIN_DB to 0dB -> 0.0-1.0
                var t = (db - MIN_DB) / (0.0 - MIN_DB);
                return t * 1.0 + 0.0;
            }
            else
            {
                // 0dB to MAX_DB -> 1.0-2.0
                var t = (db - 0.0) / (MAX_DB - 0.0);
                return t * (MAX_VOLUME - 1.0) + 1.0;
            }
        }

        /// <summary>
        /// Update fader position based on current volume.
        /// </summary>
        private void UpdateFaderPosition()
        {
            if (FaderBackground == null || FaderKnobTransform == null)
                return;

            var faderTrack = FaderBackground.Parent as FrameworkElement;
            if (faderTrack == null)
                return;

            var trackHeight = faderTrack.ActualHeight;
            if (trackHeight <= 0)
                return;

            // Calculate position from bottom (0.0 = bottom, 1.0 = top)
            // Map volume (0.0-2.0) to position (0.0-1.0)
            var volume = Volume;
            var normalizedPosition = volume / MAX_VOLUME;
            var faderPosition = trackHeight * normalizedPosition;

            // Set background height
            FaderBackground.Height = faderPosition;

            // Set knob position (knob center should be at fader position)
            var knobOffset = faderPosition - (FaderKnob?.ActualHeight ?? 20) / 2.0;
            FaderKnobTransform.Y = -knobOffset;
        }

        /// <summary>
        /// Update the value display text block with current volume in dB.
        /// </summary>
        private void UpdateValueDisplay()
        {
            if (ValueTextBlock == null)
                return;

            var db = VolumeToDb(Volume);
            if (db <= MIN_DB)
                ValueTextBlock.Text = "-∞ dB";
            else
                ValueTextBlock.Text = $"{db:F1} dB";
        }

        private void FaderKnob_PointerPressed(object sender, PointerRoutedEventArgs e)
        {
            if (FaderKnob == null || FaderBackground == null)
                return;

            _isDragging = true;
            var pointerPoint = e.GetCurrentPoint(FaderBackground.Parent as UIElement);
            _dragStartY = pointerPoint.Position.Y;
            _dragStartVolume = Volume;

            FaderKnob.CapturePointer(e.Pointer);
            e.Handled = true;
        }

        private void FaderKnob_PointerMoved(object sender, PointerRoutedEventArgs e)
        {
            if (!_isDragging || FaderBackground == null)
                return;

            var faderTrack = FaderBackground.Parent as FrameworkElement;
            if (faderTrack == null)
                return;

            var trackHeight = faderTrack.ActualHeight;
            if (trackHeight <= 0)
                return;

            var pointerPoint = e.GetCurrentPoint(faderTrack);
            var deltaY = _dragStartY - pointerPoint.Position.Y;
            
            // Convert pixel movement to volume change
            // Track goes from bottom (0.0) to top (2.0)
            // deltaY is positive when moving up (increasing volume)
            var deltaVolume = (deltaY / trackHeight) * MAX_VOLUME; // Scale to 0.0-2.0 range
            var newVolume = Math.Max(0.0, Math.Min(MAX_VOLUME, _dragStartVolume + deltaVolume));
            
            // Update drag start for next move
            _dragStartY = pointerPoint.Position.Y;
            _dragStartVolume = newVolume;
            Volume = newVolume;
            e.Handled = true;
        }

        private void FaderKnob_PointerReleased(object sender, PointerRoutedEventArgs e)
        {
            if (_isDragging && FaderKnob != null)
            {
                FaderKnob.ReleasePointerCapture(e.Pointer);
            }
            _isDragging = false;
            e.Handled = true;
        }

        // WinUI 3 UserControl doesn't have OnSizeChanged/OnLoaded overrides
        // Use event handlers instead
        private void FaderControl_SizeChanged(object sender, Microsoft.UI.Xaml.SizeChangedEventArgs e)
        {
            // Update fader position when control size changes
            UpdateFaderPosition();
        }

        private void FaderControl_Loaded(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
        {
            // Initialize value display after control is loaded
            UpdateValueDisplay();
        }
    }
}

