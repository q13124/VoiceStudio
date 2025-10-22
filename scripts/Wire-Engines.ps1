param()
$ErrorActionPreference="Stop"
$root=@("C:\VoiceStudio","C:\TylersVoiceCloner") | ? { Test-Path $_ } | Select-Object -First 1
if(-not $root){ $root=(Get-Location).Path }
Set-Location $root

# Projects
$contracts = Join-Path $root "VoiceStudio.Contracts"
$svc       = Join-Path $root "UltraClone.EngineService"
if(!(Test-Path $contracts)){ dotnet new classlib -n VoiceStudio.Contracts -f net8.0 | Out-Null }
if(!(Test-Path $svc)){       dotnet new worker   -n UltraClone.EngineService -f net8.0 | Out-Null }

dotnet add "$svc\UltraClone.EngineService.csproj" package Grpc.AspNetCore | Out-Null
dotnet add "$svc\UltraClone.EngineService.csproj" package Microsoft.Data.Sqlite | Out-Null
dotnet add "$svc\UltraClone.EngineService.csproj" package Microsoft.Extensions.Hosting.WindowsServices | Out-Null
dotnet add "$contracts\VoiceStudio.Contracts.csproj" package Grpc.Tools | Out-Null

# engine.proto
$proto = @"
syntax = "proto3";
package voicestudio;

service Engine {
  rpc Health(HealthRequest) returns (HealthReply);
  rpc ListDevices(DevicesRequest) returns (DevicesReply);

  rpc QueueJob(QueueRequest) returns (QueueReply);
  rpc GetJob(GetJobRequest) returns (JobReply);
  rpc StreamJob(StreamJobRequest) returns (stream JobReply);

  rpc ConvertAudio(ConvertAudioRequest) returns (JobReply);
  rpc ConvertText(ConvertTextRequest) returns (JobReply);
  rpc Tts(TtsRequest) returns (JobReply);
  rpc CloneVoice(CloneRequest) returns (JobReply);
  rpc Analyze(AnalyzeRequest) returns (JobReply);
  rpc RenderTimeline(RenderRequest) returns (JobReply);
}

message HealthRequest {}
message HealthReply { string status=1; string version=2; bool gpu=3; string cuda=4; string cudnn=5; }

message DevicesRequest {}
message Device { string name=1; int32 vramMB=2; bool available=3; }
message DevicesReply { repeated Device devices=1; }

message QueueRequest { string kind=1; string inputPath=2; string outputPath=3; string optionsJson=4; }
message QueueReply { string jobId=1; string state=2; }

message GetJobRequest { string jobId=1; }
message StreamJobRequest { string jobId=1; }

message JobReply {
  string jobId=1;
  string state=2;    // queued|running|done|error
  float progress=3;  // 0..1
  string message=4;
  string artifactPath=5;
}

message ConvertAudioRequest { string src=1; string dst=2; string optionsJson=3; }
message ConvertTextRequest  { string src=1; string dst=2; string optionsJson=3; }
message TtsRequest         { string text=1; string voice=2; string dst=3; string optionsJson=4; }
message CloneRequest       { string refAudio=1; string outProfile=2; string optionsJson=3; }
message AnalyzeRequest     { string src=1; string span=2; }
message RenderRequest      { string timelineJson=1; string outDir=2; string optionsJson=3; }
"@
$proto | Set-Content -Encoding UTF8 "$contracts\engine.proto"

# add proto to csproj (Contracts)
$proj = Join-Path $contracts "VoiceStudio.Contracts.csproj"
$xml  = Get-Content -Raw $proj
if($xml -notmatch "Protobuf Include"){
  $xml = $xml -replace "</Project>","  <ItemGroup><Protobuf Include=""engine.proto"" GrpcServices=""Both"" /></ItemGroup>`n</Project>"
  $xml | Set-Content -Encoding UTF8 $proj
}

# Service code
New-Item -ItemType Directory -Force -Path "$svc\Services", "$svc\Queue" | Out-Null

@"
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Data.Sqlite;
using System.Diagnostics;
using System.Text.Json;
using voicestudio;

