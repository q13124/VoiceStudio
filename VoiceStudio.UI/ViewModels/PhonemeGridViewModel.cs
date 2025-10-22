using System.Collections.ObjectModel;
using System.ComponentModel;

namespace VoiceStudio.UI.ViewModels
{
  public class PhonemeItem : INotifyPropertyChanged {
    public string Grapheme { get; set; } = "";
    public string IPA { get; set; } = "";
    string _Override = "";
    public string Override { get => _Override; set { _Override=value; PropertyChanged?.Invoke(this,new(nameof(Override))); } }
    public event PropertyChangedEventHandler? PropertyChanged;
  }

  public class PhonemeGridViewModel : INotifyPropertyChanged {
    public ObservableCollection<PhonemeItem> Items { get; } = new();
    public event PropertyChangedEventHandler? PropertyChanged;
    public string ToJson() {
      var dict = new System.Collections.Generic.Dictionary<string,string>();
      foreach(var it in Items) if(!string.IsNullOrWhiteSpace(it.Override)) dict[it.Grapheme]=it.Override;
      return System.Text.Json.JsonSerializer.Serialize(dict);
    }
  }
}
