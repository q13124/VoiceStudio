using System;
using System.Collections.ObjectModel;
using System.Linq;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Services.UndoableActions
{
    /// <summary>
    /// Undoable action for adding a voice to an ensemble.
    /// </summary>
    public class AddEnsembleVoiceAction : IUndoableAction
    {
        private readonly ObservableCollection<EnsembleVoiceItem> _voices;
        private readonly EnsembleVoiceItem _voice;
        private readonly int _insertIndex;
        private readonly Action<EnsembleVoiceItem>? _onUndo;
        private readonly Action<EnsembleVoiceItem>? _onRedo;

        public string ActionName => $"Add Voice to Ensemble";

        public AddEnsembleVoiceAction(
            ObservableCollection<EnsembleVoiceItem> voices,
            EnsembleVoiceItem voice,
            int insertIndex,
            Action<EnsembleVoiceItem>? onUndo = null,
            Action<EnsembleVoiceItem>? onRedo = null)
        {
            _voices = voices ?? throw new ArgumentNullException(nameof(voices));
            _voice = voice ?? throw new ArgumentNullException(nameof(voice));
            _insertIndex = insertIndex;
            _onUndo = onUndo;
            _onRedo = onRedo;
        }

        public void Undo()
        {
            // Remove the voice (by reference equality)
            if (_voices.Contains(_voice))
            {
                _voices.Remove(_voice);
                _onUndo?.Invoke(_voice);
            }
        }

        public void Redo()
        {
            // Re-add the voice at the original position
            if (!_voices.Contains(_voice))
            {
                if (_insertIndex >= 0 && _insertIndex <= _voices.Count)
                {
                    _voices.Insert(_insertIndex, _voice);
                }
                else
                {
                    _voices.Add(_voice);
                }
                _onRedo?.Invoke(_voice);
            }
        }
    }

    /// <summary>
    /// Undoable action for removing a voice from an ensemble.
    /// </summary>
    public class RemoveEnsembleVoiceAction : IUndoableAction
    {
        private readonly ObservableCollection<EnsembleVoiceItem> _voices;
        private readonly EnsembleVoiceItem _voice;
        private readonly int _originalIndex;
        private readonly Action<EnsembleVoiceItem>? _onUndo;
        private readonly Action<EnsembleVoiceItem>? _onRedo;

        public string ActionName => $"Remove Voice from Ensemble";

        public RemoveEnsembleVoiceAction(
            ObservableCollection<EnsembleVoiceItem> voices,
            EnsembleVoiceItem voice,
            int originalIndex,
            Action<EnsembleVoiceItem>? onUndo = null,
            Action<EnsembleVoiceItem>? onRedo = null)
        {
            _voices = voices ?? throw new ArgumentNullException(nameof(voices));
            _voice = voice ?? throw new ArgumentNullException(nameof(voice));
            _originalIndex = originalIndex;
            _onUndo = onUndo;
            _onRedo = onRedo;
        }

        public void Undo()
        {
            // Re-add the voice at the original position
            if (!_voices.Contains(_voice))
            {
                if (_originalIndex >= 0 && _originalIndex <= _voices.Count)
                {
                    _voices.Insert(_originalIndex, _voice);
                }
                else
                {
                    _voices.Add(_voice);
                }
                _onUndo?.Invoke(_voice);
            }
        }

        public void Redo()
        {
            // Remove the voice (by reference equality)
            if (_voices.Contains(_voice))
            {
                _voices.Remove(_voice);
                _onRedo?.Invoke(_voice);
            }
        }
    }
}

