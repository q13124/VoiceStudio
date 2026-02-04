using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;

namespace VoiceStudio.App.Utilities
{
  /// <summary>
  /// Utility class for input validation with user-friendly error messages.
  /// </summary>
  public static class InputValidator
  {
    /// <summary>
    /// Validates a profile name.
    /// </summary>
    public static ValidationResult ValidateProfileName(string? name)
    {
      if (string.IsNullOrWhiteSpace(name))
      {
        return ValidationResult.Error("Profile name is required.");
      }

      if (name.Length > 100)
      {
        return ValidationResult.Error("Profile name cannot exceed 100 characters.");
      }

      if (name.Length < 2)
      {
        return ValidationResult.Error("Profile name must be at least 2 characters.");
      }

      // Check for invalid characters
      if (name.Any(c => char.IsControl(c)))
      {
        return ValidationResult.Error("Profile name contains invalid characters.");
      }

      return ValidationResult.Success();
    }

    /// <summary>
    /// Validates a project name.
    /// </summary>
    public static ValidationResult ValidateProjectName(string? name)
    {
      if (string.IsNullOrWhiteSpace(name))
      {
        return ValidationResult.Error("Project name is required.");
      }

      if (name.Length > 100)
      {
        return ValidationResult.Error("Project name cannot exceed 100 characters.");
      }

      if (name.Length < 2)
      {
        return ValidationResult.Error("Project name must be at least 2 characters.");
      }

      // Check for invalid characters (no path separators)
      if (name.Contains('/') || name.Contains('\\') || name.Contains(':'))
      {
        return ValidationResult.Error("Project name cannot contain path separators.");
      }

      return ValidationResult.Success();
    }

    /// <summary>
    /// Validates text input for synthesis.
    /// </summary>
    public static ValidationResult ValidateSynthesisText(string? text)
    {
      if (string.IsNullOrWhiteSpace(text))
      {
        return ValidationResult.Error("Text is required for synthesis.");
      }

      if (text.Length > 10000)
      {
        return ValidationResult.Error("Text cannot exceed 10,000 characters.");
      }

      return ValidationResult.Success();
    }

    /// <summary>
    /// Validates a language code.
    /// </summary>
    public static ValidationResult ValidateLanguageCode(string? language)
    {
      if (string.IsNullOrWhiteSpace(language))
      {
        return ValidationResult.Error("Language is required.");
      }

      // ISO 639-1 language codes are 2 characters
      if (language.Length != 2 || !Regex.IsMatch(language, @"^[a-z]{2}$", RegexOptions.IgnoreCase))
      {
        return ValidationResult.Error("Language must be a valid 2-letter language code (e.g., 'en', 'es', 'fr').");
      }

      return ValidationResult.Success();
    }

    /// <summary>
    /// Validates a track name.
    /// </summary>
    public static ValidationResult ValidateTrackName(string? name)
    {
      if (string.IsNullOrWhiteSpace(name))
      {
        return ValidationResult.Error("Track name is required.");
      }

      if (name.Length > 100)
      {
        return ValidationResult.Error("Track name cannot exceed 100 characters.");
      }

      return ValidationResult.Success();
    }

    /// <summary>
    /// Validates a macro name.
    /// </summary>
    public static ValidationResult ValidateMacroName(string? name)
    {
      if (string.IsNullOrWhiteSpace(name))
      {
        return ValidationResult.Error("Macro name is required.");
      }

      if (name.Length > 100)
      {
        return ValidationResult.Error("Macro name cannot exceed 100 characters.");
      }

      return ValidationResult.Success();
    }

    /// <summary>
    /// Validates a numeric value within a range.
    /// </summary>
    public static ValidationResult ValidateNumericRange(double value, double min, double max, string fieldName)
    {
      if (value < min || value > max)
      {
        return ValidationResult.Error($"{fieldName} must be between {min} and {max}.");
      }

      return ValidationResult.Success();
    }

    /// <summary>
    /// Validates a file path format.
    /// </summary>
    public static ValidationResult ValidateFilePath(string? path)
    {
      if (string.IsNullOrWhiteSpace(path))
      {
        return ValidationResult.Error("File path is required.");
      }

      // Check for invalid path characters
      var invalidChars = System.IO.Path.GetInvalidPathChars();
      if (path.Any(c => invalidChars.Contains(c)))
      {
        return ValidationResult.Error("File path contains invalid characters.");
      }

      return ValidationResult.Success();
    }

    /// <summary>
    /// Validates an audio file extension.
    /// </summary>
    public static ValidationResult ValidateAudioFileExtension(string? filename)
    {
      if (string.IsNullOrWhiteSpace(filename))
      {
        return ValidationResult.Error("Filename is required.");
      }

      var validExtensions = new[] { ".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac" };
      var extension = System.IO.Path.GetExtension(filename).ToLowerInvariant();

      if (!validExtensions.Contains(extension))
      {
        return ValidationResult.Error($"Audio file must be one of: {string.Join(", ", validExtensions)}");
      }

      return ValidationResult.Success();
    }
  }

  /// <summary>
  /// Represents the result of a validation operation.
  /// </summary>
  public class ValidationResult
  {
    public bool IsValid { get; }
    public string? ErrorMessage { get; }

    private ValidationResult(bool isValid, string? errorMessage = null)
    {
      IsValid = isValid;
      ErrorMessage = errorMessage;
    }

    public static ValidationResult Success() => new ValidationResult(true);
    public static ValidationResult Error(string message) => new ValidationResult(false, message);
  }
}