using System;
using System.Threading.Tasks;
using VoiceStudio.App.Services.UndoableActions;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Extension methods for UndoRedoService to simplify action registration.
    /// </summary>
    public static class UndoRedoServiceExtensions
    {
        /// <summary>
        /// Adds an action with synchronous undo/redo callbacks.
        /// </summary>
        public static void AddAction(this UndoRedoService service, string actionName, Action undoAction, Action redoAction)
        {
            if (service == null)
                return;

            var action = new SimpleAction(actionName, undoAction, redoAction);
            service.RegisterAction(action);
        }

        /// <summary>
        /// Adds an action with asynchronous undo/redo callbacks.
        /// </summary>
        public static void AddAction(this UndoRedoService service, string actionName, Func<Task> undoActionAsync, Func<Task> redoActionAsync)
        {
            if (service == null)
                return;

            var action = new SimpleAction(actionName, undoActionAsync, redoActionAsync);
            service.RegisterAction(action);
        }
    }
}

