using System.Collections.Generic;
using System.Linq;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services
{
    public class PanelRegistry : IPanelRegistry
    {
        private readonly List<IPanelView> _panels = new List<IPanelView>();

        public IEnumerable<IPanelView> GetPanelsForRegion(PanelRegion region)
        {
            return _panels.Where(p => p.Region == region);
        }

        public IPanelView? GetDefaultPanel(PanelRegion region)
        {
            return _panels.FirstOrDefault(p => p.Region == region);
        }

        public void RegisterPanel(IPanelView panel)
        {
            if (!_panels.Contains(panel))
            {
                _panels.Add(panel);
            }
        }
    }
}

