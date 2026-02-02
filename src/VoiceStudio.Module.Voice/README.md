# VoiceStudio.Module.Voice

Voice synthesis, cloning, and text-to-speech module.

## Overview

This module contains all voice-related UI panels and ViewModels:
- Voice synthesis (TTS)
- Voice cloning
- Voice morphing/blending
- Text-to-speech editors
- SSML control
- Emotion/prosody control

## Migration Status

### Phase 1: Infrastructure (Complete)
- [x] Module project created
- [x] VoiceModule.cs implementing IUIModule
- [x] Project references configured

### Phase 2: Panel Migration (In Progress)

Views to migrate from `VoiceStudio.App.Views.Panels/`:

| View | ViewModel | Status |
|------|-----------|--------|
| VoiceSynthesisView | VoiceSynthesisViewModel | Pending |
| VoiceCloningWizardView | VoiceCloningWizardViewModel | Pending |
| VoiceQuickCloneView | VoiceQuickCloneViewModel | Pending |
| VoiceMorphView | VoiceMorphViewModel | Pending |
| VoiceMorphingBlendingView | VoiceMorphingBlendingViewModel | Pending |
| VoiceStyleTransferView | VoiceStyleTransferViewModel | Pending |
| VoiceBrowserView | VoiceBrowserViewModel | Pending |
| TextSpeechEditorView | TextSpeechEditorViewModel | Pending |
| TextBasedSpeechEditorView | TextBasedSpeechEditorViewModel | Pending |
| TextHighlightingView | TextHighlightingViewModel | Pending |
| ProsodyView | ProsodyViewModel | Pending |
| SSMLControlView | SSMLControlViewModel | Pending |
| EmotionControlView | EmotionControlViewModel | Pending |
| EmotionStyleControlView | EmotionStyleControlViewModel | Pending |
| EmotionStylePresetEditorView | EmotionStylePresetEditorViewModel | Pending |
| EnsembleSynthesisView | EnsembleSynthesisViewModel | Pending |
| MultiVoiceGeneratorView | MultiVoiceGeneratorViewModel | Pending |
| MultilingualSupportView | MultilingualSupportViewModel | Pending |
| PronunciationLexiconView | PronunciationLexiconViewModel | Pending |
| LexiconView | LexiconViewModel | Pending |
| RealTimeVoiceConverterView | RealTimeVoiceConverterViewModel | Pending |
| StyleTransferView | StyleTransferViewModel | Pending |
| RecordingView | RecordingViewModel | Pending |

## Migration Steps for Each View

1. **Copy View files** to `Views/` folder
2. **Copy ViewModel** to `ViewModels/` folder  
3. **Update namespaces**:
   - `VoiceStudio.App.Views.Panels` → `VoiceStudio.Module.Voice.Views`
   - `VoiceStudio.App.ViewModels` → `VoiceStudio.Module.Voice.ViewModels`
4. **Update XAML x:Class** attribute
5. **Update service references** to use Core interfaces
6. **Register in VoiceModule.cs**
7. **Enable XAML compilation** in csproj when views are added
8. **Test panel navigation**

## Dependencies

This module depends on:
- `VoiceStudio.Core` - Interfaces and models
- `VoiceStudio.Common.UI` - Shared controls and converters

## Build

```bash
dotnet build src/VoiceStudio.Module.Voice/VoiceStudio.Module.Voice.csproj -c Debug -p:Platform=x64
```
