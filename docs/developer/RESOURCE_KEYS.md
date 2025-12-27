# Resource Keys Reference

**Date:** 2025-01-28  
**Purpose:** Complete reference for all resource keys used in VoiceStudio Quantum+

---

## 📋 NAMING CONVENTIONS

**Format:** `Category.Item.Description`

**Examples:**

- `Button.Save` - Save button text
- `Error.ProfileNotFound` - Profile not found error message
- `Panel.Profiles.Title` - Profiles panel title
- `Toast.Success.ProfileCreated` - Success toast message

---

## 🔘 BUTTON VERBS

| Key              | Default Value | Usage               |
| ---------------- | ------------- | ------------------- |
| `Button.Save`    | "Save"        | Save button text    |
| `Button.Cancel`  | "Cancel"      | Cancel button text  |
| `Button.Delete`  | "Delete"      | Delete button text  |
| `Button.Create`  | "Create"      | Create button text  |
| `Button.Edit`    | "Edit"        | Edit button text    |
| `Button.Export`  | "Export"      | Export button text  |
| `Button.Import`  | "Import"      | Import button text  |
| `Button.Apply`   | "Apply"       | Apply button text   |
| `Button.Close`   | "Close"       | Close button text   |
| `Button.Refresh` | "Refresh"     | Refresh button text |
| `Button.Retry`   | "Retry"       | Retry button text   |

---

## 📑 PANEL TITLES

| Key                                  | Default Value       | Usage                                |
| ------------------------------------ | ------------------- | ------------------------------------ |
| `Panel.Profiles.Title`               | "Voice Profiles"    | Profiles panel title                 |
| `Panel.Profiles.DisplayName`         | "Voice Profiles"    | Profiles panel display name          |
| `Panel.Timeline.Title`               | "Timeline"          | Timeline panel title                 |
| `Panel.Timeline.DisplayName`         | "Timeline"          | Timeline panel display name          |
| `Panel.QualityControl.Title`         | "Quality Control"   | Quality Control panel title          |
| `Panel.QualityControl.DisplayName`   | "Quality Control"   | Quality Control panel display name   |
| `Panel.QualityDashboard.Title`       | "Quality Dashboard" | Quality Dashboard panel title        |
| `Panel.QualityDashboard.DisplayName` | "Quality Dashboard" | Quality Dashboard panel display name |
| `Panel.VoiceSynthesis.DisplayName`   | "Voice Synthesis"   | Voice Synthesis panel display name   |
| `Panel.EffectsMixer.DisplayName`     | "Effects & Mixer"   | Effects & Mixer panel display name   |

---

## ❌ ERROR MESSAGES

| Key                           | Default Value                                                                   | Usage                        |
| ----------------------------- | ------------------------------------------------------------------------------- | ---------------------------- |
| `Error.ProfileNotFound`       | "Profile not found. Please check the profile ID and try again."                 | Profile not found error      |
| `Error.ProjectNotFound`       | "Project not found. Please check the project ID and try again."                 | Project not found error      |
| `Error.BackendUnavailable`    | "Unable to connect to the backend. Please check your connection and try again." | Backend connection error     |
| `Error.BackendTimeout`        | "The request timed out. Please try again."                                      | Request timeout error        |
| `Error.ValidationFailed`      | "Validation failed. Please check your input and try again."                     | Validation error             |
| `Error.LoadFailed`            | "Failed to load data. Please try again."                                        | Load operation error         |
| `Error.SaveFailed`            | "Failed to save. Please try again."                                             | Save operation error         |
| `Error.DeleteFailed`          | "Failed to delete. Please try again."                                           | Delete operation error       |
| `Error.CreateProjectFailed`   | "Failed to create project"                                                      | Project creation error       |
| `Error.DeleteProjectFailed`   | "Failed to delete project"                                                      | Project deletion error       |
| `Error.LoadProfilesFailed`    | "Failed to load profiles"                                                       | Profile loading error        |
| `Error.SynthesizeFailed`      | "Failed to synthesize voice"                                                    | Voice synthesis error        |
| `Error.PlayAudioFailed`       | "Failed to play audio"                                                          | Audio playback error         |
| `Error.StopPlaybackFailed`    | "Failed to stop playback"                                                       | Stop playback error          |
| `Error.PausePlaybackFailed`   | "Failed to pause playback"                                                      | Pause playback error         |
| `Error.ResumePlaybackFailed`  | "Failed to resume playback"                                                     | Resume playback error        |
| `Error.LoadTracksFailed`      | "Failed to load tracks"                                                         | Track loading error          |
| `Error.CreateTrackFailed`     | "Failed to create track"                                                        | Track creation error         |
| `Error.AddClipFailed`         | "Failed to add clip to track"                                                   | Clip addition error          |
| `Error.DeleteClipsFailed`     | "Failed to delete clips"                                                        | Clip deletion error          |
| `Error.PreviewEnhancedFailed` | "Failed to preview enhanced audio"                                              | Enhanced audio preview error |
| `Error.ApplyEnhancedFailed`   | "Failed to apply enhanced audio"                                                | Enhanced audio apply error   |

