using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.App.Services;
using VoiceStudio.Core.State;
using VoiceStudio.Core.State.Commands;

namespace VoiceStudio.App.Tests.Services
{
    /// <summary>
    /// Unit tests for AppStateStore.
    /// Tests Redux-like state management, undo/redo, subscriptions.
    /// </summary>
    [TestClass]
    public class AppStateStoreTests
    {
        private AppStateStore _store = null!;

        [TestInitialize]
        public void Setup()
        {
            _store = new AppStateStore(maxUndoHistory: 10);
        }

        [TestCleanup]
        public void Cleanup()
        {
            _store = null!;
        }

        #region Initialization Tests

        [TestMethod]
        public void AppStateStore_InitialState_IsEmpty()
        {
            // Assert
            Assert.IsNotNull(_store.State);
            Assert.IsNull(_store.State.Profile.SelectedProfileId);
            Assert.IsNull(_store.State.Engines.ActiveEngineId);
            Assert.IsFalse(_store.CanUndo);
            Assert.IsFalse(_store.CanRedo);
        }

        [TestMethod]
        public void AppStateStore_DefaultMaxUndo_Is100()
        {
            // Arrange
            var defaultStore = new AppStateStore();

            // Act - dispatch 150 commands
            for (int i = 0; i < 150; i++)
            {
                defaultStore.Dispatch(new SelectProfileCommand($"profile-{i}", $"Profile {i}"));
            }

            // Assert - should have 100 undo items (the default max)
            Assert.AreEqual(100, defaultStore.UndoCount);
        }

        #endregion

        #region Dispatch Tests

        [TestMethod]
        public void Dispatch_WithFuncUpdate_UpdatesState()
        {
            // Arrange & Act
            _store.Dispatch(state => state with
            {
                Profile = state.Profile with { SelectedProfileId = "profile-123" }
            });

            // Assert
            Assert.AreEqual("profile-123", _store.State.Profile.SelectedProfileId);
        }

        [TestMethod]
        public void Dispatch_WithCommand_UpdatesState()
        {
            // Arrange
            var command = new SelectProfileCommand("profile-456", "Test Profile");

            // Act
            _store.Dispatch(command);

            // Assert
            Assert.AreEqual("profile-456", _store.State.Profile.SelectedProfileId);
            Assert.AreEqual("Test Profile", _store.State.Profile.SelectedProfileName);
        }

        [TestMethod]
        public void Dispatch_WithUndoableCommand_AddsToUndoStack()
        {
            // Arrange
            var command = new SelectProfileCommand("profile-789", "Test Profile");

            // Act
            _store.Dispatch(command);

            // Assert
            Assert.IsTrue(_store.CanUndo);
            Assert.AreEqual(1, _store.UndoCount);
        }

        [TestMethod]
        public void Dispatch_RaisesStateChangedEvent()
        {
            // Arrange
            StateChangedEventArgs? args = null;
            _store.StateChanged += (s, e) => args = e;

            // Act
            _store.Dispatch(new SelectProfileCommand("profile-123", "Test"));

            // Assert
            Assert.IsNotNull(args);
            Assert.IsNull(args.PreviousState.Profile.SelectedProfileId);
            Assert.AreEqual("profile-123", args.NewState.Profile.SelectedProfileId);
            Assert.AreEqual("Select Profile", args.ActionName);
        }

        [TestMethod]
        public void Dispatch_SameState_DoesNotRaiseEvent()
        {
            // Arrange
            int eventCount = 0;
            _store.StateChanged += (s, e) => eventCount++;

            // Act - dispatch func that returns same state
            _store.Dispatch(state => state);

            // Assert
            Assert.AreEqual(0, eventCount);
        }

        #endregion

        #region Undo/Redo Tests

        [TestMethod]
        public void Undo_RestoresPreviousState()
        {
            // Arrange
            _store.Dispatch(new SelectProfileCommand("profile-1", "Profile 1"));
            _store.Dispatch(new SelectProfileCommand("profile-2", "Profile 2"));

            // Act
            bool result = _store.Undo();

            // Assert
            Assert.IsTrue(result);
            Assert.AreEqual("profile-1", _store.State.Profile.SelectedProfileId);
        }

        [TestMethod]
        public void Undo_WhenEmpty_ReturnsFalse()
        {
            // Act
            bool result = _store.Undo();

            // Assert
            Assert.IsFalse(result);
        }

