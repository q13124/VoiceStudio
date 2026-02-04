using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Automation.Peers;
using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.App.Utilities
{
  /// <summary>
  /// Helper utilities for accessibility features including ARIA properties,
  /// keyboard navigation, and contrast checking.
  /// </summary>
  public static class AccessibilityHelpers
  {
    /// <summary>
    /// Sets accessibility properties on a control.
    /// </summary>
    /// <param name="element">The UI element</param>
    /// <param name="name">Accessible name</param>
    /// <param name="helpText">Help text for screen readers</param>
    /// <param name="itemStatus">Status information (e.g., "Error", "Loading")</param>
    public static void SetAccessibilityProperties(
        DependencyObject element,
        string? name = null,
        string? helpText = null,
        string? itemStatus = null)
    {
      if (element == null)
        return;

      if (!string.IsNullOrEmpty(name))
      {
        AutomationProperties.SetName(element, name);
      }

      if (!string.IsNullOrEmpty(helpText))
      {
        AutomationProperties.SetHelpText(element, helpText);
      }

      if (!string.IsNullOrEmpty(itemStatus))
      {
        AutomationProperties.SetItemStatus(element, itemStatus);
      }
    }

    /// <summary>
    /// Sets the labeled-by relationship for form fields.
    /// </summary>
    /// <param name="control">The form control</param>
    /// <param name="label">The label element</param>
    public static void SetLabeledBy(DependencyObject control, UIElement label)
    {
      if (control != null && label != null)
      {
        AutomationProperties.SetLabeledBy(control, label);
      }
    }

    /// <summary>
    /// Ensures a control meets minimum hit target size (44x44px per WCAG 2.5.5).
    /// </summary>
    /// <param name="element">The UI element</param>
    public static void EnsureMinimumHitTarget(FrameworkElement element)
    {
      if (element == null)
        return;

      const double minSize = 44.0; // WCAG 2.5.5 minimum

      if (element.MinWidth < minSize)
      {
        element.MinWidth = minSize;
      }

      if (element.MinHeight < minSize)
      {
        element.MinHeight = minSize;
      }
    }

    /// <summary>
    /// Sets keyboard focus order (TabIndex) for a control.
    /// </summary>
    /// <param name="element">The UI element</param>
    /// <param name="tabIndex">Tab order index</param>
    public static void SetTabIndex(Control element, int tabIndex)
    {
      if (element != null)
      {
        element.TabIndex = tabIndex;
      }
    }

    /// <summary>
    /// Sets whether a control is excluded from tab navigation.
    /// </summary>
    /// <param name="element">The UI element</param>
    /// <param name="excluded">True to exclude from tab navigation</param>
    public static void SetIsTabStop(Control element, bool excluded)
    {
      if (element != null)
      {
        element.IsTabStop = !excluded;
      }
    }

    /// <summary>
    /// Calculates contrast ratio between two colors (WCAG AA/AAA compliance).
    /// Returns ratio from 1.0 (no contrast) to 21.0 (maximum contrast).
    /// </summary>
    /// <param name="foreground">Foreground color (hex format, e.g., "#FFFFFF")</param>
    /// <param name="background">Background color (hex format, e.g., "#000000")</param>
    /// <returns>Contrast ratio</returns>
    public static double CalculateContrastRatio(string foreground, string background)
    {
      var fgLuminance = GetLuminance(foreground);
      var bgLuminance = GetLuminance(background);

      var lighter = Math.Max(fgLuminance, bgLuminance);
      var darker = Math.Min(fgLuminance, bgLuminance);

      return (lighter + 0.05) / (darker + 0.05);
    }

    /// <summary>
    /// Checks if contrast ratio meets WCAG AA standards.
    /// </summary>
    /// <param name="foreground">Foreground color</param>
    /// <param name="background">Background color</param>
    /// <param name="isLargeText">True if text is large (18pt+ or 14pt+ bold)</param>
    /// <returns>True if meets WCAG AA standards</returns>
    public static bool MeetsWCAGAA(string foreground, string background, bool isLargeText = false)
    {
      var ratio = CalculateContrastRatio(foreground, background);
      return isLargeText ? ratio >= 3.0 : ratio >= 4.5;
    }

    /// <summary>
    /// Checks if contrast ratio meets WCAG AAA standards.
    /// </summary>
    /// <param name="foreground">Foreground color</param>
    /// <param name="background">Background color</param>
    /// <param name="isLargeText">True if text is large (18pt+ or 14pt+ bold)</param>
    /// <returns>True if meets WCAG AAA standards</returns>
    public static bool MeetsWCAGAAA(string foreground, string background, bool isLargeText = false)
    {
      var ratio = CalculateContrastRatio(foreground, background);
      return isLargeText ? ratio >= 4.5 : ratio >= 7.0;
    }

    /// <summary>
    /// Gets relative luminance of a color (for contrast calculation).
    /// </summary>
    private static double GetLuminance(string hexColor)
    {
      // Remove # if present
      hexColor = hexColor.TrimStart('#');

      // Parse RGB values
      if (hexColor.Length == 6)
      {
        var r = Convert.ToInt32(hexColor.Substring(0, 2), 16) / 255.0;
        var g = Convert.ToInt32(hexColor.Substring(2, 2), 16) / 255.0;
        var b = Convert.ToInt32(hexColor.Substring(4, 2), 16) / 255.0;

        // Convert to linear RGB
        r = r <= 0.03928 ? r / 12.92 : Math.Pow((r + 0.055) / 1.055, 2.4);
        g = g <= 0.03928 ? g / 12.92 : Math.Pow((g + 0.055) / 1.055, 2.4);
        b = b <= 0.03928 ? b / 12.92 : Math.Pow((b + 0.055) / 1.055, 2.4);

        // Calculate relative luminance
        return (0.2126 * r) + (0.7152 * g) + (0.0722 * b);
      }

      return 0.0;
    }

    /// <summary>
    /// Sets live region properties for dynamic content updates.
    /// </summary>
    /// <param name="element">The UI element</param>
    /// <param name="liveSetting">Live region setting (Off, Polite, Assertive)</param>
    public static void SetLiveRegion(DependencyObject element, AutomationLiveSetting liveSetting)
    {
      if (element != null)
      {
        AutomationProperties.SetLiveSetting(element, liveSetting);
      }
    }

    /// <summary>
    /// Sets keyboard accelerator for a control.
    /// </summary>
    /// <param name="element">The UI element</param>
    /// <param name="key">Virtual key</param>
    /// <param name="modifiers">Modifier keys (Ctrl, Alt, Shift)</param>
    public static void SetKeyboardAccelerator(UIElement element, Windows.System.VirtualKey key, Windows.System.VirtualKeyModifiers modifiers = Windows.System.VirtualKeyModifiers.None)
    {
      if (element == null)
        return;

      var accelerator = new Microsoft.UI.Xaml.Input.KeyboardAccelerator
      {
        Key = key,
        Modifiers = modifiers
      };

      element.KeyboardAccelerators.Add(accelerator);
    }
  }
}