using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Media.Animation;
using System;
using Windows.Foundation;
using Windows.UI;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Service for providing enhanced visual feedback during drag-and-drop operations.
  /// Implements IDEA 4: Enhanced Drag-and-Drop Visual Feedback.
  /// </summary>
  public class DragDropVisualFeedbackService
  {
    private Border? _dragPreview;
    private Border? _dropTargetIndicator;
    private UIElement? _currentDropTarget;

    /// <summary>
    /// Creates a visual preview for the dragged item.
    /// </summary>
    public UIElement CreateDragPreview(UIElement sourceElement, string? label = null)
    {
      // Clone the visual appearance of the source element
      var preview = new Border
      {
        Background = new SolidColorBrush(Windows.UI.Color.FromArgb(200, 0, 120, 212)), // Semi-transparent cyan
        CornerRadius = new Microsoft.UI.Xaml.CornerRadius(4),
        Padding = new Thickness(8, 4, 8, 4),
        Opacity = 0.9,
        RenderTransform = new ScaleTransform { ScaleX = 0.95, ScaleY = 0.95 }
      };

      if (!string.IsNullOrEmpty(label))
      {
        preview.Child = new TextBlock
        {
          Text = label,
          Foreground = new SolidColorBrush(Microsoft.UI.Colors.White),
          FontSize = 12,
          FontWeight = Microsoft.UI.Text.FontWeights.SemiBold
        };
      }
      else
      {
        // Try to extract text from source element
        var text = ExtractTextFromElement(sourceElement);
        if (!string.IsNullOrEmpty(text))
        {
          preview.Child = new TextBlock
          {
            Text = text,
            Foreground = new SolidColorBrush(Microsoft.UI.Colors.White),
            FontSize = 12
          };
        }
      }

      _dragPreview = preview;
      return preview;
    }

    /// <summary>
    /// Shows drop target indicator at the specified position.
    /// </summary>
    public void ShowDropTargetIndicator(UIElement targetElement, DropPosition position)
    {
      HideDropTargetIndicator();

      var indicator = new Border
      {
        Background = new SolidColorBrush(Windows.UI.Color.FromArgb(150, 0, 255, 127)), // Semi-transparent green
        BorderBrush = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 0, 255, 127)),
        BorderThickness = new Thickness(2),
        CornerRadius = new Microsoft.UI.Xaml.CornerRadius(4),
        Opacity = 0.8
      };

      // Position indicator based on drop position
      switch (position)
      {
        case DropPosition.Before:
          indicator.Height = 4;
          indicator.Margin = new Thickness(0, -2, 0, 0);
          break;
        case DropPosition.After:
          indicator.Height = 4;
          indicator.Margin = new Thickness(0, 0, 0, -2);
          break;
        case DropPosition.On:
          indicator.Opacity = 0.3;
          break;
      }

      _dropTargetIndicator = indicator;
      _currentDropTarget = targetElement;

      // Add indicator to target element's parent or overlay
      if (targetElement is FrameworkElement fe && fe.Parent is Panel parent)
      {
        parent.Children.Add(indicator);
      }
    }

    /// <summary>
    /// Hides the drop target indicator.
    /// </summary>
    public void HideDropTargetIndicator()
    {
      if (_dropTargetIndicator != null && _currentDropTarget != null)
      {
        if (_currentDropTarget is FrameworkElement fe && fe.Parent is Panel parent)
        {
          parent.Children.Remove(_dropTargetIndicator);
        }
        _dropTargetIndicator = null;
        _currentDropTarget = null;
      }
    }

    /// <summary>
    /// Updates the drag preview position.
    /// </summary>
    public void UpdateDragPreviewPosition(Point position)
    {
      if (_dragPreview != null)
      {
        Canvas.SetLeft(_dragPreview, position.X);
        Canvas.SetTop(_dragPreview, position.Y);
      }
    }

    /// <summary>
    /// Cleans up all visual feedback.
    /// </summary>
    public void Cleanup()
    {
      HideDropTargetIndicator();
      _dragPreview = null;
    }

    /// <summary>
    /// Extracts text content from a UI element for preview.
    /// </summary>
    private string? ExtractTextFromElement(UIElement element)
    {
      if (element is TextBlock textBlock)
        return textBlock.Text;

      if (element is Button button && button.Content is string str)
        return str;

      if (element is ContentControl contentControl && contentControl.Content is string contentStr)
        return contentStr;

      // Try to find TextBlock in children
      if (element is FrameworkElement fe)
      {
        var text = FindTextInChildren(fe);
        if (!string.IsNullOrEmpty(text))
          return text;
      }

      return null;
    }

    /// <summary>
    /// Recursively finds text in child elements.
    /// </summary>
    private string? FindTextInChildren(FrameworkElement element)
    {
      if (element is TextBlock tb)
        return tb.Text;

      if (element is Panel panel)
      {
        foreach (var child in panel.Children)
        {
          if (child is FrameworkElement childFe)
          {
            var text = FindTextInChildren(childFe);
            if (!string.IsNullOrEmpty(text))
              return text;
          }
        }
      }

      return null;
    }
  }

  /// <summary>
  /// Represents the position where an item can be dropped.
  /// </summary>
  public enum DropPosition
  {
    Before = 0,  // Drop before the target
    After = 1,   // Drop after the target
    On = 2       // Drop on the target (replace/merge)
  }
}