using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Shapes;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI;
using System;

namespace VoiceStudio.UI.Controls
{
  public sealed partial class AccentWheelControl : UserControl
  {
    public double AccentX { get => (double)GetValue(AccentXProperty); set => SetValue(AccentXProperty, value); }
    public static readonly DependencyProperty AccentXProperty =
        DependencyProperty.Register(nameof(AccentX), typeof(double), typeof(AccentWheelControl), new PropertyMetadata(0.5, OnPosChanged));

    public double AccentY { get => (double)GetValue(AccentYProperty); set => SetValue(AccentYProperty, value); }
    public static readonly DependencyProperty AccentYProperty =
        DependencyProperty.Register(nameof(AccentY), typeof(double), typeof(AccentWheelControl), new PropertyMetadata(0.5, OnPosChanged));

    public event Action<double,double>? Changed;

    public AccentWheelControl(){ this.InitializeComponent(); LayoutUpdated += (_,__) => Redraw(); }

    static void OnPosChanged(DependencyObject d, DependencyPropertyChangedEventArgs e) => ((AccentWheelControl)d).Redraw();

    void Redraw(){
      double w = Wheel.Width, h = Wheel.Height;
      Canvas.SetLeft(Dot, AccentX*(w-6)); Canvas.SetTop(Dot, AccentY*(h-6));
    }

    void SetFromPoint(double x,double y){
      double w = Wheel.Width, h = Wheel.Height;
      AccentX = Math.Clamp(x/(w-6),0,1); AccentY = Math.Clamp(y/(h-6),0,1);
      Changed?.Invoke(AccentX,AccentY);
    }

    private void OnPress(object s, PointerRoutedEventArgs e){ var p=e.GetCurrentPoint(Wheel); SetFromPoint(p.Position.X, p.Position.Y); }
    private void OnMove(object s, PointerRoutedEventArgs e){ if(e.GetCurrentPoint(Wheel).IsInContact){ var p=e.GetCurrentPoint(Wheel); SetFromPoint(p.Position.X, p.Position.Y); } }
  }
}
