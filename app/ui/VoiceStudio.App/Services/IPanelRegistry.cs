using System.Collections.Generic;
using VoiceStudio.App.Models;

namespace VoiceStudio.App.Services
{
    public interface IPanelRegistry
    {
        IEnumerable<IPanelView> GetPanelsForRegion(PanelRegion region);
        IPanelView? GetDefaultPanel(PanelRegion region);
        void RegisterPanel(IPanelView panel);
    }
}

