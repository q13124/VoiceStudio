# VoiceStudio Implementation Checklist

Use this checklist when implementing or reviewing code to ensure compliance with the architecture specification.

## Pre-Implementation

- [ ] Read GUARDRAILS.md completely
- [ ] Review architecture-detailed.md
- [ ] Understand the 3×2 grid layout requirement
- [ ] Familiarize yourself with design tokens

## Panel Implementation

### Required Panels (All 6 Must Exist)

- [ ] **ProfilesView**
  - [ ] ProfilesView.xaml exists
  - [ ] ProfilesView.xaml.cs exists
  - [ ] ProfilesViewModel.cs exists
  - [ ] Uses PanelHost control
  - [ ] Placeholder regions visible

- [ ] **TimelineView**
  - [ ] TimelineView.xaml exists
  - [ ] TimelineView.xaml.cs exists
  - [ ] TimelineViewModel.cs exists
  - [ ] Uses PanelHost control
  - [ ] Toolbar, tracks, and visualizer areas visible

- [ ] **EffectsMixerView**
  - [ ] EffectsMixerView.xaml exists
  - [ ] EffectsMixerView.xaml.cs exists
  - [ ] EffectsMixerViewModel.cs exists
  - [ ] Uses PanelHost control
  - [ ] Mixer faders and FX chain areas visible

- [ ] **AnalyzerView**
  - [ ] AnalyzerView.xaml exists
  - [ ] AnalyzerView.xaml.cs exists
  - [ ] AnalyzerViewModel.cs exists
  - [ ] Uses PanelHost control
  - [ ] Tabs and chart placeholder visible

- [ ] **MacroView**
  - [ ] MacroView.xaml exists
  - [ ] MacroView.xaml.cs exists
  - [ ] MacroViewModel.cs exists
  - [ ] Uses PanelHost control
  - [ ] Tabs and node graph placeholder visible

- [ ] **DiagnosticsView**
  - [ ] DiagnosticsView.xaml exists
  - [ ] DiagnosticsView.xaml.cs exists
  - [ ] DiagnosticsViewModel.cs exists
  - [ ] Uses PanelHost control
  - [ ] Log list and metrics charts visible

## MainWindow Structure

- [ ] 3-row grid (Command Deck, Workspace, Status Bar)
- [ ] 3×2 workspace grid (Left, Center, Right columns; Top, Bottom rows)
- [ ] All panels use PanelHost controls
- [ ] Navigation sidebar in left dock
- [ ] Status bar at bottom

## File Structure

- [ ] All files in canonical locations
- [ ] No files merged "for simplicity"
- [ ] MVVM separation maintained
- [ ] Core library separate from App
- [ ] Shared contracts in shared/contracts/

## Design System

- [ ] All colors use VSQ.* design tokens
- [ ] No hardcoded colors
- [ ] Corner radius uses VSQ.CornerRadius.*
- [ ] Text styles use VSQ.Text.*
- [ ] Button styles use VSQ.Button.*

## Placeholder Regions

- [ ] TimelineView: Waveform lanes visible
- [ ] TimelineView: Spectrogram/visualizer area visible
- [ ] EffectsMixerView: Fader controls visible
- [ ] EffectsMixerView: FX chain area visible
- [ ] AnalyzerView: Chart placeholder visible
- [ ] MacroView: Node graph canvas visible
- [ ] DiagnosticsView: Log list visible
- [ ] DiagnosticsView: Metrics charts visible

## Core Library

- [ ] IPanelView interface exists
- [ ] PanelRegion enum exists
- [ ] PanelDescriptor class exists
- [ ] IPanelRegistry interface exists
- [ ] PanelRegistry implementation exists
- [ ] Models exist (VoiceProfile, AudioClip, MeterReading)
- [ ] IBackendClient interface exists

## Backend Architecture

- [ ] backend/api/ directory exists
- [ ] backend/mcp_bridge/ directory exists
- [ ] backend/models/ directory exists
- [ ] shared/contracts/ directory exists
- [ ] Contract schemas defined

## Code Quality

- [ ] No simplifications that reduce functionality
- [ ] No merged files that should be separate
- [ ] No removed placeholder regions
- [ ] No hardcoded values that should use tokens
- [ ] Architecture complexity maintained

## Final Verification

- [ ] All 6 panels implemented
- [ ] 3×2 grid layout maintained
- [ ] PanelHost used for all panels
- [ ] All placeholders visible
- [ ] Design tokens used consistently
- [ ] File structure matches canonical tree
- [ ] Core library properly separated
- [ ] No guardrails violated

## If Any Check Fails

1. **STOP** implementation
2. Review GUARDRAILS.md
3. Check architecture-detailed.md
4. Fix the issue before continuing
5. Re-run checklist

## Remember

**This is a professional studio application. Complexity is intentional. Do not simplify.**