---

## ✅ SUCCESS MESSAGES

| Key                      | Default Value                  | Usage                    |
| ------------------------ | ------------------------------ | ------------------------ |
| `Success.ProfileCreated` | "Profile created successfully" | Profile creation success |
| `Success.ProfileUpdated` | "Profile updated successfully" | Profile update success   |
| `Success.ProfileDeleted` | "Profile deleted successfully" | Profile deletion success |
| `Success.ProjectCreated` | "Project created successfully" | Project creation success |
| `Success.Saved`          | "Saved successfully"           | Generic save success     |

---

## 🔔 TOAST MESSAGES

| Key                            | Default Value                                       | Usage                              |
| ------------------------------ | --------------------------------------------------- | ---------------------------------- |
| `Toast.Success.ProfileCreated` | "Profile created successfully"                      | Success toast for profile creation |
| `Toast.Error.LoadFailed`       | "Failed to load data. Please try again."            | Error toast for load failure       |
| `Toast.Warning.UnsavedChanges` | "You have unsaved changes. Save before continuing?" | Warning toast for unsaved changes  |
| `Toast.Info.Processing`        | "Processing... This may take a few moments."        | Info toast for processing          |

---

## 📊 STATUS MESSAGES

| Key                         | Default Value                                            | Usage                            |
| --------------------------- | -------------------------------------------------------- | -------------------------------- |
| `Status.Loading`            | "Loading..."                                             | Loading status                   |
| `Status.Saving`             | "Saving..."                                              | Saving status                    |
| `Status.Processing`         | "Processing..."                                          | Processing status                |
| `Status.Complete`           | "Complete"                                               | Completion status                |
| `Status.Synthesizing`       | "Synthesizing voice..."                                  | Voice synthesis in progress      |
| `Status.SynthesisComplete`  | "Synthesis complete! Duration: {0:F2}s, Quality: {1:P0}" | Synthesis completion (formatted) |
| `Status.SynthesisCancelled` | "Synthesis cancelled"                                    | Synthesis cancelled              |
| `Status.LoadingAudio`       | "Loading audio for playback..."                          | Loading audio for playback       |
| `Status.PlayingAudio`       | "Playing audio..."                                       | Audio playback in progress       |
| `Status.PlaybackCancelled`  | "Playback cancelled"                                     | Playback cancelled               |
| `Status.PlaybackStopped`    | "Playback stopped"                                       | Playback stopped                 |
| `Status.Refreshed`          | "Refreshed"                                              | Refresh complete                 |

---

## 📭 EMPTY STATES

| Key                             | Default Value                                     | Usage                               |
| ------------------------------- | ------------------------------------------------- | ----------------------------------- |
| `EmptyState.NoProfiles.Title`   | "No Profiles"                                     | Empty state title for no profiles   |
| `EmptyState.NoProfiles.Message` | "Create your first voice profile to get started." | Empty state message for no profiles |
| `EmptyState.NoProjects.Title`   | "No Projects"                                     | Empty state title for no projects   |
| `EmptyState.NoProjects.Message` | "Create your first project to get started."       | Empty state message for no projects |

---

## 💡 TOOLTIPS

