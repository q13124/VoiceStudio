using System;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Commands
{
    /// <summary>
    /// Describes a command that can be executed via command palette or keyboard shortcut.
    /// Used by UI modules to register commands with the shell.
    /// </summary>
    public class CommandDescriptor
    {
        /// <summary>
        /// Unique command identifier (e.g., "voice.synthesize", "media.timeline").
        /// Uses dot notation: "{module}.{action}".
        /// </summary>
        public string Id { get; init; } = string.Empty;

        /// <summary>
        /// Human-readable title shown in command palette.
        /// </summary>
        public string Title { get; init; } = string.Empty;

        /// <summary>
        /// Additional search keywords for command palette fuzzy matching.
        /// </summary>
        public string[] Keywords { get; init; } = Array.Empty<string>();

        /// <summary>
        /// Default keyboard shortcut (e.g., "Ctrl+Shift+S").
        /// Format: "Modifier+Key" where Modifier is Ctrl, Shift, Alt, or Win.
        /// </summary>
        public string? DefaultHotkey { get; init; }

        /// <summary>
        /// Category for grouping in command palette (e.g., "Voice", "Media", "File").
        /// </summary>
        public string Category { get; init; } = "General";

        /// <summary>
        /// Optional icon (Unicode glyph or Segoe MDL2 Assets code point).
        /// </summary>
        public string? Icon { get; init; }

        /// <summary>
        /// Priority for ordering within category. Lower values appear first.
        /// </summary>
        public int Priority { get; init; } = 100;

        /// <summary>
        /// Async execution delegate. Called when command is invoked.
        /// </summary>
        public Func<Task>? ExecuteAsync { get; init; }

        /// <summary>
        /// Sync execution delegate. Used when ExecuteAsync is not set.
        /// </summary>
        public Action? Execute { get; init; }

        /// <summary>
        /// Predicate to determine if command can execute.
        /// Returns true if command is available, false to disable.
        /// </summary>
        public Func<bool>? CanExecute { get; init; }

        /// <summary>
        /// Whether this command should be visible in the command palette.
        /// Set to false for keyboard-shortcut-only commands.
        /// </summary>
        public bool ShowInPalette { get; init; } = true;

        /// <summary>
        /// Executes the command asynchronously.
        /// </summary>
        public async Task InvokeAsync()
        {
            if (CanExecute != null && !CanExecute())
            {
                return;
            }

            if (ExecuteAsync != null)
            {
                await ExecuteAsync();
            }
            else if (Execute != null)
            {
                Execute();
            }
        }

        /// <summary>
        /// Checks if the command can currently execute.
        /// </summary>
        public bool CheckCanExecute()
        {
            return CanExecute?.Invoke() ?? true;
        }
    }
}
