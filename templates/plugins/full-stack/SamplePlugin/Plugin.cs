using System.Threading.Tasks;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;

namespace {{CLASS_NAME}}Plugin;

public class Plugin : IPlugin
{
    private IBackendClient _backend;
    private bool _isInitialized;

    public string Name => "{{PLUGIN_NAME}}";
    public string Version => "{{VERSION}}";
    public string Author => "{{AUTHOR}}";
    public string Description => "{{DESCRIPTION}}";
    public bool IsInitialized => _isInitialized;

    public void RegisterPanels(IPanelRegistry registry)
    {
        registry.Register(new PanelDescriptor
        {
            PanelId = "{{PLUGIN_NAME}}_main",
            DisplayName = "{{DISPLAY_NAME}}",
            ViewType = typeof(MainPanel),
            Region = PanelRegion.Center
        });
    }

    public void Initialize(IBackendClient backend)
    {
        _backend = backend;
        _isInitialized = true;
    }

    public void Cleanup()
    {
        _backend = null;
        _isInitialized = false;
    }
}
