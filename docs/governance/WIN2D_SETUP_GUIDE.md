# Win2D Setup Guide
## Adding Win2D Package to VoiceStudio

**Date:** 2025-01-27  
**Status:** Setup Guide  
**Purpose:** Add Win2D NuGet package to enable custom audio visualizations

---

## 🎯 Overview

Win2D is required for custom audio visualizations (waveforms, spectrograms) in the TimelineView and AnalyzerView. The code structure is ready, but the NuGet package reference needs to be added to the project file.

---

## 📋 Steps to Add Win2D Package

### Option 1: Using Visual Studio

1. **Open Solution**
   - Open `VoiceStudio.sln` in Visual Studio

2. **Add NuGet Package**
   - Right-click on `VoiceStudio.App` project
   - Select "Manage NuGet Packages"
   - Search for "Win2D.WinUI"
   - Install version **1.1.0** (or latest stable for WinUI 3)

3. **Verify Installation**
   - Check that `Win2D.WinUI` appears in Dependencies → Packages
   - Build the project to verify

### Option 2: Using .NET CLI

1. **Navigate to Project Directory**
   ```powershell
   cd src/VoiceStudio.App
   ```

2. **Add Package**
   ```powershell
   dotnet add package Win2D.WinUI --version 1.1.0
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
     <PackageReference Include="Win2D.WinUI" Version="1.1.0" />
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
   - No missing reference errors for `Microsoft.Graphics.Canvas`

2. **Code Compiles**
   - `WaveformControl.xaml.cs` should compile
   - `SpectrogramControl.xaml.cs` should compile
   - All `Microsoft.Graphics.Canvas.*` references should resolve

3. **Runtime Test**
   - Run the application
   - Test waveform rendering in TimelineView
   - Test spectrogram in TimelineView bottom area
   - Test analyzer charts in AnalyzerView

---

## 📦 Package Details

**Package:** Win2D.WinUI  
**Version:** 1.1.0 (or latest stable)  
**Purpose:** Custom 2D graphics rendering for audio visualizations  
**Used By:** 
- `WaveformControl.xaml` - Waveform rendering
- `SpectrogramControl.xaml` - Spectrogram rendering
- `AnalyzerCharts.xaml` - Analysis charts

**Features Used:**
- `Microsoft.Graphics.Canvas.UI.Xaml.CanvasControl` - Canvas for rendering
- `Microsoft.Graphics.Canvas.CanvasDrawingSession` - Drawing operations
- `Microsoft.Graphics.Canvas.Brushes` - Brushes and colors
- `Microsoft.Graphics.Canvas.Geometry` - Path drawing

---

## 🔧 Troubleshooting

### Issue: Package Not Found
**Solution:** Ensure you're using "Win2D.WinUI" (not "Win2D" or "Win2D.UWP")

### Issue: Version Conflicts
**Solution:** Use version 1.1.0 or check for latest stable version compatible with WinUI 3 and .NET 8

### Issue: Build Errors
**Solution:** 
1. Clean solution: `dotnet clean`
2. Restore packages: `dotnet restore`
3. Rebuild: `dotnet build`

### Issue: Runtime Errors
**Solution:** Ensure Win2D native dependencies are available (usually handled automatically by NuGet)

### Issue: CanvasControl Not Found
**Solution:** Ensure you're using `Microsoft.Graphics.Canvas.UI.Xaml.CanvasControl` (WinUI 3 version, not UWP)

---

## 📚 Additional Resources

- **Win2D Documentation:** https://microsoft.github.io/Win2D/
- **Win2D GitHub:** https://github.com/microsoft/Win2D
- **NuGet Package:** https://www.nuget.org/packages/Win2D.WinUI/
- **WinUI 3 Integration:** https://microsoft.github.io/Win2D/html/Introduction.htm

---

## ✅ Completion Checklist

- [ ] Win2D.WinUI package added to project
- [ ] Project builds successfully
- [ ] WaveformControl compiles without errors
- [ ] SpectrogramControl compiles without errors
- [ ] Waveform rendering tested in TimelineView
- [ ] Spectrogram rendering tested in TimelineView
- [ ] Analyzer charts tested in AnalyzerView

---

**Last Updated:** 2025-01-27  
**Status:** Setup Guide Ready

