using Microsoft.UI.Xaml.Controls;
using VoiceStudio.App.Services;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Views.Panels
{
    /// <summary>
    /// TextBasedSpeechEditorView panel - Edit audio by editing its transcript.
    /// </summary>
    public sealed partial class TextBasedSpeechEditorView : UserControl
    {
        public TextBasedSpeechEditorViewModel ViewModel { get; }

        public TextBasedSpeechEditorView()
        {
            this.InitializeComponent();
            ViewModel = new TextBasedSpeechEditorViewModel(
                ServiceProvider.GetBackendClient()
            );
            this.DataContext = ViewModel;
        }
    }
}

