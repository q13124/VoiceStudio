using System.Windows.Input;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.App.Controls
{
    public sealed partial class OnboardingHints : UserControl
    {
        public static readonly DependencyProperty IsVisibleProperty =
            DependencyProperty.Register(nameof(IsVisible), typeof(bool), typeof(OnboardingHints), new PropertyMetadata(false));

        public static readonly DependencyProperty TitleProperty =
            DependencyProperty.Register(nameof(Title), typeof(string), typeof(OnboardingHints), new PropertyMetadata("Hint"));

        public static readonly DependencyProperty MessageProperty =
            DependencyProperty.Register(nameof(Message), typeof(string), typeof(OnboardingHints), new PropertyMetadata(string.Empty));

        public static readonly DependencyProperty ActionTextProperty =
            DependencyProperty.Register(nameof(ActionText), typeof(string), typeof(OnboardingHints), new PropertyMetadata(null));

        public static readonly DependencyProperty ActionCommandProperty =
            DependencyProperty.Register(nameof(ActionCommand), typeof(ICommand), typeof(OnboardingHints), new PropertyMetadata(null));

        public static readonly DependencyProperty ActionParameterProperty =
            DependencyProperty.Register(nameof(ActionParameter), typeof(object), typeof(OnboardingHints), new PropertyMetadata(null));

        public static readonly DependencyProperty DontShowAgainProperty =
            DependencyProperty.Register(nameof(DontShowAgain), typeof(bool), typeof(OnboardingHints), new PropertyMetadata(false));

        public bool IsVisible
        {
            get => (bool)GetValue(IsVisibleProperty);
            set => SetValue(IsVisibleProperty, value);
        }

        public string Title
        {
            get => (string)GetValue(TitleProperty);
            set => SetValue(TitleProperty, value);
        }

        public string Message
        {
            get => (string)GetValue(MessageProperty);
            set => SetValue(MessageProperty, value);
        }

        public string? ActionText
        {
            get => (string?)GetValue(ActionTextProperty);
            set => SetValue(ActionTextProperty, value);
        }

        public ICommand? ActionCommand
        {
            get => (ICommand?)GetValue(ActionCommandProperty);
            set => SetValue(ActionCommandProperty, value);
        }

        public object? ActionParameter
        {
            get => GetValue(ActionParameterProperty);
            set => SetValue(ActionParameterProperty, value);
        }

        public bool DontShowAgain
        {
            get => (bool)GetValue(DontShowAgainProperty);
            set => SetValue(DontShowAgainProperty, value);
        }

        public event RoutedEventHandler? HintDismissed;

        public OnboardingHints()
        {
            InitializeComponent();
        }

        private void CloseButton_Click(object sender, RoutedEventArgs e)
        {
            IsVisible = false;
            HintDismissed?.Invoke(this, e);
        }
    }
}

