namespace VoiceStudio.Core.Panels
{
  public interface IPanelView
  {
    string PanelId { get; }      // e.g. "Profiles", "Timeline", "Mixer"
    string DisplayName { get; }
    PanelRegion Region { get; }   // Left, Center, Right, Bottom, Floating
  }
}