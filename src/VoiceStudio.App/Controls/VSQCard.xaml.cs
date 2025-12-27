using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Automation;

namespace VoiceStudio.App.Controls
{
    public sealed partial class VSQCard : UserControl
    {
        public static new readonly DependencyProperty ContentProperty =
            DependencyProperty.Register(nameof(Content), typeof(object), typeof(VSQCard), new PropertyMetadata(null));

        public new object? Content
        {
            get => GetValue(ContentProperty);
            set => SetValue(ContentProperty, value);
        }

        public VSQCard()
        {
            InitializeComponent();
            Loaded += VSQCard_Loaded;
        }

        private void VSQCard_Loaded(object sender, RoutedEventArgs e)
        {
            // Set accessibility properties
            AutomationProperties.SetName(CardBorder, AutomationProperties.GetName(this) ?? "Card");
            AutomationProperties.SetHelpText(CardBorder, AutomationProperties.GetHelpText(this) ?? string.Empty);
        }
    }
}
