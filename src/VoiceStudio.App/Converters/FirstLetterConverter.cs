using Microsoft.UI.Xaml.Data;
using System;

namespace VoiceStudio.App.Converters
{
    /// <summary>
    /// Converter to get the first letter of a string.
    /// </summary>
    public class FirstLetterConverter : IValueConverter
    {
        public object? Convert(object value, Type targetType, object parameter, string language)
        {
            if (value is string str && !string.IsNullOrWhiteSpace(str))
            {
                try
                {
                    return str.Substring(0, Math.Min(1, str.Length)).ToUpperInvariant();
                }
                catch
                {
                    return "?";
                }
            }
            return "?";
        }

        public object ConvertBack(object value, Type targetType, object parameter, string language)
        {
            throw new NotSupportedException();
        }
    }
}

