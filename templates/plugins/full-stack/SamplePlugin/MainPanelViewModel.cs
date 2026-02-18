using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace {{CLASS_NAME}}Plugin;

public class MainPanelViewModel : INotifyPropertyChanged
{
    private string _status = "Ready";

    public string Status
    {
        get => _status;
        set => SetProperty(ref _status, value);
    }

    protected void SetProperty<T>(ref T field, T value, [CallerMemberName] string name = "")
    {
        if (!Equals(field, value))
        {
            field = value;
            OnPropertyChanged(name);
        }
    }

    protected void OnPropertyChanged([CallerMemberName] string name = "")
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
    }

    public event PropertyChangedEventHandler PropertyChanged;
}
