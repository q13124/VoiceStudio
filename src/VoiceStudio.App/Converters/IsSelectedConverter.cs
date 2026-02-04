using Microsoft.UI.Xaml.Data;
using System;

namespace VoiceStudio.App.Converters
{
  /// <summary>
  /// Converter to check if an item is selected.
  /// Looks for a selection helper passed via ConverterParameter and falls back to reflection.
  /// </summary>
  public class IsSelectedConverter : IValueConverter
  {
    public object? Convert(object value, Type targetType, object parameter, string language)
    {
      if (value == null)
        return false;

      try
      {
        // Fast path: parameter exposes an IsItemSelected/IsSelected method
        if (parameter != null)
        {
          var paramType = parameter.GetType();
          var method = paramType.GetMethod("IsItemSelected")
              ?? paramType.GetMethod("IsSelected");
          if (method != null && method.ReturnType == typeof(bool) && method.GetParameters().Length == 1)
          {
            var result = method.Invoke(parameter, new[] { value });
            if (result is bool isSelected)
            {
              return isSelected;
            }
          }
        }
      }
      catch
      {
        // Swallow and fall through to default
      }

      return false;
    }

    public object? ConvertBack(object value, Type targetType, object parameter, string language)
    {
      throw new NotSupportedException();
    }
  }
}