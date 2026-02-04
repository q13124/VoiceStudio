using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Result of text analysis for adaptive quality optimization (IDEA 53).
  /// </summary>
  public class TextAnalysisResult
  {
    /// <summary>
    /// Text complexity level (simple, moderate, complex, very_complex).
    /// </summary>
    public string Complexity { get; set; } = string.Empty;

    /// <summary>
    /// Content type classification (dialogue, narration, technical, mixed).
    /// </summary>
    public string ContentType { get; set; } = string.Empty;

    /// <summary>
    /// Word count in the text.
    /// </summary>
    public int WordCount { get; set; }

    /// <summary>
    /// Sentence count in the text.
    /// </summary>
    public int SentenceCount { get; set; }

    /// <summary>
    /// Character count in the text.
    /// </summary>
    public int CharacterCount { get; set; }

    /// <summary>
    /// Average words per sentence.
    /// </summary>
    public double AvgWordsPerSentence { get; set; }

    /// <summary>
    /// Whether the text contains dialogue (quotes).
    /// </summary>
    public bool HasDialogue { get; set; }

    /// <summary>
    /// Whether the text contains technical terms.
    /// </summary>
    public bool HasTechnicalTerms { get; set; }

    /// <summary>
    /// List of detected emotions in the text.
    /// </summary>
    public List<string> DetectedEmotions { get; set; } = new();

    /// <summary>
    /// Language code of the text.
    /// </summary>
    public string Language { get; set; } = "en";
  }
}