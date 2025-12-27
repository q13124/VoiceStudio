# VoiceStudio Canonical Files Reference

This document provides the exact, canonical versions of key files that must be implemented exactly as specified.

## 1. DesignTokens.xaml

**Location:** `src/VoiceStudio.App/Resources/DesignTokens.xaml`

**Purpose:** Defines all shared colors, brushes, typography, and spacing. All styles must derive from these tokens.

**Key Points:**
- Use `VSQ.FontSize.*` for typography (not `VSQ.Font.*`)
- Panel background brush is hardcoded to `#151921` (not from color resource)
- All colors and brushes defined here
- Corner radius and animation durations defined

**Merge into App.xaml** as a merged resource dictionary.

## 2. Panel Core Types

### PanelRegion.cs
**Location:** `src/VoiceStudio.Core/Panels/PanelRegion.cs`

Simple enum with: Left, Center, Right, Bottom, Floating

### IPanelView.cs
**Location:** `src/VoiceStudio.Core/Panels/IPanelView.cs`

Interface with: PanelId, DisplayName, Region properties

### PanelDescriptor.cs
**Location:** `src/VoiceStudio.Core/Panels/PanelDescriptor.cs`

Sealed class with init-only properties: PanelId, DisplayName, Region, ViewType, ViewModelType

### PanelRegistry.cs
**Location:** `src/VoiceStudio.Core/Panels/PanelRegistry.cs`

Contains both interface and implementation:
- `IPanelRegistry` interface
- `PanelRegistry` sealed class with TODO for registration

## 3. PanelHost Control

**Location:** `src/VoiceStudio.App/Controls/PanelHost.xaml`

**Key Features:**
- Header bar: Background `#181D26`, CornerRadius `8,8,0,0`
- Header contains: Title TextBlock, empty center TextBlock, action buttons (▢ and –)
- Body: Border with CornerRadius `0,0,8,8`, uses VSQ.Panel.BackgroundBrush and VSQ.Panel.BorderBrush
- ContentPresenter in body for panel content

**Note:** PanelHost.xaml.cs can expose Content and later Title/Icon dependency properties.

## 4. MainWindow.xaml

**Location:** `src/VoiceStudio.App/MainWindow.xaml`

**Canonical Structure:**
- 3-row grid: Command Deck (Auto), Workspace (*), Status Bar (Auto)
- Command Deck: MenuBar + Toolbar (48px) with 4 columns
- Workspace: 4 columns (Nav 64px + Left 20% + Center 55% + Right 25%), 2 rows (Top * + Bottom 18%)
- Nav rail: 8 toggle buttons with emoji icons
- 4 PanelHosts: LeftPanelHost, CenterPanelHost, RightPanelHost, BottomPanelHost
- Status bar: 3-column layout (Status, Job progress, Metrics + Clock)

**Critical:** This is the canonical MainWindow. Do not simplify it.

## Implementation Notes

1. **DesignTokens.xaml** must be merged into App.xaml
2. **PanelHost** must not be replaced with raw Grids
3. **MainWindow** structure must match exactly
4. **Core types** must compile (registration can be added later)
5. All files must use VSQ.* resources from DesignTokens
6. **PanelHost.xaml.cs** exposes Content dependency property (Title/Icon can be added later)
7. **App.xaml.cs** creates and activates MainWindow on launch

## Verification

After implementation, verify:
- [ ] DesignTokens.xaml matches specification exactly
- [ ] App.xaml merges DesignTokens
- [ ] PanelHost.xaml matches specification exactly
- [ ] MainWindow.xaml matches specification exactly
- [ ] Core types compile
- [ ] All VSQ.* resources resolve

