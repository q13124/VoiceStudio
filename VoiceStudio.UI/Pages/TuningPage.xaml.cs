using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.UI.Pages
{
  public sealed partial class TuningPage : Page
  {
    public TuningPage(){ this.InitializeComponent(); Wheel.Changed += (x,y)=> AX.Text=$"X={x:F2}, Y={y:F2}"; }
  }
}
