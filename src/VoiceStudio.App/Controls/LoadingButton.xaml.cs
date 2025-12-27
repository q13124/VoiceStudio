using System.Windows.Input;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.App.Controls
{
    public sealed partial class LoadingButton : UserControl
    {
        public static readonly DependencyProperty ButtonContentProperty =
            DependencyProperty.Register(nameof(ButtonContent), typeof(object), typeof(LoadingButton), new PropertyMetadata(null));

        public static readonly DependencyProperty CommandProperty =
            DependencyProperty.Register(nameof(Command), typeof(ICommand), typeof(LoadingButton), new PropertyMetadata(null));

        public static readonly DependencyProperty CommandParameterProperty =
            DependencyProperty.Register(nameof(CommandParameter), typeof(object), typeof(LoadingButton), new PropertyMetadata(null));

        public static readonly DependencyProperty IsLoadingProperty =
            DependencyProperty.Register(nameof(IsLoading), typeof(bool), typeof(LoadingButton), new PropertyMetadata(false));

        // IsEnabled is inherited from Control, no need to redefine

        public static readonly DependencyProperty ButtonStyleProperty =
            DependencyProperty.Register(nameof(ButtonStyle), typeof(Style), typeof(LoadingButton), new PropertyMetadata(null));

        public static readonly DependencyProperty AutomationNameProperty =
            DependencyProperty.Register(nameof(AutomationName), typeof(string), typeof(LoadingButton), new PropertyMetadata(null));

        public static readonly DependencyProperty AutomationHelpTextProperty =
            DependencyProperty.Register(nameof(AutomationHelpText), typeof(string), typeof(LoadingButton), new PropertyMetadata(null));

        public object ButtonContent
        {
            get => GetValue(ButtonContentProperty);
            set => SetValue(ButtonContentProperty, value);
        }

        public ICommand? Command
        {
            get => (ICommand?)GetValue(CommandProperty);
            set => SetValue(CommandProperty, value);
        }

        public object? CommandParameter
        {
            get => GetValue(CommandParameterProperty);
            set => SetValue(CommandParameterProperty, value);
        }

        public bool IsLoading
        {
            get => (bool)GetValue(IsLoadingProperty);
            set => SetValue(IsLoadingProperty, value);
        }

        // IsEnabled is inherited from Control, no need to redefine

        public Style? ButtonStyle
        {
            get => (Style?)GetValue(ButtonStyleProperty);
            set => SetValue(ButtonStyleProperty, value);
        }

        public string? AutomationName
        {
            get => (string?)GetValue(AutomationNameProperty);
            set => SetValue(AutomationNameProperty, value);
        }

        public string? AutomationHelpText
        {
            get => (string?)GetValue(AutomationHelpTextProperty);
            set => SetValue(AutomationHelpTextProperty, value);
        }

        // HorizontalAlignment, VerticalAlignment, Padding, Margin, HorizontalContentAlignment, 
        // and VerticalContentAlignment are all inherited from FrameworkElement/Control,
        // no need to redefine them

        public LoadingButton()
        {
            InitializeComponent();
        }
    }
}