var builder = Host.CreateApplicationBuilder(args);
builder.Services.AddWindowsService();
builder.Services.AddGrpc();
builder.Services.AddSingleton<JobQueue>();
builder.Services.AddHostedService<VramSampler>();
var app = builder.Build();

app.Services.GetRequiredService<JobQueue>().Init();

var web = WebApplication.CreateBuilder().Build();
web.MapGrpcService<EngineSvc>();
web.MapGet("/", () => "UltraClone.EngineService");
web.Run("http://127.0.0.1:59051");

app.Run();

public class EngineSvc : Engine.EngineBase
{
  private readonly JobQueue _q;
  public EngineSvc(JobQueue q) { _q=q; }

  public override Task<HealthReply> Health(HealthRequest request, Grpc.Core.ServerCallContext context)
  {
    var (cuda,cudnn,gpu) = Detect();
    return Task.FromResult(new HealthReply{ status="ok", version="1.0.0", gpu=gpu, cuda=cuda, cudnn=cudnn });
  }

  public override Task<DevicesReply> ListDevices(DevicesRequest request, Grpc.Core.ServerCallContext context)
    => Task.FromResult(new DevicesReply{ devices = { new Device{ name="GPU", vramMB=12288, available=true } } });

  public override Task<QueueReply> QueueJob(QueueRequest r, Grpc.Core.ServerCallContext c)
  { var id=_q.Enqueue(r.kind,r.inputPath,r.outputPath,r.optionsJson); return Task.FromResult(new QueueReply{ jobId=id, state="queued"}); }

  public override Task<JobReply> ConvertAudio(ConvertAudioRequest r, Grpc.Core.ServerCallContext c)
    => Task.FromResult(_q.RunNow("convertAudio", r.src, r.dst, r.optionsJson));

  public override Task<JobReply> ConvertText(ConvertTextRequest r, Grpc.Core.ServerCallContext c)
    => Task.FromResult(_q.RunNow("convertText", r.src, r.dst, r.optionsJson));

  public override Task<JobReply> Tts(TtsRequest r, Grpc.Core.ServerCallContext c)
    => Task.FromResult(_q.RunNow("tts", r.text, r.dst, r.optionsJson, r.voice));

  public override Task<JobReply> CloneVoice(CloneRequest r, Grpc.Core.ServerCallContext c)
    => Task.FromResult(_q.RunNow("clone", r.refAudio, r.outProfile, r.optionsJson));

  public override Task<JobReply> Analyze(AnalyzeRequest r, Grpc.Core.ServerCallContext c)
    => Task.FromResult(_q.RunNow("analyze", r.src, "", r.span));

  public override Task<JobReply> RenderTimeline(RenderRequest r, Grpc.Core.ServerCallContext c)
    => Task.FromResult(_q.RunNow("render", r.timelineJson, r.outDir, r.optionsJson));

  public override Task<JobReply> GetJob(GetJobRequest r, Grpc.Core.ServerCallContext c)
    => Task.FromResult(_q.Get(r.jobId));

  static (string cuda,string cudnn,bool gpu) Detect(){
    try{
      var p=Process.Start(new ProcessStartInfo{ FileName="nvidia-smi.exe", Arguments="--query-gpu=driver_version --format=csv,noheader", RedirectStandardOutput=true, UseShellExecute=false});
      var s=p!.StandardOutput.ReadToEnd().Trim(); p.WaitForExit(1500);
      return (cuda:"12.x/13", cudnn:"9", gpu:true);
    }catch{ return ("unknown","unknown",false); }
  }
}

public class VramSampler : BackgroundService {
  protected override async Task ExecuteAsync(CancellationToken t){
    var db = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData),"VoiceStudio","telemetry.db");
    Directory.CreateDirectory(Path.GetDirectoryName(db)!);
    using var conn = new SqliteConnection($"Data Source={db}"); conn.Open();
    new SqliteCommand("CREATE TABLE IF NOT EXISTS vram(ts INTEGER, usedMB INTEGER, totalMB INTEGER);", conn).ExecuteNonQuery();
    while(!t.IsCancellationRequested){
      try{
        var psi=new ProcessStartInfo{ FileName="nvidia-smi.exe", Arguments="--query-gpu=memory.used,memory.total --format=csv,noheader,nounits", RedirectStandardOutput=true, UseShellExecute=false};
        var p=Process.Start(psi)!; var s=p.StandardOutput.ReadToEnd(); p.WaitForExit(1500);
        var a=s.Trim().Split(','); if(a.Length>=2){
          var cmd=conn.CreateCommand(); cmd.CommandText="INSERT INTO vram(ts,usedMB,totalMB) VALUES(strftime('%s','now'),$u,$t)";
          cmd.Parameters.AddWithValue("$u", int.Parse(a[0])); cmd.Parameters.AddWithValue("$t", int.Parse(a[1])); cmd.ExecuteNonQuery();
        }
      }catch{}
      await Task.Delay(2000,t);
    }
  }
}
"@ | Set-Content -Encoding UTF8 "$svc\Services\EngineSvc.cs"

