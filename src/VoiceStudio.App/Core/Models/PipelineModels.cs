using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace VoiceStudio.App.Core.Models
{
  /// <summary>
  /// Request for processing text through the voice AI pipeline.
  /// </summary>
  public class PipelineRequest
  {
    /// <summary>
    /// Text to process through the pipeline.
    /// </summary>
    [JsonPropertyName("text")]
    public string Text { get; set; } = string.Empty;

    /// <summary>
    /// Pipeline mode: "streaming", "batch", or "half_cascade".
    /// </summary>
    [JsonPropertyName("mode")]
    public string Mode { get; set; } = "streaming";

    /// <summary>
    /// LLM provider to use (e.g., "ollama", "openai").
    /// </summary>
    [JsonPropertyName("llm_provider")]
    public string? LlmProvider { get; set; }

    /// <summary>
    /// LLM model to use.
    /// </summary>
    [JsonPropertyName("llm_model")]
    public string? LlmModel { get; set; }

    /// <summary>
    /// TTS engine to use (e.g., "xtts_v2").
    /// </summary>
    [JsonPropertyName("tts_engine")]
    public string? TtsEngine { get; set; }

    /// <summary>
    /// Voice profile ID for TTS.
    /// </summary>
    [JsonPropertyName("voice_profile_id")]
    public string? VoiceProfileId { get; set; }

    /// <summary>
    /// Language code (e.g., "en").
    /// </summary>
    [JsonPropertyName("language")]
    public string Language { get; set; } = "en";

    /// <summary>
    /// Enable function calling in LLM.
    /// </summary>
    [JsonPropertyName("enable_function_calling")]
    public bool EnableFunctionCalling { get; set; } = true;
  }

  /// <summary>
  /// Response from pipeline processing.
  /// </summary>
  public class PipelineResponse
  {
    /// <summary>
    /// Generated response text from LLM.
    /// </summary>
    [JsonPropertyName("response")]
    public string Response { get; set; } = string.Empty;

    /// <summary>
    /// Audio data as base64 string (if TTS enabled).
    /// </summary>
    [JsonPropertyName("audio")]
    public string? Audio { get; set; }

    /// <summary>
    /// Processing metrics.
    /// </summary>
    [JsonPropertyName("metrics")]
    public PipelineMetrics? Metrics { get; set; }
  }

  /// <summary>
  /// Pipeline processing metrics.
  /// </summary>
  public class PipelineMetrics
  {
    /// <summary>
    /// LLM processing time in milliseconds.
    /// </summary>
    [JsonPropertyName("llm_ms")]
    public double LlmMs { get; set; }

    /// <summary>
    /// TTS processing time in milliseconds.
    /// </summary>
    [JsonPropertyName("tts_ms")]
    public double TtsMs { get; set; }

    /// <summary>
    /// Total processing time in milliseconds.
    /// </summary>
    [JsonPropertyName("total_ms")]
    public double TotalMs { get; set; }

    /// <summary>
    /// Time to first token in milliseconds.
    /// </summary>
    [JsonPropertyName("time_to_first_token_ms")]
    public double? TimeToFirstTokenMs { get; set; }
  }

  /// <summary>
  /// Response containing available pipeline providers.
  /// </summary>
  public class PipelineProvidersResponse
  {
    /// <summary>
    /// Available LLM providers.
    /// </summary>
    [JsonPropertyName("llm_providers")]
    public List<PipelineProvider> LlmProviders { get; set; } = new();

    /// <summary>
    /// Available STT providers.
    /// </summary>
    [JsonPropertyName("stt_providers")]
    public List<PipelineProvider> SttProviders { get; set; } = new();

    /// <summary>
    /// Available TTS providers.
    /// </summary>
    [JsonPropertyName("tts_providers")]
    public List<PipelineProvider> TtsProviders { get; set; } = new();

    /// <summary>
    /// Available S2S providers.
    /// </summary>
    [JsonPropertyName("s2s_providers")]
    public List<PipelineProvider> S2SProviders { get; set; } = new();
  }

  /// <summary>
  /// A pipeline provider (engine).
  /// </summary>
  public class PipelineProvider
  {
    /// <summary>
    /// Provider ID.
    /// </summary>
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// Provider display name.
    /// </summary>
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Provider type (llm, stt, tts, s2s).
    /// </summary>
    [JsonPropertyName("type")]
    public string Type { get; set; } = string.Empty;

    /// <summary>
    /// Whether the provider is currently available.
    /// </summary>
    [JsonPropertyName("available")]
    public bool Available { get; set; }

    /// <summary>
    /// Provider capabilities.
    /// </summary>
    [JsonPropertyName("capabilities")]
    public List<string> Capabilities { get; set; } = new();
  }

  /// <summary>
  /// Pipeline metrics and usage statistics.
  /// </summary>
  public class PipelineMetricsResponse
  {
    /// <summary>
    /// Total number of pipeline requests.
    /// </summary>
    [JsonPropertyName("total_requests")]
    public int TotalRequests { get; set; }

    /// <summary>
    /// Total input tokens used.
    /// </summary>
    [JsonPropertyName("total_input_tokens")]
    public long TotalInputTokens { get; set; }

    /// <summary>
    /// Total output tokens generated.
    /// </summary>
    [JsonPropertyName("total_output_tokens")]
    public long TotalOutputTokens { get; set; }

    /// <summary>
    /// Average latency in milliseconds.
    /// </summary>
    [JsonPropertyName("avg_latency_ms")]
    public double AvgLatencyMs { get; set; }

    /// <summary>
    /// Estimated cost in USD.
    /// </summary>
    [JsonPropertyName("estimated_cost_usd")]
    public double EstimatedCostUsd { get; set; }
  }
}
