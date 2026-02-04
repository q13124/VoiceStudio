using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Automation;

namespace VoiceStudio.App.Controls
{
  public sealed partial class VSQFormField : UserControl
  {
    public static readonly DependencyProperty LabelProperty =
        DependencyProperty.Register(nameof(Label), typeof(string), typeof(VSQFormField), new PropertyMetadata(string.Empty));

    public static readonly DependencyProperty TextProperty =
        DependencyProperty.Register(nameof(Text), typeof(string), typeof(VSQFormField), new PropertyMetadata(string.Empty));

    public static readonly DependencyProperty PlaceholderProperty =
        DependencyProperty.Register(nameof(Placeholder), typeof(string), typeof(VSQFormField), new PropertyMetadata(string.Empty));

    public static readonly DependencyProperty ErrorMessageProperty =
        DependencyProperty.Register(nameof(ErrorMessage), typeof(string), typeof(VSQFormField), new PropertyMetadata(string.Empty));

    public static readonly DependencyProperty HelpTextProperty =
        DependencyProperty.Register(nameof(HelpText), typeof(string), typeof(VSQFormField), new PropertyMetadata(string.Empty, OnHelpTextChanged));

    public static readonly DependencyProperty HasErrorProperty =
        DependencyProperty.Register(nameof(HasError), typeof(bool), typeof(VSQFormField), new PropertyMetadata(false, OnHasErrorChanged));

    public static readonly DependencyProperty ErrorVisibilityProperty =
        DependencyProperty.Register(nameof(ErrorVisibility), typeof(Visibility), typeof(VSQFormField), new PropertyMetadata(Visibility.Collapsed));

    public static readonly DependencyProperty HelpVisibilityProperty =
        DependencyProperty.Register(nameof(HelpVisibility), typeof(Visibility), typeof(VSQFormField), new PropertyMetadata(Visibility.Collapsed));

    public string Label
    {
      get => (string)GetValue(LabelProperty);
      set => SetValue(LabelProperty, value);
    }

    public string Text
    {
      get => (string)GetValue(TextProperty);
      set => SetValue(TextProperty, value);
    }

    public string Placeholder
    {
      get => (string)GetValue(PlaceholderProperty);
      set => SetValue(PlaceholderProperty, value);
    }

    public string ErrorMessage
    {
      get => (string)GetValue(ErrorMessageProperty);
      set => SetValue(ErrorMessageProperty, value);
    }

    public string HelpText
    {
      get => (string)GetValue(HelpTextProperty);
      set => SetValue(HelpTextProperty, value);
    }

    public bool HasError
    {
      get => (bool)GetValue(HasErrorProperty);
      set => SetValue(HasErrorProperty, value);
    }

    public bool HasHelpText => !string.IsNullOrEmpty(HelpText);

    public Visibility ErrorVisibility
    {
      get => (Visibility)GetValue(ErrorVisibilityProperty);
      private set => SetValue(ErrorVisibilityProperty, value);
    }

    public Visibility HelpVisibility
    {
      get => (Visibility)GetValue(HelpVisibilityProperty);
      private set => SetValue(HelpVisibilityProperty, value);
    }

    public VSQFormField()
    {
      InitializeComponent();
      Loaded += VSQFormField_Loaded;
    }

    private void VSQFormField_Loaded(object _, RoutedEventArgs e)
    {
      // Set accessibility properties
      AutomationProperties.SetLabeledBy(InputTextBox, LabelText);
      AutomationProperties.SetName(InputTextBox, Label);
      AutomationProperties.SetHelpText(InputTextBox, HelpText);

      if (HasError)
      {
        AutomationProperties.SetItemStatus(InputTextBox, ErrorMessage);
      }

      // Ensure visibility state is correct on first render.
      UpdateHelpState();
      UpdateErrorState();
    }

    private static void OnHasErrorChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
      if (d is VSQFormField field)
      {
        field.UpdateErrorState();
      }
    }

    private static void OnHelpTextChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
      if (d is VSQFormField field)
      {
        field.UpdateHelpState();
        AutomationProperties.SetHelpText(field.InputTextBox, field.HelpText);
      }
    }

    private void UpdateErrorState()
    {
      if (HasError)
      {
        InputTextBox.BorderBrush = Application.Current.Resources["VSQ.Error.Brush"] as Microsoft.UI.Xaml.Media.Brush;
        AutomationProperties.SetItemStatus(InputTextBox, ErrorMessage);
        ErrorVisibility = Visibility.Visible;
      }
      else
      {
        InputTextBox.BorderBrush = Application.Current.Resources["VSQ.Panel.BorderBrush"] as Microsoft.UI.Xaml.Media.Brush;
        AutomationProperties.SetItemStatus(InputTextBox, string.Empty);
        ErrorVisibility = Visibility.Collapsed;
      }
    }

    private void UpdateHelpState()
    {
      HelpVisibility = !string.IsNullOrEmpty(HelpText) ? Visibility.Visible : Visibility.Collapsed;
    }

    private void InputTextBox_TextChanged(object _, TextChangedEventArgs __)
    {
      // Clear error when user starts typing
      if (HasError && !string.IsNullOrEmpty(Text))
      {
        HasError = false;
      }
    }
  }
}