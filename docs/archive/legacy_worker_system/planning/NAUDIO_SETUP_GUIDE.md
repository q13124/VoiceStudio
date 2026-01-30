# NAudio Setup Guide
## Adding NAudio Package to VoiceStudio

**Date:** 2025-01-27  
**Status:** Setup Guide  
**Purpose:** Add NAudio NuGet package to enable audio playback

---

## 🎯 Overview

The `AudioPlayerService` implementation uses NAudio for Windows audio playback. The code is complete, but the NuGet package reference needs to be added to the project file.

---

## 📋 Steps to Add NAudio Package

### Option 1: Using Visual Studio

1. **Open Solution**
   - Open `VoiceStudio.sln` in Visual Studio

2. **Add NuGet Package**
   - Right-click on `VoiceStudio.App` project
   - Select "Manage NuGet Packages"
   - Search for "NAudio"
   - Install version **2.2.1** (or latest stable)

3. **Verify Installation**
   - Check that `NAudio` appears in Dependencies → Packages
   - Build the project to verify

### Option 2: Using .NET CLI

1. **Navigate to Project Directory**
   ```powershell
   cd src/VoiceStudio.App
   ```

2. **Add Package**
   ```powershell
   dotnet add package NAudio --version 2.2.1
   ```

3. **Verify Installation**
   ```powershell
   dotnet restore
   dotnet build
   ```

### Option 3: Manual Edit (if needed)

1. **Locate Project File**
   - File: `src/VoiceStudio.App/VoiceStudio.App.csproj`

2. **Add Package Reference**
   ```xml
   <ItemGroup>
     <PackageReference Include="NAudio" Version="2.2.1" />
   </ItemGroup>
   ```

3. **Restore and Build**
   ```powershell
   dotnet restore
   dotnet build
   ```

---

## ✅ Verification

After adding the package, verify:

1. **Build Success**
   - Project should build without errors
   - No missing reference errors for `NAudio`

2. **Code Compiles**
   - `AudioPlayerService.cs` should compile
   - All `NAudio.Wave.*` references should resolve

3. **Runtime Test**
   - Run the application
   - Test audio playback in VoiceSynthesisView
   - Test profile preview in ProfilesView
   - Test timeline playback in TimelineView

---

## 📦 Package Details

**Package:** NAudio  
**Version:** 2.2.1 (or latest stable)  
**Purpose:** Windows audio playback (WAV, MP3, FLAC)  
**Used By:** `AudioPlayerService.cs`

**Features Used:**
- `NAudio.Wave.WaveOutEvent` - Audio output device
- `NAudio.Wave.AudioFileReader` - File reading
- `NAudio.Wave.RawSourceWaveStream` - Stream playback
- `NAudio.Wave.WaveFormat` - Audio format specification

---

## 🔧 Troubleshooting

### Issue: Package Not Found
**Solution:** Ensure you're using the correct package name "NAudio" (not "NAudio.Core" or other variants)

### Issue: Version Conflicts
**Solution:** Use version 2.2.1 or check for latest stable version compatible with .NET 8

### Issue: Build Errors
**Solution:** 
1. Clean solution: `dotnet clean`
2. Restore packages: `dotnet restore`
3. Rebuild: `dotnet build`

### Issue: Runtime Errors
**Solution:** Ensure NAudio native dependencies are available (usually handled automatically by NuGet)

---

## 📚 Additional Resources

- **NAudio Documentation:** https://github.com/naudio/NAudio
- **NuGet Package:** https://www.nuget.org/packages/NAudio/
- **AudioPlayerService Implementation:** `src/VoiceStudio.App/Services/AudioPlayerService.cs`

---

## ✅ Completion Checklist

- [ ] NAudio package added to project
- [ ] Project builds successfully
- [ ] AudioPlayerService compiles without errors
- [ ] Audio playback tested in VoiceSynthesisView
- [ ] Profile preview tested in ProfilesView
- [ ] Timeline playback tested in TimelineView

---

**Last Updated:** 2025-01-27  
**Status:** Setup Guide Ready

