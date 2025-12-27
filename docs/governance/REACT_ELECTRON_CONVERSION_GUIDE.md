# React/Electron to WinUI 3 Conversion Guide
## Converting Panels from C:\VoiceStudio to E:\VoiceStudio

**Purpose:** Convert React/Electron UI panels to WinUI 3 (.NET 8, C#/XAML) panels.

---

## 🔍 Discovery Phase

### Step 1: Find React/Electron Panels

```powershell
# Find React components
Get-ChildItem -Path "C:\VoiceStudio" -Recurse -Filter "*.jsx" -ErrorAction SilentlyContinue
Get-ChildItem -Path "C:\VoiceStudio" -Recurse -Filter "*.tsx" -ErrorAction SilentlyContinue

# Find Electron main files
Get-ChildItem -Path "C:\VoiceStudio" -Recurse -Filter "main.js" -ErrorAction SilentlyContinue
Get-ChildItem -Path "C:\VoiceStudio" -Recurse -Filter "preload.js" -ErrorAction SilentlyContinue

# Find package.json (indicates Node/React project)
Get-ChildItem -Path "C:\VoiceStudio" -Recurse -Filter "package.json" -ErrorAction SilentlyContinue

# Find component directories
Get-ChildItem -Path "C:\VoiceStudio" -Recurse -Directory | Where-Object { 
    $_.Name -like "*component*" -or 
    $_.Name -like "*panel*" -or 
    $_.Name -like "*view*" 
} | Select-Object FullName
```

### Step 2: Catalog All Panels

Run the discovery script:
```powershell
.\tools\Discover-ReactPanels.ps1 -SourcePath "C:\VoiceStudio"
```

This will generate:
- `docs/governance/REACT_PANEL_CATALOG.json` - Complete inventory
- `docs/governance/REACT_PANEL_CATALOG.md` - Human-readable list

---

## 🔄 Conversion Mapping

### React → WinUI 3 Equivalents

| React/JSX | WinUI 3 XAML | Notes |
|-----------|--------------|-------|
| `<div>` | `<Grid>`, `<StackPanel>`, `<Border>` | Use Grid for layout, StackPanel for vertical/horizontal, Border for containers |
| `<button>` | `<Button>` | Direct equivalent |
| `<input type="text">` | `<TextBox>` | Text input |
| `<input type="number">` | `<NumberBox>` | Numeric input |
| `<input type="range">` | `<Slider>` | Range slider |
| `<select>` | `<ComboBox>` | Dropdown |
| `<textarea>` | `<TextBox TextWrapping="Wrap" AcceptsReturn="True">` | Multi-line text |
| `<img>` | `<Image>` | Image display |
| `<ul>`, `<li>` | `<ListView>`, `<ItemsControl>` | Lists |
| `<table>` | `<DataGrid>` or `<ListView>` | Tables |
| `<canvas>` | `<Canvas>` or Win2D | Drawing surface |
| `className` | `Style="{StaticResource ...}"` | Styling |
| `onClick` | `Click="..."` | Event handlers |
| `useState` | `INotifyPropertyChanged` in ViewModel | State management |
| `useEffect` | ViewModel lifecycle methods | Side effects |
| `props` | `DependencyProperty` or ViewModel properties | Data binding |
| CSS Grid | `<Grid>` with Row/Column definitions | Layout |
| Flexbox | `<StackPanel>` or `<Grid>` | Layout |
| CSS Modules | ResourceDictionary styles | Styling |

### React Hooks → MVVM Pattern

| React Hook | WinUI 3 Equivalent |
|------------|-------------------|
| `useState` | `ObservableProperty` in ViewModel |
| `useEffect` | ViewModel constructor or `OnLoaded` |
| `useContext` | Dependency Injection or Service Locator |
| `useCallback` | ViewModel methods (already memoized) |
| `useMemo` | ViewModel computed properties |
| `useRef` | Code-behind fields or ViewModel properties |

### State Management

**React:**
```jsx
const [count, setCount] = useState(0);
const [items, setItems] = useState([]);
```

**WinUI 3 (ViewModel):**
```csharp
[ObservableProperty]
private int count;

[ObservableProperty]
private ObservableCollection<Item> items = new();
```

---

## 📋 Conversion Checklist

For each React panel:

- [ ] **Identify panel purpose and functionality**
- [ ] **Map React components to XAML equivalents**
- [ ] **Extract state management to ViewModel**
- [ ] **Convert event handlers to C# methods**
- [ ] **Convert CSS to XAML styles/DesignTokens**
- [ ] **Create ViewModel with INotifyPropertyChanged**
- [ ] **Implement data binding in XAML**
- [ ] **Test panel functionality**
- [ ] **Register panel in PanelRegistry**
- [ ] **Update panel discovery**

---

## 🛠️ Conversion Process

### Step 1: Analyze React Component

**Example React Panel:**
```jsx
// ProfilesPanel.jsx
import React, { useState, useEffect } from 'react';

export function ProfilesPanel() {
  const [profiles, setProfiles] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState(null);

  useEffect(() => {
    // Load profiles
    fetch('/api/profiles')
      .then(res => res.json())
      .then(data => setProfiles(data));
  }, []);

  return (
    <div className="profiles-panel">
      <h2>Voice Profiles</h2>
      <ul>
        {profiles.map(profile => (
          <li key={profile.id} onClick={() => setSelectedProfile(profile)}>
            {profile.name}
          </li>
        ))}
      </ul>
      {selectedProfile && (
        <div className="profile-details">
          <p>Name: {selectedProfile.name}</p>
          <p>Language: {selectedProfile.language}</p>
        </div>
      )}
    </div>
  );
}
```

### Step 2: Create WinUI 3 ViewModel

**ProfilesViewModel.cs:**
```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;

namespace VoiceStudio.App.ViewModels;

public partial class ProfilesViewModel : ObservableObject
{
    [ObservableProperty]
    private ObservableCollection<VoiceProfile> profiles = new();

    [ObservableProperty]
    private VoiceProfile? selectedProfile;

    public ProfilesViewModel()
    {
        LoadProfiles();
    }

    private async void LoadProfiles()
    {
        // Load from backend
        var client = App.GetService<IBackendClient>();
        var data = await client.GetProfilesAsync();
        Profiles = new ObservableCollection<VoiceProfile>(data);
    }

    [RelayCommand]
    private void SelectProfile(VoiceProfile profile)
    {
        SelectedProfile = profile;
    }
}
```

### Step 3: Create XAML View

**ProfilesView.xaml:**
```xml
<UserControl x:Class="VoiceStudio.App.Views.Panels.ProfilesView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:vm="using:VoiceStudio.App.ViewModels">
    <UserControl.DataContext>
        <vm:ProfilesViewModel />
    </UserControl.DataContext>
    
    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>
        
        <!-- Header -->
        <TextBlock Grid.Row="0" 
                   Text="Voice Profiles" 
                   Style="{StaticResource VSQ.Text.Heading}"
                   Margin="8"/>
        
        <!-- Profile List -->
        <ListView Grid.Row="1"
                   ItemsSource="{Binding Profiles}"
                   SelectedItem="{Binding SelectedProfile, Mode=TwoWay}"
                   SelectionMode="Single">
            <ListView.ItemTemplate>
                <DataTemplate>
                    <TextBlock Text="{Binding Name}" 
                               Style="{StaticResource VSQ.Text.Body}"/>
                </DataTemplate>
            </ListView.ItemTemplate>
        </ListView>
        
        <!-- Details -->
        <Border Grid.Row="2" 
                Visibility="{Binding SelectedProfile, Converter={StaticResource NullToVisibilityConverter}}"
                Style="{StaticResource VSQ.Panel.Border}">
            <StackPanel Margin="8">
                <TextBlock Text="{Binding SelectedProfile.Name, StringFormat='Name: {0}'}"/>
                <TextBlock Text="{Binding SelectedProfile.Language, StringFormat='Language: {0}'}"/>
            </StackPanel>
        </Border>
    </Grid>
</UserControl>
```

### Step 4: Create Code-Behind

**ProfilesView.xaml.cs:**
```csharp
using Microsoft.UI.Xaml.Controls;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Views.Panels;

public sealed partial class ProfilesView : UserControl
{
    public ProfilesViewModel ViewModel { get; }

    public ProfilesView()
    {
        InitializeComponent();
        ViewModel = new ProfilesViewModel();
        DataContext = ViewModel;
    }
}
```

---

## 🎨 Styling Conversion

### CSS → XAML Styles

**React CSS:**
```css
.profiles-panel {
  background: #121A24;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  padding: 16px;
}

.profile-item {
  padding: 8px;
  cursor: pointer;
}

.profile-item:hover {
  background: #1a2330;
}
```

**XAML Style (in Styles/Panels.xaml):**
```xml
<Style x:Key="VSQ.Panel.Profiles" TargetType="Border">
    <Setter Property="Background" Value="{StaticResource VSQ.Panel.BackgroundBrush}"/>
    <Setter Property="BorderBrush" Value="{StaticResource VSQ.Panel.BorderBrush}"/>
    <Setter Property="BorderThickness" Value="1"/>
    <Setter Property="CornerRadius" Value="{StaticResource VSQ.CornerRadius.Panel}"/>
    <Setter Property="Padding" Value="16"/>
</Style>

<Style x:Key="VSQ.ProfileItem" TargetType="ListViewItem">
    <Setter Property="Padding" Value="8"/>
    <Setter Property="Template">
        <Setter.Value>
            <ControlTemplate TargetType="ListViewItem">
                <Border Background="Transparent">
                    <VisualStateManager.VisualStateGroups>
                        <VisualStateGroup x:Name="CommonStates">
                            <VisualState x:Name="Normal"/>
                            <VisualState x:Name="PointerOver">
                                <Storyboard>
                                    <ColorAnimation Storyboard.TargetName="BackgroundBorder"
                                                     Storyboard.TargetProperty="(Border.Background).(SolidColorBrush.Color)"
                                                     To="#1a2330" Duration="0:0:0.1"/>
                                </Storyboard>
                            </VisualState>
                        </VisualStateGroup>
                    </VisualStateManager.VisualStateGroups>
                    <ContentPresenter/>
                </Border>
            </ControlTemplate>
        </Setter.Value>
    </Setter>
</Style>
```

---

## 🔌 Electron IPC → Backend API

**Electron (preload.js):**
```javascript
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  getProfiles: () => ipcRenderer.invoke('get-profiles'),
  saveProfile: (profile) => ipcRenderer.invoke('save-profile', profile)
});
```

**WinUI 3 (IBackendClient):**
```csharp
public interface IBackendClient
{
    Task<List<VoiceProfile>> GetProfilesAsync();
    Task<bool> SaveProfileAsync(VoiceProfile profile);
}

// Implementation uses HttpClient to call Python FastAPI backend
public class BackendClient : IBackendClient
{
    private readonly HttpClient _httpClient;
    
    public async Task<List<VoiceProfile>> GetProfilesAsync()
    {
        var response = await _httpClient.GetAsync("/api/profiles");
        return await response.Content.ReadFromJsonAsync<List<VoiceProfile>>();
    }
}
```

---

## 📝 Conversion Template

Use this template for each panel:

```powershell
.\tools\Convert-ReactPanel.ps1 `
    -SourceFile "C:\VoiceStudio\src\panels\ProfilesPanel.jsx" `
    -OutputDir "E:\VoiceStudio\src\VoiceStudio.App\Views\Panels" `
    -PanelName "Profiles"
```

This will generate:
- `ProfilesView.xaml`
- `ProfilesView.xaml.cs`
- `ProfilesViewModel.cs`
- Basic styling in `Styles/Panels.xaml`

---

## ✅ Post-Conversion Steps

1. **Register Panel:**
   - Add to `PanelRegistry.cs`
   - Set `PanelRegion` (Left, Center, Right, Bottom)
   - Set `PanelTier` (Core, Pro, Advanced, Technical, Meta)

2. **Update Discovery:**
   ```powershell
   .\tools\Find-AllPanels.ps1
   ```

3. **Test Panel:**
   - Build solution
   - Launch app
   - Verify panel loads
   - Test functionality

4. **Update Documentation:**
   - Add to `PANEL_CATALOG.md`
   - Update conversion status

---

## 🚀 Automated Conversion Tools

### Tool 1: React Panel Discovery
**File:** `tools/Discover-ReactPanels.ps1`
- Scans C:\VoiceStudio for React components
- Generates catalog JSON and Markdown
- Identifies dependencies

### Tool 2: React to XAML Converter
**File:** `tools/Convert-ReactPanel.ps1`
- Parses React JSX/TSX
- Generates XAML skeleton
- Creates ViewModel stub
- Maps common patterns

### Tool 3: CSS to XAML Style Converter
**File:** `tools/Convert-CSSStyles.ps1`
- Converts CSS to XAML ResourceDictionary
- Maps to DesignTokens
- Generates VisualStateManager for hover/focus

---

## 📚 Reference

- **WinUI 3 Docs:** https://learn.microsoft.com/en-us/windows/apps/winui/winui3/
- **MVVM Toolkit:** https://learn.microsoft.com/en-us/dotnet/communitytoolkit/mvvm/
- **XAML Controls:** https://learn.microsoft.com/en-us/windows/apps/design/controls/

---

**Status:** Ready for conversion when React/Electron panels are discovered.

