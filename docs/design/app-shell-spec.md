# App Shell & Top Command Deck Specification

## 1. Window & Root Structure

### MainWindow.xaml
- **Root**: `<Window>` (AppWindow or MainWindow)
- **Background**: Dark gradient using design token brushes
- **Content**: Root Grid with 3 rows

```xml
<Grid>
  <Grid.RowDefinitions>
    <RowDefinition Height="Auto"/>   <!-- Top Command Deck -->
    <RowDefinition Height="*"/>      <!-- Main Workspace -->
    <RowDefinition Height="Auto"/>   <!-- Status Bar -->
  </Grid.RowDefinitions>
</Grid>
```

## 2. Top Command Deck (Row 0)

### Composition
- **Total Height**: ~80px
- **MenuBar**: 32px (standard WinUI MenuBar)
- **Command Toolbar**: 48px (StackPanel/CommandBar)

### MenuBar Structure
Menus (left to right):
- File
- Edit
- View
- Modules
- Playback
- Tools
- AI
- Help

*Note: Keep menu items simple for now; focus on structure.*

### Command Toolbar Sections (left → right)

1. **Transport Controls**
   - Play
   - Pause
   - Stop
   - Record
   - Loop

2. **Project Section**
   - Project name display
   - Workspace dropdown

3. **Engine Section**
   - Model selector (XTTS / RVC / etc.)
   - ComboBox for engine selection

4. **Performance HUD**
   - GPU indicator (ProgressBar + TextBlock)
   - CPU indicator (ProgressBar + TextBlock)
   - Latency indicator (TextBlock)

5. **History Controls**
   - Undo button
   - Redo button
   - History button

### XAML Structure
```xml
<Grid Grid.Row="0">
  <Grid.RowDefinitions>
    <RowDefinition Height="Auto"/> <!-- Menu -->
    <RowDefinition Height="48"/>   <!-- Toolbar -->
  </Grid.RowDefinitions>

  <MenuBar Grid.Row="0">
    <!-- File / Edit / View / Modules / Playback / Tools / AI / Help -->
  </MenuBar>

  <CommandBar Grid.Row="1">
    <!-- PrimaryCommands: transport + project; SecondaryCommands: settings etc. -->
  </CommandBar>
</Grid>
```

## 3. Design Tokens

### 3.1 Colors
- `VSQ.Background.Darker`: #FF0A0F15
- `VSQ.Background.Dark`: #FF121A24
- `VSQ.Accent.Cyan`: #FF00B7C2
- `VSQ.Accent.CyanGlow`: #3030E0FF
- `VSQ.Accent.Lime`: #FF9AFF33
- `VSQ.Accent.Magenta`: #FFB040FF
- `VSQ.Text.Primary`: #FFCDD9E5
- `VSQ.Text.Secondary`: #FF8A9BB3
- `VSQ.Border.Subtle`: #26FFFFFF
- `VSQ.Warn`: #FFFFB540
- `VSQ.Error`: #FFFF4060

### 3.2 Brushes
- `VSQ.Window.Background`: LinearGradientBrush (Darker → Dark)
- `VSQ.Text.PrimaryBrush`: SolidColorBrush
- `VSQ.Accent.CyanBrush`: SolidColorBrush
- `VSQ.Panel.BorderBrush`: SolidColorBrush

*Future: Add Acrylic/Mica brushes using WinUI 3 BackdropMaterial for glassmorphism*

### 3.3 Typography
- **Primary Font**: Inter (or Segoe UI as fallback)
- **Sizes**:
  - `VSQ.Font.Caption`: 10
  - `VSQ.Font.Body`: 12
  - `VSQ.Font.Title`: 16
  - `VSQ.Font.Heading`: 20

**TextBlock Styles**:
- `VSQ.Text.Body`: FontSize=12, Foreground=Primary
- `VSQ.Text.Caption`: FontSize=10, Foreground=Secondary
- `VSQ.Text.Title`: FontSize=16, Foreground=Primary, SemiBold
- `VSQ.Text.Heading`: FontSize=20, Foreground=Primary, Bold

### 3.4 Corner Radius & Shadows
- `VSQ.CornerRadius.Panel`: 8
- `VSQ.CornerRadius.Button`: 4
- `VSQ.Animation.Duration.Fast`: 100
- `VSQ.Animation.Duration.Medium`: 150

*Shadows: Use ThemeShadow or DropShadowPanel where necessary*

## 4. Main Workspace Layout (Row 1)

### Visual Layout
- **Left**: Navigation + side stack (≈ 18–20% width)
- **Center**: Production area (≈ 55–60%)
- **Right**: Rack (≈ 22–25%)
- **Bottom**: Deck across full width (≈ 15% height)

### Grid Structure
```xml
<Grid Grid.Row="1">
  <Grid.RowDefinitions>
    <RowDefinition Height="*"/>        <!-- Top main band -->
    <RowDefinition Height="0.18*"/>    <!-- Bottom deck (macros/diag) -->
  </Grid.RowDefinitions>

  <Grid.ColumnDefinitions>
    <ColumnDefinition Width="0.2*"/>   <!-- Left dock -->
    <ColumnDefinition Width="0.55*"/>  <!-- Center -->
    <ColumnDefinition Width="0.25*"/>  <!-- Right dock -->
  </Grid.ColumnDefinitions>

  <!-- Row 0: [0,0] left; [0,1] center; [0,2] right -->
  <!-- Row 1: [1,0..2] bottom deck (col-span=3) -->
</Grid>
```

### Panel Placement
- **Row 0, Column 0**: Left dock (ProfilesPanel)
- **Row 0, Column 1**: Center (TimelinePanel)
- **Row 0, Column 2**: Right dock (EffectsMixerPanel, AnalyzerPanel)
- **Row 1, Columns 0-2**: Bottom deck (MacroPanel, DiagnosticsPanel)

