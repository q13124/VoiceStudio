using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls.Primitives;

namespace VoiceStudio.App.Controls
{
    public sealed partial class NavIconButton : ToggleButton
    {
        public static readonly DependencyProperty IconGlyphProperty =
            DependencyProperty.Register(
                nameof(IconGlyph),
                typeof(string),
                typeof(NavIconButton),
                new PropertyMetadata("\uE700", OnIconGlyphChanged));

        public string IconGlyph
        {
            get => (string)GetValue(IconGlyphProperty);
            set => SetValue(IconGlyphProperty, value);
        }

        public NavIconButton()
        {
            this.InitializeComponent();
        }

        private static void OnIconGlyphChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is NavIconButton button && e.NewValue is string glyph)
            {
                var fontIcon = button.FindName("Icon") as Microsoft.UI.Xaml.Controls.FontIcon;
                if (fontIcon != null)
                {
                    fontIcon.Glyph = glyph;
                }
            }
        }
    }
}

