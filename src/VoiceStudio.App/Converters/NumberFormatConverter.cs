using System;
using System.Globalization;
using Microsoft.UI.Xaml.Data;

namespace VoiceStudio.App.Converters
{
    /// <summary>
    /// Converter to format numbers with a specified format string.
    /// Used for WinUI 3 which doesn't support StringFormat on x:Bind.
    /// </summary>
    public class NumberFormatConverter : IValueConverter
    {
        /// <summary>
        /// Format string (e.g., "F0", "F1", "N2", "C")
        /// </summary>
        public string Format { get; set; } = "F0";

        /// <summary>
        /// Optional suffix to append (e.g., "%", "ms")
        /// </summary>
        public string? Suffix { get; set; }

        public object? Convert(object? value, Type targetType, object? parameter, string language)
        {
            if (value == null)
                return string.Empty;

            var format = Format;
            if (parameter is string p && !string.IsNullOrWhiteSpace(p))
            {
                format = p;
            }

            string formatted;
            if (value is IFormattable formattable)
            {
                formatted = formattable.ToString(format, CultureInfo.InvariantCulture);
            }
            else if (double.TryParse(
                value.ToString(),
                NumberStyles.Float | NumberStyles.AllowThousands,
                CultureInfo.InvariantCulture,
                out var numValue))
            {
                formatted = numValue.ToString(format, CultureInfo.InvariantCulture);
            }
            else
            {
                return value.ToString() ?? string.Empty;
            }
            
            if (!string.IsNullOrEmpty(Suffix))
                formatted += Suffix;

            return formatted;
        }

        public object? ConvertBack(object? value, Type targetType, object? parameter, string language)
        {
            throw new NotSupportedException();
        }
    }
}