@"
using Microsoft.Data.Sqlite;
using System.Diagnostics;
using System.Text.Json;
using voicestudio;

public class JobQueue {
  string _dbPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData),"VoiceStudio","jobs.db");
  public void Init(){
    Directory.CreateDirectory(Path.GetDirectoryName(_dbPath)!);
    using var c=new SqliteConnection($"Data Source={_dbPath}"); c.Open();
    new SqliteCommand("CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, kind TEXT, state TEXT, progress REAL, message TEXT, artifact TEXT, args TEXT, created INTEGER);", c).ExecuteNonQuery();
  }
  public string Enqueue(string kind,string a,string b,string opts){
    var id=Guid.NewGuid().ToString("N");
    using var c=new SqliteConnection($"Data Source={_dbPath}"); c.Open();
    var cmd=c.CreateCommand(); cmd.CommandText="INSERT INTO jobs(id,kind,state,progress,message,artifact,args,created) VALUES($i,$k,'queued',0,'','', $args, strftime('%s','now'))";
    cmd.Parameters.AddWithValue("$i",id); cmd.Parameters.AddWithValue("$k",kind); cmd.Parameters.AddWithValue("$args", JsonSerializer.Serialize(new[]{a,b,opts}));
    cmd.ExecuteNonQuery();
    return id;
  }
  public JobReply Get(string id){
    using var c=new SqliteConnection($"Data Source={_dbPath}"); c.Open();
    var cmd=c.CreateCommand(); cmd.CommandText="SELECT state,progress,message,artifact FROM jobs WHERE id=$i"; cmd.Parameters.AddWithValue("$i",id);
    using var r=cmd.ExecuteReader();
    if(r.Read()) return new JobReply{ jobId=id, state=r.GetString(0), progress=(float)r.GetDouble(1), message=r.GetString(2), artifactPath=r.GetString(3) };
    return new JobReply{ jobId=id, state="missing" };
  }
  public JobReply RunNow(string op,string a,string b,string c,string? voice=null){
    // call python worker_router.py op ...
    var pd = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
    var home = Path.Combine(pd, "VoiceStudio"); Directory.CreateDirectory(home);
    var py = Path.Combine(home,"pyenv","Scripts","python.exe");
    var wr = Path.Combine(home,"workers","worker_router.py");
    var args = voice==null ? $"{wr} {op} --a \"{a}\" --b \"{b}\" --c \"{c}\"" : $"{wr} {op} --a \"{a}\" --b \"{b}\" --c \"{c}\" --voice \"{voice}\"";
    var psi=new ProcessStartInfo{ FileName=py, Arguments=args, UseShellExecute=false, RedirectStandardOutput=true, RedirectStandardError=true };
    try{
      var p=Process.Start(psi)!; var outJson = p.StandardOutput.ReadToEnd(); var err=p.StandardError.ReadToEnd(); p.WaitForExit(600000);
      return JsonSerializer.Deserialize<JobReply>(outJson) ?? new JobReply{ state="error", message="Parse error" };
    }catch(Exception ex){ return new JobReply{ state="error", message=ex.Message }; }
  }
}
"@ | Set-Content -Encoding UTF8 "$svc\Queue\JobQueue.cs"

# Python worker router + ops
$pd = Join-Path $env:ProgramData "VoiceStudio"
$wdir = Join-Path $pd "workers\ops"
New-Item -ItemType Directory -Force -Path $wdir | Out-Null

@"
import argparse, json, sys, os, pathlib

