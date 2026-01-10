using Microsoft.UI.Xaml.Data;
using System;

namespace VoiceStudio.App.Converters
{
    /// <summary>
    /// Converter to check if an item is selected.
    /// Requires a ViewModel with IsItemSelected method accessible via ConverterParameter.
    /// </summary>
    public class IsSelectedConverter : IValueConverter
    {
        public object? Convert(object value, Type targetType, object parameter, string language)
        {
            // Value is the item (profile, clip, etc.)
            // Parameter should be the ViewModel or a way to access IsSelected method
            // This converter will be used with a binding to ViewModel
            
            // For now, return false - the actual check will be done via method binding in XAML
            return false;
        }

        public object? ConvertBack(object value, Type targetType, object parameter, string language)
        {
            throw new NotSupportedException();
        }
    }
}

