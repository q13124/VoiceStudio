using Microsoft.UI.Xaml.Data;
using System;

namespace VoiceStudio.App.Converters
{
    /// <summary>
    /// Converter to subtract a value from a number.
    /// Usage: ConverterParameter="20" to subtract 20.
    /// </summary>
    public class SubtractConverter : IValueConverter
    {
        public object? Convert(object value, Type targetType, object parameter, string language)
        {
            if (value is double doubleValue && parameter is string paramStr && double.TryParse(paramStr, out var subtractValue))
            {
                return doubleValue - subtractValue;
            }
            if (value is int intValue && parameter is string paramStr2 && int.TryParse(paramStr2, out var subtractValue2))
            {
                return intValue - subtractValue2;
            }
            return value;
        }

        public object ConvertBack(object value, Type targetType, object parameter, string language)
        {
            throw new NotSupportedException();
        }
    }
}