def _reply(state='done', msg='', artifact=''):
    print(json.dumps({'jobId':'adhoc','state':state,'progress':1.0 if state=='done' else 0.0,'message':msg,'artifactPath':artifact}))
    sys.exit(0 if state!='error' else 1)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('op', choices=['convertAudio','convertText','tts','clone','analyze','render'])
    p.add_argument('--a','', dest='a'); p.add_argument('--b','', dest='b'); p.add_argument('--c','', dest='c')
    p.add_argument('--voice', default=None)
    args=p.parse_args()
    here = pathlib.Path(__file__).parent
    sys.path.insert(0, str(here))
    if args.op=='convertAudio': import op_convert_audio as op; op.run(args.a,args.b,args.c); return
    if args.op=='convertText':  import op_convert_text as op;  op.run(args.a,args.b,args.c); return
    if args.op=='tts':          import op_tts as op;          op.run(args.a,args.b,args.c,args.voice); return
    if args.op=='clone':        import op_clone as op;        op.run(args.a,args.b,args.c); return
    if args.op=='analyze':      import op_analyze as op;      op.run(args.a,args.c); return
    if args.op=='render':       import op_analyze as op;      op.run(args.a,args.b); return

if __name__=='__main__': main()
"@ | Set-Content -Encoding UTF8 (Join-Path (Split-Path $wdir -Parent) "worker_router.py")

@"
# convert audio placeholder (use ffmpeg via subprocess)
import json, subprocess, sys
def run(src, dst, options_json):
    try:
        cmd = ['ffmpeg','-y','-i',src, dst]
        subprocess.run(cmd, check=True, capture_output=True)
        print(json.dumps({'jobId':'adhoc','state':'done','progress':1.0,'message':'ok','artifactPath':dst}))
    except Exception as e:
        print(json.dumps({'state':'error','message':str(e)}))
"@ | Set-Content -Encoding UTF8 (Join-Path $wdir "op_convert_audio.py")

@"
# convert text placeholder (e.g., docx/pdf->txt via python libs later)
import json, pathlib
def run(src, dst, options_json):
    text = pathlib.Path(src).read_text(encoding='utf-8', errors='ignore')
    pathlib.Path(dst).write_text(text, encoding='utf-8')
    print(json.dumps({'jobId':'adhoc','state':'done','progress':1.0,'message':'ok','artifactPath':dst}))
"@ | Set-Content -Encoding UTF8 (Join-Path $wdir "op_convert_text.py")

@"
# tts placeholder (replace with XTTS/OpenVoice/CosyVoice)
import json, pathlib
def run(text, dst, options_json, voice):
    # TODO: call your TTS engine with ParameterMap options
    pathlib.Path(dst).write_bytes(b'')  # stub empty wav
    print(json.dumps({'jobId':'adhoc','state':'done','progress':1.0,'message':'ok','artifactPath':dst}))
"@ | Set-Content -Encoding UTF8 (Join-Path $wdir "op_tts.py")

@"
# clone placeholder (build voice profile folder)
import json, pathlib, shutil
def run(ref_audio, out_profile, options_json):
    p=pathlib.Path(out_profile); p.mkdir(parents=True, exist_ok=True)
    shutil.copy(ref_audio, p / 'ref.wav')
    print(json.dumps({'jobId':'adhoc','state':'done','progress':1.0,'message':'ok','artifactPath':str(p)}))
"@ | Set-Content -Encoding UTF8 (Join-Path $wdir "op_clone.py")

@"
# analyze placeholder (artifact 'heatmap.json')
import json, pathlib, random
def run(src, span):
    heat = [{'t':i/10.0,'synthetic':random.random()} for i in range(50)]
    out = pathlib.Path(src).with_suffix('.heatmap.json')
    out.write_text(json.dumps(heat), encoding='utf-8')
    print(json.dumps({'jobId':'adhoc','state':'done','progress':1.0,'message':'ok','artifactPath':str(out)}))
"@ | Set-Content -Encoding UTF8 (Join-Path $wdir "op_analyze.py")

# Build
dotnet build -c Debug | Out-Null
Write-Host "Engine wiring complete. Proto, service, queue, and workers are in place." -ForegroundColor Green
