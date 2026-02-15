// VoiceStudio - Panel Architecture: Drop Zone Visual Overlay
// Provides visual feedback during drag operations

using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Visual overlay that indicates a valid drop zone during drag operations.
    /// </summary>
    public sealed partial class DropZoneOverlay : UserControl
    {
        private bool _isShowing;
        private bool _isValid = true;

        /// <summary>
        /// Gets or sets the hint text displayed in the overlay.
        /// </summary>
        public string HintText
        {
            get => DropHintText.Text;
            set => DropHintText.Text = value;
        }

        /// <summary>
        /// Gets or sets the icon glyph displayed in the overlay.
        /// </summary>
        public string IconGlyph
        {
            get => DropIcon.Glyph;
            set => DropIcon.Glyph = value;
        }

        /// <summary>
        /// Gets or sets whether the drop is valid at this location.
        /// </summary>
        public bool IsValidDrop
        {
            get => _isValid;
            set
            {
                _isValid = value;
                UpdateValidState();
            }
        }

        /// <summary>
        /// Gets whether the overlay is currently showing.
        /// </summary>
        public bool IsShowing => _isShowing;

        public DropZoneOverlay()
        {
            this.InitializeComponent();
            this.Visibility = Visibility.Collapsed;
        }

        /// <summary>
        /// Shows the overlay.
        /// </summary>
        public void Show()
        {
            if (_isShowing) return;
            _isShowing = true;

            this.Visibility = Visibility.Visible;
            UpdateValidState();
            RootGrid.Opacity = 1;
        }

        /// <summary>
        /// Hides the overlay.
        /// </summary>
        public void Hide()
        {
            if (!_isShowing) return;
            _isShowing = false;

            this.Visibility = Visibility.Collapsed;
            RootGrid.Opacity = 0;
        }

        /// <summary>
        /// Configures the overlay for a specific payload type.
        /// </summary>
        /// <param name="payloadType">The type of drag payload.</param>
        public void ConfigureForPayload(DragPayloadType payloadType)
        {
            switch (payloadType)
            {
                case DragPayloadType.Asset:
                    IconGlyph = "\uE8A5"; // Document icon
                    HintText = "Drop asset here";
                    break;

                case DragPayloadType.Profile:
                    IconGlyph = "\uE77B"; // Contact icon
                    HintText = "Drop profile here";
                    break;

                case DragPayloadType.TimelineClip:
                    IconGlyph = "\uE8B1"; // Video icon
                    HintText = "Drop clip here";
                    break;

                case DragPayloadType.TextBlock:
                    IconGlyph = "\uE8F2"; // Font icon
                    HintText = "Drop text here";
                    break;

                case DragPayloadType.ReferenceAudio:
                    IconGlyph = "\uE8D6"; // Audio icon
                    HintText = "Drop reference audio here";
                    break;

                case DragPayloadType.ExternalFile:
                    IconGlyph = "\uE8E5"; // Import icon
                    HintText = "Drop file here";
                    break;

                case DragPayloadType.MultiSelect:
                    IconGlyph = "\uE762"; // Multiple selection icon
                    HintText = "Drop items here";
                    break;

                default:
                    IconGlyph = "\uE896"; // Download icon
                    HintText = "Drop here";
                    break;
            }
        }

        private void UpdateValidState()
        {
            if (_isValid)
            {
                InvalidOverlay.Visibility = Visibility.Collapsed;
                OverlayBorder.Visibility = Visibility.Visible;
                AccentBorder.Visibility = Visibility.Visible;
                ValidDropContent.Visibility = Visibility.Visible;
            }
            else
            {
                InvalidOverlay.Visibility = Visibility.Visible;
                OverlayBorder.Visibility = Visibility.Collapsed;
                AccentBorder.Visibility = Visibility.Collapsed;
                ValidDropContent.Visibility = Visibility.Collapsed;
            }
        }
    }
}
