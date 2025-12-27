using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Automation.Peers;
using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.App.Helpers
{
    /// <summary>
    /// Helper class for setting automation properties for screen reader support.
    /// Works in both DEBUG and RELEASE builds for accessibility.
    /// </summary>
    public static class AutomationHelper
    {
        /// <summary>
        /// Sets the automation ID for a UI element.
        /// </summary>
        public static void SetAutomationId(UIElement element, string id)
        {
            AutomationProperties.SetAutomationId(element, id);
        }

        /// <summary>
        /// Sets the automation name for a UI element (screen reader announcement).
        /// </summary>
        public static void SetAutomationName(UIElement element, string name)
        {
            AutomationProperties.SetName(element, name);
        }

        /// <summary>
        /// Sets the automation help text for a UI element (contextual help).
        /// </summary>
        public static void SetAutomationHelpText(UIElement element, string helpText)
        {
            AutomationProperties.SetHelpText(element, helpText);
        }

        /// <summary>
        /// Sets the labeled-by reference for a UI element (associates label with input).
        /// </summary>
        public static void SetLabeledBy(UIElement element, UIElement label)
        {
            AutomationProperties.SetLabeledBy(element, label);
        }

        /// <summary>
        /// Sets the live setting for dynamic content announcements.
        /// </summary>
        /// <param name="element">The UI element</param>
        /// <param name="setting">"Off", "Polite", or "Assertive"</param>
        public static void SetLiveSetting(UIElement element, string setting)
        {
            AutomationLiveSetting liveSetting = setting?.ToLower() switch
            {
                "polite" => AutomationLiveSetting.Polite,
                "assertive" => AutomationLiveSetting.Assertive,
                _ => AutomationLiveSetting.Off
            };
            AutomationProperties.SetLiveSetting(element, liveSetting);
        }

        /// <summary>
        /// Sets the position in set for list items.
        /// </summary>
        public static void SetPositionInSet(UIElement element, int position)
        {
            AutomationProperties.SetPositionInSet(element, position);
        }

        /// <summary>
        /// Sets the size of set for list items.
        /// </summary>
        public static void SetSizeOfSet(UIElement element, int size)
        {
            AutomationProperties.SetSizeOfSet(element, size);
        }

        /// <summary>
        /// Sets the heading level for heading elements.
        /// </summary>
        public static void SetHeadingLevel(UIElement element, int level)
        {
            // Convert int level (1-9) to AutomationHeadingLevel enum
            AutomationHeadingLevel headingLevel = level switch
            {
                1 => AutomationHeadingLevel.Level1,
                2 => AutomationHeadingLevel.Level2,
                3 => AutomationHeadingLevel.Level3,
                4 => AutomationHeadingLevel.Level4,
                5 => AutomationHeadingLevel.Level5,
                6 => AutomationHeadingLevel.Level6,
                7 => AutomationHeadingLevel.Level7,
                8 => AutomationHeadingLevel.Level8,
                9 => AutomationHeadingLevel.Level9,
                _ => AutomationHeadingLevel.None
            };
            AutomationProperties.SetHeadingLevel(element, headingLevel);
        }

        /// <summary>
        /// Configures a button with comprehensive automation properties.
        /// </summary>
        public static void ConfigureButton(Button button, string name, string helpText, string? automationId = null)
        {
            SetAutomationName(button, name);
            SetAutomationHelpText(button, helpText);
            if (!string.IsNullOrEmpty(automationId))
            {
                SetAutomationId(button, automationId);
            }
        }

        /// <summary>
        /// Configures a text input with label association.
        /// </summary>
        public static void ConfigureTextInput(TextBox textBox, string name, string helpText, UIElement? label = null, string? automationId = null)
        {
            SetAutomationName(textBox, name);
            SetAutomationHelpText(textBox, helpText);
            if (label != null)
            {
                SetLabeledBy(textBox, label);
            }
            if (!string.IsNullOrEmpty(automationId))
            {
                SetAutomationId(textBox, automationId);
            }
        }

        /// <summary>
        /// Configures a slider with value announcement.
        /// </summary>
        public static void ConfigureSlider(Slider slider, string name, string helpText, string? automationId = null)
        {
            SetAutomationName(slider, name);
            SetAutomationHelpText(slider, helpText);
            if (!string.IsNullOrEmpty(automationId))
            {
                SetAutomationId(slider, automationId);
            }
        }

        /// <summary>
        /// Configures dynamic content with live region.
        /// </summary>
        public static void ConfigureLiveRegion(UIElement element, string name, string liveSetting = "Polite", string? automationId = null)
        {
            SetAutomationName(element, name);
            SetLiveSetting(element, liveSetting);
            if (!string.IsNullOrEmpty(automationId))
            {
                SetAutomationId(element, automationId);
            }
        }
    }
}

