using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using System.Text.Json;
using System.Net.Http;
using System.Net.Http.Json;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Channels;
using Microsoft.UI.Xaml;
using Windows.Media.Audio;
using Windows.Media.MediaProperties;
using Windows.Storage.Streams;
using Windows.Media;

namespace VoiceStudioWinUI.Services
{
    public class RealtimeVoiceCloningService
    {
        private readonly HttpClient _httpClient;
        private readonly string _baseUrl;
        private AudioGraph _audioGraph;
        private AudioDeviceInputNode _inputNode;
        private AudioDeviceOutputNode _outputNode;
        private AudioFrameInputNode _frameInputNode;
        private Channel<AudioFrame> _audioChannel;
        private CancellationTokenSource _cancellationTokenSource;
        private bool _isRealtimeActive = false;
        private Task _processingTask;

        public event EventHandler<RealtimeStatusEventArgs> StatusChanged;
        public event EventHandler<RealtimeLatencyEventArgs> LatencyUpdated;

        public RealtimeVoiceCloningService()
        {
            _httpClient = new HttpClient();
            _baseUrl = "http://127.0.0.1:8083";
            _audioChannel = Channel.CreateUnbounded<AudioFrame>();
        }

        public async Task<bool> InitializeAudioGraphAsync()
        {
            try
            {
                var settings = new AudioGraphSettings(AudioRenderCategory.Media);
                var result = await AudioGraph.CreateAsync(settings);

                if (result.Status == AudioGraphCreationStatus.Success)
                {
                    _audioGraph = result.Graph;
                    return true;
                }
                return false;
            }
            catch (Exception ex)
            {
                throw new Exception($"Failed to initialize audio graph: {ex.Message}", ex);
            }
        }

        public async Task<bool> StartRealtimeProcessingAsync(RealtimeSettings settings)
        {
            try
            {
                if (_isRealtimeActive)
                {
                    return true;
                }

                // Initialize audio graph if not already done
                if (_audioGraph == null)
                {
                    var initialized = await InitializeAudioGraphAsync();
                    if (!initialized)
                    {
                        throw new Exception("Failed to initialize audio graph");
                    }
                }

                // Create input node based on source
                switch (settings.AudioInputSource)
                {
                    case "microphone":
                        await CreateMicrophoneInputNodeAsync();
                        break;
                    case "system":
                        await CreateSystemAudioInputNodeAsync();
                        break;
                    case "file":
                        await CreateFileStreamInputNodeAsync(settings.FilePath);
                        break;
                }

                // Create output node
                var outputResult = await _audioGraph.CreateDeviceOutputNodeAsync();
                if (outputResult.Status == AudioDeviceNodeCreationStatus.Success)
                {
                    _outputNode = outputResult.DeviceOutputNode;
                }
                else
                {
                    throw new Exception($"Failed to create output node: {outputResult.Status}");
                }

                // Start processing
                _cancellationTokenSource = new CancellationTokenSource();
                _processingTask = ProcessRealtimeAudioAsync(_cancellationTokenSource.Token);

                _audioGraph.Start();
                _isRealtimeActive = true;

                OnStatusChanged("Real-time processing started", RealtimeStatus.Active);
                return true;
            }
            catch (Exception ex)
            {
                OnStatusChanged($"Failed to start real-time processing: {ex.Message}", RealtimeStatus.Error);
                return false;
            }
        }

        public async Task StopRealtimeProcessingAsync()
        {
            try
            {
                if (!_isRealtimeActive)
                {
                    return;
                }

                _isRealtimeActive = false;
                _cancellationTokenSource?.Cancel();

                if (_processingTask != null)
                {
                    await _processingTask;
                }

                _audioGraph?.Stop();
                _inputNode?.Dispose();
                _outputNode?.Dispose();
                _frameInputNode?.Dispose();
                _audioGraph?.Dispose();

                OnStatusChanged("Real-time processing stopped", RealtimeStatus.Stopped);
            }
            catch (Exception ex)
            {
                OnStatusChanged($"Error stopping real-time processing: {ex.Message}", RealtimeStatus.Error);
            }
        }

