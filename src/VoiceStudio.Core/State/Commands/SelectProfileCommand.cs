namespace VoiceStudio.Core.State.Commands
{
  /// <summary>
  /// Command to select a profile in the application state.
  /// </summary>
  public sealed class SelectProfileCommand : UndoableCommandBase
  {
    private readonly string? _profileId;
    private readonly string? _profileName;
    private readonly string? _previousProfileId;
    private readonly string? _previousProfileName;

    /// <inheritdoc />
    public override string Name => "Select Profile";

    /// <summary>
    /// Creates a command to select a profile.
    /// </summary>
    /// <param name="profileId">The profile ID to select.</param>
    /// <param name="profileName">The profile name (for display).</param>
    public SelectProfileCommand(string? profileId, string? profileName = null)
    {
      _profileId = profileId;
      _profileName = profileName;
    }

    /// <summary>
    /// Creates a command to select a profile, capturing the previous state.
    /// </summary>
    internal SelectProfileCommand(string? profileId, string? profileName, string? previousId, string? previousName)
      : this(profileId, profileName)
    {
      _previousProfileId = previousId;
      _previousProfileName = previousName;
    }

    /// <inheritdoc />
    protected override AppState ExecuteCore(AppState state)
    {
      return state with
      {
        Profile = state.Profile with
        {
          SelectedProfileId = _profileId,
          SelectedProfileName = _profileName
        }
      };
    }

    /// <inheritdoc />
    protected override AppState UndoCore(AppState state)
    {
      return state with
      {
        Profile = state.Profile with
        {
          SelectedProfileId = _previousProfileId,
          SelectedProfileName = _previousProfileName
        }
      };
    }
  }
}
