using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Media;
using Windows.System;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Helper service for managing keyboard navigation across panels.
    /// Provides utilities for Tab navigation, focus management, and keyboard shortcuts.
    /// </summary>
    public class KeyboardNavigationHelper
    {
        /// <summary>
        /// Sets up logical Tab navigation order for a panel by assigning TabIndex values.
        /// </summary>
        public static void SetupTabNavigation(DependencyObject root, int startIndex = 0)
        {
            var focusableElements = new List<DependencyObject>();
            CollectFocusableElements(root, focusableElements);

            // Sort elements by their visual order (top-to-bottom, left-to-right)
            var sortedElements = focusableElements
                .OrderBy(e => GetVisualOrder(e))
                .ToList();

            // Assign TabIndex values
            for (int i = 0; i < sortedElements.Count; i++)
            {
                if (sortedElements[i] is Control control)
                {
                    control.TabIndex = startIndex + i;
                    control.IsTabStop = true;
                }
            }
        }

        /// <summary>
        /// Collects all focusable elements from a dependency object tree.
        /// </summary>
        private static void CollectFocusableElements(DependencyObject parent, List<DependencyObject> elements)
        {
            var childrenCount = VisualTreeHelper.GetChildrenCount(parent);
            for (int i = 0; i < childrenCount; i++)
            {
                var child = VisualTreeHelper.GetChild(parent, i);
                
                // Check if element is focusable
                if (IsFocusableElement(child))
                {
                    elements.Add(child);
                }

                // Recursively collect from children
                CollectFocusableElements(child, elements);
            }
        }

        /// <summary>
        /// Checks if an element is focusable and should be included in Tab navigation.
        /// </summary>
        private static bool IsFocusableElement(DependencyObject element)
        {
            if (element is Control control)
            {
                // Skip elements that are not tab stops
                if (control.IsTabStop == false)
                    return false;

                // Skip disabled elements
                if (control.IsEnabled == false)
                    return false;

                // Include buttons, text boxes, combo boxes, etc.
                return element is Button ||
                       element is TextBox ||
                       element is ComboBox ||
                       element is CheckBox ||
                       element is ToggleSwitch ||
                       element is NumberBox ||
                       element is Slider ||
                       element is ListView ||
                       element is ListBox;
                       // ToggleButton and DataGrid not available in WinUI 3 - removed
            }

            return false;
        }

        /// <summary>
        /// Gets a visual order value for sorting elements (Y position * 10000 + X position).
        /// </summary>
        private static int GetVisualOrder(DependencyObject element)
        {
            if (element is FrameworkElement fe)
            {
                var transform = fe.TransformToVisual(null);
                if (transform != null)
                {
                    var point = transform.TransformPoint(new Windows.Foundation.Point(0, 0));
                    return (int)((point.Y * 10000) + point.X);
                }
            }
            return 0;
        }

        /// <summary>
        /// Sets up Enter key handling for buttons and other controls.
        /// </summary>
        public static void SetupEnterKeyHandling(UIElement element, Action? enterAction)
        {
            if (enterAction == null)
                return;

            element.KeyDown += (sender, e) =>
            {
                if (e.Key == VirtualKey.Enter && !e.KeyStatus.IsMenuKeyDown)
                {
                    enterAction();
                    e.Handled = true;
                }
            };
        }

        /// <summary>
        /// Sets up Escape key handling to close dialogs or overlays.
        /// </summary>
        public static void SetupEscapeKeyHandling(UIElement element, Action? escapeAction)
        {
            if (escapeAction == null)
                return;

            element.KeyDown += (sender, e) =>
            {
                if (e.Key == VirtualKey.Escape)
                {
                    escapeAction();
                    e.Handled = true;
                }
            };
        }

        /// <summary>
        /// Sets up Space key handling for buttons and toggles.
        /// </summary>
        public static void SetupSpaceKeyHandling(UIElement element, Action? spaceAction)
        {
            if (spaceAction == null)
                return;

            element.KeyDown += (sender, e) =>
            {
                if (e.Key == VirtualKey.Space && !e.KeyStatus.IsMenuKeyDown)
                {
                    spaceAction();
                    e.Handled = true;
                }
            };
        }

        /// <summary>
        /// Focuses the first focusable element in a panel.
        /// </summary>
        public static bool FocusFirstElement(DependencyObject root)
        {
            var focusableElements = new List<DependencyObject>();
            CollectFocusableElements(root, focusableElements);

            var sortedElements = focusableElements
                .OrderBy(e => GetVisualOrder(e))
                .ToList();

            if (sortedElements.Count > 0 && sortedElements[0] is Control firstControl)
            {
                return firstControl.Focus(FocusState.Programmatic);
            }

            return false;
        }

        /// <summary>
        /// Focuses the next focusable element after the current one.
        /// </summary>
        public static bool FocusNextElement(DependencyObject root, DependencyObject currentElement)
        {
            var focusableElements = new List<DependencyObject>();
            CollectFocusableElements(root, focusableElements);

            var sortedElements = focusableElements
                .OrderBy(e => GetVisualOrder(e))
                .ToList();

            var currentIndex = sortedElements.IndexOf(currentElement);
            if (currentIndex >= 0 && currentIndex < sortedElements.Count - 1)
            {
                if (sortedElements[currentIndex + 1] is Control nextControl)
                {
                    return nextControl.Focus(FocusState.Programmatic);
                }
            }

            return false;
        }

        /// <summary>
        /// Focuses the previous focusable element before the current one.
        /// </summary>
        public static bool FocusPreviousElement(DependencyObject root, DependencyObject currentElement)
        {
            var focusableElements = new List<DependencyObject>();
            CollectFocusableElements(root, focusableElements);

            var sortedElements = focusableElements
                .OrderBy(e => GetVisualOrder(e))
                .ToList();

            var currentIndex = sortedElements.IndexOf(currentElement);
            if (currentIndex > 0)
            {
                if (sortedElements[currentIndex - 1] is Control previousControl)
                {
                    return previousControl.Focus(FocusState.Programmatic);
                }
            }

            return false;
        }

        /// <summary>
        /// Applies focus visual style to a control using design tokens.
        /// </summary>
        public static void ApplyFocusStyle(Control control)
        {
            // Focus styles are already defined in DesignTokens.xaml
            // This method can be used to ensure focus styles are applied
            if (control is Button button)
            {
                // Button focus style is already in DesignTokens.xaml as VSQ.Button.FocusStyle
                // Just ensure it's applied
                control.Style = Application.Current.Resources["VSQ.Button.FocusStyle"] as Style ?? control.Style;
            }
        }
    }
}

