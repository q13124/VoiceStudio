// Phase 5.0: Service Unification
// Task 5.0.3: Unified Accessibility Service Interface
// This interface unifies Services/AccessibilityService and Features/Accessibility/AccessibilityService

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Automation.Peers;
using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.App.Services;

/// <summary>
/// Unified accessibility settings combining system detection and user preferences.
/// </summary>
public class UnifiedAccessibilitySettings
{
    // Screen reader support
    public bool ScreenReaderAnnouncements { get; set; } = true;
    public bool VerboseDescriptions { get; set; } = false;
    
    // Visual accessibility
    public bool HighContrastMode { get; set; } = false;
    public bool ReduceMotion { get; set; } = false;
    public double TextScaling { get; set; } = 1.0;
    public bool LargeText { get; set; } = false;
    
    // Color accessibility
    public bool ColorBlindSupport { get; set; } = false;
    public ColorBlindnessType ColorBlindType { get; set; } = ColorBlindnessType.None;
    
    // Keyboard accessibility
    public bool KeyboardNavigationIndicator { get; set; } = true;
    public bool FocusHighlight { get; set; } = true;
    
    // Audio accessibility
    public bool CaptionsEnabled { get; set; } = false;
    public bool VisualAudioIndicators { get; set; } = true;
    
    // Motor accessibility
    public int ClickDelayMs { get; set; } = 0;
    public bool StickyKeys { get; set; } = false;
}

/// <summary>
/// Types of color blindness.
/// </summary>
public enum ColorBlindnessType
{
    None,
    Protanopia,
    Deuteranopia,
    Tritanopia,
    Achromatopsia
}

/// <summary>
/// Announcement priority levels.
/// </summary>
public enum AnnouncePriority
{
    Polite,     // Wait for idle
    Assertive,  // Interrupt
    Off         // No announcement
}

/// <summary>
/// Accessibility settings changed event args.
/// </summary>
public class AccessibilitySettingsChangedEventArgs : EventArgs
{
    public string SettingName { get; set; } = string.Empty;
    public object? OldValue { get; set; }
    public object? NewValue { get; set; }
}

/// <summary>
/// Unified accessibility service interface combining system awareness,
/// screen reader support, visual accessibility, and focus management.
/// </summary>
public interface IUnifiedAccessibilityService
{
    #region Properties

    /// <summary>
    /// Gets the current accessibility settings.
    /// </summary>
    UnifiedAccessibilitySettings Settings { get; }

    /// <summary>
    /// Gets whether high contrast mode is enabled (system or user preference).
    /// </summary>
    bool IsHighContrastEnabled { get; }

    /// <summary>
    /// Gets whether reduced motion is preferred (system or user preference).
    /// </summary>
    bool IsReducedMotionEnabled { get; }

    /// <summary>
    /// Gets whether a screen reader is likely active.
    /// </summary>
    bool IsScreenReaderActive { get; }

    /// <summary>
    /// Gets the current text scale factor.
    /// </summary>
    double TextScaleFactor { get; }

    #endregion

    #region Initialization

    /// <summary>
    /// Initializes the accessibility service and detects system settings.
    /// </summary>
    Task InitializeAsync();

    #endregion

    #region Screen Reader Announcements

    /// <summary>
    /// Announces a message to screen readers.
    /// </summary>
    void Announce(string message, AnnouncePriority priority = AnnouncePriority.Polite);

    /// <summary>
    /// Announces a status update.
    /// </summary>
    void AnnounceStatus(string status);

    /// <summary>
    /// Announces an error message.
    /// </summary>
    void AnnounceError(string error);

    /// <summary>
    /// Announces a success message.
    /// </summary>
    void AnnounceSuccess(string message);

    #endregion

    #region Automation Properties

    /// <summary>
    /// Sets automation name for an element.
    /// </summary>
    void SetAccessibleName(UIElement element, string name);

    /// <summary>
    /// Sets automation help text for an element.
    /// </summary>
    void SetAccessibleDescription(UIElement element, string description);

    /// <summary>
    /// Sets the labeled-by relationship.
    /// </summary>
    void SetLabeledBy(UIElement element, UIElement label);

    /// <summary>
    /// Sets live region settings for dynamic content.
    /// </summary>
    void SetLiveRegion(UIElement element, AutomationLiveSetting setting);

    #endregion

    #region Focus Management

    /// <summary>
    /// Sets focus to an element with optional announcement.
    /// </summary>
    void SetFocusWithAnnouncement(Control control, string? announcement = null);

    /// <summary>
    /// Gets focusable elements in a container.
    /// </summary>
    IEnumerable<Control> GetFocusableElements(DependencyObject container);

    /// <summary>
    /// Creates a focus trap for modal dialogs.
    /// </summary>
    FocusTrap CreateFocusTrap(UIElement container);

    #endregion

    #region Color Accessibility

    /// <summary>
    /// Gets a color adjusted for color blindness.
    /// </summary>
    Windows.UI.Color GetAccessibleColor(Windows.UI.Color originalColor);

    /// <summary>
    /// Checks if two colors have sufficient contrast (WCAG AA).
    /// </summary>
    bool HasSufficientContrast(Windows.UI.Color foreground, Windows.UI.Color background, double minimumRatio = 4.5);

    /// <summary>
    /// Calculates contrast ratio between two colors.
    /// </summary>
    double CalculateContrastRatio(Windows.UI.Color foreground, Windows.UI.Color background);

    #endregion

    #region Animation Control

    /// <summary>
    /// Gets animation duration respecting reduced motion preference.
    /// </summary>
    TimeSpan GetAnimationDuration(TimeSpan normalDuration);

    /// <summary>
    /// Checks if animations should be skipped.
    /// </summary>
    bool ShouldSkipAnimation();

    #endregion

    #region Settings

    /// <summary>
    /// Updates accessibility settings.
    /// </summary>
    void UpdateSettings(Action<UnifiedAccessibilitySettings> update);

    /// <summary>
    /// Saves settings to persistent storage.
    /// </summary>
    Task SaveSettingsAsync();

    #endregion

    #region Events

    /// <summary>
    /// Event raised when accessibility settings change.
    /// </summary>
    event EventHandler<AccessibilitySettingsChangedEventArgs>? SettingsChanged;

    #endregion
}
