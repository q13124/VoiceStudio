using System.Text;
using System.Text.Json;

namespace VoiceStudio.App.Utilities
{
  /// <summary>
  /// Converts CLR property names to snake_case JSON keys (e.g. AudioId -> audio_id).
  /// </summary>
  public sealed class SnakeCaseJsonNamingPolicy : JsonNamingPolicy
  {
    public static SnakeCaseJsonNamingPolicy Instance { get; } = new SnakeCaseJsonNamingPolicy();

    private SnakeCaseJsonNamingPolicy()
    {
    }

    public override string ConvertName(string name)
    {
      if (string.IsNullOrEmpty(name))
      {
        return name;
      }

      var sb = new StringBuilder(capacity: name.Length + 8);

      for (int i = 0; i < name.Length; i++)
      {
        var c = name[i];

        if (char.IsUpper(c))
        {
          var hasPrev = i > 0;
          var hasNext = i + 1 < name.Length;

          if (hasPrev)
          {
            var prev = name[i - 1];
            var next = hasNext ? name[i + 1] : '\0';

            var prevIsLowerOrDigit = char.IsLower(prev) || char.IsDigit(prev);
            var prevIsUpper = char.IsUpper(prev);
            var nextIsLower = hasNext && char.IsLower(next);

            // Boundary cases:
            // - lower/digit -> Upper (AudioId -> audio_id)
            // - UPPER -> UpperLower (GPUSettings -> gpu_settings)
            if (prevIsLowerOrDigit || (prevIsUpper && nextIsLower))
            {
              sb.Append('_');
            }
          }

          sb.Append(char.ToLowerInvariant(c));
          continue;
        }

        sb.Append(c);
      }

      return sb.ToString();
    }
  }
}