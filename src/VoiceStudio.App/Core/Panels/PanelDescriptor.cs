using System;

namespace VoiceStudio.Core.Panels
{
    public sealed class PanelDescriptor
    {
        public string PanelId { get; init; } = string.Empty;
        public string DisplayName { get; init; } = string.Empty;
        public PanelRegion Region { get; init; }
        public Type ViewType { get; init; } = typeof(object);
        public Type ViewModelType { get; init; } = typeof(object);
    }
}
