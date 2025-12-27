# VoiceStudio Project Structure

## Frontend Structure (WinUI 3)

```
VoiceStudio.App/
├── Models/              # Data models
├── ViewModels/          # MVVM ViewModels
├── Views/               # XAML views
│   ├── Shell/          # App shell components
│   ├── Panels/          # Panel views
│   └── Controls/        # Custom controls
├── Services/            # Services (API clients, etc.)
├── Converters/          # Value converters
├── Resources/           # Resources, styles, themes
└── App.xaml             # Application entry point
```

## Panel System

All panels follow a consistent structure:
- `Views/Panels/{PanelName}Panel.xaml` - Panel view
- `ViewModels/{PanelName}PanelViewModel.cs` - Panel view model
- `Models/{PanelName}Model.cs` - Panel data model (if needed)

