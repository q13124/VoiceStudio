using System;
using Microsoft.UI.Xaml.Data;

namespace VoiceStudio.App.Converters
{
    /// <summary>
    /// Converts a value to boolean: true when non-null (and non-empty for strings), false otherwise.
    /// Can be inverted by setting ConverterParameter="Invert".
    /// </summary>
    public sealed class NullToBooleanConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, string language)
        {
            var hasValue = value switch
            {
                null => false,
                string s => !string.IsNullOrWhiteSpace(s),
                _ => true
            };

            var invert = parameter is string p && p.Equals("Invert", StringComparison.OrdinalIgnoreCase);
            return invert ? !hasValue : hasValue;
        }

        public object ConvertBack(object value, Type targetType, object parameter, string language)
        {
            throw new NotSupportedException();
        }
    }
}

