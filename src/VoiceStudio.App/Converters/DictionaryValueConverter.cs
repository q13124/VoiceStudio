using System;
using System.Collections.Generic;
using Microsoft.UI.Xaml.Data;

namespace VoiceStudio.App.Converters
{
    /// <summary>
    /// Converter to get a value from a dictionary by key.
    /// Usage: Value="{Binding Dictionary, Converter={StaticResource DictionaryValueConverter}, ConverterParameter='Key'}"
    /// </summary>
    public class DictionaryValueConverter : IValueConverter
    {
        public object? Convert(object value, Type targetType, object parameter, string language)
        {
            if (value is Dictionary<string, double> doubleDict && parameter is string key)
            {
                return doubleDict.TryGetValue(key, out var val) ? val : 0.0;
            }
            if (value is Dictionary<string, bool> boolDict && parameter is string key2)
            {
                return boolDict.TryGetValue(key2, out var val) ? val : false;
            }
            return null;
        }

        public object ConvertBack(object value, Type targetType, object parameter, string language)
        {
            // Dictionary updates are handled in code-behind for send levels
            // This converter is primarily for one-way binding (reading from dictionary)
            throw new NotImplementedException("Dictionary updates should be handled in code-behind");
        }
    }
}