| Key               | Default Value           | Usage                  |
| ----------------- | ----------------------- | ---------------------- |
| `Tooltip.Save`    | "Save changes (Ctrl+S)" | Save button tooltip    |
| `Tooltip.Delete`  | "Delete selected item"  | Delete button tooltip  |
| `Tooltip.Refresh` | "Refresh data (F5)"     | Refresh button tooltip |

---

## 📝 USAGE EXAMPLES

### In ViewModels

```csharp
using VoiceStudio.App.Utilities;

// Basic usage
Title = ResourceHelper.GetString("Panel.Profiles.Title", "Voice Profiles");

// With formatting
var message = ResourceHelper.FormatString("Success.ProfileCreated", profileName);

// Error messages
ErrorMessage = ResourceHelper.GetString("Error.ProfileNotFound");
```

### In XAML

```xml
<TextBlock Text="{x:Bind ViewModel.Title}" />
<!-- Title property uses ResourceHelper.GetString() -->
```

---

## 🔄 ADDING NEW RESOURCE KEYS

1. **Add to Resources.resw:**

   ```xml
   <data name="Button.NewAction" xml:space="preserve">
     <value>New Action</value>
   </data>
   ```

2. **Add to en-US/Resources.resw:**

   ```xml
   <data name="Button.NewAction" xml:space="preserve">
     <value>New Action</value>
   </data>
   ```

3. **Update this document** with the new key

4. **Use in code:**

   ```csharp
   var text = ResourceHelper.GetString("Button.NewAction", "New Action");
   ```

---

## 📋 CATEGORIES

- **Button.** - Button text (verbs)
- **Panel.** - Panel titles and display names
- **Error.** - Error messages
- **Success.** - Success messages
- **Toast.** - Toast notification messages
- **Status.** - Status messages
- **EmptyState.** - Empty state titles and messages
- **Tooltip.** - Tooltip text
- **Profile.** - Profile-related messages
- **Project.** - Project-related messages
- **Timeline.** - Timeline-related messages
- **VoiceSynthesis.** - Voice synthesis messages
- **EffectsMixer.** - Effects mixer messages
- **QualityDashboard.** - Quality dashboard messages

---

## 📝 PROFILE MESSAGES

| Key                                  | Default Value                                                                  | Usage                            |
| ------------------------------------ | ------------------------------------------------------------------------------ | -------------------------------- |
| `Profile.Unnamed`                    | "Unnamed Profile"                                                              | Default profile name             |
| `Profile.LoadFailed`                 | "Failed to load profiles"                                                      | Profile loading error            |
| `Profile.CreateFailed`               | "Failed to create profile"                                                     | Profile creation error           |
| `Profile.DeleteFailed`               | "Failed to delete profile"                                                     | Profile deletion error           |
| `Profile.PreviewFailed`              | "Failed to preview profile"                                                    | Profile preview error            |
| `Profile.StopPreviewFailed`          | "Failed to stop preview"                                                       | Stop preview error               |
| `Profile.EnhancementFailed`          | "Failed to enhance reference audio"                                            | Enhancement error                |
| `Profile.EnhancementComplete`        | "Enhancement complete. Quality improved by {0:P0}"                             | Enhancement success (formatted)  |
| `Profile.EnhancementApplied`         | "Enhanced reference audio has been applied to the profile"                     | Enhancement applied              |
| `Profile.PreviewEnhancedFailed`      | "Failed to preview enhanced audio"                                             | Enhanced preview error           |
| `Profile.ApplyEnhancedFailed`        | "Failed to apply enhanced audio"                                               | Apply enhanced error             |
| `Profile.QualityDegradationAlert`    | "Quality Degradation Alert"                                                    | Quality degradation alert title  |
| `Profile.QualityDegradationCritical` | "Critical quality degradation detected: {0} critical alert(s), {1} warning(s)" | Critical degradation (formatted) |
| `Profile.QualityDegradationWarning`  | "Quality degradation detected: {0} warning(s)"                                 | Warning degradation (formatted)  |
| `Profile.BatchDeleteComplete`        | "Deleted {0} profile(s)"                                                       | Batch delete success (formatted) |
| `Profile.BatchDeletePartial`         | "Some profiles could not be deleted ({0}/{1} succeeded)"                       | Partial batch delete (formatted) |
| `Profile.BatchDeleteFailed`          | "Failed to delete profiles"                                                    | Batch delete error               |

