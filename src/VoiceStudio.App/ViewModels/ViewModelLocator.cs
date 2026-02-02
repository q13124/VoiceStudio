using System;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Views.Panels;

namespace VoiceStudio.App.ViewModels
{
    /// <summary>
    /// Locator for ViewModels to enable XAML design-time and runtime resolution.
    /// Provides a bridge between XAML DataContext binding and DI container.
    /// </summary>
    /// <remarks>
    /// Usage in XAML:
    /// <code>
    /// &lt;Page DataContext="{Binding VoiceSynthesisViewModel, Source={StaticResource Locator}}" /&gt;
    /// </code>
    /// 
    /// Register in App.xaml:
    /// <code>
    /// &lt;Application.Resources&gt;
    ///   &lt;local:ViewModelLocator x:Key="Locator" /&gt;
    /// &lt;/Application.Resources&gt;
    /// </code>
    /// </remarks>
    public class ViewModelLocator
    {
        private static IViewModelFactory? _factory;

        /// <summary>
        /// Initializes the ViewModelLocator with the factory.
        /// Called during app initialization after DI container is built.
        /// </summary>
        public static void Initialize(IViewModelFactory factory)
        {
            _factory = factory ?? throw new ArgumentNullException(nameof(factory));
        }

        /// <summary>
        /// Gets whether the locator is initialized.
        /// </summary>
        public static bool IsInitialized => _factory != null;

        /// <summary>
        /// Gets a ViewModel by type using the factory.
        /// Returns null in design mode or if not initialized.
        /// </summary>
        private TViewModel? GetViewModel<TViewModel>() where TViewModel : class
        {
            if (_factory == null)
            {
                // Design-time or not initialized - return null
                // Views should handle null DataContext gracefully
                return null;
            }

            try
            {
                return _factory.Create<TViewModel>();
            }
            catch
            {
                // If ViewModel creation fails, return null
                // This allows the View to still render in design mode
                return null;
            }
        }

        // Common ViewModel properties for XAML binding
        // Add more as needed for design-time support

        /// <summary>Voice synthesis ViewModel.</summary>
        public VoiceSynthesisViewModel? VoiceSynthesisViewModel => GetViewModel<VoiceSynthesisViewModel>();

        /// <summary>Settings ViewModel.</summary>
        public SettingsViewModel? SettingsViewModel => GetViewModel<SettingsViewModel>();

        /// <summary>Profiles ViewModel.</summary>
        public ProfilesViewModel? ProfilesViewModel => GetViewModel<ProfilesViewModel>();

        /// <summary>Command palette ViewModel.</summary>
        public CommandPaletteViewModel? CommandPaletteViewModel => GetViewModel<CommandPaletteViewModel>();

        /// <summary>Quality dashboard ViewModel.</summary>
        public QualityDashboardViewModel? QualityDashboardViewModel => GetViewModel<QualityDashboardViewModel>();

        /// <summary>Transcribe ViewModel.</summary>
        public TranscribeViewModel? TranscribeViewModel => GetViewModel<TranscribeViewModel>();
    }
}