        private async Task CreateMicrophoneInputNodeAsync()
        {
            var inputResult = await _audioGraph.CreateDeviceInputNodeAsync(MediaCategory.Media);
            if (inputResult.Status == AudioDeviceNodeCreationStatus.Success)
            {
                _inputNode = inputResult.DeviceInputNode;
                _inputNode.AddOutgoingConnection(_frameInputNode);
            }
            else
            {
                throw new Exception($"Failed to create microphone input: {inputResult.Status}");
            }
        }

        private async Task CreateSystemAudioInputNodeAsync()
        {
            // For system audio, we'll use a frame input node
            var frameInputResult = await _audioGraph.CreateFrameInputNodeAsync();
            if (frameInputResult.Status == AudioFrameInputNodeCreationStatus.Success)
            {
                _frameInputNode = frameInputResult.FrameInputNode;
                _frameInputNode.AddOutgoingConnection(_outputNode);
            }
            else
            {
                throw new Exception($"Failed to create frame input: {frameInputResult.Status}");
            }
        }

        private async Task CreateFileStreamInputNodeAsync(string filePath)
        {
            if (string.IsNullOrEmpty(filePath) || !File.Exists(filePath))
            {
                throw new Exception("Invalid file path for audio streaming");
            }

            // Create frame input node for file streaming
            var frameInputResult = await _audioGraph.CreateFrameInputNodeAsync();
            if (frameInputResult.Status == AudioFrameInputNodeCreationStatus.Success)
            {
                _frameInputNode = frameInputResult.FrameInputNode;
                _frameInputNode.AddOutgoingConnection(_outputNode);

                // Start file streaming task
                _ = Task.Run(() => StreamAudioFileAsync(filePath));
            }
            else
            {
                throw new Exception($"Failed to create file input: {frameInputResult.Status}");
            }
        }

        private async Task ProcessRealtimeAudioAsync(CancellationToken cancellationToken)
        {
            try
            {
                while (!cancellationToken.IsCancellationRequested && _isRealtimeActive)
                {
                    var startTime = DateTime.UtcNow;

                    // Process audio frame
                    if (_audioChannel.Reader.TryRead(out var audioFrame))
                    {
                        var processedFrame = await ProcessAudioFrameAsync(audioFrame);

                        if (processedFrame != null)
                        {
                            // Send to output
                            _outputNode.AddFrame(processedFrame);
                        }
                    }

                    // Calculate and report latency
                    var processingTime = (DateTime.UtcNow - startTime).TotalMilliseconds;
                    OnLatencyUpdated(processingTime);

                    // Small delay to prevent excessive CPU usage
                    await Task.Delay(10, cancellationToken);
                }
            }
            catch (OperationCanceledException)
            {
                // Expected when stopping
            }
            catch (Exception ex)
            {
                OnStatusChanged($"Real-time processing error: {ex.Message}", RealtimeStatus.Error);
            }
        }

        private async Task<AudioFrame> ProcessAudioFrameAsync(AudioFrame audioFrame)
        {
            try
            {
                // Convert audio frame to bytes
                var audioData = await ConvertAudioFrameToBytesAsync(audioFrame);

                // Send to voice cloning service
                var clonedAudio = await SendAudioForCloningAsync(audioData);

                if (clonedAudio != null)
                {
                    // Convert back to audio frame
                    return await ConvertBytesToAudioFrameAsync(clonedAudio);
                }

                return null;
            }
            catch (Exception ex)
            {
                OnStatusChanged($"Audio processing error: {ex.Message}", RealtimeStatus.Error);
                return null;
            }
        }