---

## 📁 PROJECT MESSAGES

| Key                            | Default Value                                                       | Usage                              |
| ------------------------------ | ------------------------------------------------------------------- | ---------------------------------- |
| `Project.Unnamed`              | "Unnamed Project"                                                   | Default project name               |
| `Project.LoadFailed`           | "Failed to load projects"                                           | Project loading error              |
| `Project.CreateFailed`         | "Failed to create project"                                          | Project creation error             |
| `Project.DeleteFailed`         | "Failed to delete project"                                          | Project deletion error             |
| `Project.TrackLoadFailed`      | "Failed to load tracks"                                             | Track loading error                |
| `Project.TrackCreateFailed`    | "Failed to create track"                                            | Track creation error               |
| `Project.AudioLoadFailed`      | "Failed to load project audio files"                                | Audio file loading error           |
| `Project.AudioPlayFailed`      | "Failed to play audio file"                                         | Audio playback error               |
| `Project.ClipAddFailed`        | "Failed to add clip to track"                                       | Clip addition error                |
| `Project.ClipDeleteFailed`     | "Failed to delete clips"                                            | Clip deletion error                |
| `Project.ClipSaveWarning`      | "Warning: Failed to save clip to backend: {0}. Clip added locally." | Clip save warning (formatted)      |
| `Project.AudioSaveWarning`     | "Warning: Failed to save audio to project: {0}"                     | Audio save warning (formatted)     |
| `Project.SynthesisSaveWarning` | "Synthesis succeeded but failed to save to project: {0}"            | Synthesis save warning (formatted) |
| `Project.ClipsDeleted`         | "Deleted {0} clip(s)"                                               | Clips deleted (formatted)          |
| `Project.ClipsDeletePartial`   | "Some clips could not be deleted ({0}/{1} succeeded)"               | Partial clip deletion (formatted)  |

---

## ⏱️ TIMELINE MESSAGES

| Key                             | Default Value                | Usage                     |
| ------------------------------- | ---------------------------- | ------------------------- |
| `Timeline.PlaybackFailed`       | "Failed to play audio"       | Playback error            |
| `Timeline.PlaybackStopFailed`   | "Failed to stop playback"    | Stop playback error       |
| `Timeline.PlaybackPauseFailed`  | "Failed to pause playback"   | Pause playback error      |
| `Timeline.PlaybackResumeFailed` | "Failed to resume playback"  | Resume playback error     |
| `Timeline.SynthesisComplete`    | "Voice synthesis completed"  | Synthesis complete        |
| `Timeline.SynthesisFailed`      | "Failed to synthesize voice" | Synthesis error           |
| `Timeline.TrackCreated`         | "Track '{0}' created"        | Track created (formatted) |
| `Timeline.ClipAdded`            | "Clip '{0}' added to track"  | Clip added (formatted)    |

---

## 🎙️ VOICE SYNTHESIS MESSAGES

