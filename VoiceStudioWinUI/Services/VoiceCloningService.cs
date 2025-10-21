using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using System.Text.Json;
using System.Net.Http;
using System.Net.Http.Json;
using System.Collections.Generic;
using Microsoft.UI.Xaml;

namespace VoiceStudioWinUI.Services
{
    public class VoiceCloningService
    {
        private readonly HttpClient _httpClient;
        private readonly string _baseUrl;
        private Process _pythonProcess;
        private bool _isBackendRunning = false;

        public VoiceCloningService()
        {
            _httpClient = new HttpClient();
            _baseUrl = "http://127.0.0.1:8083";
        }

        public async Task<bool> StartPythonBackendAsync()
        {
            try
            {
                if (_isBackendRunning)
                {
                    return await TestBackendConnection();
                }

                var pythonPath = "python";
                var scriptPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Assets", "services", "voice_cloning", "ultimate_web_server.py");

                if (!File.Exists(scriptPath))
                {
                    throw new FileNotFoundException($"Python script not found: {scriptPath}");
                }

                var startInfo = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = $"\"{scriptPath}\" --host 127.0.0.1 --port 8083",
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true
                };

                _pythonProcess = Process.Start(startInfo);

                // Wait for service to start
                await Task.Delay(3000);

                // Test if service is running
                _isBackendRunning = await TestBackendConnection();
                return _isBackendRunning;
            }
            catch (Exception ex)
            {
                throw new Exception($"Failed to start Python backend: {ex.Message}", ex);
            }
        }

        private async Task<bool> TestBackendConnection()
        {
            try
            {
                var response = await _httpClient.GetAsync($"{_baseUrl}/api/status");
                return response.IsSuccessStatusCode;
            }
            catch
            {
                return false;
            }
        }

        public async Task<CloneResult> CloneVoiceAsync(CloneRequest request)
        {
            try
            {
                // Ensure backend is running
                if (!_isBackendRunning)
                {
                    await StartPythonBackendAsync();
                }

                using var formData = new MultipartFormDataContent();

                // Add audio file
                var audioBytes = await File.ReadAllBytesAsync(request.AudioPath);
                var audioContent = new ByteArrayContent(audioBytes);
                audioContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("audio/wav");
                formData.Add(audioContent, "reference_audio", Path.GetFileName(request.AudioPath));

                // Add other parameters
                formData.Add(new StringContent(request.TargetText), "target_text");
                formData.Add(new StringContent(request.ModelId ?? ""), "selected_model_id");
                formData.Add(new StringContent(request.Emotion ?? "neutral"), "emotion");
                formData.Add(new StringContent(request.Accent ?? "neutral"), "accent");
                formData.Add(new StringContent(request.QualityPreset ?? "ultimate"), "quality_preset");
                formData.Add(new StringContent(request.RealTime.ToString().ToLower()), "real_time");

                // Add advanced voice settings
                formData.Add(new StringContent(request.VoiceSettings.Speed.ToString()), "speed");
                formData.Add(new StringContent(request.VoiceSettings.Pitch.ToString()), "pitch");
                formData.Add(new StringContent(request.VoiceSettings.Volume.ToString()), "volume");
                formData.Add(new StringContent(request.VoiceSettings.Language ?? "en"), "language");

                // Add processing options
                formData.Add(new StringContent(request.ProcessingOptions.UseGpu.ToString().ToLower()), "use_gpu");
                formData.Add(new StringContent(request.ProcessingOptions.MaxWorkers.ToString()), "max_workers");
                formData.Add(new StringContent(request.ProcessingOptions.TimeoutSeconds.ToString()), "timeout_seconds");
                formData.Add(new StringContent(request.ProcessingOptions.EnableCaching.ToString().ToLower()), "enable_caching");
                formData.Add(new StringContent(request.ProcessingOptions.QualityMode ?? "balanced"), "quality_mode");

                var response = await _httpClient.PostAsync($"{_baseUrl}/api/clone/ultimate", formData);

                if (response.IsSuccessStatusCode)
                {
                    var result = await response.Content.ReadFromJsonAsync<CloneResult>();
                    return result;
                }
                else
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    return new CloneResult
                    {
                        Success = false,
                        Error = $"HTTP {response.StatusCode}: {errorContent}"
                    };
                }
            }
            catch (Exception ex)
            {
                return new CloneResult
                {
                    Success = false,
                    Error = ex.Message
                };
            }
        }

        public async Task<SystemStatus> GetSystemStatusAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync($"{_baseUrl}/api/status");
                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<SystemStatus>();
                }
                return null;
            }
            catch
            {
                return null;
            }
        }

        public async Task<Dictionary<string, object>> GetAvailableModelsAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync($"{_baseUrl}/api/models");
                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<Dictionary<string, object>>();
                }
                return new Dictionary<string, object>();
            }
            catch
            {
                return new Dictionary<string, object>();
            }
        }

        public void StopPythonBackend()
        {
            try
            {
                _pythonProcess?.Kill();
                _pythonProcess?.Dispose();
                _isBackendRunning = false;
            }
            catch { }
        }

        public void Dispose()
        {
            StopPythonBackend();
            _httpClient?.Dispose();
        }
    }

    public class VoiceSettings
    {
        public double Speed { get; set; } = 1.0;
        public double Pitch { get; set; } = 1.0;
        public double Volume { get; set; } = 1.0;
        public string Language { get; set; } = "en";
    }

    public class ProcessingOptions
    {
        public bool UseGpu { get; set; } = true;
        public int MaxWorkers { get; set; } = 8;
        public int TimeoutSeconds { get; set; } = 300;
        public bool EnableCaching { get; set; } = true;
        public string QualityMode { get; set; } = "balanced";
    }

    public class CloneRequest
    {
        public string AudioPath { get; set; }
        public string TargetText { get; set; }
        public string ModelId { get; set; }
        public string Emotion { get; set; }
        public string Accent { get; set; }
        public string QualityPreset { get; set; }
        public bool RealTime { get; set; }
        public VoiceSettings VoiceSettings { get; set; } = new VoiceSettings();
        public ProcessingOptions ProcessingOptions { get; set; } = new ProcessingOptions();
    }

    public class CloneResult
    {
        public bool Success { get; set; }
        public string OutputPath { get; set; }
        public string Error { get; set; }
        public double ProcessingTime { get; set; }
        public string ModelUsed { get; set; }
    }

    public class SystemStatus
    {
        public string Status { get; set; }
        public string Service { get; set; }
        public string Version { get; set; }
        public bool ServicesAvailable { get; set; }
        public bool RealAiAvailable { get; set; }
        public string Timestamp { get; set; }
        public string[] Features { get; set; }
    }
}
