using System.Collections.Generic;
using Microsoft.Extensions.DependencyInjection;
using VoiceStudio.Core.Commands;
using VoiceStudio.Core.Modules;

namespace VoiceStudio.Module.Media
{
    /// <summary>
    /// Media module containing video generation, image generation, timeline, and effects panels.
    /// This module encapsulates all media-related UI components.
    /// </summary>
    public class MediaModule : IUIModule
    {
        public string ModuleId => "Media";
        public string DisplayName => "Media Generation";
        public string Version => "1.0.0";
        public int Priority => 20; // Load after Voice module

        public void RegisterServices(IServiceCollection services)
        {
            // ViewModels will be registered when views are migrated
        }

        public void OnInitialized(IServiceProvider provider)
        {
            // Panel registration will happen when views are migrated
        }

        public void OnShutdown()
        {
            // Cleanup resources if needed
        }

        public IEnumerable<CommandDescriptor> GetCommands()
        {
            yield return new CommandDescriptor
            {
                Id = "media.timeline",
                Title = "Open Timeline",
                Keywords = new[] { "timeline", "edit", "arrange" },
                DefaultHotkey = "Ctrl+T",
                Category = "Media",
                Icon = "\uE916"
            };
            
            yield return new CommandDescriptor
            {
                Id = "media.recording",
                Title = "Open Recording",
                Keywords = new[] { "record", "microphone", "capture" },
                DefaultHotkey = "Ctrl+R",
                Category = "Media",
                Icon = "\uE720"
            };
            
            yield return new CommandDescriptor
            {
                Id = "media.effects",
                Title = "Open Effects Mixer",
                Keywords = new[] { "effects", "mixer", "audio", "fx" },
                Category = "Media",
                Icon = "\uE9E9"
            };
        }
    }
}