| Key                                           | Default Value                                                | Usage                                      |
| --------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------ |
| `VoiceSynthesis.ProfilesLoaded`               | "Profiles Loaded"                                            | Profiles loaded title                      |
| `VoiceSynthesis.ProfilesLoadedCount`          | "Loaded {0} voice profile(s)"                                | Profiles loaded count (formatted)          |
| `VoiceSynthesis.ProfilesLoadFailed`           | "Failed to Load Profiles"                                    | Profiles load failed                       |
| `VoiceSynthesis.SynthesisComplete`            | "Synthesis Complete"                                         | Synthesis complete title                   |
| `VoiceSynthesis.SynthesisCompleteDetail`      | "Voice synthesis complete! Duration: {0:F2}s, Quality: {1}"  | Synthesis complete detail (formatted)      |
| `VoiceSynthesis.SynthesisFailed`              | "Synthesis Failed"                                           | Synthesis failed title                     |
| `VoiceSynthesis.SynthesisFailedDetail`        | "Synthesis failed: {0}"                                      | Synthesis failed detail (formatted)        |
| `VoiceSynthesis.SynthesisCancelled`           | "Synthesis cancelled"                                        | Synthesis cancelled                        |
| `VoiceSynthesis.PlaybackLoading`              | "Loading audio for playback..."                              | Playback loading                           |
| `VoiceSynthesis.PlaybackPlaying`              | "Playing audio..."                                           | Playback playing                           |
| `VoiceSynthesis.PlaybackCancelled`            | "Playback cancelled"                                         | Playback cancelled                         |
| `VoiceSynthesis.PlaybackStopped`              | "Playback stopped"                                           | Playback stopped                           |
| `VoiceSynthesis.PlaybackFailed`               | "Failed to play audio"                                       | Playback error                             |
| `VoiceSynthesis.StopPlaybackFailed`           | "Failed to stop playback"                                    | Stop playback error                        |
| `VoiceSynthesis.TextAnalysisFailed`           | "Text Analysis Failed"                                       | Text analysis failed                       |
| `VoiceSynthesis.QualityRecommendationFailed`  | "Quality Recommendation Failed"                              | Quality recommendation failed              |
| `VoiceSynthesis.RecommendationsApplied`       | "Recommendations Applied"                                    | Recommendations applied title              |
| `VoiceSynthesis.RecommendationsAppliedDetail` | "Engine: {0}, Enhance Quality: {1}"                          | Recommendations applied detail (formatted) |
| `VoiceSynthesis.ApplyRecommendationsFailed`   | "Failed to Apply Recommendations"                            | Apply recommendations failed               |
| `VoiceSynthesis.EnsembleStarted`              | "Ensemble Started"                                           | Ensemble started title                     |
| `VoiceSynthesis.EnsembleStartedDetail`        | "Multi-engine ensemble synthesis started with {0} engine(s)" | Ensemble started detail (formatted)        |
| `VoiceSynthesis.EnsembleFailed`               | "Ensemble Failed"                                            | Ensemble failed                            |
| `VoiceSynthesis.EnsembleComplete`             | "Ensemble Complete"                                          | Ensemble complete title                    |
| `VoiceSynthesis.EnsembleCompleteDetail`       | "Best engine selected. Quality: {0:P0}"                      | Ensemble complete detail (formatted)       |
| `VoiceSynthesis.CheckStatusFailed`            | "Failed to Check Status"                                     | Check status failed                        |
| `VoiceSynthesis.PipelinesLoadFailed`          | "Failed to Load Pipelines"                                   | Pipelines load failed                      |
| `VoiceSynthesis.PipelinePreview`              | "Pipeline Preview"                                           | Pipeline preview title                     |
| `VoiceSynthesis.PreviewGenerated`             | "Preview generated successfully"                             | Preview generated                          |
| `VoiceSynthesis.PreviewFailed`                | "Preview Failed"                                             | Preview failed                             |
| `VoiceSynthesis.ComparisonFailed`             | "Comparison Failed"                                          | Comparison failed                          |
| `VoiceSynthesis.PipelineComparison`           | "Pipeline Comparison"                                        | Pipeline comparison title                  |
| `VoiceSynthesis.ComparisonCompleted`          | "Comparison completed"                                       | Comparison completed                       |
| `VoiceSynthesis.AudioPlayback`                | "Audio Playback"                                             | Audio playback title                       |

---

## 🎚️ EFFECTS MIXER MESSAGES

