using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using System;
using Windows.Foundation;

namespace VoiceStudio.App.Controls
{
  /// <summary>
  /// Resize handle control for panels.
  /// Implements IDEA 9: Panel Resize Handles with Visual Feedback.
  /// </summary>
  public sealed partial class PanelResizeHandle : UserControl
  {
    private bool _isResizing;
    private Point _lastPointerPosition;
    private FrameworkElement? _targetElement;

    public static readonly DependencyProperty ResizeDirectionProperty =
        DependencyProperty.Register(
            nameof(ResizeDirection),
            typeof(ResizeDirection),
            typeof(PanelResizeHandle),
            new PropertyMetadata(ResizeDirection.Horizontal));

    public static readonly DependencyProperty TargetElementProperty =
        DependencyProperty.Register(
            nameof(TargetElement),
            typeof(FrameworkElement),
            typeof(PanelResizeHandle),
            new PropertyMetadata(null, OnTargetElementChanged));

    public ResizeDirection ResizeDirection
    {
      get => (ResizeDirection)GetValue(ResizeDirectionProperty);
      set => SetValue(ResizeDirectionProperty, value);
    }

    public FrameworkElement? TargetElement
    {
      get => (FrameworkElement?)GetValue(TargetElementProperty);
      set => SetValue(TargetElementProperty, value);
    }

    public PanelResizeHandle()
    {
      this.InitializeComponent();
      this.PointerPressed += PanelResizeHandle_PointerPressed;
      this.PointerMoved += PanelResizeHandle_PointerMoved;
      this.PointerReleased += PanelResizeHandle_PointerReleased;
      this.PointerCanceled += PanelResizeHandle_PointerCanceled;
    }

    private static void OnTargetElementChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
      if (d is PanelResizeHandle handle)
      {
        handle._targetElement = e.NewValue as FrameworkElement;
      }
    }

    private void PanelResizeHandle_PointerPressed(object _, PointerRoutedEventArgs e)
    {
      if (_targetElement == null)
        return;

      _isResizing = true;
      _lastPointerPosition = e.GetCurrentPoint(this).Position;
      this.CapturePointer(e.Pointer);
      e.Handled = true;

      // Change cursor based on resize direction
      var cursorShape = ResizeDirection switch
      {
        ResizeDirection.Horizontal => Microsoft.UI.Input.InputSystemCursorShape.SizeWestEast,
        ResizeDirection.Vertical => Microsoft.UI.Input.InputSystemCursorShape.SizeNorthSouth,
        ResizeDirection.Both => Microsoft.UI.Input.InputSystemCursorShape.SizeNorthwestSoutheast,
        _ => Microsoft.UI.Input.InputSystemCursorShape.SizeWestEast
      };
      this.ProtectedCursor = Microsoft.UI.Input.InputSystemCursor.Create(cursorShape);
    }

    private void PanelResizeHandle_PointerMoved(object _, PointerRoutedEventArgs e)
    {
      if (!_isResizing || _targetElement == null)
        return;

      var currentPosition = e.GetCurrentPoint(this).Position;
      var deltaX = currentPosition.X - _lastPointerPosition.X;
      var deltaY = currentPosition.Y - _lastPointerPosition.Y;

      // Try to resize Grid column/row first (preferred method)
      if (TryResizeGridColumnOrRow(_targetElement, deltaX, deltaY))
      {
        _lastPointerPosition = currentPosition;
        e.Handled = true;
        return;
      }

      // Fallback: Resize target element directly
      if (ResizeDirection == ResizeDirection.Horizontal)
      {
        // Resize width
        var currentWidth = _targetElement.Width;
        if (double.IsNaN(currentWidth) || currentWidth == 0)
        {
          currentWidth = _targetElement.ActualWidth;
        }
        var newWidth = currentWidth + deltaX;
        var minWidth = _targetElement.MinWidth > 0 ? _targetElement.MinWidth : 100;
        var maxWidth = _targetElement.MaxWidth < double.PositiveInfinity ? _targetElement.MaxWidth : double.PositiveInfinity;

        if (newWidth >= minWidth && (maxWidth == double.PositiveInfinity || newWidth <= maxWidth))
        {
          _targetElement.Width = newWidth;
        }
      }
      else if (ResizeDirection == ResizeDirection.Vertical)
      {
        // Resize height
        var currentHeight = _targetElement.Height;
        if (double.IsNaN(currentHeight) || currentHeight == 0)
        {
          currentHeight = _targetElement.ActualHeight;
        }
        var newHeight = currentHeight + deltaY;
        var minHeight = _targetElement.MinHeight > 0 ? _targetElement.MinHeight : 100;
        var maxHeight = _targetElement.MaxHeight < double.PositiveInfinity ? _targetElement.MaxHeight : double.PositiveInfinity;

        if (newHeight >= minHeight && (maxHeight == double.PositiveInfinity || newHeight <= maxHeight))
        {
          _targetElement.Height = newHeight;
        }
      }
      else if (ResizeDirection == ResizeDirection.Both)
      {
        // Resize both
        var currentWidth = _targetElement.Width;
        var currentHeight = _targetElement.Height;
        if (double.IsNaN(currentWidth) || currentWidth == 0)
          currentWidth = _targetElement.ActualWidth;
        if (double.IsNaN(currentHeight) || currentHeight == 0)
          currentHeight = _targetElement.ActualHeight;

        var newWidth = currentWidth + deltaX;
        var newHeight = currentHeight + deltaY;

        var minWidth = _targetElement.MinWidth > 0 ? _targetElement.MinWidth : 100;
        var maxWidth = _targetElement.MaxWidth < double.PositiveInfinity ? _targetElement.MaxWidth : double.PositiveInfinity;
        var minHeight = _targetElement.MinHeight > 0 ? _targetElement.MinHeight : 100;
        var maxHeight = _targetElement.MaxHeight < double.PositiveInfinity ? _targetElement.MaxHeight : double.PositiveInfinity;

        if (newWidth >= minWidth && (maxWidth == double.PositiveInfinity || newWidth <= maxWidth))
        {
          _targetElement.Width = newWidth;
        }
        if (newHeight >= minHeight && (maxHeight == double.PositiveInfinity || newHeight <= maxHeight))
        {
          _targetElement.Height = newHeight;
        }
      }

      _lastPointerPosition = currentPosition;
      e.Handled = true;
    }

