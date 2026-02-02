using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Data;

namespace VoiceStudio.Common.UI.Converters;

/// <summary>
/// Converts null to boolean (false for null, true otherwise).
/// </summary>
public class NullToBooleanConverter : IValueConverter
{
    public bool NullValue { get; set; } = false;

    public object Convert(object value, Type targetType, object parameter, string language)
    {
        return value != null ? !NullValue : NullValue;
    }

    public object ConvertBack(object value, Type targetType, object parameter, string language)
    {
        throw new NotImplementedException();
    }
}

/// <summary>
/// Converts null to Visibility (Collapsed for null, Visible otherwise).
/// </summary>
public class NullToVisibilityConverter : IValueConverter
{
    public Visibility NullVisibility { get; set; } = Visibility.Collapsed;
    public Visibility NotNullVisibility { get; set; } = Visibility.Visible;

    public object Convert(object value, Type targetType, object parameter, string language)
    {
        return value != null ? NotNullVisibility : NullVisibility;
    }

    public object ConvertBack(object value, Type targetType, object parameter, string language)
    {
        throw new NotImplementedException();
    }
}
