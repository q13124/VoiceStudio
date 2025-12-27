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

            double numValue;
            if (value is double d)
                numValue = d;
            else if (value is float f)
                numValue = f;
            else if (value is int i)
                numValue = i;
            else if (value is decimal dec)
                numValue = (double)dec;
            else if (double.TryParse(value.ToString(), out numValue))
                // Try to parse as double
                ;
            else
                return value.ToString() ?? string.Empty;

            string formatted = numValue.ToString(Format, CultureInfo.InvariantCulture);
            
            if (!string.IsNullOrEmpty(Suffix))
                formatted += Suffix;

            return formatted;
        }

        public object? ConvertBack(object? value, Type targetType, object? parameter, string language)
        {
            throw new NotImplementedException();
        }
    }
}

