using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using System.IO;
using System;

namespace VoiceStudio.UI.Pages
{
    public class ABComparePage : PageModel
    {
        private static string DataRoot
        {
            get
            {
                string root = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
                try { Directory.CreateDirectory(Path.Combine(root, "VoiceStudio")); return root; }
                catch { /* fall through */ }
                try
                {
                    root = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
                    Directory.CreateDirectory(Path.Combine(root, "VoiceStudio"));
                    return root;
                }
                catch { /* fall through */ }
                var home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
                root = Path.Combine(home, ".local", "share");
                Directory.CreateDirectory(Path.Combine(root, "VoiceStudio"));
                return root;
            }
        }
        private static string EvalDir => Path.Combine(DataRoot, "VoiceStudio", "eval");

        public void OnGet()
        {
            Directory.CreateDirectory(EvalDir);
            EnsureDefaultSamples();
        }

        [NonAction]
        private void EnsureDefaultSamples()
        {
            var aPath = Path.Combine(EvalDir, "A.wav");
            var bPath = Path.Combine(EvalDir, "B.wav");
            if (!System.IO.File.Exists(aPath))
            {
                GenerateSine(aPath, 440.0);
            }
            if (!System.IO.File.Exists(bPath))
            {
                GenerateSine(bPath, 443.0);
            }
        }

        public IActionResult OnGetAudio(string id)
        {
            var file = id?.Equals("A", StringComparison.OrdinalIgnoreCase) == true ? "A.wav" : "B.wav";
            var path = Path.Combine(EvalDir, file);
            if (!System.IO.File.Exists(path)) return NotFound();
            return PhysicalFile(path, "audio/wav");
        }

        public IActionResult OnGetNullDiff()
        {
            var aPath = Path.Combine(EvalDir, "A.wav");
            var bPath = Path.Combine(EvalDir, "B.wav");
            var outPath = Path.Combine(EvalDir, "null-diff.wav");
            try
            {
                NullDiff(aPath, bPath, outPath);
                return PhysicalFile(outPath, "audio/wav", fileDownloadName: "null-diff.wav");
            }
            catch (Exception ex)
            {
                return new JsonResult(new { error = ex.Message }) { StatusCode = 500 };
            }
        }

        private static void GenerateSine(string path, double freq, int sampleRate = 16000, double seconds = 2.0)
        {
            int n = (int)(sampleRate * seconds);
            short[] pcm = new short[n];
            for (int i = 0; i < n; i++)
            {
                double t = i / (double)sampleRate;
                double s = Math.Sin(2 * Math.PI * freq * t) * 0.2;
                pcm[i] = (short)Math.Clamp((int)(s * short.MaxValue), short.MinValue, short.MaxValue);
            }
            WriteWavMono16(path, pcm, sampleRate);
        }

        private static void NullDiff(string aPath, string bPath, string outPath)
        {
            if (!System.IO.File.Exists(aPath) || !System.IO.File.Exists(bPath))
                throw new FileNotFoundException("Missing input WAV(s)");

            ReadWavMono16(aPath, out var aPcm, out var srA);
            ReadWavMono16(bPath, out var bPcm, out var srB);
            if (srA != srB) throw new InvalidOperationException("Sample rates differ");

            int n = Math.Min(aPcm.Length, bPcm.Length);
            short[] diff = new short[n];
            for (int i = 0; i < n; i++)
            {
                int v = aPcm[i] - bPcm[i];
                v = Math.Clamp(v, short.MinValue, short.MaxValue);
                diff[i] = (short)v;
            }
            WriteWavMono16(outPath, diff, srA);
        }

        private static void WriteWavMono16(string path, short[] pcm, int sampleRate)
        {
            using var fs = System.IO.File.Create(path);
            using var bw = new BinaryWriter(fs);
            int bytes = pcm.Length * 2;
            bw.Write(System.Text.Encoding.ASCII.GetBytes("RIFF"));
            bw.Write(36 + bytes);
            bw.Write(System.Text.Encoding.ASCII.GetBytes("WAVE"));
            bw.Write(System.Text.Encoding.ASCII.GetBytes("fmt "));
            bw.Write(16);
            bw.Write((short)1);
            bw.Write((short)1);
            bw.Write(sampleRate);
            bw.Write(sampleRate * 2);
            bw.Write((short)2);
            bw.Write((short)16);
            bw.Write(System.Text.Encoding.ASCII.GetBytes("data"));
            bw.Write(bytes);
            foreach (var s in pcm) bw.Write(s);
        }

        private static void ReadWavMono16(string path, out short[] pcm, out int sampleRate)
        {
            using var fs = System.IO.File.OpenRead(path);
            using var br = new BinaryReader(fs);
            Span<byte> buf4 = stackalloc byte[4];
            br.Read(buf4);
            if (System.Text.Encoding.ASCII.GetString(buf4) != "RIFF") throw new InvalidDataException("Not RIFF");
            br.ReadInt32();
            br.Read(buf4);
            if (System.Text.Encoding.ASCII.GetString(buf4) != "WAVE") throw new InvalidDataException("Not WAVE");
            short channels = 0; int bits = 0; sampleRate = 0;
            while (br.BaseStream.Position < br.BaseStream.Length)
            {
                br.Read(buf4);
                var id = System.Text.Encoding.ASCII.GetString(buf4);
                int size = br.ReadInt32();
                if (id == "fmt ")
                {
                    var audioFormat = br.ReadInt16();
                    channels = br.ReadInt16();
                    sampleRate = br.ReadInt32();
                    br.ReadInt32();
                    br.ReadInt16();
                    bits = br.ReadInt16();
                    if (size > 16) br.ReadBytes(size - 16);
                    if (audioFormat != 1 || channels != 1 || bits != 16)
                        throw new InvalidDataException("Expect PCM mono 16-bit");
                }
                else if (id == "data")
                {
                    int samples = size / 2;
                    pcm = new short[samples];
                    for (int i = 0; i < samples; i++) pcm[i] = br.ReadInt16();
                    return;
                }
                else
                {
                    br.ReadBytes(size);
                }
            }
            throw new InvalidDataException("data chunk not found");
        }
    }
}
