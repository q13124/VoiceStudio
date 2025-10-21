using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Numerics;
using MathNet.Numerics.IntegralTransforms;
using NAudio.Wave;
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;

namespace VoiceStudio.ClientApp
{
    public static class SpectrogramUtil
    {
        public static void RenderSpectrogram(string inputPath, string outputPath, int fftSize = 1024, int hopSize = 256)
        {
            if (fftSize <= 0 || (fftSize & (fftSize - 1)) != 0)
                throw new ArgumentException("fftSize must be a power of two and > 0", nameof(fftSize));
            if (hopSize <= 0 || hopSize > fftSize)
                throw new ArgumentException("hopSize must be > 0 and <= fftSize", nameof(hopSize));

            // Read and convert to mono 32-bit float PCM
            float[] mono = ReadMonoAudio(inputPath, out int sampleRate);
            if (mono.Length < fftSize)
            {
                // zero-pad to at least one frame
                Array.Resize(ref mono, fftSize);
            }

            // Prepare window
            double[] window = CreateHannWindow(fftSize);

            int numFrames = 1 + (mono.Length - fftSize) / hopSize;
            if (numFrames <= 0) numFrames = 1;
            int numBins = fftSize / 2; // exclude Nyquist for display

            // Compute STFT magnitudes in dB
            double[,] mags = new double[numFrames, numBins];
            double eps = 1e-10;

            var buffer = new Complex[fftSize];
            for (int frame = 0; frame < numFrames; frame++)
            {
                int start = frame * hopSize;
                for (int i = 0; i < fftSize; i++)
                {
                    double sample = start + i < mono.Length ? mono[start + i] : 0.0;
                    buffer[i] = new Complex(sample * window[i], 0.0);
                }
                Fourier.Forward(buffer, FourierOptions.Matlab);
                for (int k = 0; k < numBins; k++)
                {
                    double mag = buffer[k].Magnitude;
                    double db = 20.0 * Math.Log10(mag + eps);
                    mags[frame, k] = db;
                }
            }

            // Normalize to 0..1 (clip to [-80, 0] dB)
            double minDb = -80.0;
            double maxDb = 0.0;

            int width = numFrames;
            int height = numBins;
            using var img = new Image<Rgba32>(width, height);

            for (int x = 0; x < width; x++)
            {
                for (int y = 0; y < height; y++)
                {
                    // invert y so low freq at bottom
                    int bin = height - 1 - y;
                    double db = mags[x, bin];
                    double norm = (db - minDb) / (maxDb - minDb);
                    if (norm < 0) norm = 0; if (norm > 1) norm = 1;
                    byte v = (byte)(norm * 255);
                    img[x, y] = new Rgba32(v, v, v, 255);
                }
            }

            Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(outputPath)) ?? ".");
            img.Save(outputPath);
        }

        private static float[] ReadMonoAudio(string path, out int sampleRate)
        {
            using var rdr = new AudioFileReader(path);
            sampleRate = rdr.WaveFormat.SampleRate;
            int channels = rdr.WaveFormat.Channels;
            var buf = new float[4096 * channels];
            var mono = new List<float>(rdr.Length > 0 ? (int)(rdr.Length / (rdr.WaveFormat.BitsPerSample / 8)) : 1024);
            int n;
            while ((n = rdr.Read(buf, 0, buf.Length)) > 0)
            {
                if (channels == 1)
                {
                    for (int i = 0; i < n; i++) mono.Add(buf[i]);
                }
                else
                {
                    for (int i = 0; i < n; i += channels)
                    {
                        double sum = 0;
                        for (int c = 0; c < channels; c++) sum += buf[i + c];
                        mono.Add((float)(sum / channels));
                    }
                }
            }
            return mono.ToArray();
        }

        private static double[] CreateHannWindow(int size)
        {
            var w = new double[size];
            for (int n = 0; n < size; n++)
            {
                w[n] = 0.5 - 0.5 * Math.Cos(2.0 * Math.PI * n / (size - 1));
            }
            return w;
        }
    }
}
