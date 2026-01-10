using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Data;
using System;

namespace VoiceStudio.App.Converters
{
    public class BooleanToOpacityConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, string language)
        {
            if (value is bool boolValue)
            {
                return boolValue ? 0.5 : 1.0; // 50% opacity when loading, 100% when not
            }
            return 1.0;
        }

        public object ConvertBack(object value, Type targetType, object parameter, string language)
        {
            throw new NotSupportedException();
        }
    }
}

