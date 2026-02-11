using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.App.Views.Dialogs;

/// <summary>
/// First-run dialog for telemetry consent.
/// </summary>
public sealed partial class TelemetryConsentDialog : ContentDialog
{
    /// <summary>
    /// Gets whether the user checked "Don't ask me again".
    /// </summary>
    public bool DontShowAgain => DontShowAgainCheckBox.IsChecked ?? false;

    /// <summary>
    /// Gets whether the user consented to analytics.
    /// </summary>
    public bool ConsentGiven { get; private set; }

    public TelemetryConsentDialog()
    {
        this.InitializeComponent();
        
        // Wire up button clicks
        this.PrimaryButtonClick += (s, e) => ConsentGiven = true;
        this.SecondaryButtonClick += (s, e) => ConsentGiven = false;
        this.CloseButtonClick += (s, e) => ConsentGiven = false;
    }
}
