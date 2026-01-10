using System;
using System.Globalization;
using Microsoft.UI.Xaml.Data;

namespace VoiceStudio.App.Converters
{
    /// <summary>
    /// Converter to format strings with placeholders.
    /// Usage: ConverterParameter="Text: {0}" where {0} will be replaced with the value.
    /// </summary>
    public class StringFormatConverter : IValueConverter
    {
        public object? Convert(object? value, Type targetType, object? parameter, string language)
        {
            if (parameter is string format)
            {
                return string.Format(CultureInfo.InvariantCulture, format, value ?? string.Empty);
            }
            return value?.ToString() ?? string.Empty;
        }

        public object? ConvertBack(object? value, Type targetType, object? parameter, string language)
        {
            throw new NotSupportedException();
        }
    }
}

