using System.Windows.Input;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Automation;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Reusable toast notification control with standardized styling.
    /// </summary>
    public sealed partial class VSQToastNotification : UserControl
    {
        public static readonly DependencyProperty ToastTypeProperty =
            DependencyProperty.Register(nameof(ToastType), typeof(Services.ToastType), typeof(VSQToastNotification),
                new PropertyMetadata(Services.ToastType.Info, OnToastTypeChanged));

        public static readonly DependencyProperty MessageProperty =
            DependencyProperty.Register(nameof(Message), typeof(string), typeof(VSQToastNotification),
                new PropertyMetadata(string.Empty));

        public static readonly DependencyProperty TitleProperty =
            DependencyProperty.Register(nameof(Title), typeof(string), typeof(VSQToastNotification),
                new PropertyMetadata(null));

        public static readonly DependencyProperty IsProgressProperty =
            DependencyProperty.Register(nameof(IsProgress), typeof(bool), typeof(VSQToastNotification),
                new PropertyMetadata(false));

        public static readonly DependencyProperty ActionButtonTextProperty =
            DependencyProperty.Register(nameof(ActionButtonText), typeof(string), typeof(VSQToastNotification),
                new PropertyMetadata(null));

        public static readonly DependencyProperty ActionButtonCommandProperty =
            DependencyProperty.Register(nameof(ActionButtonCommand), typeof(ICommand), typeof(VSQToastNotification),
                new PropertyMetadata(null));

        public Services.ToastType ToastType
        {
            get => (Services.ToastType)GetValue(ToastTypeProperty);
            set => SetValue(ToastTypeProperty, value);
        }

        public string Message
        {
            get => (string)GetValue(MessageProperty);
            set => SetValue(MessageProperty, value);
        }

        public string? Title
        {
            get => (string?)GetValue(TitleProperty);
            set => SetValue(TitleProperty, value);
        }

        public bool IsProgress
        {
            get => (bool)GetValue(IsProgressProperty);
            set => SetValue(IsProgressProperty, value);
        }

        public string? ActionButtonText
        {
            get => (string?)GetValue(ActionButtonTextProperty);
            set => SetValue(ActionButtonTextProperty, value);
        }

        public ICommand? ActionButtonCommand
        {
            get => (ICommand?)GetValue(ActionButtonCommandProperty);
            set => SetValue(ActionButtonCommandProperty, value);
        }

        public event RoutedEventHandler? Dismissed;

        public VSQToastNotification()
        {
            InitializeComponent();
            Loaded += VSQToastNotification_Loaded;
        }

        private void VSQToastNotification_Loaded(object sender, RoutedEventArgs e)
        {
            // Set accessibility properties
            var toastTypeName = ToastType switch
            {
                Services.ToastType.Success => "Success",
                Services.ToastType.Error => "Error",
                Services.ToastType.Warning => "Warning",
                Services.ToastType.Info => "Information",
                Services.ToastType.Progress => "Progress",
                _ => "Notification"
            };

            AutomationProperties.SetName(this, $"{toastTypeName} notification: {Message}");
            AutomationProperties.SetHelpText(this, Title != null ? $"{Title}: {Message}" : Message);
            // AutomationLiveSetting.Polite not available in WinUI 3 - removed for compatibility
        }

        private static void OnToastTypeChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is VSQToastNotification toast && e.NewValue is Services.ToastType newType)
            {
                // Apply style based on type
                var styleKey = newType switch
                {
                    Services.ToastType.Success => "VSQ.Toast.Success",
                    Services.ToastType.Error => "VSQ.Toast.Error",
                    Services.ToastType.Warning => "VSQ.Toast.Warning",
                    Services.ToastType.Info => "VSQ.Toast.Info",
                    Services.ToastType.Progress => "VSQ.Toast.Progress",
                    _ => "VSQ.Toast.Container"
                };

                if (Application.Current.Resources.TryGetValue(styleKey, out var style) && style is Style toastStyle)
                {
                    toast.ToastBorder.Style = toastStyle;
                }
            }
        }

        private void DismissButton_Click(object sender, RoutedEventArgs e)
        {
            Dismissed?.Invoke(this, e);
        }
    }
}
