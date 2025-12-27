using Microsoft.UI.Xaml.Controls;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Views
{
    /// <summary>
    /// Dialog for displaying update information and managing updates.
    /// </summary>
    public sealed partial class UpdateDialog : ContentDialog
    {
        public UpdateViewModel ViewModel { get; }
        
        public UpdateDialog(UpdateViewModel viewModel)
        {
            InitializeComponent();
            ViewModel = viewModel;
            DataContext = ViewModel;
            
            // Handle dismiss event
            ViewModel.Dismiss += () => Hide();
        }
    }
}

