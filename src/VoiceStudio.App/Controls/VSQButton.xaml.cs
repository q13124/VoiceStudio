using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Automation;
using System.Windows.Input;
using Windows.UI.ViewManagement;

namespace VoiceStudio.App.Controls
{
  public sealed partial class VSQButton : UserControl
  {
    private static readonly UISettings UiSettings = new();
    private bool _isPointerOver;
    private bool _isPressed;

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

    private void OnPointerEntered(object sender, PointerRoutedEventArgs e)
    {
      _isPointerOver = true;
      UpdateVisualState();
    }

    private void OnPointerExited(object sender, PointerRoutedEventArgs e)
    {
      _isPointerOver = false;
      _isPressed = false;
      UpdateVisualState();
    }

    private void OnPointerPressed(object sender, PointerRoutedEventArgs e)
    {
      _isPressed = true;
      UpdateVisualState();
    }

    private void OnPointerReleased(object sender, PointerRoutedEventArgs e)
    {
      _isPressed = false;
      UpdateVisualState();
    }

    private void UpdateVisualState()
    {
      // Check system animation preference - skip animation if user prefers reduced motion
      bool useAnimations = UiSettings.AnimationsEnabled;

      if (_isPressed)
      {
        VisualStateManager.GoToState(this, "Pressed", useAnimations);
      }
      else if (_isPointerOver)
      {
        VisualStateManager.GoToState(this, "PointerOver", useAnimations);
      }
      else
      {
        VisualStateManager.GoToState(this, "Normal", useAnimations);
      }
    }

    private void VSQButton_Loaded(object _, RoutedEventArgs e)
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

    private void ButtonControl_Click(object _, RoutedEventArgs __)
    {
      if (Command?.CanExecute(CommandParameter) == true)
      {
        Command.Execute(CommandParameter);
      }
    }
  }
}