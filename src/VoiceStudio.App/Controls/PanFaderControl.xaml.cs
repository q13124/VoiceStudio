using System;
using Microsoft.UI.Input;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Horizontal pan fader control for stereo panning.
    /// Value range: -1.0 (Left) to 1.0 (Right), 0.0 = Center
    /// </summary>
    public sealed partial class PanFaderControl : UserControl
    {
        public static readonly DependencyProperty PanProperty =
            DependencyProperty.Register(
                nameof(Pan),
                typeof(double),
                typeof(PanFaderControl),
                new PropertyMetadata(0.0, OnPanChanged));

        public double Pan
        {
            get => (double)GetValue(PanProperty);
            set => SetValue(PanProperty, value);
        }

        private bool _isDragging = false;
        private double _dragStartX = 0;
        private double _dragStartPan = 0;

        public PanFaderControl()
        {
            this.InitializeComponent();
            UpdatePanDisplay();
            UpdateKnobPosition();
        }

        private static void OnPanChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is PanFaderControl control)
            {
                control.UpdatePanDisplay();
                control.UpdateKnobPosition();
            }
        }

        private void UpdatePanDisplay()
        {
            var pan = Pan;
            if (Math.Abs(pan) < 0.01)
            {
                ValueTextBlock.Text = "C";
            }
            else if (pan < 0)
            {
                // Left
                var percent = Math.Abs(pan) * 100;
                ValueTextBlock.Text = $"L{percent:F0}%";
            }
            else
            {
                // Right
                var percent = pan * 100;
                ValueTextBlock.Text = $"R{percent:F0}%";
            }
        }

        private void UpdateKnobPosition()
        {
            if (PanFaderKnobTransform == null)
                return;

            // Clamp pan to -1.0 to 1.0
            var pan = Math.Clamp(Pan, -1.0, 1.0);

            // Get the track width (accounting for margins)
            var trackWidth = ActualWidth - 8; // 4px margin on each side
            if (trackWidth <= 0)
                return;

            // Calculate position: -1.0 = left edge, 0.0 = center, 1.0 = right edge
            var maxOffset = (trackWidth - 20) / 2.0; // Half width minus knob width
            var xOffset = pan * maxOffset;

            PanFaderKnobTransform.X = xOffset;
        }

        private void PanFaderKnob_PointerPressed(object sender, PointerRoutedEventArgs e)
        {
            if (e.Pointer.PointerDeviceType == PointerDeviceType.Mouse)
            {
                var pointerPoint = e.GetCurrentPoint(this);
                _isDragging = true;
                _dragStartX = pointerPoint.Position.X;
                _dragStartPan = Pan;
                PanFaderKnob.CapturePointer(e.Pointer);
                e.Handled = true;
            }
        }

        private void PanFaderKnob_PointerMoved(object sender, PointerRoutedEventArgs e)
        {
            if (!_isDragging)
                return;

            var pointerPoint = e.GetCurrentPoint(this);
            var deltaX = pointerPoint.Position.X - _dragStartX;

            // Get the track width
            var trackWidth = ActualWidth - 8;
            if (trackWidth <= 0)
                return;

            var maxOffset = (trackWidth - 20) / 2.0;
            var currentOffset = PanFaderKnobTransform.X + deltaX;

            // Clamp to valid range
            currentOffset = Math.Clamp(currentOffset, -maxOffset, maxOffset);

            // Convert offset to pan value
            var newPan = maxOffset > 0 ? currentOffset / maxOffset : 0.0;
            newPan = Math.Clamp(newPan, -1.0, 1.0);

            Pan = newPan;
            _dragStartX = pointerPoint.Position.X;
            _dragStartPan = newPan;
            UpdateKnobPosition();
            e.Handled = true;
        }

        private void PanFaderKnob_PointerReleased(object sender, PointerRoutedEventArgs e)
        {
            if (_isDragging)
            {
                _isDragging = false;
                PanFaderKnob.ReleasePointerCapture(e.Pointer);
                e.Handled = true;
            }
        }

        // WinUI 3 UserControl doesn't have OnSizeChanged override with sender parameter
        // Use event handler instead
        private void PanFaderControl_SizeChanged(object sender, Microsoft.UI.Xaml.SizeChangedEventArgs e)
        {
            UpdateKnobPosition();
        }
    }
}

