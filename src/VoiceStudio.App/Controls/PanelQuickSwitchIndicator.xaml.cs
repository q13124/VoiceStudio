using Microsoft.UI.Xaml.Controls;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.App.Controls
{
  /// <summary>
  /// Visual indicator for panel quick-switch (IDEA 1).
  /// Shows panel name and region when switching panels with Ctrl+1-9.
  /// </summary>
  public sealed partial class PanelQuickSwitchIndicator : UserControl
  {
    public PanelQuickSwitchIndicator()
    {
      this.InitializeComponent();
    }

    /// <summary>
    /// Sets the panel name and region to display.
    /// </summary>
    public void SetPanelInfo(string panelName, PanelRegion region)
    {
      PanelNameText.Text = panelName;
      PanelRegionText.Text = GetRegionDisplayName(region);
    }

    private string GetRegionDisplayName(PanelRegion region)
    {
      return region switch
      {
        PanelRegion.Left => "Left Panel",
        PanelRegion.Center => "Center Panel",
        PanelRegion.Right => "Right Panel",
        PanelRegion.Bottom => "Bottom Panel",
        _ => "Panel"
      };
    }
  }
}