using System.Windows.Input;
using CommunityToolkit.Mvvm.Input;

namespace VoiceStudio.App.Utilities;

public static class CommandExtensions
{
  public static void NotifyCanExecuteChanged(this ICommand command)
  {
    if (command is IRelayCommand relayCommand)
    {
      relayCommand.NotifyCanExecuteChanged();
    }
  }
}