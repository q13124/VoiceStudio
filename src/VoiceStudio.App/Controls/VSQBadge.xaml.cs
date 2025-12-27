using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Automation;

namespace VoiceStudio.App.Controls
{
    public sealed partial class VSQBadge : UserControl
    {
        public static readonly DependencyProperty TextProperty =
            DependencyProperty.Register(nameof(Text), typeof(string), typeof(VSQBadge), new PropertyMetadata(string.Empty));

        public static readonly DependencyProperty BadgeTypeProperty =
            DependencyProperty.Register(nameof(BadgeType), typeof(BadgeType), typeof(VSQBadge), new PropertyMetadata(BadgeType.Info, OnBadgeTypeChanged));

        public static readonly DependencyProperty BadgeBackgroundProperty =
            DependencyProperty.Register(nameof(BadgeBackground), typeof(Brush), typeof(VSQBadge), new PropertyMetadata(null));

        public static readonly DependencyProperty BadgeForegroundProperty =
            DependencyProperty.Register(nameof(BadgeForeground), typeof(Brush), typeof(VSQBadge), new PropertyMetadata(null));

        public string Text
        {
            get => (string)GetValue(TextProperty);
            set => SetValue(TextProperty, value);
        }

        public BadgeType BadgeType
        {
            get => (BadgeType)GetValue(BadgeTypeProperty);
            set => SetValue(BadgeTypeProperty, value);
        }

        public Brush? BadgeBackground
        {
            get => (Brush?)GetValue(BadgeBackgroundProperty);
            set => SetValue(BadgeBackgroundProperty, value);
        }

        public Brush? BadgeForeground
        {
            get => (Brush?)GetValue(BadgeForegroundProperty);
            set => SetValue(BadgeForegroundProperty, value);
        }

        public VSQBadge()
        {
            InitializeComponent();
            Loaded += VSQBadge_Loaded;
        }

        private void VSQBadge_Loaded(object sender, RoutedEventArgs e)
        {
            UpdateBadgeStyle();
            
            // Set accessibility properties
            AutomationProperties.SetName(BadgeBorder, $"{BadgeType} badge: {Text}");
            AutomationProperties.SetHelpText(BadgeBorder, $"Status badge indicating {BadgeType.ToString().ToLowerInvariant()} state");
        }

        private static void OnBadgeTypeChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is VSQBadge badge)
            {
                badge.UpdateBadgeStyle();
            }
        }

        private void UpdateBadgeStyle()
        {
            var resources = Application.Current.Resources;
            
            switch (BadgeType)
            {
                case BadgeType.Info:
                    BadgeBackground = resources["VSQ.Accent.CyanBrush"] as Brush;
                    BadgeForeground = resources["VSQ.Text.PrimaryBrush"] as Brush;
                    break;
                case BadgeType.Success:
                    BadgeBackground = resources["VSQ.Success.Brush"] as Brush;
                    BadgeForeground = resources["VSQ.Text.PrimaryBrush"] as Brush;
                    break;
                case BadgeType.Warning:
                    BadgeBackground = resources["VSQ.Warn.Brush"] as Brush;
                    BadgeForeground = resources["VSQ.Text.PrimaryBrush"] as Brush;
                    break;
                case BadgeType.Error:
                    BadgeBackground = resources["VSQ.Error.Brush"] as Brush;
                    BadgeForeground = resources["VSQ.Text.PrimaryBrush"] as Brush;
                    break;
            }
        }
    }

    public enum BadgeType
    {
        Info,
        Success,
        Warning,
        Error
    }
}