        [TestMethod]
        public void Redo_RestoresUndoneState()
        {
            // Arrange
            _store.Dispatch(new SelectProfileCommand("profile-1", "Profile 1"));
            _store.Undo();

            // Act
            bool result = _store.Redo();

            // Assert
            Assert.IsTrue(result);
            Assert.AreEqual("profile-1", _store.State.Profile.SelectedProfileId);
        }

        [TestMethod]
        public void Redo_WhenEmpty_ReturnsFalse()
        {
            // Act
            bool result = _store.Redo();

            // Assert
            Assert.IsFalse(result);
        }

        [TestMethod]
        public void Redo_ClearedByNewDispatch()
        {
            // Arrange
            _store.Dispatch(new SelectProfileCommand("profile-1", "Profile 1"));
            _store.Undo();
            Assert.IsTrue(_store.CanRedo);

            // Act - new dispatch clears redo stack
            _store.Dispatch(new SelectProfileCommand("profile-2", "Profile 2"));

            // Assert
            Assert.IsFalse(_store.CanRedo);
        }

        [TestMethod]
        public void UndoRedo_MultipleOperations()
        {
            // Arrange
            _store.Dispatch(new SelectProfileCommand("profile-1", "Profile 1"));
            _store.Dispatch(new SelectProfileCommand("profile-2", "Profile 2"));
            _store.Dispatch(new SelectProfileCommand("profile-3", "Profile 3"));

            // Act & Assert
            Assert.AreEqual("profile-3", _store.State.Profile.SelectedProfileId);

            _store.Undo();
            Assert.AreEqual("profile-2", _store.State.Profile.SelectedProfileId);

            _store.Undo();
            Assert.AreEqual("profile-1", _store.State.Profile.SelectedProfileId);

            _store.Redo();
            Assert.AreEqual("profile-2", _store.State.Profile.SelectedProfileId);

            _store.Redo();
            Assert.AreEqual("profile-3", _store.State.Profile.SelectedProfileId);
        }

        [TestMethod]
        public void ClearHistory_RemovesAllUndoRedo()
        {
            // Arrange
            _store.Dispatch(new SelectProfileCommand("profile-1", "Profile 1"));
            _store.Dispatch(new SelectProfileCommand("profile-2", "Profile 2"));
            _store.Undo();
            Assert.IsTrue(_store.CanUndo);
            Assert.IsTrue(_store.CanRedo);

            // Act
            _store.ClearHistory();

            // Assert
            Assert.IsFalse(_store.CanUndo);
            Assert.IsFalse(_store.CanRedo);
            Assert.AreEqual(0, _store.UndoCount);
            Assert.AreEqual(0, _store.RedoCount);
        }

        [TestMethod]
        public void UndoStack_TrimsWhenExceedsMax()
        {
            // Arrange - store with max 10 undo
            for (int i = 0; i < 15; i++)
            {
                _store.Dispatch(new SelectProfileCommand($"profile-{i}", $"Profile {i}"));
            }

            // Assert - should have max 10
            Assert.AreEqual(10, _store.UndoCount);
        }

        #endregion

        #region Subscription Tests

        [TestMethod]
        public void Subscribe_ReceivesUpdates()
        {
            // Arrange
            string? receivedProfileId = null;
            using var sub = _store.Subscribe(
                state => state.Profile.SelectedProfileId,
                profileId => receivedProfileId = profileId
            );

            // Act
            _store.Dispatch(new SelectProfileCommand("profile-123", "Test"));

            // Assert
            Assert.AreEqual("profile-123", receivedProfileId);
        }

        [TestMethod]
        public void Subscribe_DisposedSubscription_NoLongerReceives()
        {
            // Arrange
            int callCount = 0;
            var sub = _store.Subscribe(
                state => state.Profile.SelectedProfileId,
                _ => callCount++
            );

            // Act
            _store.Dispatch(new SelectProfileCommand("profile-1", "Profile 1"));
            Assert.AreEqual(1, callCount);

            sub.Dispose();
            _store.Dispatch(new SelectProfileCommand("profile-2", "Profile 2"));

            // Assert - should not have received the second update
            Assert.AreEqual(1, callCount);
        }

