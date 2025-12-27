# Microcopy Guide - VoiceStudio Quantum+

**Last Updated:** 2025-01-28  
**Purpose:** Standardize UI text, button labels, error messages, and toast notifications for consistency and clarity.

---

## Table of Contents

1. [General Principles](#general-principles)
2. [Button Verbs](#button-verbs)
3. [Titles and Headings](#titles-and-headings)
4. [Error Messages](#error-messages)
5. [Toast Notifications](#toast-notifications)
6. [Empty States](#empty-states)
7. [Loading States](#loading-states)
8. [Confirmation Dialogs](#confirmation-dialogs)
9. [Tooltips](#tooltips)
10. [Accessibility Labels](#accessibility-labels)

---

## General Principles

### Tone
- **Professional but approachable**: Use clear, concise language
- **Action-oriented**: Focus on what the user can do
- **Helpful**: Provide context and next steps
- **Consistent**: Use the same terminology throughout

### Voice
- **Active voice**: "Save changes" not "Changes will be saved"
- **Present tense**: "Saving..." not "Will save"
- **User-centric**: "Your profile" not "The profile"

### Length
- **Concise**: Keep messages short and scannable
- **Complete**: Include necessary context
- **No redundancy**: Don't repeat information

---

## Button Verbs

### Primary Actions
Use action verbs that clearly describe what happens:

| Action | Button Text | Context |
|--------|-------------|---------|
| Create new item | "Create" or "New" | Profiles, Projects, Documents |
| Save changes | "Save" | After editing |
| Delete item | "Delete" | With confirmation |
| Apply changes | "Apply" | Settings, filters |
| Confirm action | "Confirm" or "OK" | Dialogs |
| Cancel action | "Cancel" | Dialogs, editing |

### Secondary Actions
- "Edit" - Modify existing item
- "Duplicate" - Create copy
- "Rename" - Change name
- "Reset" - Restore defaults
- "Clear" - Remove all
- "Refresh" - Reload data
- "Export" - Save to file
- "Import" - Load from file

### Destructive Actions
Always use clear, specific language:
- "Delete Profile" (not "Remove" or "Clear")
- "Remove Item" (for less critical removals)
- "Clear All" (for bulk operations)

**Format:** `[Action] [Object]` when space allows, otherwise just `[Action]`

---

## Titles and Headings

### Panel Titles
- Use noun phrases: "Voice Profiles", "Timeline", "Effects Mixer"
- Capitalize all major words
- No trailing punctuation

### Dialog Titles
- Use question format for confirmations: "Delete Profile?"
- Use statement format for information: "Export Complete"
- Keep under 50 characters

### Section Headers
- Use descriptive labels: "Profile Settings", "Audio Settings"
- Match panel terminology
- Use sentence case for secondary headers

---

## Error Messages

### Structure
**Format:** `[What happened] [Why] [What to do]`

### Error Types

#### Validation Errors
- **Format**: "Invalid [field]: [reason]. [Fix suggestion]"
- **Example**: "Invalid email address: Missing @ symbol. Please enter a valid email."

#### Network Errors
- **Format**: "Unable to [action]. [Reason]. [Retry option]"
- **Example**: "Unable to load profiles. Connection timeout. Please check your internet connection and try again."

#### Permission Errors
- **Format**: "Cannot [action]. [Permission needed]. [How to fix]"
- **Example**: "Cannot save file. Write permission denied. Please check file permissions or choose a different location."

#### Not Found Errors
- **Format**: "[Item] not found. [Context]. [Alternative action]"
- **Example**: "Profile not found. It may have been deleted. Create a new profile or refresh the list."

#### Generic Errors
- **Format**: "An error occurred while [action]. [Technical details optional]. Please try again."
- **Example**: "An error occurred while saving your changes. Please try again."

### Error Message Guidelines
- **Be specific**: "Failed to connect to server" not "Error occurred"
- **Provide context**: Include what the user was trying to do
- **Suggest solutions**: Always include next steps when possible
- **Avoid technical jargon**: Use user-friendly language
- **Use positive framing**: "Please check connection" not "Connection failed"

---

## Toast Notifications

### Success Toasts
**Format:** `[Action] completed successfully. [Optional detail]`

**Examples:**
- "Profile saved successfully."
- "Export completed. File saved to Downloads."
- "Changes applied."

**Guidelines:**
- Keep under 60 characters
- Use past tense
- Include result when relevant

### Error Toasts
**Format:** `[Action] failed. [Brief reason]. [Optional action]`

**Examples:**
- "Failed to save profile. Please try again."
- "Export failed. Disk full. Free up space and try again."
- "Connection lost. Reconnecting..."

**Guidelines:**
- Be concise but informative
- Include actionable information
- Don't auto-dismiss (user must dismiss)

### Warning Toasts
**Format:** `[Warning]. [Implication]. [Optional action]`

**Examples:**
- "Unsaved changes detected. Save before closing?"
- "Low disk space. Free up space to continue."
- "Profile in use. Cannot delete while active."

**Guidelines:**
- Alert to potential issues
- Suggest preventive actions
- Auto-dismiss after 5 seconds

### Info Toasts
**Format:** `[Information]. [Optional context]`

**Examples:**
- "Profile updated."
- "3 items selected."
- "Search complete. 12 results found."

**Guidelines:**
- Provide status updates
- Keep very brief
- Auto-dismiss after 5 seconds

### Progress Toasts
**Format:** `[Action] in progress... [Optional detail]`

**Examples:**
- "Exporting audio..."
- "Processing 5 of 10 files..."
- "Saving changes..."

**Guidelines:**
- Use present continuous tense
- Show progress when available
- Don't auto-dismiss

---

## Empty States

### No Results
**Format:** `No [items] found. [Optional suggestion]`

**Examples:**
- "No profiles found. Create your first profile to get started."
- "No search results. Try different keywords."
- "No projects available. Create a new project."

### No Data
**Format:** `[Area] is empty. [Action suggestion]`

**Examples:**
- "Timeline is empty. Add clips to get started."
- "No effects applied. Add effects to enhance your audio."
- "Library is empty. Import audio files to begin."

### Empty State Guidelines
- **Be helpful**: Always suggest next steps
- **Be encouraging**: Use positive language
- **Be specific**: Reference the current context
- **Include action**: Provide a clear call-to-action button when possible

---

## Loading States

### Loading Messages
**Format:** `[Action]...` or `Loading [items]...`

**Examples:**
- "Loading profiles..."
- "Saving changes..."
- "Processing audio..."
- "Searching..."

### Guidelines
- Use present continuous tense
- Be specific about what's loading
- Keep under 30 characters
- Show progress when available: "Processing 3 of 10 files..."

---

## Confirmation Dialogs

### Delete Confirmations
**Format:** `Delete [item]? This action cannot be undone.`

**Examples:**
- "Delete profile 'John Doe'? This action cannot be undone."
- "Delete selected items? This action cannot be undone."

### Unsaved Changes
**Format:** `You have unsaved changes. [Action] anyway?`

**Example:**
- "You have unsaved changes. Close without saving?"

### Destructive Actions
**Format:** `[Action] will [consequence]. Continue?`

**Examples:**
- "Resetting will clear all settings. Continue?"
- "Clearing will remove all items. Continue?"

### Guidelines
- Always explain consequences
- Use question format
- Make "Cancel" the default for destructive actions

---

## Tooltips

### Format
**Short tooltips**: `[Action/Description]`
**Long tooltips**: `[Action/Description]. [Additional context]`

### Examples
- "Save changes" (button)
- "Search profiles" (search box)
- "Delete profile. This action cannot be undone." (delete button)
- "Toggle fullscreen timeline" (menu item)

### Guidelines
- Keep under 80 characters
- Start with action or description
- Add context only when helpful
- Use sentence case

---

## Accessibility Labels

### AutomationProperties.Name
**Format:** `[Element type]: [Purpose/Content]`

**Examples:**
- "Button: Save profile"
- "Search box: Search profiles"
- "List: Profile list, 5 items"
- "Checkbox: Enable auto-save"

### AutomationProperties.HelpText
**Format:** `[What it does]. [How to use it]. [Optional keyboard shortcut]`

**Examples:**
- "Saves the current profile. Click to save or press Ctrl+S."
- "Searches profiles by name. Type to filter results."
- "Deletes the selected profile. Press Delete key or click to remove."

### Guidelines
- Be descriptive but concise
- Include interaction methods
- Mention keyboard shortcuts when available
- Use present tense

---

## Common Patterns

### File Operations
- "Save" / "Save As..." / "Save All"
- "Open" / "Open Recent"
- "Export" / "Import"
- "New" / "Delete" / "Rename"

### Edit Operations
- "Undo" / "Redo"
- "Cut" / "Copy" / "Paste"
- "Select All" / "Clear Selection"
- "Find" / "Replace"

### Navigation
- "Back" / "Forward"
- "Next" / "Previous"
- "Go to" / "Jump to"
- "Close" / "Minimize" / "Maximize"

### Status Messages
- "[Action] in progress..."
- "[Action] completed successfully."
- "[Action] failed. [Reason]."
- "Ready" / "Idle" / "Processing"

---

## Localization Notes

When preparing text for localization:

1. **Avoid concatenation**: "Delete " + itemName → "Delete {0}" with parameter
2. **Use placeholders**: "Processing {0} of {1} files"
3. **Keep strings complete**: Don't split sentences across multiple strings
4. **Context matters**: Same word may need different translations
5. **Test length**: Some languages are longer - allow 30% expansion

---

## Examples by Context

### Profile Management
- Button: "Create Profile"
- Toast (success): "Profile 'John Doe' created successfully."
- Toast (error): "Failed to create profile. Name already exists."
- Empty state: "No profiles found. Create your first profile to get started."

### Timeline
- Button: "Add Clip"
- Toast (success): "Clip added to timeline."
- Toast (warning): "Timeline full. Remove clips to add more."
- Empty state: "Timeline is empty. Add clips to begin editing."

### Settings
- Button: "Apply Changes"
- Toast (success): "Settings saved successfully."
- Toast (info): "Settings will take effect after restart."
- Confirmation: "Discard unsaved changes?"

---

## Revision History

- **2025-01-28**: Initial version created

---

## References

- [Microsoft Writing Style Guide](https://docs.microsoft.com/en-us/style-guide/welcome/)
- [Material Design Writing](https://material.io/design/communication/writing.html)
- [Apple Human Interface Guidelines - Writing](https://developer.apple.com/design/human-interface-guidelines/ios/user-interaction/writing/)
