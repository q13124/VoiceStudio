namespace VoiceStudio.Core.State.Commands
{
    /// <summary>
    /// Command to switch the active workspace in the application state.
    /// </summary>
    public sealed class SwitchWorkspaceCommand : UndoableCommandBase
    {
        private readonly string? _workspaceId;
        private readonly string? _workspaceName;
        private readonly string? _previousWorkspaceId;
        private readonly string? _previousWorkspaceName;

        /// <inheritdoc />
        public override string Name => "Switch Workspace";

        /// <summary>
        /// Creates a command to switch to a workspace.
        /// </summary>
        /// <param name="workspaceId">The workspace ID to switch to.</param>
        /// <param name="workspaceName">The workspace name (for display).</param>
        public SwitchWorkspaceCommand(string? workspaceId, string? workspaceName = null)
        {
            _workspaceId = workspaceId;
            _workspaceName = workspaceName;
        }

        /// <summary>
        /// Creates a command to switch workspace, capturing the previous state.
        /// </summary>
        internal SwitchWorkspaceCommand(
            string? workspaceId, 
            string? workspaceName, 
            string? previousId, 
            string? previousName)
            : this(workspaceId, workspaceName)
        {
            _previousWorkspaceId = previousId;
            _previousWorkspaceName = previousName;
        }

        /// <summary>
        /// Creates a command with captured previous state from the current state.
        /// </summary>
        public static SwitchWorkspaceCommand Create(AppState state, string? workspaceId, string? workspaceName = null)
        {
            return new SwitchWorkspaceCommand(
                workspaceId,
                workspaceName,
                state.Workspace.ActiveWorkspaceId,
                state.Workspace.ActiveWorkspaceName);
        }

        /// <inheritdoc />
        protected override AppState ExecuteCore(AppState state)
        {
            return state with
            {
                Workspace = state.Workspace with
                {
                    ActiveWorkspaceId = _workspaceId,
                    ActiveWorkspaceName = _workspaceName,
                    PreviousWorkspaceId = state.Workspace.ActiveWorkspaceId
                }
            };
        }

        /// <inheritdoc />
        protected override AppState UndoCore(AppState state)
        {
            return state with
            {
                Workspace = state.Workspace with
                {
                    ActiveWorkspaceId = _previousWorkspaceId,
                    ActiveWorkspaceName = _previousWorkspaceName,
                    PreviousWorkspaceId = state.Workspace.ActiveWorkspaceId
                }
            };
        }
    }
}
