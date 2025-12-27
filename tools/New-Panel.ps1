param(
    [string[]]$Names,
    [string]$Tier = "Core",
    [string]$Category = "Studio",
    [string]$Region = "Center"
)

$viewTpl = @"
<UserControl x:Class="VoiceStudio.App.Views.Panels.{0}View"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             Background="{StaticResource VSQ.Panel}">
  <Grid Padding="{StaticResource VSQ.PanelPadding}">
    <StackPanel>
      <TextBlock Text="{0}" FontSize="18" Foreground="{StaticResource VSQ.Text}"/>
      <TextBlock Text="TODO: wire backend + meters" Foreground="{StaticResource VSQ.SubtleText}"/>
    </StackPanel>
  </Grid>
</UserControl>
"@

$vmTpl = @"
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.ViewModels.Panels {{
  public sealed partial class {0}PanelViewModel : ObservableObject {{
    [ObservableProperty] private bool isBusy;
    public IRelayCommand AnalyzeCmd {{ get; }}
    public IRelayCommand ApplyCmd   {{ get; }}
    private readonly IBackendClient backend;
    public {0}PanelViewModel(IBackendClient b) {{ backend = b; AnalyzeCmd = new RelayCommand(()=>{{}}); ApplyCmd = new RelayCommand(()=>{{}}); }}
  }}
}}
"@

$viewCsTpl = @"
using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.App.Views.Panels
{{
    public sealed partial class {0}View : UserControl
    {{
        public {0}View()
        {{
            this.InitializeComponent();
        }}
    }}
}}
"@

foreach($n in $Names){
  $viewPath = "src\VoiceStudio.App\Views\Panels\$($n)View.xaml"
  $viewCsPath = "src\VoiceStudio.App\Views\Panels\$($n)View.xaml.cs"
  $vmPath = "src\VoiceStudio.App\ViewModels\Panels\$($n)PanelViewModel.cs"
  
  New-Item -Force -ItemType Directory (Split-Path $viewPath) | Out-Null
  New-Item -Force -ItemType Directory (Split-Path $vmPath) | Out-Null
  
  $viewTpl -f $n | Set-Content -Path $viewPath -Encoding UTF8
  $viewCsTpl -f $n | Set-Content -Path $viewCsPath -Encoding UTF8
  $vmTpl -f $n | Set-Content -Path $vmPath -Encoding UTF8
  
  Write-Host "Generated: $n (Tier: $Tier, Category: $Category, Region: $Region)" -ForegroundColor Green
}

Write-Host "`nGenerated $($Names.Count) panels successfully" -ForegroundColor Cyan
Write-Host "Note: Register each panel in PanelRegistry with tier, category, and region." -ForegroundColor Yellow

