using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Serilog;
using Serilog.Formatting.Compact;

static string ResolveWritableDataRoot()
{
    // Prefer CommonApplicationData, but fall back to LocalApplicationData or ~/.local/share on Linux
    string root = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
    try
    {
        Directory.CreateDirectory(Path.Combine(root, "VoiceStudio"));
        return root;
    }
    catch
    {
        try
        {
            root = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            Directory.CreateDirectory(Path.Combine(root, "VoiceStudio"));
            return root;
        }
        catch
        {
            var home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            root = Path.Combine(home, ".local", "share");
            Directory.CreateDirectory(Path.Combine(root, "VoiceStudio"));
            return root;
        }
    }
}

var dataRoot = ResolveWritableDataRoot();
var logDir = Path.Combine(dataRoot, "VoiceStudio", "logs");
Directory.CreateDirectory(logDir);

Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .Enrich.FromLogContext()
    .WriteTo.Console(new CompactJsonFormatter())
    .WriteTo.File(new CompactJsonFormatter(), Path.Combine(logDir, "service.json"), rollingInterval: RollingInterval.Day, retainedFileCountLimit: 14, shared: true)
    .CreateLogger();

try
{
    Log.Information("Booting UltraClone.EngineService");

    var builder = WebApplication.CreateBuilder(args);
    builder.Host.UseSerilog();

    builder.Services.AddGrpc();

    var app = builder.Build();

    app.MapGet("/health", () => new { status = "ok", service = "UltraClone.EngineService" });

    // gRPC endpoints can be added later as needed

    Log.Information("Starting UltraClone.EngineService web host");
    app.Run("http://127.0.0.1:5072");
}
catch (Exception ex)
{
    Log.Fatal(ex, "UltraClone.EngineService crashed during startup");
}
finally
{
    Log.CloseAndFlush();
}
