using System;
using Microsoft.UI.Xaml.Data;
using Microsoft.UI.Xaml.Media;

namespace VoiceStudio.App.Converters;

/// <summary>
/// Converter to convert boolean to Brush (Brush for true, different Brush for false).
/// Returns green brush for true, red/gray brush for false.
/// </summary>
public class BooleanToBrushConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, string language)
    {
        if (value is bool boolValue)
        {
            // Return green for true (initialized), red/gray for false (not initialized)
            if (boolValue)
            {
                // Plugin is initialized - green
                return new SolidColorBrush(Microsoft.UI.Colors.Green);
            }
            else
            {
                // Plugin is not initialized - red/orange
                return new SolidColorBrush(Microsoft.UI.Colors.Orange);
            }
        }
        // Default to gray for unknown state
        return new SolidColorBrush(Microsoft.UI.Colors.Gray);
    }

    public object ConvertBack(object value, Type targetType, object parameter, string language)
    {
        throw new NotImplementedException("BooleanToBrushConverter does not support ConvertBack");
    }
}