| Key                                     | Default Value                              | Usage                                   |
| --------------------------------------- | ------------------------------------------ | --------------------------------------- |
| `EffectsMixer.EffectChainsLoaded`       | "Effect Chains Loaded"                     | Effect chains loaded title              |
| `EffectsMixer.EffectChainsLoadedCount`  | "Loaded {0} effect chain(s)"               | Effect chains loaded count (formatted)  |
| `EffectsMixer.EffectChainsLoadFailed`   | "Failed to Load Effect Chains"             | Effect chains load failed               |
| `EffectsMixer.EffectPresetsLoaded`      | "Effect Presets Loaded"                    | Effect presets loaded title             |
| `EffectsMixer.EffectPresetsLoadedCount` | "Loaded {0} preset(s)"                     | Effect presets loaded count (formatted) |
| `EffectsMixer.EffectPresetsLoadFailed`  | "Failed to Load Effect Presets"            | Effect presets load failed              |
| `EffectsMixer.EffectChainCreated`       | "Effect Chain Created"                     | Effect chain created title              |
| `EffectsMixer.EffectChainCreatedDetail` | "Effect chain '{0}' created successfully"  | Effect chain created detail (formatted) |
| `EffectsMixer.EffectChainCreateFailed`  | "Failed to Create Effect Chain"            | Effect chain create failed              |
| `EffectsMixer.EffectChainDeleted`       | "Effect Chain Deleted"                     | Effect chain deleted title              |
| `EffectsMixer.EffectChainDeletedDetail` | "Effect chain '{0}' deleted successfully"  | Effect chain deleted detail (formatted) |
| `EffectsMixer.EffectChainDeleteFailed`  | "Failed to Delete Effect Chain"            | Effect chain delete failed              |
| `EffectsMixer.EffectChainApplied`       | "Effect Chain Applied"                     | Effect chain applied title              |
| `EffectsMixer.EffectChainAppliedDetail` | "Effect chain '{0}' applied successfully"  | Effect chain applied detail (formatted) |
| `EffectsMixer.EffectChainApplyFailed`   | "Failed to Apply Effect Chain"             | Effect chain apply failed               |
| `EffectsMixer.EffectAdded`              | "Effect Added"                             | Effect added title                      |
| `EffectsMixer.EffectAddedDetail`        | "Effect '{0}' added to chain successfully" | Effect added detail (formatted)         |
| `EffectsMixer.EffectAddFailed`          | "Failed to Add Effect"                     | Effect add failed                       |
| `EffectsMixer.EffectRemoved`            | "Effect Removed"                           | Effect removed title                    |
| `EffectsMixer.EffectRemovedDetail`      | "Effect removed from chain successfully"   | Effect removed detail                   |
| `EffectsMixer.EffectRemoveFailed`       | "Failed to Remove Effect"                  | Effect remove failed                    |
| `EffectsMixer.EffectChainSaved`         | "Effect Chain Saved"                       | Effect chain saved title                |
| `EffectsMixer.EffectChainSavedDetail`   | "Effect chain '{0}' saved successfully"    | Effect chain saved detail (formatted)   |
| `EffectsMixer.EffectChainSaveFailed`    | "Failed to Save Effect Chain"              | Effect chain save failed                |
| `EffectsMixer.MixerStateLoadFailed`     | "Failed to load mixer state"               | Mixer state load failed                 |
| `EffectsMixer.MixerStateSaveFailed`     | "Failed to save mixer state"               | Mixer state save failed                 |
| `EffectsMixer.MixerStateResetFailed`    | "Failed to reset mixer state"              | Mixer state reset failed                |
| `EffectsMixer.MixerPresetsLoadFailed`   | "Failed to load mixer presets"             | Mixer presets load failed               |
| `EffectsMixer.MixerPresetCreateFailed`  | "Failed to create mixer preset"            | Mixer preset create failed              |
| `EffectsMixer.MixerPresetApplyFailed`   | "Failed to apply mixer preset"             | Mixer preset apply failed               |
| `EffectsMixer.SendCreateFailed`         | "Failed to create send"                    | Send create failed                      |
| `EffectsMixer.ReturnCreateFailed`       | "Failed to create return"                  | Return create failed                    |
| `EffectsMixer.SubGroupCreateFailed`     | "Failed to create sub-group"               | Sub-group create failed                 |
| `EffectsMixer.SubGroupDeleteFailed`     | "Failed to delete sub-group"               | Sub-group delete failed                 |
| `EffectsMixer.SubGroupUpdateFailed`     | "Failed to update sub-group"               | Sub-group update failed                 |
| `EffectsMixer.SendUpdateFailed`         | "Failed to update send"                    | Send update failed                      |
| `EffectsMixer.ReturnUpdateFailed`       | "Failed to update return"                  | Return update failed                    |
| `EffectsMixer.SendDeleteFailed`         | "Failed to delete send"                    | Send delete failed                      |
| `EffectsMixer.ReturnDeleteFailed`       | "Failed to delete return"                  | Return delete failed                    |
| `EffectsMixer.UnknownChain`             | "Unknown Chain"                            | Unknown chain name                      |

