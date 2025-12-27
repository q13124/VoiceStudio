using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using System.Collections.ObjectModel;
using System.Linq;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Controls
{
    public sealed partial class CommandPalette : UserControl
    {
        private ICommandRegistry? _commandRegistry;
        private ObservableCollection<CommandItem> _allCommands = new();
        private ObservableCollection<CommandItem> _filteredCommands = new();

        public CommandPalette()
        {
            this.InitializeComponent();
            ResultsList.ItemsSource = _filteredCommands;
        }

        public void Initialize(ICommandRegistry commandRegistry)
        {
            _commandRegistry = commandRegistry;
            _allCommands = new ObservableCollection<CommandItem>(_commandRegistry.GetAllCommands());
            _filteredCommands = new ObservableCollection<CommandItem>(_allCommands);
        }

        private void SearchBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(SearchBox.Text))
            {
                _filteredCommands.Clear();
                foreach (var cmd in _allCommands)
                {
                    _filteredCommands.Add(cmd);
                }
            }
            else
            {
                var query = SearchBox.Text.ToLower();
                _filteredCommands.Clear();
                foreach (var cmd in _allCommands)
                {
                    if (cmd.Title.ToLower().Contains(query) ||
                        cmd.Description.ToLower().Contains(query) ||
                        cmd.Category.ToLower().Contains(query))
                    {
                        _filteredCommands.Add(cmd);
                    }
                }
            }

            if (_filteredCommands.Count > 0)
            {
                ResultsList.SelectedIndex = 0;
            }
        }

        private void SearchBox_KeyDown(object sender, KeyRoutedEventArgs e)
        {
            if (e.Key == Windows.System.VirtualKey.Enter)
            {
                if (ResultsList.SelectedItem is CommandItem selected)
                {
                    ExecuteCommand(selected);
                }
                else if (_filteredCommands.Count > 0)
                {
                    ExecuteCommand(_filteredCommands[0]);
                }
            }
            else if (e.Key == Windows.System.VirtualKey.Escape)
            {
                Hide();
            }
            else if (e.Key == Windows.System.VirtualKey.Down)
            {
                if (ResultsList.SelectedIndex < _filteredCommands.Count - 1)
                {
                    ResultsList.SelectedIndex++;
                }
                e.Handled = true;
            }
            else if (e.Key == Windows.System.VirtualKey.Up)
            {
                if (ResultsList.SelectedIndex > 0)
                {
                    ResultsList.SelectedIndex--;
                }
                e.Handled = true;
            }
        }

        private void ResultsList_ItemClick(object sender, ItemClickEventArgs e)
        {
            if (e.ClickedItem is CommandItem command)
            {
                ExecuteCommand(command);
            }
        }

        private void ExecuteCommand(CommandItem command)
        {
            _commandRegistry?.ExecuteCommand(command.CommandId);
            Hide();
        }

        public void Show()
        {
            this.Visibility = Visibility.Visible;
            SearchBox.Text = string.Empty;
            SearchBox.Focus(FocusState.Programmatic);
        }

        public void Hide()
        {
            this.Visibility = Visibility.Collapsed;
        }
    }
}

