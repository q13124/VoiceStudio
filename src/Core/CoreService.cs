using System;
using System.Threading.Tasks;
using Grpc.Core;
using VoiceStudio.IPC;

namespace VoiceStudio.CoreRuntime
{
    public class CoreService : Core.CoreBase
    {
        private readonly JobRunner _runner;
        public CoreService(JobRunner runner) { _runner = runner; }

        public override Task<HealthReply> Health(Empty request, ServerCallContext context)
            => Task.FromResult(new HealthReply { Status = "OK", Version = "0.1.0" });

        public override async Task<RunResponse> Run(RunRequest request, ServerCallContext context)
        {
            var job = request.Job;
            try
            {
                var (ok, code, message, outputs) = await _runner.RunAsync(job);
                var resp = new RunResponse { Status = ok ? "ok" : "error", Code = code ?? "", Message = message ?? "" };
                if (outputs != null) resp.Outputs.AddRange(outputs);
                return resp;
            }
            catch (Exception ex)
            {
                return new RunResponse { Status = "error", Code = "E_UNHANDLED", Message = ex.Message };
            }
        }

        public override async Task RunStream(RunRequest request, IServerStreamWriter<RunUpdate> responseStream, ServerCallContext context)
        {
            var job = request.Job;
            try
            {
                // starting
                await responseStream.WriteAsync(new RunUpdate { Status = "starting", Code = "", Message = "" });

                var jobTask = _runner.RunAsync(job);

                // periodic heartbeats while running
                while (!jobTask.IsCompleted && !context.CancellationToken.IsCancellationRequested)
                {
                    await responseStream.WriteAsync(new RunUpdate { Status = "running", Code = "", Message = DateTime.UtcNow.ToString("O") });
                    try
                    {
                        await Task.WhenAny(jobTask, Task.Delay(1000, context.CancellationToken));
                    }
                    catch (TaskCanceledException)
                    {
                        break;
                    }
                }

                if (context.CancellationToken.IsCancellationRequested)
                {
                    // client went away; just stop
                    return;
                }

                if (jobTask.IsFaulted)
                {
                    var ex = jobTask.Exception?.GetBaseException();
                    await responseStream.WriteAsync(new RunUpdate { Status = "error", Code = "E_UNHANDLED", Message = ex?.Message ?? "Unknown error" });
                    return;
                }

                var (ok, code, message, outputs) = await jobTask;
                var final = new RunUpdate { Status = ok ? "ok" : "error", Code = code ?? "", Message = message ?? "" };
                if (outputs != null) final.Outputs.AddRange(outputs);
                await responseStream.WriteAsync(final);
            }
            catch (Exception ex)
            {
                try { await responseStream.WriteAsync(new RunUpdate { Status = "error", Code = "E_UNHANDLED", Message = ex.Message }); } catch { }
            }
        }
    }
}
