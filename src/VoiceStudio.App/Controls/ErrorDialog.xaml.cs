using System.Collections.Generic;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.App.Controls;

public sealed partial class ErrorDialog : ContentDialog
{
  public static readonly DependencyProperty ErrorMessageProperty =
      DependencyProperty.Register(
          nameof(ErrorMessage),
          typeof(string),
          typeof(ErrorDialog),
          new PropertyMetadata("An error occurred"));

  public static readonly DependencyProperty ErrorDetailsProperty =
      DependencyProperty.Register(
          nameof(ErrorDetails),
          typeof(string),
          typeof(ErrorDialog),
          new PropertyMetadata(string.Empty));

  public static readonly DependencyProperty TechnicalDetailsProperty =
      DependencyProperty.Register(
          nameof(TechnicalDetails),
          typeof(string),
          typeof(ErrorDialog),
          new PropertyMetadata(string.Empty));

  public static readonly DependencyProperty SuggestedActionsProperty =
      DependencyProperty.Register(
          nameof(SuggestedActions),
          typeof(IEnumerable<string>),
          typeof(ErrorDialog),
          new PropertyMetadata(null));

  public string ErrorMessage
  {
    get => (string)GetValue(ErrorMessageProperty);
    set => SetValue(ErrorMessageProperty, value);
  }

  public string ErrorDetails
  {
    get => (string)GetValue(ErrorDetailsProperty);
    set => SetValue(ErrorDetailsProperty, value);
  }

  public string TechnicalDetails
  {
    get => (string)GetValue(TechnicalDetailsProperty);
    set => SetValue(TechnicalDetailsProperty, value);
  }

  public IEnumerable<string>? SuggestedActions
  {
    get => GetValue(SuggestedActionsProperty) as IEnumerable<string>;
    set => SetValue(SuggestedActionsProperty, value);
  }

  public bool HasDetails => !string.IsNullOrEmpty(ErrorDetails);
  public bool ShowTechnicalDetails => !string.IsNullOrEmpty(TechnicalDetails);
  public bool HasSuggestedActions => SuggestedActions?.Any() == true;

  // XAML compiler stability: bind Visibility to Visibility-typed properties (avoid bool->Visibility mismatch).
  public Visibility DetailsVisibility => HasDetails ? Visibility.Visible : Visibility.Collapsed;
  public Visibility TechnicalDetailsVisibility => ShowTechnicalDetails ? Visibility.Visible : Visibility.Collapsed;
  public Visibility SuggestedActionsVisibility => HasSuggestedActions ? Visibility.Visible : Visibility.Collapsed;

  public ErrorDialog()
  {
    this.InitializeComponent();
  }

  private void SuggestedAction_Click(object _, Microsoft.UI.Xaml.RoutedEventArgs __)
  {
    // Handle suggested action click
    // This can be extended with a command or event
  }
}