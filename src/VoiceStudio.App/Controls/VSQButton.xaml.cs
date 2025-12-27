using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Automation;
using System.Windows.Input;

namespace VoiceStudio.App.Controls
{
    public sealed partial class VSQButton : UserControl
    {
        public static new readonly DependencyProperty ContentProperty =
            DependencyProperty.Register(nameof(Content), typeof(object), typeof(VSQButton), new PropertyMetadata(null));

        public static readonly DependencyProperty IsLoadingProperty =
            DependencyProperty.Register(nameof(IsLoading), typeof(bool), typeof(VSQButton), new PropertyMetadata(false, OnIsLoadingChanged));

        public static readonly DependencyProperty CommandProperty =
            DependencyProperty.Register(nameof(Command), typeof(ICommand), typeof(VSQButton), new PropertyMetadata(null));

        public static readonly DependencyProperty CommandParameterProperty =
            DependencyProperty.Register(nameof(CommandParameter), typeof(object), typeof(VSQButton), new PropertyMetadata(null));

        public new object? Content
        {
            get => GetValue(ContentProperty);
            set => SetValue(ContentProperty, value);
        }

        public bool IsLoading
        {
            get => (bool)GetValue(IsLoadingProperty);
            set => SetValue(IsLoadingProperty, value);
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

        public VSQButton()
        {
            InitializeComponent();
            Loaded += VSQButton_Loaded;
        }

        private void VSQButton_Loaded(object sender, RoutedEventArgs e)
        {
            // Set accessibility properties
            AutomationProperties.SetName(ButtonControl, AutomationProperties.GetName(this) ?? "Button");
            AutomationProperties.SetHelpText(ButtonControl, AutomationProperties.GetHelpText(this) ?? string.Empty);
            
            // Ensure minimum hit target size
            if (ButtonControl.ActualWidth < 44)
                ButtonControl.MinWidth = 44;
            if (ButtonControl.ActualHeight < 44)
                ButtonControl.MinHeight = 44;
        }

        private static void OnIsLoadingChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is VSQButton button)
            {
                button.UpdateLoadingState();
            }
        }

        private void UpdateLoadingState()
        {
            if (IsLoading)
            {
                LoadingSpinner.Visibility = Visibility.Visible;
                LoadingSpinner.IsActive = true;
                ButtonControl.IsEnabled = false;
            }
            else
            {
                LoadingSpinner.Visibility = Visibility.Collapsed;
                LoadingSpinner.IsActive = false;
                ButtonControl.IsEnabled = true;
            }
        }

        private void ButtonControl_Click(object sender, RoutedEventArgs e)
        {
            if (Command != null && Command.CanExecute(CommandParameter))
            {
                Command.Execute(CommandParameter);
            }
        }
    }
}
