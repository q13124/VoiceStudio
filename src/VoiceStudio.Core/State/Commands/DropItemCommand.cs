using System;
using System.Collections.Generic;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.Core.State.Commands
{
    /// <summary>
    /// Command to record a drag/drop action for undo/redo support.
    /// Captures both the drop action and associated state changes.
    /// </summary>
    public sealed class DropItemCommand : UndoableCommandBase
    {
        private readonly string _targetPanelId;
        private readonly DragPayloadType _payloadType;
        private readonly IReadOnlyList<DragItem> _items;
        private readonly DropAction _action;
        private readonly Func<AppState, AppState>? _stateTransform;
        private readonly Func<AppState, AppState>? _undoTransform;
        
        /// <summary>
        /// Gets the target panel ID where the drop occurred.
        /// </summary>
        public string TargetPanelId => _targetPanelId;
        
        /// <summary>
        /// Gets the type of payload that was dropped.
        /// </summary>
        public DragPayloadType PayloadType => _payloadType;
        
        /// <summary>
        /// Gets the items that were dropped.
        /// </summary>
        public IReadOnlyList<DragItem> Items => _items;
        
        /// <summary>
        /// Gets the action that was performed.
        /// </summary>
        public DropAction Action => _action;

        /// <inheritdoc />
        public override string Name => $"Drop {PayloadType} to {TargetPanelId}";

        /// <summary>
        /// Creates a drop item command.
        /// </summary>
        /// <param name="targetPanelId">The target panel ID.</param>
        /// <param name="payloadType">The type of payload.</param>
        /// <param name="items">The items being dropped.</param>
        /// <param name="action">The action to perform.</param>
        /// <param name="stateTransform">Optional state transformation to apply on execute.</param>
        /// <param name="undoTransform">Optional state transformation to apply on undo.</param>
        public DropItemCommand(
            string targetPanelId,
            DragPayloadType payloadType,
            IReadOnlyList<DragItem> items,
            DropAction action,
            Func<AppState, AppState>? stateTransform = null,
            Func<AppState, AppState>? undoTransform = null)
        {
            _targetPanelId = targetPanelId ?? throw new ArgumentNullException(nameof(targetPanelId));
            _payloadType = payloadType;
            _items = items ?? throw new ArgumentNullException(nameof(items));
            _action = action;
            _stateTransform = stateTransform;
            _undoTransform = undoTransform;
        }

        /// <summary>
        /// Creates a command for dropping a profile onto a panel (e.g., synthesis panel).
        /// </summary>
        public static DropItemCommand ForProfileDrop(
            AppState currentState,
            string targetPanelId,
            string profileId,
            string? profileName)
        {
            var items = new List<DragItem>
            {
                new DragItem
                {
                    Id = profileId,
                    DisplayName = profileName ?? profileId,
                    Metadata = new Dictionary<string, object> { ["type"] = "profile" }
                }
            };

            var previousProfileId = currentState.Profile.SelectedProfileId;
            var previousProfileName = currentState.Profile.SelectedProfileName;

            return new DropItemCommand(
                targetPanelId,
                DragPayloadType.Profile,
                items,
                DropAction.Select,
                // Execute: select the dropped profile
                state => state with
                {
                    Profile = state.Profile with
                    {
                        SelectedProfileId = profileId,
                        SelectedProfileName = profileName
                    }
                },
                // Undo: restore previous profile selection
                state => state with
                {
                    Profile = state.Profile with
                    {
                        SelectedProfileId = previousProfileId,
                        SelectedProfileName = previousProfileName
                    }
                });
        }

        /// <summary>
        /// Creates a command for dropping an asset onto a panel.
        /// </summary>
        public static DropItemCommand ForAssetDrop(
            AppState currentState,
            string targetPanelId,
            string assetId,
            string? assetName,
            string? assetType)
        {
            var items = new List<DragItem>
            {
                new DragItem
                {
                    Id = assetId,
                    DisplayName = assetName ?? assetId,
                    Metadata = new Dictionary<string, object> { ["type"] = assetType ?? "asset" }
                }
            };

            var previousAssetId = currentState.Assets.SelectedAssetId;
            var previousAssetName = currentState.Assets.SelectedAssetName;
            var previousAssetType = currentState.Assets.SelectedAssetType;

            return new DropItemCommand(
                targetPanelId,
                DragPayloadType.Asset,
                items,
                DropAction.Insert,
                // Execute: select the dropped asset
                state => state with
                {
                    Assets = state.Assets with
                    {
                        SelectedAssetId = assetId,
                        SelectedAssetName = assetName,
                        SelectedAssetType = assetType
                    }
                },
                // Undo: restore previous asset selection
                state => state with
                {
                    Assets = state.Assets with
                    {
                        SelectedAssetId = previousAssetId,
                        SelectedAssetName = previousAssetName,
                        SelectedAssetType = previousAssetType
                    }
                });
        }

        /// <summary>
        /// Creates a command for a generic drop action without state changes.
        /// </summary>
        public static DropItemCommand ForGenericDrop(
            string targetPanelId,
            DragPayload payload,
            DropAction action)
        {
            return new DropItemCommand(
                targetPanelId,
                payload.PayloadType,
                payload.Items,
                action);
        }

        /// <inheritdoc />
        protected override AppState ExecuteCore(AppState state)
        {
            return _stateTransform?.Invoke(state) ?? state;
        }

        /// <inheritdoc />
        protected override AppState UndoCore(AppState state)
        {
            return _undoTransform?.Invoke(state) ?? state;
        }
    }

    /// <summary>
    /// Represents the action performed during a drop.
    /// </summary>
    public enum DropAction
    {
        /// <summary>No action taken.</summary>
        None,
        
        /// <summary>Item was selected.</summary>
        Select,
        
        /// <summary>Item was inserted/added.</summary>
        Insert,
        
        /// <summary>Item was copied.</summary>
        Copy,
        
        /// <summary>Item was moved.</summary>
        Move,
        
        /// <summary>Item was linked/referenced.</summary>
        Link,
        
        /// <summary>Item was imported from external source.</summary>
        Import
    }
}