    /// <summary>
    /// Attempts to resize the Grid column or row that contains the target element.
    /// Returns true if successful, false if target is not in a Grid or resize failed.
    /// </summary>
    private bool TryResizeGridColumnOrRow(FrameworkElement target, double deltaX, double deltaY)
    {
      // Find parent Grid
      var parent = target.Parent;
      Grid? parentGrid = null;

      while (parent != null)
      {
        if (parent is Grid grid)
        {
          parentGrid = grid;
          break;
        }
        if (parent is FrameworkElement fe)
        {
          parent = fe.Parent;
        }
        else
        {
          break;
        }
      }

      if (parentGrid == null)
        return false;

      // Get Grid column/row indices
      var column = Grid.GetColumn(target);
      var row = Grid.GetColumnSpan(target) > 1 ? -1 : column; // Handle column span
      var actualRow = Grid.GetRow(target);

      bool resized = false;

      // Resize Grid column (for horizontal resize)
      if (ResizeDirection == ResizeDirection.Horizontal && deltaX != 0 && column >= 0)
      {
        if (column < parentGrid.ColumnDefinitions.Count)
        {
          var colDef = parentGrid.ColumnDefinitions[column];
          if (colDef.Width.IsStar)
          {
            // Resize star-sized column
            var currentValue = colDef.Width.Value;
            var newValue = Math.Max(0.1, currentValue + (deltaX / 100.0)); // Scale delta for star units
            colDef.Width = new GridLength(newValue, GridUnitType.Star);
            resized = true;
          }
          else if (colDef.Width.IsAbsolute)
          {
            // Resize absolute-sized column
            var currentValue = colDef.Width.Value;
            var newValue = Math.Max(100, currentValue + deltaX);
            colDef.Width = new GridLength(newValue, GridUnitType.Pixel);
            resized = true;
          }
        }
      }

      // Resize Grid row (for vertical resize)
      if (ResizeDirection == ResizeDirection.Vertical && deltaY != 0 && actualRow >= 0)
      {
        if (actualRow < parentGrid.RowDefinitions.Count)
        {
          var rowDef = parentGrid.RowDefinitions[actualRow];
          if (rowDef.Height.IsStar)
          {
            // Resize star-sized row
            var currentValue = rowDef.Height.Value;
            var newValue = Math.Max(0.1, currentValue + (deltaY / 100.0)); // Scale delta for star units
            rowDef.Height = new GridLength(newValue, GridUnitType.Star);
            resized = true;
          }
          else if (rowDef.Height.IsAbsolute)
          {
            // Resize absolute-sized row
            var currentValue = rowDef.Height.Value;
            var newValue = Math.Max(100, currentValue + deltaY);
            rowDef.Height = new GridLength(newValue, GridUnitType.Pixel);
            resized = true;
          }
        }
      }

      return resized;
    }

    private void PanelResizeHandle_PointerReleased(object _, PointerRoutedEventArgs e)
    {
      EndResize();
      e.Handled = true;
    }

    private void PanelResizeHandle_PointerCanceled(object _, PointerRoutedEventArgs e)
    {
      EndResize();
      e.Handled = true;
    }

    private void EndResize()
    {
      if (_isResizing)
      {
        _isResizing = false;
        if (this.PointerCaptures.Count > 0)
        {
          this.ReleasePointerCapture(this.PointerCaptures[0]);
        }
        this.ProtectedCursor = null;
      }
    }
  }

  /// <summary>
  /// Direction in which the resize handle allows resizing.
  /// </summary>
  public enum ResizeDirection
  {
    Horizontal = 0,  // Resize width only
    Vertical = 1,    // Resize height only
    Both = 2         // Resize both width and height
  }
}