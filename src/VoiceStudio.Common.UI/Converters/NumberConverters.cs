using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Data;

namespace VoiceStudio.Common.UI.Converters;

/// <summary>
/// Formats numbers using a format string.
/// </summary>
public class NumberFormatConverter : IValueConverter
{
    public string Format { get; set; } = "N2";

    public object Convert(object value, Type targetType, object parameter, string language)
    {
        var format = parameter as string ?? Format;

        return value switch
        {
            double d => d.ToString(format),
            float f => f.ToString(format),
            decimal dec => dec.ToString(format),
            int i => i.ToString(format),
            long l => l.ToString(format),
            _ => value?.ToString() ?? string.Empty
        };
    }

    public object ConvertBack(object value, Type targetType, object parameter, string language)
    {
        // One-way converter - return unset value
        return DependencyProperty.UnsetValue;
    }
}

/// <summary>
/// Converts a count to Visibility (Collapsed when 0).
/// </summary>
public class CountToVisibilityConverter : IValueConverter
{
    public Visibility ZeroVisibility { get; set; } = Visibility.Collapsed;
    public Visibility NonZeroVisibility { get; set; } = Visibility.Visible;

    public object Convert(object value, Type targetType, object parameter, string language)
    {
        var count = value switch
        {
            int i => i,
            long l => (int)l,
            double d => (int)d,
            System.Collections.ICollection c => c.Count,
            _ => 0
        };

        return count > 0 ? NonZeroVisibility : ZeroVisibility;
    }

    public object ConvertBack(object value, Type targetType, object parameter, string language)
    {
        // One-way converter - return unset value
        return DependencyProperty.UnsetValue;
    }
}

/// <summary>
/// Subtracts a value from the input.
/// </summary>
public class SubtractConverter : IValueConverter
{
    public double SubtractValue { get; set; } = 0;

    public object Convert(object value, Type targetType, object parameter, string language)
    {
        double subtract = SubtractValue;
        if (parameter is string paramStr && double.TryParse(paramStr, out var paramValue))
        {
            subtract = paramValue;
        }

        return value switch
        {
            double d => d - subtract,
            float f => f - subtract,
            int i => i - subtract,
            _ => value
        };
    }

    public object ConvertBack(object value, Type targetType, object parameter, string language)
    {
        // One-way converter - return unset value
        return DependencyProperty.UnsetValue;
    }
}

/// <summary>
/// Converts byte sizes to human-readable format.
/// </summary>
public class SizeConverter : IValueConverter
{
    private static readonly string[] Units = { "B", "KB", "MB", "GB", "TB" };

    public object Convert(object value, Type targetType, object parameter, string language)
    {
        double bytes = value switch
        {
            long l => l,
            int i => i,
            double d => d,
            _ => 0
        };

        int unitIndex = 0;
        while (bytes >= 1024 && unitIndex < Units.Length - 1)
        {
            bytes /= 1024;
            unitIndex++;
        }

        return $"{bytes:N2} {Units[unitIndex]}";
    }

    public object ConvertBack(object value, Type targetType, object parameter, string language)
    {
        // One-way converter - return unset value
        return DependencyProperty.UnsetValue;
    }
}
