using System;
using System.Collections.Generic;
using System.Linq;

namespace VoiceStudio.Core.Panels
{
    public sealed class PanelRegistry : IPanelRegistry
    {
        private readonly List<PanelDescriptor> _panels = new();

        public PanelRegistry()
        {
            // Core panels are registered via Register() method
            // Panels can be registered dynamically by plugins or at application startup
            // See PanelRegistry.Auto.cs for auto-discovered panel paths
        }

        /// <summary>
        /// Registers a panel descriptor.
        /// </summary>
        public void Register(PanelDescriptor descriptor)
        {
            if (descriptor == null)
                throw new ArgumentNullException(nameof(descriptor));

            // Check if panel with same ID already exists
            var existing = _panels.FirstOrDefault(p => p.PanelId == descriptor.PanelId);
            if (existing != null)
            {
                // Update existing panel
                _panels.Remove(existing);
            }

            _panels.Add(descriptor);
        }

        public IEnumerable<PanelDescriptor> GetPanelsForRegion(PanelRegion region) =>
            _panels.Where(p => p.Region == region);

        public PanelDescriptor? GetDefaultPanel(PanelRegion region) =>
            _panels.FirstOrDefault(p => p.Region == region);
    }
}
