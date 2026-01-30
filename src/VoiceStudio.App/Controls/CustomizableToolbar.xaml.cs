using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Controls.Primitives;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Controls
{
    public sealed partial class CustomizableToolbar : UserControl
    {
        private ToolbarConfigurationService? _toolbarService;
        private readonly Dictionary<string, UIElement> _toolbarButtons = new Dictionary<string, UIElement>();

        private static Style? TryGetFocusStyle()
        {
            try
            {
                return Application.Current?.Resources?["VSQ.Button.FocusStyle"] as Style;
            }
            catch
            {
                return null;
            }
        }

        public CustomizableToolbar()
        {
            this.InitializeComponent();
            _toolbarService = ServiceProvider.TryGetToolbarConfigurationService();
            
            if (_toolbarService != null)
            {
                _toolbarService.ConfigurationChanged += ToolbarService_ConfigurationChanged;
                LoadToolbar();
            }
        }

        private void ToolbarService_ConfigurationChanged(object? sender, ToolbarConfigurationChangedEventArgs e)
        {
            LoadToolbar();
        }

        private void LoadToolbar()
        {
            if (_toolbarService == null)
                return;

            var config = _toolbarService.GetConfiguration();
            
            // Clear existing buttons
            TransportSection.Children.Clear();
            ProjectSection.Children.Clear();
            HistorySection.Children.Clear();
            PerformanceSection.Children.Clear();

            // Group items by section and order
            var visibleItems = config.Items
                .Where(i => i.IsVisible)
                .OrderBy(i => i.Order)
                .ToList();

            foreach (var item in visibleItems)
            {
                var button = CreateToolbarButton(item);
                if (button != null)
                {
                    AddButtonToSection(item.Section, button);
                }
            }
        }

        private UIElement? CreateToolbarButton(ToolbarItem item)
        {
            // Create appropriate control based on item ID
            return item.Id switch
            {
                "play" => CreateButton("▶", "Play (Space)", item),
                "pause" => CreateButton("⏸", "Pause (Space)", item),
                "stop" => CreateButton("⏹", "Stop", item),
                "record" => CreateButton("⏺", "Record (Ctrl+R)", item),
                "loop" => CreateToggleButton("Loop", "Toggle loop playback", item),
                "project" => CreateProjectControl(item),
                "engine" => CreateEngineControl(item),
                "undo" => CreateButton("Undo", "Undo last action (Ctrl+Z)", item),
                "redo" => CreateButton("Redo", "Redo last action (Ctrl+Y)", item),
                "workspace" => CreateWorkspaceControl(item),
                "cpu" => CreatePerformanceControl("CPU", item),
                "gpu" => CreatePerformanceControl("GPU", item),
                "latency" => CreatePerformanceControl("Latency", item),
                _ => null
            };
        }

        private Button CreateButton(string content, string tooltip, ToolbarItem item)
        {
            var button = new Button
            {
                Content = content,
                Margin = new Thickness(0, 0, 4, 0),
                Style = TryGetFocusStyle()
            };
            if (!string.IsNullOrEmpty(tooltip))
            {
                ToolTipService.SetToolTip(button, tooltip);
            }
            
            // Wire up click handler based on item ID
            button.Click += (s, e) => HandleToolbarButtonClick(item.Id);
            
            return button;
        }

        private ToggleButton CreateToggleButton(string content, string tooltip, ToolbarItem item)
        {
            var button = new ToggleButton
            {
                Content = content,
                Margin = new Thickness(8, 0, 0, 0),
                Style = TryGetFocusStyle()
            };
            if (!string.IsNullOrEmpty(tooltip))
            {
                ToolTipService.SetToolTip(button, tooltip);
            }
            
            // Wire up click handler based on item ID
            button.Click += (s, e) => HandleToolbarButtonClick(item.Id);
            
            return button;
        }

        private StackPanel CreateProjectControl(ToolbarItem item)
        {
            var panel = new StackPanel { Orientation = Orientation.Horizontal };
            panel.Children.Add(new TextBlock { Text = "Project:", Margin = new Thickness(0, 0, 4, 0) });
            panel.Children.Add(new TextBox { Width = 200, Text = "Untitled Project" });
            return panel;
        }

        private StackPanel CreateEngineControl(ToolbarItem item)
        {
            var panel = new StackPanel { Orientation = Orientation.Horizontal, Margin = new Thickness(16, 0, 0, 0) };
            panel.Children.Add(new TextBlock { Text = "Engine:", Margin = new Thickness(0, 0, 4, 0) });
            var comboBox = new ComboBox { Width = 140 };
            comboBox.Items.Add("XTTS v2");
            comboBox.Items.Add("OpenVoice");
            comboBox.Items.Add("RVC");
            panel.Children.Add(comboBox);
            return panel;
        }

        private StackPanel CreateWorkspaceControl(ToolbarItem item)
        {
            var panel = new StackPanel { Orientation = Orientation.Horizontal, Margin = new Thickness(0, 0, 12, 0) };
            panel.Children.Add(new TextBlock { Text = "Workspace:", Margin = new Thickness(0, 0, 4, 0) });
            var comboBox = new ComboBox { Width = 150 };
            comboBox.Items.Add("Studio");
            comboBox.Items.Add("Batch Lab");
            comboBox.Items.Add("Training");
            comboBox.Items.Add("Pro Mix");
            panel.Children.Add(comboBox);
            return panel;
        }

        private StackPanel CreatePerformanceControl(string label, ToolbarItem item)
        {
            var panel = new StackPanel { Margin = new Thickness(0, 0, 12, 0) };
            panel.Children.Add(new TextBlock 
            { 
                Text = label, 
                FontSize = 10, 
                HorizontalAlignment = HorizontalAlignment.Right 
            });
            panel.Children.Add(new ProgressBar 
            { 
                Width = 80, 
                Height = 6, 
                Value = label == "CPU" ? 20 : label == "GPU" ? 10 : 5 
            });
            return panel;
        }

        private void AddButtonToSection(ToolbarSection section, UIElement button)
        {
            switch (section)
            {
                case ToolbarSection.Transport:
                    TransportSection.Children.Add(button);
                    break;
                case ToolbarSection.Project:
                    ProjectSection.Children.Add(button);
                    break;
                case ToolbarSection.History:
                case ToolbarSection.Workspace:
                    HistorySection.Children.Add(button);
                    break;
                case ToolbarSection.Performance:
                    PerformanceSection.Children.Add(button);
                    break;
            }
        }

        /// <summary>
        /// Handles toolbar button clicks by executing the appropriate command.
        /// </summary>
        private void HandleToolbarButtonClick(string itemId)
        {
            // Map toolbar item IDs to command IDs and execute via KeyboardShortcutService
            var keyboardService = ServiceProvider.TryGetKeyboardShortcutService();
            if (keyboardService == null)
                return;

            // Map toolbar item IDs to command IDs
            var commandId = itemId switch
            {
                "play" => "playback.play",
                "pause" => "playback.play", // Toggle play/pause (same as play)
                "stop" => "playback.stop",
                "record" => "playback.record",
                "undo" => "edit.undo",
                "redo" => "edit.redo",
                _ => null
            };

            if (commandId != null)
            {
                // Execute the command by finding the shortcut and invoking its action
                var shortcuts = keyboardService.GetAllShortcuts();
                var shortcut = shortcuts.FirstOrDefault(s => s.Id == commandId);
                shortcut?.Action?.Invoke();
            }
            // Note: "loop" toggle button is handled by its own click event
        }
    }
}

