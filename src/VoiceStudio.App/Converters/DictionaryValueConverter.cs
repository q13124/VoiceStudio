using System;
using System.Collections.Generic;
using System.Collections;
using Microsoft.UI.Xaml.Data;
using Microsoft.UI.Xaml;

namespace VoiceStudio.App.Converters
{
    /// <summary>
    /// Converter to get a value from a dictionary by key.
    /// Usage: Value="{Binding Dictionary, Converter={StaticResource DictionaryValueConverter}, ConverterParameter='Key'}"
    /// </summary>
    public sealed class DictionaryValueConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, string language)
        {
            if (parameter is not string key || string.IsNullOrWhiteSpace(key))
            {
                return GetDefaultForTargetType(targetType);
            }

            if (value is null)
            {
                return GetDefaultForTargetType(targetType);
            }

            if (value is IDictionary<string, double> doubleDict)
            {
                return doubleDict.TryGetValue(key, out var val) ? val : GetDefaultForTargetType(targetType);
            }

            if (value is IDictionary<string, bool> boolDict)
            {
                return boolDict.TryGetValue(key, out var val) ? val : GetDefaultForTargetType(targetType);
            }

            if (value is IDictionary<string, object?> objDict)
            {
                return objDict.TryGetValue(key, out var val)
                    ? CoerceToTargetType(val, targetType)
                    : GetDefaultForTargetType(targetType);
            }

            if (value is IDictionary legacyDict)
            {
                if (legacyDict.Contains(key))
                {
                    return CoerceToTargetType(legacyDict[key], targetType);
                }

                return GetDefaultForTargetType(targetType);
            }

            return GetDefaultForTargetType(targetType);
        }

        public object ConvertBack(object value, Type targetType, object parameter, string language)
        {
            throw new NotSupportedException();
        }

        private static object GetDefaultForTargetType(Type targetType)
        {
            if (targetType == typeof(bool) || targetType == typeof(bool?))
                return false;

            if (targetType == typeof(double) || targetType == typeof(double?))
                return 0d;

            if (targetType == typeof(int) || targetType == typeof(int?))
                return 0;

            if (targetType == typeof(string))
                return string.Empty;

            return DependencyProperty.UnsetValue;
        }

        private static object CoerceToTargetType(object? value, Type targetType)
        {
            if (value == null)
                return GetDefaultForTargetType(targetType);

            if (targetType.IsInstanceOfType(value))
                return value;

            try
            {
                if (targetType == typeof(string))
                    return value.ToString() ?? string.Empty;

                if (targetType == typeof(bool) || targetType == typeof(bool?))
                    return System.Convert.ToBoolean(value);

                if (targetType == typeof(double) || targetType == typeof(double?))
                    return System.Convert.ToDouble(value);

                if (targetType == typeof(int) || targetType == typeof(int?))
                    return System.Convert.ToInt32(value);
            }
            catch
            {
            }

            return GetDefaultForTargetType(targetType);
        }
    }
}

