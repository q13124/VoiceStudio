using System.Diagnostics;
using System.Text;
using System.Text.Json;
using System.Runtime.InteropServices;
using VoiceStudio.IPC;

namespace VoiceStudio.CoreRuntime;

public class JobRunner
{
    // === helper methods injected ===
    static (int rc, string stdout, string stderr) RunProcess(string fileName, string arguments, string? workingDir = null)
    {
        var psi = new System.Diagnostics.ProcessStartInfo
        {
            FileName = fileName,
            Arguments = arguments,
            WorkingDirectory = workingDir ?? Environment.CurrentDirectory,
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError   = true,
            CreateNoWindow = true,
        };

        var p  = new System.Diagnostics.Process { StartInfo = psi };
        var so = new StringBuilder();
        var se = new StringBuilder();
        p.OutputDataReceived += (_, e) => { if (e.Data != null) so.AppendLine(e.Data); };
        p.ErrorDataReceived  += (_, e) => { if (e.Data != null) se.AppendLine(e.Data); };

        p.Start();
        p.BeginOutputReadLine();
        p.BeginErrorReadLine();
        p.WaitForExit();

        return (p.ExitCode, so.ToString(), se.ToString());
    }

    static string Q(string s) => $"\"{s}\"";

    private static string DetectRepoRoot()
    {
        var envRoot = Environment.GetEnvironmentVariable("VOICESTUDIO_ROOT");
        if (!string.IsNullOrWhiteSpace(envRoot) && Directory.Exists(envRoot))
            return envRoot!;

        var candidates = new[]
        {
            @"C:\\VoiceStudio",
            @"/workspace",
            AppContext.BaseDirectory,
        };
        foreach (var c in candidates)
        {
            try { if (!string.IsNullOrWhiteSpace(c) && Directory.Exists(c)) return c!; } catch { }
        }
        return Directory.GetCurrentDirectory();
    }

    private static string RepoRoot => DetectRepoRoot();

    private static string DetectPythonExe()
    {
        if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
        {
            var winCandidates = new[]
            {
                Path.Combine(RepoRoot, "workers", "python", "vsdml", ".venv", "Scripts", "python.exe"),
                @"C:\\Python311\\python.exe",
                @"C:\\Python310\\python.exe",
                @"C:\\Windows\\py.exe"
            };
            foreach (var c in winCandidates)
            {
                try { if (File.Exists(c)) return c; } catch { }
            }
            return "python";
        }
        else
        {
            var nixCandidates = new[]
            {
                Path.Combine(RepoRoot, "workers", "python", "vsdml", ".venv", "bin", "python"),
                "/usr/bin/python3",
                "/usr/local/bin/python3",
                "python3",
                "python"
            };
            foreach (var c in nixCandidates)
            {
                try { if (File.Exists(c) || c.Contains("python")) return c; } catch { }
            }
            return "python3";
        }
    }

    private static string PyExe => DetectPythonExe();
    private static string PyRoot => Path.Combine(RepoRoot, "workers", "python", "vsdml");

    public async Task<(bool ok, string? code, string? message, string[]? outputs)> RunAsync(Job job)
    {
        switch (job.Type)
        {
            case "Audio.Convert":
                return await RunCmd($@"ffmpeg -y -hide_banner -loglevel error -i ""{job.InPath}"" -ac 1 -ar 48000 -vn -map_metadata -1 -sample_fmt s16 ""{job.OutPath}""");

            case "Dataset.VAD":
                return await RunPy("vad.py", $@"--in ""{job.InPath}"" --out ""{job.OutPath}"" --aggr 2 --min 0.6");

            case "ASR.Transcribe":
                return await RunPy("asr_transcribe.py", $@"--in ""{job.InPath}"" --out ""{job.OutPath}""");

            case "Align.Run":
                // out_path is aligned.json; pass its folder to the script
                return await RunPy("align_whisperx.py", $@"--segments ""{System.IO.Path.GetDirectoryName(job.OutPath)}"" --lang en");

            case "TTS.Synthesize":
                return await RunPy(
                    "tts_piper.py",
                    $@"--text {QuoteArg(GetArg(job, "text", "Hello from VoiceStudio"))} --voice ""{GetArg(job, "voice", @"C:\VoiceStudio\tools\piper\voices\en_US-amy-low.onnx")}"" --out ""{job.OutPath}"" --piper ""C:\VoiceStudio\tools\piper\piper.exe"""
                );

            case "VC.Convert":
                return await RunPy("vc_pitch.py", $@"--in ""{job.InPath}"" --out ""{job.OutPath}"" --semitones {GetArg(job, "semitones", "3")}");

            case "Analyze.Heatmap":
            {
                var latency = GetArg(job, "latency_ms", "50");
                var outJson = job.OutPath;
                return await RunPy("analyze_heatmap.py", $@"--in ""{job.InPath}"" --out ""{outJson}"" --latency_ms {latency}");
            }

            case "Clone.CreateProfile":
            {
                var optsJson = GetArg(job, "opts_json", job.ArgsJson ?? "{}");
                return await RunPy("clone_profile.py", $@"--ref ""{job.InPath}"" --out ""{job.OutPath}"" --opts {QuoteArg(optsJson)}");
            }

            default:
                return (false, "E_NOT_IMPLEMENTED", $"Job type '{job.Type}' not implemented", null);
        }
    }

    private static string QuoteArg(string s)
        => $@"""{s.Replace(@"""", @"\""")}""";

    private static string GetArg(Job job, string key, string def)
    {
        if (string.IsNullOrWhiteSpace(job.ArgsJson)) return def;
        try
        {
            var dict = JsonSerializer.Deserialize<Dictionary<string, object?>>(job.ArgsJson);
            if (dict != null && dict.TryGetValue(key, out var v) && v != null)
                return v.ToString() ?? def;
        }
        catch { }
        return def;
    }

    private async Task<(bool, string?, string?, string[]?)> RunPy(string script, string args)
        => await RunCmd($@"""{PyExe}"" ""{System.IO.Path.Combine(PyRoot, script)}"" {args}");

    private async Task<(bool, string?, string?, string[]?)> RunCmd(string cmd)
    {
        ProcessStartInfo psi;
        if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
        {
            psi = new ProcessStartInfo
            {
                FileName = "cmd.exe",
                Arguments = $@"/C {cmd}",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true
            };
        }
        else
        {
            var escaped = cmd.Replace("\"", "\\\"");
            psi = new ProcessStartInfo
            {
                FileName = "/bin/bash",
                Arguments = $"-lc \"{escaped}\"",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true
            };
        }
        using var p = Process.Start(psi)!;
        string stderr = await p.StandardError.ReadToEndAsync();
        string stdout = await p.StandardOutput.ReadToEndAsync();
        await p.WaitForExitAsync();

        var outs = new List<string>();
        foreach (var line in (stdout + "\n" + stderr).Split(Environment.NewLine))
        {
            var t = line.Trim();
            try { if (System.IO.File.Exists(t)) outs.Add(t); } catch { }
        }

        return p.ExitCode == 0
            ? (true, null, null, outs.Count > 0 ? outs.ToArray() : null)
            : (false, "E_JOB_FAIL", $"Exit {p.ExitCode}: {stderr} {stdout}", null);
    }
}


