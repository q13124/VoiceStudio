using Microsoft.UI.Xaml;
using System;
using System.IO;
using System.Text.Json;

namespace VoiceStudio.App.Services
{
    public sealed class ThemeManager
    {
        public string CurrentTheme { get; private set; } = "SciFi";
        public string Density { get; private set; } = "Compact";

        public void ApplyTheme(string name)
        {
            CurrentTheme = name;
            
            // Remove existing theme dictionaries
            var toRemove = new System.Collections.Generic.List<ResourceDictionary>();
            foreach (var dict in Application.Current.Resources.MergedDictionaries)
            {
                if (dict.Source != null && dict.Source.ToString().Contains("Theme."))
                {
                    toRemove.Add(dict);
                }
            }
            foreach (var dict in toRemove)
            {
                Application.Current.Resources.MergedDictionaries.Remove(dict);
            }
            
            // Add new theme
            var themeDict = new ResourceDictionary 
            { 
                Source = new Uri($"ms-appx:///Resources/Theme.{name}.xaml") 
            };
            Application.Current.Resources.MergedDictionaries.Add(themeDict);
            
            Persist();
        }

        public void ApplyLayoutDensity(string density)
        {
            Density = density;
            
            // Remove existing density dictionaries
            var toRemove = new System.Collections.Generic.List<ResourceDictionary>();
            foreach (var dict in Application.Current.Resources.MergedDictionaries)
            {
                if (dict.Source != null && dict.Source.ToString().Contains("Density."))
                {
                    toRemove.Add(dict);
                }
            }
            foreach (var dict in toRemove)
            {
                Application.Current.Resources.MergedDictionaries.Remove(dict);
            }
            
            // Add new density
            var densityDict = new ResourceDictionary 
            { 
                Source = new Uri($"ms-appx:///Resources/Density.{density}.xaml") 
            };
            Application.Current.Resources.MergedDictionaries.Add(densityDict);
            
            Persist();
        }

        private void Persist()
        {
            var settingsDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "VoiceStudio"
            );
            Directory.CreateDirectory(settingsDir);
            var path = Path.Combine(settingsDir, "settings.json");
            File.WriteAllText(path, JsonSerializer.Serialize(new 
            { 
                theme = CurrentTheme, 
                density = Density 
            }));
        }
    }
}

