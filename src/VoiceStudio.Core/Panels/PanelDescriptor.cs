using System;

namespace VoiceStudio.Core.Panels
{
    /// <summary>
    /// Describes a panel that can be registered and displayed in the UI.
    /// </summary>
    public sealed class PanelDescriptor
    {
        public string PanelId { get; init; } = string.Empty;
        public string DisplayName { get; init; } = string.Empty;
        public PanelRegion DefaultRegion { get; init; }
        public Type ViewType { get; init; } = typeof(object);
        public Type? ViewModelType { get; init; }
        public string? Icon { get; init; }
        public string? Description { get; init; }
        
        /// <summary>
        /// Backward compatibility alias for DefaultRegion.
        /// </summary>
        public PanelRegion Region
        {
            get => DefaultRegion;
            init => DefaultRegion = value;
        }
    }
}