        [TestMethod]
        public void Subscribe_MultipleSubscriptions_AllReceive()
        {
            // Arrange
            int count1 = 0, count2 = 0, count3 = 0;
            using var sub1 = _store.Subscribe(state => state.Profile.SelectedProfileId, _ => count1++);
            using var sub2 = _store.Subscribe(state => state.Engines.ActiveEngineId, _ => count2++);
            using var sub3 = _store.Subscribe(state => state.Profile.SelectedProfileId, _ => count3++);

            // Act
            _store.Dispatch(new SelectProfileCommand("profile-1", "Profile 1"));

            // Assert - all subscribers notified on any state change
            Assert.AreEqual(1, count1);
            Assert.AreEqual(1, count2);
            Assert.AreEqual(1, count3);
        }

        #endregion

        #region Select Tests

        [TestMethod]
        public void Select_ReturnsCurrentStateSlice()
        {
            // Arrange
            _store.Dispatch(new SelectProfileCommand("profile-123", "Test Profile"));

            // Act
            var profileId = _store.Select(state => state.Profile.SelectedProfileId);

            // Assert
            Assert.AreEqual("profile-123", profileId);
        }

        [TestMethod]
        public void Select_WithComplexSelector_Works()
        {
            // Arrange
            _store.Dispatch(new SelectProfileCommand("profile-1", "Profile One"));

            // Act
            var summary = _store.Select(state => new
            {
                HasProfile = state.Profile.SelectedProfileId != null,
                ProfileName = state.Profile.SelectedProfileName
            });

            // Assert
            Assert.IsTrue(summary.HasProfile);
            Assert.AreEqual("Profile One", summary.ProfileName);
        }

        #endregion

        #region Thread Safety Tests

        [TestMethod]
        public void ConcurrentDispatch_IsThreadSafe()
        {
            // Arrange
            var tasks = new List<Task>();
            int iterations = 100;

            // Act
            for (int i = 0; i < iterations; i++)
            {
                int capturedI = i;
                tasks.Add(Task.Run(() =>
                {
                    _store.Dispatch(new SelectProfileCommand($"profile-{capturedI}", $"Profile {capturedI}"));
                }));
            }

            Task.WaitAll(tasks.ToArray());

            // Assert - should complete without exceptions
            Assert.IsNotNull(_store.State.Profile.SelectedProfileId);
            Assert.IsTrue(_store.UndoCount <= 10); // max undo is 10
        }

        [TestMethod]
        public async Task DispatchAsync_UpdatesState()
        {
            // Act
            await _store.DispatchAsync(async state =>
            {
                await Task.Delay(10); // Simulate async work
                return state with
                {
                    Profile = state.Profile with { SelectedProfileId = "async-profile" }
                };
            });

            // Assert
            Assert.AreEqual("async-profile", _store.State.Profile.SelectedProfileId);
        }

        #endregion

        #region ExecuteCommand Tests

        [TestMethod]
        public void ExecuteCommand_DispatchesCommand()
        {
            // Arrange
            var command = new SelectProfileCommand("exec-profile", "Execute Test");

            // Act
            _store.ExecuteCommand(command);

            // Assert
            Assert.AreEqual("exec-profile", _store.State.Profile.SelectedProfileId);
            Assert.IsTrue(_store.CanUndo);
        }

        #endregion
    }

    /// <summary>
    /// Unit tests for state commands.
    /// </summary>
    [TestClass]
    public class StateCommandTests
    {
        #region SelectProfileCommand Tests

        [TestMethod]
        public void SelectProfileCommand_Execute_UpdatesProfile()
        {
            // Arrange
            var state = AppState.Empty;
            var command = new SelectProfileCommand("profile-123", "Test Profile");

            // Act
            var newState = command.Execute(state);

            // Assert
            Assert.AreEqual("profile-123", newState.Profile.SelectedProfileId);
            Assert.AreEqual("Test Profile", newState.Profile.SelectedProfileName);
        }

        [TestMethod]
        public void SelectProfileCommand_Undo_RestoresPrevious()
        {
            // Arrange
            var state = AppState.Empty with
            {
                Profile = ProfileState.Empty with
                {
                    SelectedProfileId = "original-profile",
                    SelectedProfileName = "Original"
                }
            };
            var command = new SelectProfileCommand("new-profile", "New");

            // Act
            var afterExecute = command.Execute(state);
            var afterUndo = command.Undo(afterExecute);

            // Assert - undo should restore original (via snapshot)
            Assert.AreEqual("original-profile", afterUndo.Profile.SelectedProfileId);
        }

