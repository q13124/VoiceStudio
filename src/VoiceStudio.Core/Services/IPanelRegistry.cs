using System.Collections.Generic;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.Core.Services
{
    public interface IPanelRegistry
    {
        IEnumerable<IPanelView> GetPanelsForRegion(PanelRegion region);
        IPanelView? GetDefaultPanel(PanelRegion region);
        void RegisterPanel(IPanelView panel);
    }
}

