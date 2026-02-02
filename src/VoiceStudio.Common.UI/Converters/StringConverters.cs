using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Data;

namespace VoiceStudio.Common.UI.Converters;

/// <summary>
/// Converts empty/null strings to Visibility.
/// </summary>
public class StringToVisibilityConverter : IValueConverter
{
    public Visibility EmptyVisibility { get; set; } = Visibility.Collapsed;
    public Visibility NotEmptyVisibility { get; set; } = Visibility.Visible;

    public object Convert(object value, Type targetType, object parameter, string language)
    {
        var str = value as string;
        return string.IsNullOrWhiteSpace(str) ? EmptyVisibility : NotEmptyVisibility;
    }

    public object ConvertBack(object value, Type targetType, object parameter, string language)
    {
        throw new NotImplementedException();
    }
}

/// <summary>
/// Formats strings using string.Format.
/// </summary>
public class StringFormatConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, string language)
    {
        if (parameter is string format && value != null)
        {
            return string.Format(format, value);
        }
        return value?.ToString() ?? string.Empty;
    }

    public object ConvertBack(object value, Type targetType, object parameter, string language)
    {
        throw new NotImplementedException();
    }
}

/// <summary>
/// Gets the first letter of a string (for avatars).
/// </summary>
public class FirstLetterConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, string language)
    {
        var str = value as string;
        if (!string.IsNullOrEmpty(str))
        {
            return str[0].ToString().ToUpperInvariant();
        }
        return "?";
    }

    public object ConvertBack(object value, Type targetType, object parameter, string language)
    {
        throw new NotImplementedException();
    }
}

/// <summary>
/// Gets initials from a name (e.g., "John Doe" -> "JD").
/// </summary>
public class InitialsConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, string language)
    {
        var str = value as string;
        if (string.IsNullOrWhiteSpace(str))
        {
            return "?";
        }

        var parts = str.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        if (parts.Length >= 2)
        {
            return $"{parts[0][0]}{parts[^1][0]}".ToUpperInvariant();
        }
        return parts[0][0].ToString().ToUpperInvariant();
    }

    public object ConvertBack(object value, Type targetType, object parameter, string language)
    {
        throw new NotImplementedException();
    }
}
