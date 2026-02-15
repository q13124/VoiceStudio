using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Shapes;
using System.Collections.Generic;
using Windows.Foundation;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Node-based macro graph editor: draws nodes and connections.
    /// </summary>
    public sealed partial class MacroNodeEditorControl : UserControl
    {
        public static readonly DependencyProperty MacroProperty =
            DependencyProperty.Register(nameof(Macro), typeof(Macro), typeof(MacroNodeEditorControl),
                new PropertyMetadata(null, OnMacroChanged));

        public Macro? Macro { get => (Macro?)GetValue(MacroProperty); set => SetValue(MacroProperty, value); }
        public bool HasSelectedNode { get => (bool)GetValue(HasSelectedNodeProperty); private set => SetValue(HasSelectedNodeProperty, value); }
        public bool HasUnsavedChanges { get => (bool)GetValue(HasUnsavedChangesProperty); private set => SetValue(HasUnsavedChangesProperty, value); }

        public static readonly DependencyProperty HasSelectedNodeProperty =
            DependencyProperty.Register(nameof(HasSelectedNode), typeof(bool), typeof(MacroNodeEditorControl), new PropertyMetadata(false));
        public static readonly DependencyProperty HasUnsavedChangesProperty =
            DependencyProperty.Register(nameof(HasUnsavedChanges), typeof(bool), typeof(MacroNodeEditorControl), new PropertyMetadata(false));

        private static void OnMacroChanged(DependencyObject d, DependencyPropertyChangedEventArgs e) => ((MacroNodeEditorControl)d).UpdateVisual();

        public MacroNodeEditorControl()
        {
            InitializeComponent();
            Loaded += (_, _) => UpdateVisual();
            SizeChanged += (_, _) => UpdateVisual();
        }

        private void UpdateVisual()
        {
            var macro = Macro;
            ConnectionsLayer.Children.Clear();
            NodesLayer.Children.Clear();
            if (macro?.Nodes == null || macro.Nodes.Count == 0)
            {
                EmptyText.Visibility = Visibility.Visible;
                return;
            }
            EmptyText.Visibility = Visibility.Collapsed;
            double w = Root.ActualWidth;
            double h = Root.ActualHeight;
            if (w <= 0 || h <= 0) return;

            double minX = double.MaxValue, minY = double.MaxValue, maxX = double.MinValue, maxY = double.MinValue;
            foreach (var n in macro.Nodes)
            {
                if (n.X < minX) minX = n.X; if (n.X > maxX) maxX = n.X;
                if (n.Y < minY) minY = n.Y; if (n.Y > maxY) maxY = n.Y;
            }
            if (maxX <= minX) maxX = minX + 100;
            if (maxY <= minY) maxY = minY + 100;
            double pad = 40;
            double scaleX = (w - 2 * pad) / (maxX - minX);
            double scaleY = (h - 2 * pad) / (maxY - minY);
            double scale = System.Math.Min(scaleX, scaleY);
            var pos = new Dictionary<string, Point>();
            foreach (var n in macro.Nodes)
            {
                double x = pad + (n.X - minX) * scale;
                double y = pad + (n.Y - minY) * scale;
                pos[n.Id] = new Point(x, y);
            }

            foreach (var c in macro.Connections ?? new List<MacroConnection>())
            {
                if (!pos.TryGetValue(c.SourceNodeId, out var p1) || !pos.TryGetValue(c.TargetNodeId, out var p2)) continue;
                var line = new Line
                {
                    X1 = p1.X, Y1 = p1.Y, X2 = p2.X, Y2 = p2.Y,
                    Stroke = new SolidColorBrush(Microsoft.UI.Colors.Gray),
                    StrokeThickness = 2
                };
                ConnectionsLayer.Children.Add(line);
            }

            double nodeW = 48, nodeH = 28;
            foreach (var n in macro.Nodes)
            {
                if (!pos.TryGetValue(n.Id, out var pt)) continue;
                var el = new Ellipse
                {
                    Width = nodeW, Height = nodeH,
                    Fill = new SolidColorBrush(Microsoft.UI.Colors.DodgerBlue),
                    Stroke = new SolidColorBrush(Microsoft.UI.Colors.White),
                    StrokeThickness = 1
                };
                Canvas.SetLeft(el, pt.X - nodeW / 2);
                Canvas.SetTop(el, pt.Y - nodeH / 2);
                NodesLayer.Children.Add(el);
                var tb = new TextBlock { Text = string.IsNullOrEmpty(n.Name) ? n.Type : n.Name, FontSize = 10, Foreground = new SolidColorBrush(Microsoft.UI.Colors.White) };
                Canvas.SetLeft(tb, pt.X - nodeW / 2 + 4);
                Canvas.SetTop(tb, pt.Y - nodeH / 2 + 4);
                NodesLayer.Children.Add(tb);
            }
        }
    }
}
