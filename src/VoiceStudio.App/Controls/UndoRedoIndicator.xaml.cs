using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml;
using System.Windows.Input;
using VoiceStudio.App.Services;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Mvvm.ComponentModel;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Visual indicator for undo/redo operations.
    /// Implements IDEA 15: Undo/Redo Visual Indicator.
    /// </summary>
    public sealed partial class UndoRedoIndicator : UserControl
    {
        private UndoRedoService? _undoRedoService;
        private RelayCommand? _undoCommand;
        private RelayCommand? _redoCommand;

        public static readonly DependencyProperty ShowCountProperty =
            DependencyProperty.Register(
                nameof(ShowCount),
                typeof(bool),
                typeof(UndoRedoIndicator),
                new PropertyMetadata(true));

        public bool ShowCount
        {
            get => (bool)GetValue(ShowCountProperty);
            set => SetValue(ShowCountProperty, value);
        }

        public ICommand UndoCommand => _undoCommand ??= new RelayCommand(
            () => _undoRedoService?.Undo(),
            () => _undoRedoService?.CanUndo ?? false);

        public ICommand RedoCommand => _redoCommand ??= new RelayCommand(
            () => _undoRedoService?.Redo(),
            () => _undoRedoService?.CanRedo ?? false);

        public UndoRedoIndicator()
        {
            this.InitializeComponent();
            
            _undoRedoService = ServiceProvider.GetUndoRedoService();

            // Subscribe to service property changes
            if (_undoRedoService != null)
            {
                _undoRedoService.PropertyChanged += UndoRedoService_PropertyChanged;
                UpdateDisplay();
            }

            // Set initial command bindings
            UndoButton.Command = UndoCommand;
            RedoButton.Command = RedoCommand;
        }

        private void UndoRedoService_PropertyChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
        {
            UpdateDisplay();
            
            // Update command can execute
            _undoCommand?.NotifyCanExecuteChanged();
            _redoCommand?.NotifyCanExecuteChanged();
        }

        private void UpdateDisplay()
        {
            if (_undoRedoService == null)
                return;

            var undoCount = _undoRedoService.UndoCount;
            var redoCount = _undoRedoService.RedoCount;

            UndoCountText.Text = undoCount > 0 ? $"({undoCount})" : string.Empty;
            RedoCountText.Text = redoCount > 0 ? $"({redoCount})" : string.Empty;

            // Update tooltips with action names
            var nextUndo = _undoRedoService.NextUndoActionName;
            var undoToolTip = nextUndo != null 
                ? $"Undo: {nextUndo} (Ctrl+Z)" 
                : "Undo (Ctrl+Z)";

            var nextRedo = _undoRedoService.NextRedoActionName;
            var redoToolTip = nextRedo != null 
                ? $"Redo: {nextRedo} (Ctrl+Y)" 
                : "Redo (Ctrl+Y)";

            // Update history in tooltip (show last 5 actions)
            var undoHistory = _undoRedoService.GetUndoHistory(5);
            if (undoHistory.Count > 0)
            {
                undoToolTip += "\n\nRecent actions:\n" + string.Join("\n", undoHistory);
            }

            var redoHistory = _undoRedoService.GetRedoHistory(5);
            if (redoHistory.Count > 0)
            {
                redoToolTip += "\n\nRedo actions:\n" + string.Join("\n", redoHistory);
            }

            ToolTipService.SetToolTip(UndoButton, undoToolTip);
            ToolTipService.SetToolTip(RedoButton, redoToolTip);
        }
    }
}

