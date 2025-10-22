using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Linq;

namespace VoiceStudio.UI.Util
{
  public class CoachingRule { public string id {get;set;}=""; public double threshold{get;set;}=0.7; public string message{get;set;}=""; }

  public static class Coaching
  {
    static List<CoachingRule>? _rules;
    static void Ensure(){
      if(_rules!=null) return;
      var appDir = Path.GetDirectoryName(typeof(Coaching).Assembly.Location)!;
      var guess = Path.Combine(Path.GetDirectoryName(appDir)!, "VoiceStudio.UI","Assets","coaching_rules.json");
      var path = File.Exists(guess)? guess : Path.Combine(appDir,"coaching_rules.json");
      _rules = File.Exists(path) ? JsonSerializer.Deserialize<List<CoachingRule>>(File.ReadAllText(path)) : new();
    }

    public static IEnumerable<string> Evaluate(double syntheticScore){
      Ensure();
      foreach(var r in _rules!){
        if(syntheticScore >= r.threshold) yield return r.message;
      }
    }

    public static async void Toast(Page host, string text){
      var d = new ContentDialog{ XamlRoot = host.XamlRoot, Title="AI Coaching", Content=text, PrimaryButtonText="OK" };
      await d.ShowAsync();
    }
  }
}