---

## 📊 QUALITY DASHBOARD MESSAGES

| Key                                         | Default Value                                                                                                              | Usage                                   |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| `QualityDashboard.OverviewLoaded`           | "Quality overview loaded successfully."                                                                                    | Overview loaded                         |
| `QualityDashboard.OverviewLoadFailed`       | "Failed to load quality overview"                                                                                          | Overview load failed                    |
| `QualityDashboard.OverviewLoadFailedDetail` | "Failed to load quality overview: {0}"                                                                                     | Overview load failed detail (formatted) |
| `QualityDashboard.PresetsLoaded`            | "Loaded {0} quality presets."                                                                                              | Presets loaded (formatted)              |
| `QualityDashboard.PresetsLoadFailed`        | "Failed to load quality presets"                                                                                           | Presets load failed                     |
| `QualityDashboard.PresetsLoadFailedDetail`  | "Failed to load quality presets: {0}"                                                                                      | Presets load failed detail (formatted)  |
| `QualityDashboard.TrendsLoaded`             | "Loaded {0} quality trend data points."                                                                                    | Trends loaded (formatted)               |
| `QualityDashboard.TrendsLoadFailed`         | "Failed to load quality trends"                                                                                            | Trends load failed                      |
| `QualityDashboard.TrendsLoadFailedDetail`   | "Failed to load quality trends: {0}"                                                                                       | Trends load failed detail (formatted)   |
| `QualityDashboard.RefreshComplete`          | "Quality dashboard refreshed successfully."                                                                                | Refresh complete                        |
| `QualityDashboard.RefreshFailed`            | "Failed to refresh"                                                                                                        | Refresh failed                          |
| `QualityDashboard.RefreshFailedDetail`      | "Failed to refresh: {0}"                                                                                                   | Refresh failed detail (formatted)       |
| `QualityDashboard.StatusMessage`            | "Quality dashboard requires database integration for full functionality. Basic quality metrics and presets are available." | Status message                          |
| `QualityDashboard.StatusMessageBasic`       | "Full quality dashboard requires database integration. Showing available quality metrics and presets."                     | Basic status message                    |
| `QualityDashboard.StatusMessageSuccess`     | "Quality dashboard data loaded successfully."                                                                              | Success status message                  |

---

## 🔔 TOAST TITLES

| Key                               | Default Value           | Usage                             |
| --------------------------------- | ----------------------- | --------------------------------- |
| `Toast.Title.ProfileCreated`      | "Profile Created"       | Profile created toast title       |
| `Toast.Title.ProfileDeleted`      | "Profile Deleted"       | Profile deleted toast title       |
| `Toast.Title.ProjectCreated`      | "Project Created"       | Project created toast title       |
| `Toast.Title.ProjectDeleted`      | "Project Deleted"       | Project deleted toast title       |
| `Toast.Title.TrackCreated`        | "Track Created"         | Track created toast title         |
| `Toast.Title.EnhancementComplete` | "Enhancement Complete"  | Enhancement complete toast title  |
| `Toast.Title.EnhancementApplied`  | "Enhancement Applied"   | Enhancement applied toast title   |
| `Toast.Title.BatchDeleteComplete` | "Batch Delete Complete" | Batch delete complete toast title |
| `Toast.Title.PartialDelete`       | "Partial Delete"        | Partial delete toast title        |
| `Toast.Title.DeleteFailed`        | "Delete Failed"         | Delete failed toast title         |
| `Toast.Title.CreateFailed`        | "Create Failed"         | Create failed toast title         |
| `Toast.Title.LoadFailed`          | "Load Failed"           | Load failed toast title           |
| `Toast.Title.SaveFailed`          | "Save Failed"           | Save failed toast title           |
| `Toast.Title.ClipsDeleted`        | "Clips Deleted"         | Clips deleted toast title         |
| `Toast.Title.DeleteClipsFailed`   | "Delete Clips Failed"   | Delete clips failed toast title   |
| `Toast.Title.CreateTrackFailed`   | "Create Track Failed"   | Create track failed toast title   |

---

**Last Updated:** 2025-01-28  
**Total Keys:** 200+ (expanded during ViewModel migration)
