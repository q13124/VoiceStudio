using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Automation.Peers;
using Microsoft.UI.Xaml.Controls;
using Windows.UI.ViewManagement;

namespace VoiceStudio.App.Services;

/// <summary>
/// Accessibility service for WCAG compliance.
/// 
/// Phase 15.2: Accessibility
/// Provides comprehensive accessibility support including screen reader,
/// high contrast, reduced motion, and focus management.
/// </summary>
public class AccessibilityService
{
    private readonly UISettings _uiSettings;
    private readonly AccessibilitySettings _accessibilitySettings;
    private bool _isHighContrastEnabled;
    private bool _isReducedMotionEnabled;
    private bool _isScreenReaderActive;

    public event EventHandler<AccessibilityChangedEventArgs>? SettingsChanged;

    public AccessibilityService()
    {
        _uiSettings = new UISettings();
        _accessibilitySettings = new AccessibilitySettings();

        // Initialize settings
        _isHighContrastEnabled = _accessibilitySettings.HighContrast;
        _isReducedMotionEnabled = !_uiSettings.AnimationsEnabled;

        // Listen for changes
        _accessibilitySettings.HighContrastChanged += OnHighContrastChanged;
        _uiSettings.AnimationsEnabledChanged += OnAnimationsEnabledChanged;
    }

    #region Properties

    /// <summary>
    /// Gets whether high contrast mode is enabled.
    /// </summary>
    public bool IsHighContrastEnabled => _isHighContrastEnabled;

    /// <summary>
    /// Gets whether reduced motion is preferred.
    /// </summary>
    public bool IsReducedMotionEnabled => _isReducedMotionEnabled;

    /// <summary>
    /// Gets whether a screen reader is likely active.
    /// </summary>
    public bool IsScreenReaderActive => _isScreenReaderActive;

    /// <summary>
    /// Gets whether animations should be used.
    /// </summary>
    public bool ShouldUseAnimations => !_isReducedMotionEnabled;

    #endregion

    #region Screen Reader Support

    /// <summary>
    /// Announce a message to screen readers.
    /// </summary>
    public void Announce(string message, AutomationNotificationKind kind = AutomationNotificationKind.Other)
    {
        // Create a temporary TextBlock for announcement
        var announcer = new TextBlock
        {
            Text = message,
        };

        AutomationProperties.SetLiveSetting(announcer, AutomationLiveSetting.Assertive);

        // Raise notification
        if (AutomationPeer.ListenerExists(AutomationEvents.LiveRegionChanged))
        {
            var peer = FrameworkElementAutomationPeer.CreatePeerForElement(announcer);
            peer?.RaiseAutomationEvent(AutomationEvents.LiveRegionChanged);
        }
    }

    /// <summary>
    /// Announce a polite message (non-interrupting).
    /// </summary>
    public void AnnouncePolite(string message)
    {
        var announcer = new TextBlock
        {
            Text = message,
        };

        AutomationProperties.SetLiveSetting(announcer, AutomationLiveSetting.Polite);

        if (AutomationPeer.ListenerExists(AutomationEvents.LiveRegionChanged))
        {
            var peer = FrameworkElementAutomationPeer.CreatePeerForElement(announcer);
            peer?.RaiseAutomationEvent(AutomationEvents.LiveRegionChanged);
        }
    }

    /// <summary>
    /// Set accessible name for an element.
    /// </summary>
    public static void SetAccessibleName(UIElement element, string name)
    {
        AutomationProperties.SetName(element, name);
    }

    /// <summary>
    /// Set accessible description for an element.
    /// </summary>
    public static void SetAccessibleDescription(UIElement element, string description)
    {
        AutomationProperties.SetHelpText(element, description);
    }

    /// <summary>
    /// Set accessible label for an element.
    /// </summary>
    public static void SetLabeledBy(UIElement element, UIElement label)
    {
        AutomationProperties.SetLabeledBy(element, label);
    }

    /// <summary>
    /// Set live region settings for dynamic content.
    /// </summary>
    public static void SetLiveRegion(UIElement element, AutomationLiveSetting setting)
    {
        AutomationProperties.SetLiveSetting(element, setting);
    }

    #endregion

    #region Focus Management

    /// <summary>
    /// Set focus to an element with announcement.
    /// </summary>
    public void SetFocusWithAnnouncement(Control control, string announcement)
    {
        control.Focus(FocusState.Programmatic);
        Announce(announcement);
    }

    /// <summary>
    /// Create a focus trap for modal dialogs.
    /// </summary>
    public FocusTrap CreateFocusTrap(UIElement container)
    {
        return new FocusTrap(container);
    }

    /// <summary>
    /// Get focusable elements in a container.
    /// </summary>
    public static IEnumerable<Control> GetFocusableElements(DependencyObject container)
    {
        var focusable = new List<Control>();
        GetFocusableElementsRecursive(container, focusable);
        return focusable;
    }

    private static void GetFocusableElementsRecursive(DependencyObject parent, List<Control> focusable)
    {
        int count = Microsoft.UI.Xaml.Media.VisualTreeHelper.GetChildrenCount(parent);

        for (int i = 0; i < count; i++)
        {
            var child = Microsoft.UI.Xaml.Media.VisualTreeHelper.GetChild(parent, i);

            if (child is Control control &&
                control.IsEnabled &&
                control.IsTabStop &&
                control.Visibility == Visibility.Visible)
            {
                focusable.Add(control);
            }

            GetFocusableElementsRecursive(child, focusable);
        }
    }

