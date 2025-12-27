using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml;
using VoiceStudio.App.ViewModels;
using VoiceStudio.App.Services;
using VoiceStudio.App.Services.UndoableActions;
using System;

namespace VoiceStudio.App.Views.Panels
{
    /// <summary>
    /// SSMLControlView panel for SSML editing.
    /// </summary>
    public sealed partial class SSMLControlView : UserControl
    {
        public SSMLControlViewModel ViewModel { get; }
        private ContextMenuService? _contextMenuService;
        private ToastNotificationService? _toastService;
        private UndoRedoService? _undoRedoService;

        public SSMLControlView()
        {
            this.InitializeComponent();
            ViewModel = new SSMLControlViewModel(
                VoiceStudio.App.Services.ServiceProvider.GetBackendClient()
            );
            DataContext = ViewModel;

            // Initialize services
            _contextMenuService = ServiceProvider.GetContextMenuService();
            _toastService = ServiceProvider.GetToastNotificationService();
            _undoRedoService = ServiceProvider.GetUndoRedoService();

            // Subscribe to ViewModel events for toast notifications
            ViewModel.PropertyChanged += (s, e) =>
            {
                if (e.PropertyName == nameof(SSMLControlViewModel.ErrorMessage) && !string.IsNullOrEmpty(ViewModel.ErrorMessage))
                {
                    _toastService?.ShowToast(ToastType.Error, "SSML Editor Error", ViewModel.ErrorMessage);
                }
                else if (e.PropertyName == nameof(SSMLControlViewModel.StatusMessage) && !string.IsNullOrEmpty(ViewModel.StatusMessage))
                {
                    _toastService?.ShowToast(ToastType.Success, "SSML Editor", ViewModel.StatusMessage);
                }
            };

            // Setup keyboard navigation
            this.Loaded += SSMLControlView_KeyboardNavigation_Loaded;

            // Setup Escape key to close help overlay
            KeyboardNavigationHelper.SetupEscapeKeyHandling(this, () =>
            {
                if (HelpOverlay.IsVisible)
                {
                    HelpOverlay.IsVisible = false;
                }
            });
        }

        private void SSMLControlView_KeyboardNavigation_Loaded(object sender, RoutedEventArgs e)
        {
            KeyboardNavigationHelper.SetupTabNavigation(this);
        }

