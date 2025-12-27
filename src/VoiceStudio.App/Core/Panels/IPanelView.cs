namespace VoiceStudio.Core.Panels
{
    public interface IPanelView
    {
        string PanelId { get; }         // e.g. "profiles", "timeline"
        string DisplayName { get; }
        PanelRegion Region { get; }
    }
}
