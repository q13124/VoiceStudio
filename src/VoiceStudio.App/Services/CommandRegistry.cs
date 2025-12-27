using System;
using System.Collections.Generic;
using System.Linq;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services
{
    public class CommandRegistry : ICommandRegistry
    {
        private readonly Dictionary<string, CommandDefinition> _commands = new();

        public void RegisterCommand(string commandId, string title, string description, string category, Action action, string? shortcut = null)
        {
            _commands[commandId] = new CommandDefinition
            {
                CommandId = commandId,
                Title = title,
                Description = description,
                Category = category,
                Action = action,
                Shortcut = shortcut ?? string.Empty
            };
        }

        public IEnumerable<CommandItem> GetAllCommands()
        {
            return _commands.Values.Select(cmd => new CommandItem
            {
                CommandId = cmd.CommandId,
                Title = cmd.Title,
                Description = cmd.Description,
                Category = cmd.Category,
                Shortcut = cmd.Shortcut
            });
        }

        public void ExecuteCommand(string commandId)
        {
            if (_commands.TryGetValue(commandId, out var command))
            {
                command.Action?.Invoke();
            }
        }

        private class CommandDefinition
        {
            public string CommandId { get; set; } = string.Empty;
            public string Title { get; set; } = string.Empty;
            public string Description { get; set; } = string.Empty;
            public string Category { get; set; } = string.Empty;
            public Action? Action { get; set; }
            public string Shortcut { get; set; } = string.Empty;
        }
    }
}