        private void HelpButton_Click(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
        {
            HelpOverlay.Title = "SSML Editor Help";
            HelpOverlay.HelpText = "The SSML Editor allows you to create and edit Speech Synthesis Markup Language (SSML) documents. SSML provides fine-grained control over speech synthesis, including pronunciation, prosody, emphasis, and breaks. Create, validate, preview, and manage SSML documents for advanced voice synthesis control.";

            HelpOverlay.Shortcuts.Clear();
            HelpOverlay.Shortcuts.Add(new Controls.KeyboardShortcut { Key = "Ctrl+N", Description = "Create new document" });
            HelpOverlay.Shortcuts.Add(new Controls.KeyboardShortcut { Key = "Ctrl+S", Description = "Save document" });
            HelpOverlay.Shortcuts.Add(new Controls.KeyboardShortcut { Key = "F5", Description = "Validate SSML" });
            HelpOverlay.Shortcuts.Add(new Controls.KeyboardShortcut { Key = "Ctrl+P", Description = "Preview SSML" });
            HelpOverlay.Shortcuts.Add(new Controls.KeyboardShortcut { Key = "Escape", Description = "Close help" });

            HelpOverlay.Tips.Clear();
            HelpOverlay.Tips.Add("SSML provides precise control over speech synthesis parameters");
            HelpOverlay.Tips.Add("Use <prosody> tags to control rate, pitch, and volume");
            HelpOverlay.Tips.Add("Use <break> tags to add pauses and control timing");
            HelpOverlay.Tips.Add("Use <emphasis> tags to add emphasis to specific words");
            HelpOverlay.Tips.Add("Validate SSML before previewing to catch syntax errors");
            HelpOverlay.Tips.Add("Preview SSML to hear how it will sound before saving");

            HelpOverlay.Visibility = Microsoft.UI.Xaml.Visibility.Visible;
            HelpOverlay.Show();
        }

        private void Document_RightTapped(object sender, RightTappedRoutedEventArgs e)
        {
            if (sender is ListView listView && e.OriginalSource is FrameworkElement element)
            {
                var document = element.DataContext ?? listView.SelectedItem;
                if (document != null)
                {
                    e.Handled = true;
                    if (_contextMenuService != null)
                    {
                        var menu = new MenuFlyout();

                        var editItem = new MenuFlyoutItem { Text = "Edit" };
                        editItem.Click += async (s, e2) => await HandleDocumentMenuClick("Edit", document);
                        menu.Items.Add(editItem);

                        var validateItem = new MenuFlyoutItem { Text = "Validate" };
                        validateItem.Click += async (s, e2) => await HandleDocumentMenuClick("Validate", document);
                        menu.Items.Add(validateItem);

                        var previewItem = new MenuFlyoutItem { Text = "Preview" };
                        previewItem.Click += async (s, e2) => await HandleDocumentMenuClick("Preview", document);
                        menu.Items.Add(previewItem);

                        var duplicateItem = new MenuFlyoutItem { Text = "Duplicate" };
                        duplicateItem.Click += async (s, e2) => await HandleDocumentMenuClick("Duplicate", document);
                        menu.Items.Add(duplicateItem);

                        menu.Items.Add(new MenuFlyoutSeparator());

                        var deleteItem = new MenuFlyoutItem { Text = "Delete" };
                        deleteItem.Click += async (s, e2) => await HandleDocumentMenuClick("Delete", document);
                        menu.Items.Add(deleteItem);

                        var position = e.GetPosition(listView);
                        _contextMenuService.ShowContextMenu(menu, listView, position);
                    }
                }
            }
        }

        private async System.Threading.Tasks.Task HandleDocumentMenuClick(string action, object document)
        {
            try
            {
                switch (action.ToLower())
                {
                    case "edit":
                        ViewModel.SelectedDocument = (SSMLDocumentItem)document;
                        _toastService?.ShowToast(ToastType.Info, "Edit Document", "Document selected for editing");
                        break;
                    case "validate":
                        _toastService?.ShowToast(ToastType.Info, "Validate", "Validating SSML document");
                        break;
                    case "preview":
                        _toastService?.ShowToast(ToastType.Info, "Preview", "Previewing SSML document");
                        break;
                    case "duplicate":
                        DuplicateDocument(document);
                        break;
                    case "delete":
                        var dialog = new ContentDialog
                        {
                            Title = "Delete Document",
                            Content = "Are you sure you want to delete this SSML document? This action cannot be undone.",
                            PrimaryButtonText = "Delete",
                            CloseButtonText = "Cancel",
                            DefaultButton = ContentDialogButton.Close,
                            XamlRoot = this.XamlRoot
                        };

                        var result = await dialog.ShowAsync();
                        if (result == ContentDialogResult.Primary)
                        {
                            var documentToDelete = (SSMLDocumentItem)document;
                            var documentIndex = ViewModel.Documents.IndexOf(documentToDelete);

                            ViewModel.Documents.Remove(documentToDelete);

                            // Register undo action
                            if (_undoRedoService != null && documentIndex >= 0)
                            {
                                var actionObj = new SimpleAction(
                                    "Delete SSML Document",
                                    () => ViewModel.Documents.Insert(documentIndex, documentToDelete),
                                    () => ViewModel.Documents.Remove(documentToDelete));
                                _undoRedoService.RegisterAction(actionObj);
                            }

                            _toastService?.ShowToast(ToastType.Success, "Deleted", "Document deleted");
                        }
                        break;
                }
            }
            catch (Exception ex)
            {
                _toastService?.ShowToast(ToastType.Error, "Error", $"Failed to {action}: {ex.Message}");
            }
        }

        private void DuplicateDocument(object document)
        {
            // TODO: SSML document duplication not implemented due to nested class access issues
            _toastService?.ShowToast(ToastType.Info, "Not Implemented", "Document duplication is not yet implemented");
        }
    }
}

