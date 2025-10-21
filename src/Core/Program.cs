using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.Hosting;
using Serilog;
using Serilog.Formatting.Json;

// Determine base data directory (ProgramData on Windows)
var programDataEnv = Environment.GetEnvironmentVariable("PROGRAMDATA");
string baseDir;
if (!string.IsNullOrWhiteSpace(programDataEnv))
{
    baseDir = Path.Combine(programDataEnv, "VoiceStudio");
}
else
{
    var commonData = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
    if (string.IsNullOrWhiteSpace(commonData))
        commonData = AppContext.BaseDirectory;
    baseDir = Path.Combine(commonData, "VoiceStudio");
}

var logDir = Path.Combine(baseDir, "logs");
Directory.CreateDirectory(logDir);

Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Debug()
    .Enrich.FromLogContext()
    .WriteTo.File(new JsonFormatter(), Path.Combine(logDir, "core.json"),
                  rollingInterval: RollingInterval.Day,
                  retainedFileCountLimit: 7,
                  shared: true)
    .WriteTo.Console(new JsonFormatter())
    .CreateLogger();

try
{
    Log.Information("Booting VoiceStudio.Core...");
    var builder = WebApplication.CreateBuilder(args);
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
