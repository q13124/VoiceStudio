using VoiceStudio.App.Models;
using VoiceStudio.App.Views.Panels;

namespace VoiceStudio.App.ViewModels
{
    public class ProfilesPanelViewModel : IPanelView
    {
        public string PanelId => "Profiles";
        public string DisplayName => "Profiles";
        public PanelRegion Region => PanelRegion.Left;
    }

    public class TimelinePanelViewModel : IPanelView
    {
        public string PanelId => "Timeline";
        public string DisplayName => "Timeline";
        public PanelRegion Region => PanelRegion.Center;
    }

    public class EffectsMixerPanelViewModel : IPanelView
    {
        public string PanelId => "EffectsMixer";
        public string DisplayName => "Effects & Mixer";
        public PanelRegion Region => PanelRegion.Right;
    }

    public class AnalyzerPanelViewModel : IPanelView
    {
        public string PanelId => "Analyzer";
        public string DisplayName => "Analyzer";
        public PanelRegion Region => PanelRegion.Right;
    }

    public class MacroPanelViewModel : IPanelView
    {
        public string PanelId => "Macro";
        public string DisplayName => "Macros";
        public PanelRegion Region => PanelRegion.Bottom;
    }

    public class DiagnosticsPanelViewModel : IPanelView
    {
        public string PanelId => "Diagnostics";
        public string DisplayName => "Diagnostics";
        public PanelRegion Region => PanelRegion.Bottom;
    }
}

