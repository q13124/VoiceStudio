using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.Hosting;
using Serilog;

// Structured JSON logging to common app data, cross-platform
var commonData = System.Environment.GetFolderPath(System.Environment.SpecialFolder.CommonApplicationData);
var logDir = System.IO.Path.Combine(commonData, "VoiceStudio", "logs");
System.IO.Directory.CreateDirectory(logDir);

Log.Logger = new LoggerConfiguration()
    .Enrich.FromLogContext()
    .MinimumLevel.Debug()
    .WriteTo.File(
        path: System.IO.Path.Combine(logDir, "core-.json"),
        rollingInterval: RollingInterval.Day,
        retainedFileCountLimit: 10,
        shared: true,
        formatter: new Serilog.Formatting.Json.JsonFormatter()
    )
    .WriteTo.Console()
    .CreateLogger();

try
{
    Log.Information("Booting VoiceStudio.Core...");
    var builder = WebApplication.CreateBuilder(args);
    builder.Logging.ClearProviders();
    builder.Host.UseSerilog();
    builder.Services.AddGrpc();

    var app = builder.Build();
    app.MapGrpcService<CoreService>();
    app.MapGet("/", () => "OK");
    Log.Information("Starting web host...");
    app.Run("http://127.0.0.1:5071");
}
catch (Exception ex)
{
    Log.Fatal(ex, "Core crashed during startup");
}
finally
{
    Log.CloseAndFlush();
}
