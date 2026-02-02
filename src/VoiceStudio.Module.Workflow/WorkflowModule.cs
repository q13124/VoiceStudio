using System.Collections.Generic;
using Microsoft.Extensions.DependencyInjection;
using VoiceStudio.Core.Commands;
using VoiceStudio.Core.Modules;

namespace VoiceStudio.Module.Workflow
{
    /// <summary>
    /// Workflow module containing automation, batch processing, macros, and engine management panels.
    /// This module encapsulates all workflow and automation UI components.
    /// </summary>
    public class WorkflowModule : IUIModule
    {
        public string ModuleId => "Workflow";
        public string DisplayName => "Workflow & Automation";
        public string Version => "1.0.0";
        public int Priority => 40; // Load after analysis module

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
                Id = "workflow.batch",
                Title = "Open Batch Processing",
                Keywords = new[] { "batch", "bulk", "process" },
                DefaultHotkey = "Ctrl+B",
                Category = "Workflow",
                Icon = "\uE8F1"
            };
            
            yield return new CommandDescriptor
            {
                Id = "workflow.automation",
                Title = "Open Workflow Automation",
                Keywords = new[] { "automation", "workflow", "pipeline" },
                Category = "Workflow",
                Icon = "\uE912"
            };
            
            yield return new CommandDescriptor
            {
                Id = "workflow.macros",
                Title = "Open Macros",
                Keywords = new[] { "macro", "script", "automate" },
                Category = "Workflow",
                Icon = "\uE943"
            };
        }
    }
}
