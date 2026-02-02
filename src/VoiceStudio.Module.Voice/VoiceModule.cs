using System.Collections.Generic;
using Microsoft.Extensions.DependencyInjection;
using VoiceStudio.Core.Commands;
using VoiceStudio.Core.Modules;

namespace VoiceStudio.Module.Voice
{
    /// <summary>
    /// Voice module containing voice synthesis, cloning, morphing, and text-to-speech panels.
    /// This module encapsulates all voice-related UI components.
    /// Views will be migrated from VoiceStudio.App in a future phase.
    /// </summary>
    public class VoiceModule : IUIModule
    {
        public string ModuleId => "Voice";
        public string DisplayName => "Voice Synthesis";
        public string Version => "1.0.0";
        public int Priority => 10; // Load early as it's a primary feature

        public void RegisterServices(IServiceCollection services)
        {
            // ViewModels will be registered when views are migrated
        }

        public void OnInitialized(IServiceProvider provider)
        {
            // Panel registration will happen when views are migrated
            // For now, panels are registered in VoiceStudio.App
        }

        public void OnShutdown()
        {
            // Cleanup resources if needed
        }

        public IEnumerable<CommandDescriptor> GetCommands()
        {
            yield return new CommandDescriptor
            {
                Id = "voice.synthesize",
                Title = "Open Voice Synthesis",
                Keywords = new[] { "tts", "speak", "generate", "speech" },
                DefaultHotkey = "Ctrl+Shift+V",
                Category = "Voice",
                Icon = "\uE8D6"
            };
            
            yield return new CommandDescriptor
            {
                Id = "voice.clone",
                Title = "Open Voice Cloning Wizard",
                Keywords = new[] { "clone", "copy", "replicate" },
                Category = "Voice",
                Icon = "\uE77B"
            };
            
            yield return new CommandDescriptor
            {
                Id = "voice.morph",
                Title = "Open Voice Morph",
                Keywords = new[] { "morph", "transform", "blend" },
                Category = "Voice",
                Icon = "\uE8B1"
            };
        }
    }
}