        [TestMethod]
        public void SelectProfileCommand_Name_IsCorrect()
        {
            var command = new SelectProfileCommand("test", "test");
            Assert.AreEqual("Select Profile", command.Name);
        }

        #endregion

        #region SelectEngineCommand Tests

        [TestMethod]
        public void SelectEngineCommand_Execute_UpdatesEngine()
        {
            // Arrange
            var state = AppState.Empty;
            var command = new SelectEngineCommand("xtts", "XTTS v2");

            // Act
            var newState = command.Execute(state);

            // Assert
            Assert.AreEqual("xtts", newState.Engines.ActiveEngineId);
            Assert.AreEqual("XTTS v2", newState.Engines.ActiveEngineName);
        }

        [TestMethod]
        public void SelectEngineCommand_Undo_RestoresPrevious()
        {
            // Arrange
            var state = AppState.Empty with
            {
                Engines = EngineState.Empty with
                {
                    ActiveEngineId = "bark",
                    ActiveEngineName = "Bark"
                }
            };
            var command = new SelectEngineCommand("xtts", "XTTS");

            // Act
            var afterExecute = command.Execute(state);
            var afterUndo = command.Undo(afterExecute);

            // Assert
            Assert.AreEqual("bark", afterUndo.Engines.ActiveEngineId);
        }

        #endregion

        #region SelectAssetCommand Tests

        [TestMethod]
        public void SelectAssetCommand_Execute_UpdatesAsset()
        {
            // Arrange
            var state = AppState.Empty;
            var command = new SelectAssetCommand("asset-123", "MyAudio.wav", "audio");

            // Act
            var newState = command.Execute(state);

            // Assert
            Assert.AreEqual("asset-123", newState.Assets.SelectedAssetId);
            Assert.AreEqual("MyAudio.wav", newState.Assets.SelectedAssetName);
            Assert.AreEqual("audio", newState.Assets.SelectedAssetType);
        }

        [TestMethod]
        public void SelectAssetCommand_ClearAsset_SetsNull()
        {
            // Arrange
            var state = AppState.Empty with
            {
                Assets = AssetState.Empty with
                {
                    SelectedAssetId = "asset-123",
                    SelectedAssetName = "Test"
                }
            };
            var command = new SelectAssetCommand(null, null, null);

            // Act
            var newState = command.Execute(state);

            // Assert
            Assert.IsNull(newState.Assets.SelectedAssetId);
            Assert.IsNull(newState.Assets.SelectedAssetName);
        }

        #endregion

        #region SwitchWorkspaceCommand Tests

        [TestMethod]
        public void SwitchWorkspaceCommand_Execute_UpdatesWorkspace()
        {
            // Arrange
            var state = AppState.Empty;
            var command = new SwitchWorkspaceCommand("workspace-1", "Default Layout");

            // Act
            var newState = command.Execute(state);

            // Assert
            Assert.AreEqual("workspace-1", newState.Workspace.ActiveWorkspaceId);
            Assert.AreEqual("Default Layout", newState.Workspace.ActiveWorkspaceName);
        }

        [TestMethod]
        public void SwitchWorkspaceCommand_TracksPreviousWorkspace()
        {
            // Arrange
            var state = AppState.Empty with
            {
                Workspace = WorkspaceState.Empty with
                {
                    ActiveWorkspaceId = "workspace-old",
                    ActiveWorkspaceName = "Old Layout"
                }
            };
            var command = new SwitchWorkspaceCommand("workspace-new", "New Layout");

            // Act
            var newState = command.Execute(state);

            // Assert
            Assert.AreEqual("workspace-new", newState.Workspace.ActiveWorkspaceId);
            Assert.AreEqual("workspace-old", newState.Workspace.PreviousWorkspaceId);
        }

        #endregion

        #region UndoableCommandBase Tests

        [TestMethod]
        public void UndoableCommandBase_CanMerge_DefaultsFalse()
        {
            var command = new SelectProfileCommand("test", "test");
            Assert.IsFalse(command.CanMerge);
        }

        [TestMethod]
        public void UndoableCommandBase_Merge_ReturnsNull()
        {
            var command1 = new SelectProfileCommand("test1", "test1");
            var command2 = new SelectProfileCommand("test2", "test2");

            var merged = command1.Merge(command2);

            Assert.IsNull(merged);
        }

        #endregion
    }
}
