using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Automation;

namespace VoiceStudio.App.Controls
{
  public sealed partial class VSQProgressIndicator : UserControl
  {
    public static readonly DependencyProperty ProgressProperty =
        DependencyProperty.Register(nameof(Progress), typeof(double), typeof(VSQProgressIndicator), new PropertyMetadata(0.0, OnProgressChanged));

    public static readonly DependencyProperty IsIndeterminateProperty =
        DependencyProperty.Register(nameof(IsIndeterminate), typeof(bool), typeof(VSQProgressIndicator), new PropertyMetadata(false, OnIsIndeterminateChanged));

    public static readonly DependencyProperty ProgressTextProperty =
        DependencyProperty.Register(nameof(ProgressText), typeof(string), typeof(VSQProgressIndicator), new PropertyMetadata(string.Empty));

    public static readonly DependencyProperty ShowTextProperty =
        DependencyProperty.Register(nameof(ShowText), typeof(bool), typeof(VSQProgressIndicator), new PropertyMetadata(false, OnShowTextChanged));

    public static readonly DependencyProperty ProgressBarVisibilityProperty =
        DependencyProperty.Register(nameof(ProgressBarVisibility), typeof(Visibility), typeof(VSQProgressIndicator), new PropertyMetadata(Visibility.Visible));

    public static readonly DependencyProperty ProgressRingVisibilityProperty =
        DependencyProperty.Register(nameof(ProgressRingVisibility), typeof(Visibility), typeof(VSQProgressIndicator), new PropertyMetadata(Visibility.Collapsed));

    public static readonly DependencyProperty ProgressTextVisibilityProperty =
        DependencyProperty.Register(nameof(ProgressTextVisibility), typeof(Visibility), typeof(VSQProgressIndicator), new PropertyMetadata(Visibility.Collapsed));

    public double Progress
    {
      get => (double)GetValue(ProgressProperty);
      set => SetValue(ProgressProperty, value);
    }

    public bool IsIndeterminate
    {
      get => (bool)GetValue(IsIndeterminateProperty);
      set => SetValue(IsIndeterminateProperty, value);
    }

    public string ProgressText
    {
      get => (string)GetValue(ProgressTextProperty);
      set => SetValue(ProgressTextProperty, value);
    }

    public bool ShowText
    {
      get => (bool)GetValue(ShowTextProperty);
      set => SetValue(ShowTextProperty, value);
    }

    public Visibility ProgressBarVisibility
    {
      get => (Visibility)GetValue(ProgressBarVisibilityProperty);
      private set => SetValue(ProgressBarVisibilityProperty, value);
    }

    public Visibility ProgressRingVisibility
    {
      get => (Visibility)GetValue(ProgressRingVisibilityProperty);
      private set => SetValue(ProgressRingVisibilityProperty, value);
    }

    public Visibility ProgressTextVisibility
    {
      get => (Visibility)GetValue(ProgressTextVisibilityProperty);
      private set => SetValue(ProgressTextVisibilityProperty, value);
    }

    public VSQProgressIndicator()
    {
      InitializeComponent();
      Loaded += VSQProgressIndicator_Loaded;
    }

    private void VSQProgressIndicator_Loaded(object _, RoutedEventArgs e)
    {
      UpdateVisualState();
      UpdateAccessibility();
    }

    private static void OnProgressChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
      if (d is VSQProgressIndicator indicator)
      {
        indicator.UpdateAccessibility();
      }
    }

    private static void OnIsIndeterminateChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
      if (d is VSQProgressIndicator indicator)
      {
        indicator.UpdateVisualState();
        indicator.UpdateAccessibility();
      }
    }

    private static void OnShowTextChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
      if (d is VSQProgressIndicator indicator)
      {
        indicator.UpdateVisualState();
      }
    }

    private void UpdateVisualState()
    {
      ProgressBarVisibility = IsIndeterminate ? Visibility.Collapsed : Visibility.Visible;
      ProgressRingVisibility = IsIndeterminate ? Visibility.Visible : Visibility.Collapsed;
      ProgressTextVisibility = ShowText ? Visibility.Visible : Visibility.Collapsed;
    }

    private void UpdateAccessibility()
    {
      if (IsIndeterminate)
      {
        AutomationProperties.SetName(ProgressRingControl, "Loading in progress");
        AutomationProperties.SetHelpText(ProgressRingControl, "Please wait while the operation completes");
      }
      else
      {
        var percentage = (int)Progress;
        AutomationProperties.SetName(ProgressBarControl, $"Progress: {percentage}%");
        // SetValue is not available in WinUI 3 - use SetHelpText instead
        AutomationProperties.SetHelpText(ProgressBarControl, $"Operation is {percentage}% complete");
      }
    }
  }
}