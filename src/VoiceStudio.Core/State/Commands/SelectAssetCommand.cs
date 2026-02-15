namespace VoiceStudio.Core.State.Commands
{
    /// <summary>
    /// Command to select an asset in the application state.
    /// </summary>
    public sealed class SelectAssetCommand : UndoableCommandBase
    {
        private readonly string? _assetId;
        private readonly string? _assetName;
        private readonly string? _assetType;
        private readonly string? _previousAssetId;
        private readonly string? _previousAssetName;
        private readonly string? _previousAssetType;

        /// <inheritdoc />
        public override string Name => "Select Asset";

        /// <summary>
        /// Creates a command to select an asset.
        /// </summary>
        /// <param name="assetId">The asset ID to select.</param>
        /// <param name="assetName">The asset name (for display).</param>
        /// <param name="assetType">The asset type (e.g., "audio", "video").</param>
        public SelectAssetCommand(string? assetId, string? assetName = null, string? assetType = null)
        {
            _assetId = assetId;
            _assetName = assetName;
            _assetType = assetType;
        }

        /// <summary>
        /// Creates a command to select an asset, capturing the previous state.
        /// </summary>
        internal SelectAssetCommand(
            string? assetId, 
            string? assetName, 
            string? assetType,
            string? previousId, 
            string? previousName,
            string? previousType)
            : this(assetId, assetName, assetType)
        {
            _previousAssetId = previousId;
            _previousAssetName = previousName;
            _previousAssetType = previousType;
        }

        /// <summary>
        /// Creates a command with captured previous state from the current state.
        /// </summary>
        public static SelectAssetCommand Create(AppState state, string? assetId, string? assetName = null, string? assetType = null)
        {
            return new SelectAssetCommand(
                assetId,
                assetName,
                assetType,
                state.Assets.SelectedAssetId,
                state.Assets.SelectedAssetName,
                state.Assets.SelectedAssetType);
        }

        /// <inheritdoc />
        protected override AppState ExecuteCore(AppState state)
        {
            return state with
            {
                Assets = state.Assets with
                {
                    SelectedAssetId = _assetId,
                    SelectedAssetName = _assetName,
                    SelectedAssetType = _assetType
                }
            };
        }

        /// <inheritdoc />
        protected override AppState UndoCore(AppState state)
        {
            return state with
            {
                Assets = state.Assets with
                {
                    SelectedAssetId = _previousAssetId,
                    SelectedAssetName = _previousAssetName,
                    SelectedAssetType = _previousAssetType
                }
            };
        }
    }
}
