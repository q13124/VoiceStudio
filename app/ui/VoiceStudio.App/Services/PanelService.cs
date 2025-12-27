using VoiceStudio.App.Models;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Services
{
    public class PanelService
    {
        private readonly IPanelRegistry _registry;

        public PanelService(IPanelRegistry registry)
        {
            _registry = registry;
        }

        public void RegisterDefaultPanels()
        {
            // Register default panels for each region
            _registry.RegisterPanel(new ProfilesPanelViewModel());
            _registry.RegisterPanel(new TimelinePanelViewModel());
            _registry.RegisterPanel(new EffectsMixerPanelViewModel());
            _registry.RegisterPanel(new AnalyzerPanelViewModel());
            _registry.RegisterPanel(new MacroPanelViewModel());
            _registry.RegisterPanel(new DiagnosticsPanelViewModel());
        }
    }
}

