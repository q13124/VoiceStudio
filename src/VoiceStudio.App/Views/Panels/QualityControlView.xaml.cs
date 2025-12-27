using Microsoft.UI.Xaml.Controls;
using VoiceStudio.App.ViewModels;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Views.Panels
{
    /// <summary>
    /// Quality Control View - Quality management dashboard panel.
    /// </summary>
    public sealed partial class QualityControlView : UserControl
    {
        public QualityControlViewModel ViewModel { get; }
        private ToastNotificationService? _toastService;

        public QualityControlView()
        {
            InitializeComponent();
            ViewModel = new QualityControlViewModel(ServiceProvider.GetBackendClient());
            DataContext = ViewModel;
            
            // Initialize services
            _toastService = ServiceProvider.GetToastNotificationService();
            
            // Subscribe to ViewModel events for toast notifications
            ViewModel.PropertyChanged += (s, e) =>
            {
                if (e.PropertyName == nameof(QualityControlViewModel.ErrorMessage) && !string.IsNullOrEmpty(ViewModel.ErrorMessage))
                {
                    _toastService?.ShowToast(ToastType.Error, "Quality Control Error", ViewModel.ErrorMessage);
                }
                else if (e.PropertyName == nameof(QualityControlViewModel.StatusMessage) && !string.IsNullOrEmpty(ViewModel.StatusMessage))
                {
                    _toastService?.ShowToast(ToastType.Success, "Quality Control", ViewModel.StatusMessage);
                }
            };
            
            // Setup keyboard navigation
            this.Loaded += QualityControlView_KeyboardNavigation_Loaded;
            
            // Setup Escape key to close help overlay
            KeyboardNavigationHelper.SetupEscapeKeyHandling(this, () =>
            {
                if (HelpOverlay.IsVisible)
                {
                    HelpOverlay.IsVisible = false;
                }
            });
        }
        
        private void QualityControlView_KeyboardNavigation_Loaded(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
        {
            KeyboardNavigationHelper.SetupTabNavigation(this);
        }

        private void HelpButton_Click(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
        {
            HelpOverlay.Title = "Quality Control Help";
            HelpOverlay.HelpText = "The Quality Control panel provides a comprehensive dashboard for managing and monitoring audio quality across all voice synthesis projects. View quality metrics, track quality trends, set quality thresholds, and receive alerts for quality issues. The dashboard helps maintain consistent quality standards and identify areas for improvement in voice synthesis workflows.";
            
            HelpOverlay.Shortcuts.Clear();
            
            HelpOverlay.Tips.Clear();
            HelpOverlay.Tips.Add("Quality control dashboard monitors all voice synthesis operations");
            HelpOverlay.Tips.Add("Set quality thresholds to automatically flag low-quality outputs");
            HelpOverlay.Tips.Add("Track quality trends over time to identify improvements");
            HelpOverlay.Tips.Add("Quality alerts notify you of potential issues");
            HelpOverlay.Tips.Add("Use quality reports to analyze and improve synthesis settings");
            
            HelpOverlay.Visibility = Microsoft.UI.Xaml.Visibility.Visible;
            HelpOverlay.Show();
        }
    }
}

