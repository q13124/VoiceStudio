using System.Collections.Generic;

namespace VoiceStudio.Core.Panels
{
    public interface IPanelRegistry
    {
        IEnumerable<PanelDescriptor> GetPanelsForRegion(PanelRegion region);
        PanelDescriptor? GetDefaultPanel(PanelRegion region);
    }
}

