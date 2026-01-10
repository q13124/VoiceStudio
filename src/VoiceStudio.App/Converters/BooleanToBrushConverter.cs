using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Data;
using Microsoft.UI.Xaml.Media;

namespace VoiceStudio.App.Converters;

/// <summary>
/// Converts a boolean to a Brush.
/// Prefer setting TrueBrush/FalseBrush/NullBrush from XAML resources (VSQ tokens).
/// </summary>
public sealed class BooleanToBrushConverter : IValueConverter
{
    public Brush? TrueBrush { get; set; }
    public Brush? FalseBrush { get; set; }
    public Brush? NullBrush { get; set; }

    public object Convert(object value, Type targetType, object parameter, string language)
    {
        if (value is bool b)
        {
            return b ? ResolveTrueBrush() : ResolveFalseBrush();
        }

        return ResolveNullBrush();
    }

    public object ConvertBack(object value, Type targetType, object parameter, string language)
    {
        throw new NotSupportedException();
    }

    private Brush ResolveTrueBrush()
    {
        return TrueBrush
            ?? TryGetAppBrush("VSQ.Success.Brush")
            ?? new SolidColorBrush(Microsoft.UI.Colors.Transparent);
    }

    private Brush ResolveFalseBrush()
    {
        return FalseBrush
            ?? TryGetAppBrush("VSQ.Warn.Brush")
            ?? new SolidColorBrush(Microsoft.UI.Colors.Transparent);
    }

    private Brush ResolveNullBrush()
    {
        return NullBrush
            ?? TryGetAppBrush("VSQ.Text.SecondaryBrush")
            ?? new SolidColorBrush(Microsoft.UI.Colors.Transparent);
    }

    private static Brush? TryGetAppBrush(string key)
    {
        try
        {
            var resources = Application.Current?.Resources;
            if (resources != null && resources.ContainsKey(key))
            {
                return resources[key] as Brush;
            }
        }
        catch
        {
        }

        return null;
    }
}
