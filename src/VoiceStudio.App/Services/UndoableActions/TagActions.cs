using System;
using System.Collections.ObjectModel;
using System.Linq;
using VoiceStudio.Core.Services;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Services.UndoableActions
{
    /// <summary>
    /// Undoable action for creating a tag.
    /// </summary>
    public class CreateTagAction : IUndoableAction
    {
        private readonly ObservableCollection<TagItem> _tags;
        private readonly IBackendClient _backendClient;
        private readonly TagItem _tag;
        private readonly Action<TagItem>? _onUndo;
        private readonly Action<TagItem>? _onRedo;

        public string ActionName => $"Create Tag '{_tag.Name ?? "Unnamed"}'";

        public CreateTagAction(
            ObservableCollection<TagItem> tags,
            IBackendClient backendClient,
            TagItem tag,
            Action<TagItem>? onUndo = null,
            Action<TagItem>? onRedo = null)
        {
            _tags = tags ?? throw new ArgumentNullException(nameof(tags));
            _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));
            _tag = tag ?? throw new ArgumentNullException(nameof(tag));
            _onUndo = onUndo;
            _onRedo = onRedo;
        }

        public void Undo()
        {
            var tagToRemove = _tags.FirstOrDefault(t => t.Id == _tag.Id);
            if (tagToRemove != null)
            {
                _tags.Remove(tagToRemove);
                _onUndo?.Invoke(tagToRemove);
            }
        }

        public void Redo()
        {
            if (!_tags.Any(t => t.Id == _tag.Id))
            {
                _tags.Add(_tag);
                _onRedo?.Invoke(_tag);
            }
        }
    }

    /// <summary>
    /// Undoable action for deleting a tag.
    /// </summary>
    public class DeleteTagAction : IUndoableAction
    {
        private readonly ObservableCollection<TagItem> _tags;
        private readonly IBackendClient _backendClient;
        private readonly TagItem _tag;
        private readonly int _originalIndex;
        private readonly Action<TagItem>? _onUndo;
        private readonly Action<TagItem>? _onRedo;

        public string ActionName => $"Delete Tag '{_tag.Name ?? "Unnamed"}'";

        public DeleteTagAction(
            ObservableCollection<TagItem> tags,
            IBackendClient backendClient,
            TagItem tag,
            int originalIndex,
            Action<TagItem>? onUndo = null,
            Action<TagItem>? onRedo = null)
        {
            _tags = tags ?? throw new ArgumentNullException(nameof(tags));
            _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));
            _tag = tag ?? throw new ArgumentNullException(nameof(tag));
            _originalIndex = originalIndex;
            _onUndo = onUndo;
            _onRedo = onRedo;
        }

        public void Undo()
        {
            if (!_tags.Any(t => t.Id == _tag.Id))
            {
                if (_originalIndex >= 0 && _originalIndex <= _tags.Count)
                {
                    _tags.Insert(_originalIndex, _tag);
                }
                else
                {
                    _tags.Add(_tag);
                }
                _onUndo?.Invoke(_tag);
            }
        }

        public void Redo()
        {
            var tagToRemove = _tags.FirstOrDefault(t => t.Id == _tag.Id);
            if (tagToRemove != null)
            {
                _tags.Remove(tagToRemove);
                _onRedo?.Invoke(tagToRemove);
            }
        }
    }
}

