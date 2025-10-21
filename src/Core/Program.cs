using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.Hosting;
using Serilog;
using System.Text.Json;
using System.Diagnostics;
using VoiceStudio.IPC;
using VoiceStudio.CoreRuntime;

var logDir = @"C:\VoiceStudio\logs";
System.IO.Directory.CreateDirectory(logDir);

Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Debug()
    .WriteTo.File(
        formatter: new Serilog.Formatting.Json.JsonFormatter(),
        path: System.IO.Path.Combine(logDir, "core-.json"),
        rollingInterval: RollingInterval.Day,
        retainedFileCountLimit: 10,
        shared: true)
    .WriteTo.Console()
    .CreateLogger();

try
{
    Log.Information("Booting VoiceStudio.Core...");
    var builder = WebApplication.CreateBuilder(args);
    builder.Host.UseSerilog();
    builder.Services.AddGrpc();
    builder.Services.AddSingleton<JobRunner>();

    var app = builder.Build();
    app.UseDefaultFiles();
    app.UseStaticFiles();
    app.MapGrpcService<CoreService>();
    app.MapGet("/", () => "OK");

    // Redirect to A/B Compare page
    app.MapGet("/ab", () => Results.Redirect("/ab/index.html"));

    // Simple A/B TTS endpoints writing to wwwroot for browser playback
    app.MapPost("/api/tts", async (TtsRequest req) =>
    {
        var variant = string.IsNullOrWhiteSpace(req.Variant) ? "A" : req.Variant!.Trim().ToUpperInvariant();
        if (variant != "A" && variant != "B") variant = "A";

        var wwwroot = System.IO.Path.Combine(AppContext.BaseDirectory, "wwwroot");
        var outDir  = System.IO.Path.Combine(wwwroot, "ab", "out");
        System.IO.Directory.CreateDirectory(outDir);
        var outPath = System.IO.Path.Combine(outDir, $"ab_{variant}.wav");

        var job = new Job
        {
            Id = $"VSJ-{DateTime.UtcNow:yyyyMMddHHmmssfff}",
            Type = "TTS.Synthesize",
            InPath = "",
            OutPath = outPath,
            ArgsJson = JsonSerializer.Serialize(new
            {
                text = req.Text ?? "",
                voice = string.IsNullOrWhiteSpace(req.Voice)
                    ? @"C:\\VoiceStudio\\tools\\piper\\voices\\en_US-amy-low.onnx"
                    : req.Voice
            })
        };

        var runner = new JobRunner();
        var (ok, code, message, outputs) = await runner.RunAsync(job);
        if (!ok)
        {
            Log.Error("TTS failed for variant {Variant}: {Code} {Message}", variant, code, message);
            return Results.Json(new { error = message, code }, statusCode: 500);
        }

        return Results.Json(new { path = $"/ab/out/ab_{variant}.wav" });
    });

    // Null-difference endpoint: produces ab_delta.wav under wwwroot for inspection
    app.MapPost("/api/null", (NullRequest req) =>
    {
        var wwwroot = System.IO.Path.Combine(AppContext.BaseDirectory, "wwwroot");
        var outDir  = System.IO.Path.Combine(wwwroot, "ab", "out");
        System.IO.Directory.CreateDirectory(outDir);
        var aPath = System.IO.Path.Combine(outDir, "ab_A.wav");
        var bPath = System.IO.Path.Combine(outDir, "ab_B.wav");
        var dst   = System.IO.Path.Combine(outDir, "ab_delta.wav");

        // If client didn't provide explicit filenames, use defaults above
        var a = string.IsNullOrWhiteSpace(req.A) ? aPath : req.A!;
        var b = string.IsNullOrWhiteSpace(req.B) ? bPath : req.B!;

        try
        {
            var psi = new ProcessStartInfo
            {
                FileName = "ffmpeg",
                Arguments = $"-y -i \"{a}\" -i \"{b}\" -filter_complex amerge=inputs=2,pan=mono|c0=c0-c1 -c:a pcm_s16le \"{dst}\"",
                RedirectStandardError = true,
                RedirectStandardOutput = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };
            using var p = Process.Start(psi)!;
            p.WaitForExit();
            if (p.ExitCode != 0)
            {
                var err = p.StandardError.ReadToEnd();
                Log.Error("ffmpeg null-diff failed: {Error}", err);
                return Results.Json(new { error = "ffmpeg failed" }, statusCode: 500);
            }
            return Results.Json(new { path = "/ab/out/ab_delta.wav" });
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Null test error");
            return Results.Json(new { error = ex.Message }, statusCode: 500);
        }
    });
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

public record TtsRequest(string Text, string? Voice, string? Variant);
public record NullRequest(string? A, string? B);