        private async Task<byte[]> ConvertAudioFrameToBytesAsync(AudioFrame audioFrame)
        {
            using var buffer = audioFrame.LockBuffer(AudioBufferAccessMode.Read);
            using var reference = buffer.CreateReference();

            var data = new byte[buffer.Length];
            reference.AsStream().Read(data, 0, data.Length);

            return data;
        }

        private async Task<AudioFrame> ConvertBytesToAudioFrameAsync(byte[] audioData)
        {
            var frame = new AudioFrame((uint)audioData.Length);
            using var buffer = frame.LockBuffer(AudioBufferAccessMode.Write);
            using var reference = buffer.CreateReference();

            await reference.AsStream().WriteAsync(audioData, 0, audioData.Length);

            return frame;
        }

        private async Task<byte[]> SendAudioForCloningAsync(byte[] audioData)
        {
            try
            {
                using var formData = new MultipartFormDataContent();

                // Add audio data
                var audioContent = new ByteArrayContent(audioData);
                audioContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("audio/wav");
                formData.Add(audioContent, "audio_data", "realtime_audio.wav");

                // Add real-time parameters
                formData.Add(new StringContent("realtime"), "mode");
                formData.Add(new StringContent("true"), "streaming");
                formData.Add(new StringContent("low"), "latency_mode");

                var response = await _httpClient.PostAsync($"{_baseUrl}/api/realtime/clone", formData);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadAsByteArrayAsync();
                }
                else
                {
                    OnStatusChanged($"Real-time cloning failed: {response.StatusCode}", RealtimeStatus.Error);
                    return null;
                }
            }
            catch (Exception ex)
            {
                OnStatusChanged($"Real-time cloning error: {ex.Message}", RealtimeStatus.Error);
                return null;
            }
        }

        private async Task StreamAudioFileAsync(string filePath)
        {
            try
            {
                var file = await Windows.Storage.StorageFile.GetFileFromPathAsync(filePath);
                var stream = await file.OpenAsync(Windows.Storage.FileAccessMode.Read);

                var buffer = new byte[4096];
                while (_isRealtimeActive)
                {
                    var bytesRead = await stream.ReadAsync(buffer.AsBuffer(), 4096, Windows.Storage.Streams.InputStreamOptions.None);
                    if (bytesRead == 0) break;

                    var audioData = new byte[bytesRead];
                    Array.Copy(buffer, audioData, bytesRead);

                    // Convert to audio frame and queue
                    var audioFrame = await ConvertBytesToAudioFrameAsync(audioData);
                    await _audioChannel.Writer.WriteAsync(audioFrame);
                }
            }
            catch (Exception ex)
            {
                OnStatusChanged($"File streaming error: {ex.Message}", RealtimeStatus.Error);
            }
        }

        private void OnStatusChanged(string message, RealtimeStatus status)
        {
            StatusChanged?.Invoke(this, new RealtimeStatusEventArgs { Message = message, Status = status });
        }

        private void OnLatencyUpdated(double latencyMs)
        {
            LatencyUpdated?.Invoke(this, new RealtimeLatencyEventArgs { LatencyMs = latencyMs });
        }

        public void Dispose()
        {
            StopRealtimeProcessingAsync().Wait();
            _httpClient?.Dispose();
            _cancellationTokenSource?.Dispose();
        }
    }

    public class RealtimeSettings
    {
        public string AudioInputSource { get; set; } = "microphone";
        public string FilePath { get; set; } = "";
        public int BufferSizeMs { get; set; } = 100;
        public string LatencyMode { get; set; } = "low";
        public string ModelId { get; set; } = "gpt_sovits_2";
        public VoiceSettings VoiceSettings { get; set; } = new VoiceSettings();
    }

    public class RealtimeStatusEventArgs : EventArgs
    {
        public string Message { get; set; }
        public RealtimeStatus Status { get; set; }
    }

    public class RealtimeLatencyEventArgs : EventArgs
    {
        public double LatencyMs { get; set; }
    }

    public enum RealtimeStatus
    {
        Ready,
        Active,
        Stopped,
        Error
    }
}
