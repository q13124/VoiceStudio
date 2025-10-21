param(
  [switch]$WithMetrics
)

$ErrorActionPreference = 'Stop'

$programData = [Environment]::GetFolderPath('CommonApplicationData')
$evalDir = Join-Path $programData 'VoiceStudio/eval'
New-Item -ItemType Directory -Force -Path $evalDir | Out-Null

# Generate placeholder A/B WAVs if missing using .NET helper
$helper = @"
using System;
using System.IO;
class H {
  static void WriteWavMono16(string path, short[] pcm, int sr){
    using var fs = File.Create(path); using var bw = new BinaryWriter(fs);
    int bytes = pcm.Length*2; bw.Write(System.Text.Encoding.ASCII.GetBytes("RIFF"));
    bw.Write(36+bytes); bw.Write(System.Text.Encoding.ASCII.GetBytes("WAVE"));
    bw.Write(System.Text.Encoding.ASCII.GetBytes("fmt ")); bw.Write(16);
    bw.Write((short)1); bw.Write((short)1); bw.Write(sr); bw.Write(sr*2);
    bw.Write((short)2); bw.Write((short)16); bw.Write(System.Text.Encoding.ASCII.GetBytes("data"));
    bw.Write(bytes); foreach(var s in pcm) bw.Write(s);
  }
  static void Gen(string path, double f, int sr=16000, double sec=2.0){
    int n=(int)(sr*sec); var pcm=new short[n];
    for(int i=0;i<n;i++){ double t=i/(double)sr; double s=Math.Sin(2*Math.PI*f*t)*0.2; int v=(int)(s*short.MaxValue); if(v>32767)v=32767; if(v<-32768)v=-32768; pcm[i]=(short)v; }
    WriteWavMono16(path, pcm, sr);
  }
  public static int Main(string[] a){ var dir=a[0]; var A=Path.Combine(dir,"A.wav"); var B=Path.Combine(dir,"B.wav"); if(!File.Exists(A)) Gen(A,440); if(!File.Exists(B)) Gen(B,443); return 0; }
}
"@

$src = Join-Path $env:TEMP 'vs_eval_helper.cs'
Set-Content -Path $src -Value $helper -Encoding UTF8

& dotnet new console -o "$env:TEMP/vs_eval_helper" --force | Out-Null
Copy-Item $src "$env:TEMP/vs_eval_helper/Program.cs" -Force
Push-Location "$env:TEMP/vs_eval_helper"
& dotnet run -- "$evalDir" | Out-Null
Pop-Location

# Create null-diff file
function New-NullDiff($a,$b,$out){
  Add-Type -Language CSharp -TypeDefinition @"
using System; using System.IO; public static class ND{
  static void Read(string p, out short[] pcm, out int sr){ using var fs=File.OpenRead(p); using var br=new BinaryReader(fs);
    Span<byte> b=stackalloc byte[4]; br.Read(b); br.ReadInt32(); br.Read(b); 
    while(br.BaseStream.Position<br.BaseStream.Length){ br.Read(b); var id=System.Text.Encoding.ASCII.GetString(b); int size=br.ReadInt32();
      if(id=="fmt "){ var af=br.ReadInt16(); var ch=br.ReadInt16(); sr=br.ReadInt32(); br.ReadInt32(); br.ReadInt16(); var bits=br.ReadInt16(); if(size>16) br.ReadBytes(size-16); if(af!=1||ch!=1||bits!=16) throw new InvalidDataException(); }
      else if(id=="data"){ int samples=size/2; pcm=new short[samples]; for(int i=0;i<samples;i++) pcm[i]=br.ReadInt16(); return; }
      else br.ReadBytes(size);
    } throw new InvalidDataException();
  }
  static void Write(string p, short[] pcm, int sr){ using var fs=File.Create(p); using var bw=new BinaryWriter(fs); int bytes=pcm.Length*2; bw.Write(System.Text.Encoding.ASCII.GetBytes("RIFF")); bw.Write(36+bytes); bw.Write(System.Text.Encoding.ASCII.GetBytes("WAVE")); bw.Write(System.Text.Encoding.ASCII.GetBytes("fmt ")); bw.Write(16); bw.Write((short)1); bw.Write((short)1); bw.Write(sr); bw.Write(sr*2); bw.Write((short)2); bw.Write((short)16); bw.Write(System.Text.Encoding.ASCII.GetBytes("data")); bw.Write(bytes); foreach(var s in pcm) bw.Write(s);
  }
  public static int Main(string[] a){ Read(a[0], out var A, out var srA); Read(a[1], out var B, out var srB); if(srA!=srB) throw new Exception("SR"); int n=Math.Min(A.Length,B.Length); var D=new short[n]; for(int i=0;i<n;i++){ int v=A[i]-B[i]; if(v>32767)v=32767; if(v<-32768)v=-32768; D[i]=(short)v; } Write(a[2], D, srA); return 0; }
}
"@
  Add-Type -TypeDefinition $typeDef -Language CSharp -OutputAssembly "$env:TEMP/null_diff.dll"
  & dotnet "$env:TEMP/null_diff.dll" @($a,$b,$out)
}

New-NullDiff (Join-Path $evalDir 'A.wav') (Join-Path $evalDir 'B.wav') (Join-Path $evalDir 'null-diff.wav')

if ($WithMetrics) {
  $seg = Join-Path $evalDir 'segments'
  New-Item -ItemType Directory -Force -Path $seg | Out-Null
  $manifest = @{ segments = @(
      @{ path = (Join-Path $evalDir 'A.wav') },
      @{ path = (Join-Path $evalDir 'B.wav') }
    ) } | ConvertTo-Json -Depth 5
  Set-Content -Path (Join-Path $seg 'manifest.json') -Value $manifest -Encoding UTF8
  python3 "$(Join-Path $PSScriptRoot '..' 'SCRIPTS' 'snr_report.py')" --segments $seg
}

Write-Host "Eval assets ready at $evalDir"
