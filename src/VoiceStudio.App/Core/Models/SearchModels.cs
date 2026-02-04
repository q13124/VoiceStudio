using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace VoiceStudio.Core.Models;

/// <summary>
/// Individual search result item.
/// </summary>
public class SearchResultItem
{
  [JsonPropertyName("id")]
  public string Id { get; set; } = string.Empty;

  [JsonPropertyName("type")]
  public string Type { get; set; } = string.Empty;

  [JsonPropertyName("title")]
  public string Title { get; set; } = string.Empty;

  [JsonPropertyName("description")]
  public string? Description { get; set; }

  [JsonPropertyName("panel_id")]
  public string PanelId { get; set; } = string.Empty;

  [JsonPropertyName("preview")]
  public string? Preview { get; set; }

  [JsonPropertyName("metadata")]
  public Dictionary<string, object> Metadata { get; set; } = new();
}

/// <summary>
/// Response from global search endpoint.
/// </summary>
public class SearchResponse
{
  [JsonPropertyName("query")]
  public string Query { get; set; } = string.Empty;

  [JsonPropertyName("results")]
  public List<SearchResultItem> Results { get; set; } = new();

  [JsonPropertyName("total_results")]
  public int TotalResults { get; set; }

  [JsonPropertyName("results_by_type")]
  public Dictionary<string, int> ResultsByType { get; set; } = new();
}