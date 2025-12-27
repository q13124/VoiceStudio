using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Data;
using System;

namespace VoiceStudio.App.Converters
{
    /// <summary>
    /// Converts an object to Visibility: Visible when not null, Collapsed when null.
    /// Can be inverted by setting ConverterParameter="Invert" (Visible when null, Collapsed when not null).
    /// </summary>
    public class NullToVisibilityConverter : IValueConverter
    {
        public object? Convert(object value, Type targetType, object parameter, string language)
        {
            var isNull = value == null;
            var invert = parameter?.ToString() == "Invert";
            
            if (invert)
                return isNull ? Visibility.Visible : Visibility.Collapsed;
            return isNull ? Visibility.Collapsed : Visibility.Visible;
        }

        public object? ConvertBack(object value, Type targetType, object parameter, string language)
        {
            throw new NotImplementedException();
        }
    }
}
