# VoiceStudio Technical Specification

## 0. Tech + Project Assumptions

### Frontend Technology Stack
- **Language**: C# / .NET 8
- **Framework**: WinUI 3 (Windows App SDK)
- **Platform**: Windows Desktop Application
- **Architecture Pattern**: MVVM (Model-View-ViewModel)

### App Structure

#### VoiceStudio.App
- WinUI 3 desktop application
- UI layer only
- Communicates with backend via REST/WebSocket (backend implementation out of scope for this spec)

### Implementation Goals

#### Core Shell Components
1. **App Shell**
   - Window chrome
   - Menu system
   - Navigation
   - Status bar

2. **Main Layout**
   - 3×2 grid layout system

3. **Panel System**
   - Dockable panel host controls
   - Panel management infrastructure

#### Initial Concrete Panels
1. **ProfilesPanel** - User profile management
2. **TimelinePanel** - Audio timeline editing
3. **EffectsMixerPanel** - Audio effects and mixing
4. **AnalyzerPanel** - Audio analysis tools
5. **MacroPanel** - Macro/automation controls
6. **DiagnosticsPanel** - System diagnostics and monitoring

#### Extensibility
- Additional panels (transcribe, training, etc.) can be plugged into the system
- Panel system designed for extensibility

