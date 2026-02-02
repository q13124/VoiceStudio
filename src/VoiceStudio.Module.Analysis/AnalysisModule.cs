using System.Collections.Generic;
using Microsoft.Extensions.DependencyInjection;
using VoiceStudio.Core.Commands;
using VoiceStudio.Core.Modules;

namespace VoiceStudio.Module.Analysis
{
    /// <summary>
    /// Analysis module containing quality metrics, diagnostics, training, and visualization panels.
    /// This module encapsulates all analysis and quality-related UI components.
    /// </summary>
    public class AnalysisModule : IUIModule
    {
        public string ModuleId => "Analysis";
        public string DisplayName => "Quality & Analysis";
        public string Version => "1.0.0";
        public int Priority => 30; // Load after primary feature modules

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
                Id = "analysis.quality",
                Title = "Open Quality Dashboard",
                Keywords = new[] { "quality", "metrics", "dashboard" },
                DefaultHotkey = "Ctrl+Q",
                Category = "Analysis",
                Icon = "\uE9D9"
            };
            
            yield return new CommandDescriptor
            {
                Id = "analysis.diagnostics",
                Title = "Open Diagnostics",
                Keywords = new[] { "diagnostics", "debug", "system" },
                Category = "Analysis",
                Icon = "\uE9D5"
            };
            
            yield return new CommandDescriptor
            {
                Id = "analysis.training",
                Title = "Open Training",
                Keywords = new[] { "train", "model", "finetune" },
                Category = "Analysis",
                Icon = "\uE90F"
            };
        }
    }
}
