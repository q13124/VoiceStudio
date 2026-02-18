using Microsoft.UI.Xaml.Controls;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;

namespace {{CLASS_NAME}}Plugin;

public sealed partial class MainPanel : UserControl, ILifecyclePanelView
{
    private MainPanelViewModel _viewModel;
    public string PanelId => "{{PLUGIN_NAME}}_main";
    public string DisplayName => "{{DISPLAY_NAME}}";
    public PanelRegion Region => PanelRegion.Center;

    public MainPanel()
    {
        InitializeComponent();
        _viewModel = new MainPanelViewModel();
        DataContext = _viewModel;
    }

    public async System.Threading.Tasks.Task OnActivatedAsync(System.Threading.CancellationToken ct = default)
    {
        await RefreshAsync(ct);
    }

    public async System.Threading.Tasks.Task OnDeactivatedAsync(System.Threading.CancellationToken ct = default)
    {
        await System.Threading.Tasks.Task.CompletedTask;
    }

    public async System.Threading.Tasks.Task RefreshAsync(System.Threading.CancellationToken ct = default)
    {
        await System.Threading.Tasks.Task.CompletedTask;
    }
}
