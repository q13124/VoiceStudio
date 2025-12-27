using System.Collections.Generic;

namespace VoiceStudio.Core.Services
{
    public interface ICommandRegistry
    {
        void RegisterCommand(string commandId, string title, string description, string category, System.Action action, string? shortcut = null);
        IEnumerable<CommandItem> GetAllCommands();
        void ExecuteCommand(string commandId);
    }

    public class CommandItem
    {
        public string CommandId { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Category { get; set; } = string.Empty;
        public string Shortcut { get; set; } = string.Empty;
    }
}

