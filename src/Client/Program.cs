using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Grpc.Net.Client;
using Grpc.Core;
using VoiceStudio.IPC;
using VoiceStudio.ClientApp;

class Program
{
    static async Task<int> Main(string[] args)
    {
        AppContext.SetSwitch("System.Net.Http.SocketsHttpHandler.Http2UnencryptedSupport", true);

        if (args.Length == 0)
        {
            PrintUsage();
            return 1;
        }

        if (args[0] == "--spectrogram")
        {
            if (args.Length < 3)
            {
                Console.Error.WriteLine("Usage: --spectrogram <input.wav> <output.png> [--fft N] [--hop H]");
                return 1;
            }
            string inPath = args[1];
            string outPath = args[2];
            int fft = GetIntFlag(args, "--fft", 1024);
            int hop = GetIntFlag(args, "--hop", 256);
            try
            {
                SpectrogramUtil.RenderSpectrogram(inPath, outPath, fft, hop);
                Console.WriteLine($"Spectrogram saved: {outPath}");
                return 0;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("Spectrogram error: " + ex.Message);
                return 2;
            }
        }

        if (args[0] == "--job")
        {
            if (args.Length < 2)
            {
                Console.Error.WriteLine("Usage: --job <path.json> [--stream]");
                return 1;
            }

            var jobPath = args[1];
            if (!File.Exists(jobPath))
            {
                Console.Error.WriteLine("Job file not found: " + jobPath);
                return 2;
            }

            using var doc = JsonDocument.Parse(File.ReadAllText(jobPath));
            var root = doc.RootElement;
            var job = new Job
            {
                Id       = root.TryGetProperty("Id", out var id) ? id.GetString() ?? $"VSJ-{DateTime.UtcNow:yyyyMMddHHmmss}" : $"VSJ-{DateTime.UtcNow:yyyyMMddHHmmss}",
                Type     = root.GetProperty("Type").GetString() ?? "",
                InPath   = root.TryGetProperty("InPath", out var ip) ? ip.GetString() ?? "" : "",
                OutPath  = root.TryGetProperty("OutPath", out var op) ? op.GetString() ?? "" : "",
                ArgsJson = root.TryGetProperty("ArgsJson", out var aj) ? aj.GetString() ?? "" : ""
            };

            var channel = GrpcChannel.ForAddress("http://127.0.0.1:5071");
            var client  = new Core.CoreClient(channel);

            var health = await client.HealthAsync(new Empty());
            Console.WriteLine($"Health: {health.Status} v{health.Version}");

            bool stream = args.Any(a => a == "--stream");
            if (!stream)
            {
                var res = await client.RunAsync(new RunRequest { Job = job });
                Console.WriteLine($"Run status: {res.Status}, code: {res.Code}");
                if (!string.IsNullOrWhiteSpace(res.Message))
                    Console.WriteLine("Message:\n" + res.Message.Trim());
                foreach (var p in res.Outputs)
                    Console.WriteLine("Output: " + p);
                return res.Status == "ok" ? 0 : 3;
            }
            else
            {
                var call = client.RunStream(new RunRequest { Job = job });
                string? finalStatus = null;
                string? finalCode = null;
                string? finalMessage = null;
                try
                {
                    while (await call.ResponseStream.MoveNext(CancellationToken.None))
                    {
                        var u = call.ResponseStream.Current;
                        Console.WriteLine($"Update: {u.Status} {(string.IsNullOrWhiteSpace(u.Code) ? "" : "[" + u.Code + "]")} {(string.IsNullOrWhiteSpace(u.Message) ? "" : u.Message)}");
                        foreach (var p in u.Outputs)
                            Console.WriteLine("Output: " + p);
                        if (u.Status == "ok" || u.Status == "error")
                        {
                            finalStatus = u.Status; finalCode = u.Code; finalMessage = u.Message; break;
                        }
                    }
                }
                catch (RpcException ex) when (ex.StatusCode == Grpc.Core.StatusCode.Cancelled)
                {
                    Console.Error.WriteLine("Stream cancelled.");
                }

                if (finalStatus == null)
                {
                    Console.Error.WriteLine("No final status received.");
                    return 4;
                }
                if (finalStatus == "ok") return 0;
                Console.Error.WriteLine($"Job failed: {finalCode} {finalMessage}");
                return 3;
            }
        }

        PrintUsage();
        return 1;
    }

    static void PrintUsage()
    {
        Console.WriteLine("Usage:\n  --job <job.json> [--stream]\n  --spectrogram <input.wav> <output.png> [--fft N] [--hop H]");
    }

    static int GetIntFlag(string[] args, string name, int defValue)
    {
        for (int i = 0; i < args.Length - 1; i++)
        {
            if (args[i] == name && int.TryParse(args[i + 1], out var v)) return v;
        }
        return defValue;
    }
}