    #endregion

    #region Contrast and Colors

    /// <summary>
    /// Get high contrast safe color.
    /// </summary>
    public Windows.UI.Color GetAccessibleColor(Windows.UI.Color normalColor, Windows.UI.Color highContrastColor)
    {
        return _isHighContrastEnabled ? highContrastColor : normalColor;
    }

    /// <summary>
    /// Check if two colors have sufficient contrast (WCAG AA).
    /// </summary>
    public static bool HasSufficientContrast(Windows.UI.Color foreground, Windows.UI.Color background, double minimumRatio = 4.5)
    {
        var ratio = CalculateContrastRatio(foreground, background);
        return ratio >= minimumRatio;
    }

    /// <summary>
    /// Calculate contrast ratio between two colors.
    /// </summary>
    public static double CalculateContrastRatio(Windows.UI.Color foreground, Windows.UI.Color background)
    {
        var l1 = GetRelativeLuminance(foreground);
        var l2 = GetRelativeLuminance(background);

        var lighter = Math.Max(l1, l2);
        var darker = Math.Min(l1, l2);

        return (lighter + 0.05) / (darker + 0.05);
    }

    private static double GetRelativeLuminance(Windows.UI.Color color)
    {
        double r = GetLuminanceComponent(color.R / 255.0);
        double g = GetLuminanceComponent(color.G / 255.0);
        double b = GetLuminanceComponent(color.B / 255.0);

        return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    }

    private static double GetLuminanceComponent(double value)
    {
        return value <= 0.03928
            ? value / 12.92
            : Math.Pow((value + 0.055) / 1.055, 2.4);
    }

    #endregion

    #region Motion and Animation

    /// <summary>
    /// Get animation duration respecting reduced motion preference.
    /// </summary>
    public TimeSpan GetAnimationDuration(TimeSpan normalDuration)
    {
        return _isReducedMotionEnabled ? TimeSpan.Zero : normalDuration;
    }

    /// <summary>
    /// Check if animations should be skipped.
    /// </summary>
    public bool ShouldSkipAnimation() => _isReducedMotionEnabled;

    #endregion

    #region Text Scaling

    /// <summary>
    /// Get scaled font size.
    /// </summary>
    public double GetScaledFontSize(double baseFontSize)
    {
        var textScaleFactor = _uiSettings.TextScaleFactor;
        return baseFontSize * textScaleFactor;
    }

    /// <summary>
    /// Get current text scale factor.
    /// </summary>
    public double TextScaleFactor => _uiSettings.TextScaleFactor;

    #endregion

    #region Event Handlers

    private void OnHighContrastChanged(AccessibilitySettings sender, object args)
    {
        _isHighContrastEnabled = sender.HighContrast;
        SettingsChanged?.Invoke(this, new AccessibilityChangedEventArgs
        {
            SettingName = "HighContrast",
            NewValue = _isHighContrastEnabled,
        });
    }

    private void OnAnimationsEnabledChanged(UISettings sender, UISettingsAnimationsEnabledChangedEventArgs args)
    {
        _isReducedMotionEnabled = !_uiSettings.AnimationsEnabled;
        SettingsChanged?.Invoke(this, new AccessibilityChangedEventArgs
        {
            SettingName = "ReducedMotion",
            NewValue = _isReducedMotionEnabled,
        });
    }

    #endregion

    #region Cleanup

    public void Dispose()
    {
        _accessibilitySettings.HighContrastChanged -= OnHighContrastChanged;
        _uiSettings.AnimationsEnabledChanged -= OnAnimationsEnabledChanged;
    }

    #endregion
}

/// <summary>
/// Focus trap for modal dialogs to keep focus within container.
/// </summary>
public class FocusTrap : IDisposable
{
    private readonly UIElement _container;
    private readonly List<Control> _focusableElements;
    private bool _isActive;

    public FocusTrap(UIElement container)
    {
        _container = container;
        _focusableElements = new List<Control>(AccessibilityService.GetFocusableElements(container));
    }

    public void Activate()
    {
        _isActive = true;
        if (_focusableElements.Count > 0)
        {
            _focusableElements[0].Focus(FocusState.Programmatic);
        }
    }

    public void Deactivate()
    {
        _isActive = false;
    }

    public void HandleTabNavigation(bool isShiftPressed)
    {
        if (!_isActive || _focusableElements.Count == 0)
            return;

        var currentFocus = FocusManager.GetFocusedElement() as Control;
        var currentIndex = _focusableElements.IndexOf(currentFocus!);

        int nextIndex;
        if (isShiftPressed)
        {
            nextIndex = currentIndex <= 0 ? _focusableElements.Count - 1 : currentIndex - 1;
        }
        else
        {
            nextIndex = currentIndex >= _focusableElements.Count - 1 ? 0 : currentIndex + 1;
        }

        _focusableElements[nextIndex].Focus(FocusState.Keyboard);
    }

    public void Dispose()
    {
        Deactivate();
    }
}

/// <summary>
/// Event args for accessibility setting changes.
/// </summary>
public class AccessibilityChangedEventArgs : EventArgs
{
    public string SettingName { get; set; } = string.Empty;
    public object? NewValue { get; set; }
}
