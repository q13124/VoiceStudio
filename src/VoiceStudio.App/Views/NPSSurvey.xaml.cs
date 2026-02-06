// ============================================================================
// NPSSurvey.xaml.cs - Code-behind for NPS survey dialog
//
// AI GUIDELINES:
// - Minimal code-behind, logic is in NPSSurveyViewModel
// - Follows MVVM pattern
// ============================================================================

using Microsoft.UI.Xaml.Controls;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Views;

/// <summary>
/// Net Promoter Score survey dialog.
/// </summary>
public sealed partial class NPSSurvey : ContentDialog
{
    /// <summary>
    /// Gets the ViewModel for data binding.
    /// </summary>
    public NPSSurveyViewModel ViewModel { get; }

    /// <summary>
    /// Creates a new NPS survey dialog.
    /// </summary>
    public NPSSurvey()
    {
        ViewModel = new NPSSurveyViewModel();
        this.InitializeComponent();
        this.DataContext = ViewModel;
    }

    /// <summary>
    /// Creates a new NPS survey dialog with a custom ViewModel.
    /// </summary>
    /// <param name="viewModel">The ViewModel to use.</param>
    public NPSSurvey(NPSSurveyViewModel viewModel)
    {
        ViewModel = viewModel;
        this.InitializeComponent();
        this.DataContext = ViewModel;
    }
}
