using Microsoft.UI.Xaml.Data;
using Microsoft.UI.Xaml.Media;
using System;
using Windows.UI;

namespace VoiceStudio.App.Converters
{
    /// <summary>
    /// Converter to convert a hex color string to a SolidColorBrush.
    /// </summary>
    public class StringToBrushConverter : IValueConverter
    {
        public object? Convert(object value, Type targetType, object parameter, string language)
        {
            if (value is string colorString)
            {
                try
                {
                    // Parse hex color (#AARRGGBB or #RRGGBB)
                    if (colorString.StartsWith("#"))
                    {
                        colorString = colorString.Substring(1);
                    }

                    if (colorString.Length == 8)
                    {
                        // ARGB format
                        var a = System.Convert.ToByte(colorString.Substring(0, 2), 16);
                        var r = System.Convert.ToByte(colorString.Substring(2, 2), 16);
                        var g = System.Convert.ToByte(colorString.Substring(4, 2), 16);
                        var b = System.Convert.ToByte(colorString.Substring(6, 2), 16);
                        return new SolidColorBrush(Color.FromArgb(a, r, g, b));
                    }
                    else if (colorString.Length == 6)
                    {
                        // RGB format (assume full opacity)
                        var r = System.Convert.ToByte(colorString.Substring(0, 2), 16);
                        var g = System.Convert.ToByte(colorString.Substring(2, 2), 16);
                        var b = System.Convert.ToByte(colorString.Substring(4, 2), 16);
                        return new SolidColorBrush(Color.FromArgb(255, r, g, b));
                    }
                }
                catch
                {
                    // Return default color on parse error
                }
            }

            return new SolidColorBrush(Color.FromArgb(255, 0, 255, 0)); // Default green
        }

        public object ConvertBack(object value, Type targetType, object parameter, string language)
        {
            throw new NotImplementedException();
        }
    }
}

