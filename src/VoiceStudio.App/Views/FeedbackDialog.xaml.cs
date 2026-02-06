// ============================================================================
// FeedbackDialog.xaml.cs - Code-behind for the feedback dialog
//
// AI GUIDELINES:
// - Minimal code-behind following MVVM pattern
// - ViewModel handles all logic; this file only wires up the dialog
// ============================================================================

using Microsoft.UI.Xaml.Controls;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Views;

/// <summary>
/// Dialog for collecting user feedback about VoiceStudio.
/// </summary>
public sealed partial class FeedbackDialog : ContentDialog
{
    /// <summary>
    /// Gets the ViewModel for this dialog.
    /// </summary>
    public FeedbackViewModel ViewModel { get; }

    /// <summary>
    /// Creates a new FeedbackDialog instance.
    /// </summary>
    /// <param name="viewModel">The ViewModel to use for data binding.</param>
    public FeedbackDialog(FeedbackViewModel viewModel)
    {
        InitializeComponent();
        ViewModel = viewModel;
        DataContext = ViewModel;

        // Wire up dismiss event
        ViewModel.Dismiss += () => Hide();

        // Disable primary button when form is invalid
        IsPrimaryButtonEnabled = ViewModel.CanSubmit;
        ViewModel.PropertyChanged += (s, e) =>
        {
            if (e.PropertyName == nameof(FeedbackViewModel.CanSubmit))
            {
                IsPrimaryButtonEnabled = ViewModel.CanSubmit;
            }
        };
    }

    /// <summary>
    /// Creates a new FeedbackDialog with a default ViewModel.
    /// </summary>
    public FeedbackDialog() : this(new FeedbackViewModel())
    {
    }
}
