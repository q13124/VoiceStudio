namespace VoiceStudio.Core.State.Commands
{
  /// <summary>
  /// Command to select an engine in the application state.
  /// </summary>
  public sealed class SelectEngineCommand : UndoableCommandBase
  {
    private readonly string? _engineId;
    private readonly string? _engineName;

    /// <inheritdoc />
    public override string Name => "Select Engine";

    /// <summary>
    /// Creates a command to select an engine.
    /// </summary>
    /// <param name="engineId">The engine ID to select.</param>
    /// <param name="engineName">The engine name (for display).</param>
    public SelectEngineCommand(string? engineId, string? engineName = null)
    {
      _engineId = engineId;
      _engineName = engineName;
    }

    /// <inheritdoc />
    protected override AppState ExecuteCore(AppState state)
    {
      return state with
      {
        Engines = state.Engines with
        {
          ActiveEngineId = _engineId,
          ActiveEngineName = _engineName
        }
      };
    }
  }

  /// <summary>
  /// Command to update the current project state.
  /// </summary>
  public sealed class UpdateProjectCommand : UndoableCommandBase
  {
    private readonly string? _projectId;
    private readonly string? _projectName;
    private readonly bool? _isDirty;

    /// <inheritdoc />
    public override string Name => "Update Project";

    /// <summary>
    /// Creates a command to update project state.
    /// </summary>
    public UpdateProjectCommand(string? projectId = null, string? projectName = null, bool? isDirty = null)
    {
      _projectId = projectId;
      _projectName = projectName;
      _isDirty = isDirty;
    }

    /// <inheritdoc />
    protected override AppState ExecuteCore(AppState state)
    {
      var project = state.Project;
      
      if (_projectId != null)
        project = project with { CurrentProjectId = _projectId };
      if (_projectName != null)
        project = project with { CurrentProjectName = _projectName };
      if (_isDirty.HasValue)
        project = project with { IsDirty = _isDirty.Value };

      return state with { Project = project };
    }
  }

  /// <summary>
  /// Command to update UI state (active panel, loading, etc.).
  /// </summary>
  public sealed class UpdateUIStateCommand : IStateCommand
  {
    private readonly string? _activePanelId;
    private readonly string? _activeModalId;
    private readonly bool? _isLoading;
    private readonly string? _loadingMessage;

    /// <inheritdoc />
    public string Name => "Update UI State";

    /// <summary>
    /// Creates a command to update UI state.
    /// </summary>
    public UpdateUIStateCommand(
      string? activePanelId = null,
      string? activeModalId = null,
      bool? isLoading = null,
      string? loadingMessage = null)
    {
      _activePanelId = activePanelId;
      _activeModalId = activeModalId;
      _isLoading = isLoading;
      _loadingMessage = loadingMessage;
    }

    /// <inheritdoc />
    public AppState Execute(AppState state)
    {
      var ui = state.UI;
      
      if (_activePanelId != null)
        ui = ui with { ActivePanelId = _activePanelId };
      if (_activeModalId != null)
        ui = ui with { ActiveModalId = _activeModalId };
      if (_isLoading.HasValue)
        ui = ui with { IsLoading = _isLoading.Value };
      if (_loadingMessage != null)
        ui = ui with { LoadingMessage = _loadingMessage };

      return state with { UI = ui };
    }
  }

  /// <summary>
  /// Command to update job queue state.
  /// </summary>
  public sealed class UpdateJobStateCommand : IStateCommand
  {
    private readonly string? _currentJobId;
    private readonly string? _currentJobDescription;
    private readonly double? _progress;
    private readonly int? _pendingCount;
    private readonly int? _runningCount;

    /// <inheritdoc />
    public string Name => "Update Job State";

    /// <summary>
    /// Creates a command to update job state.
    /// </summary>
    public UpdateJobStateCommand(
      string? currentJobId = null,
      string? currentJobDescription = null,
      double? progress = null,
      int? pendingCount = null,
      int? runningCount = null)
    {
      _currentJobId = currentJobId;
      _currentJobDescription = currentJobDescription;
      _progress = progress;
      _pendingCount = pendingCount;
      _runningCount = runningCount;
    }

    /// <inheritdoc />
    public AppState Execute(AppState state)
    {
      var jobs = state.Jobs;
      
      if (_currentJobId != null)
        jobs = jobs with { CurrentJobId = _currentJobId };
      if (_currentJobDescription != null)
        jobs = jobs with { CurrentJobDescription = _currentJobDescription };
      if (_progress.HasValue)
        jobs = jobs with { CurrentJobProgress = _progress.Value };
      if (_pendingCount.HasValue)
        jobs = jobs with { PendingCount = _pendingCount.Value };
      if (_runningCount.HasValue)
        jobs = jobs with { RunningCount = _runningCount.Value };

      return state with { Jobs = jobs };
    }
  }
}
