using System;
using Microsoft.UI.Xaml.Data;

namespace VoiceStudio.App.Converters
{
    /// <summary>
    /// Converter to convert null to boolean (false if null, true if not null).
    /// Can be inverted by setting ConverterParameter="Invert".
    /// </summary>
    public class NullToBooleanConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, string language)
        {
            var isNull = value == null;
            var invert = parameter?.ToString() == "Invert";
            
            if (invert)
                return !isNull;
            return isNull;
        }

        public object ConvertBack(object value, Type targetType, object parameter, string language)
        {
            throw new NotImplementedException();
        }
    }
}

