using Microsoft.UI.Xaml.Controls;
using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading.Tasks;
using VoiceStudio.App.Services;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Views.Dialogs
{
  public sealed partial class ToolbarCustomizationDialog : ContentDialog
  {
    private readonly ToolbarConfigurationService _toolbarService;
    private ToolbarConfiguration _currentConfiguration;
    private ObservableCollection<ToolbarItemViewModel> _items;

    public ToolbarCustomizationDialog()
    {
      this.InitializeComponent();
      _toolbarService = ServiceProvider.GetToolbarConfigurationService();
      _currentConfiguration = _toolbarService.GetConfiguration();
      _items = new ObservableCollection<ToolbarItemViewModel>();

      LoadConfiguration();
      LoadPresets();

      this.PrimaryButtonClick += ContentDialog_PrimaryButtonClick;
    }

    private void LoadConfiguration()
    {
      _items.Clear();
      foreach (var item in _currentConfiguration.Items.OrderBy(i => i.Order))
      {
        _items.Add(new ToolbarItemViewModel(item));
      }
      ToolbarItemsListView.ItemsSource = _items;
    }

    private void LoadPresets()
    {
      PresetComboBox.Items.Clear();
      foreach (var preset in _toolbarService.GetPresets())
      {
        PresetComboBox.Items.Add(preset.Name);
      }
      PresetComboBox.SelectedIndex = 0;
    }

    private async void PresetComboBox_SelectionChanged(object _, Microsoft.UI.Xaml.Controls.SelectionChangedEventArgs __)
    {
      if (PresetComboBox.SelectedItem is string presetName)
      {
        await _toolbarService.ApplyPresetAsync(presetName);
        _currentConfiguration = _toolbarService.GetConfiguration();
        LoadConfiguration();
      }
    }

    private async void SavePresetButton_Click(object _, Microsoft.UI.Xaml.RoutedEventArgs __)
    {
      var inputDialog = new TextInputDialog("Save Preset", "Enter preset name:", "Custom Preset");
      var result = await inputDialog.ShowAsync();

      if (result == ContentDialogResult.Primary && !string.IsNullOrWhiteSpace(inputDialog.InputText))
      {
        // Update order based on current list view order
        UpdateItemOrders();
        await _toolbarService.SavePresetAsync(inputDialog.InputText, _currentConfiguration);
        LoadPresets();
      }
    }

    private void UpdateItemOrders()
    {
      for (int i = 0; i < _items.Count; i++)
      {
        _items[i].Order = i;
      }
    }

    private async void ContentDialog_PrimaryButtonClick(ContentDialog sender, ContentDialogButtonClickEventArgs args)
    {
      // Update configuration with current state
      UpdateItemOrders();
      _currentConfiguration.Items.Clear();
      foreach (var itemViewModel in _items)
      {
        _currentConfiguration.Items.Add(itemViewModel.ToToolbarItem());
      }

      await _toolbarService.UpdateConfigurationAsync(_currentConfiguration);
    }
  }

  public class ToolbarItemViewModel
  {
    public string Id { get; set; } = string.Empty;
    public string Label { get; set; } = string.Empty;
    public string Icon { get; set; } = string.Empty;
    public bool IsVisible { get; set; } = true;
    public int Order { get; set; }
    public ToolbarSection Section { get; set; }

    public ToolbarItemViewModel(ToolbarItem item)
    {
      Id = item.Id;
      Label = item.Label;
      Icon = item.Icon;
      IsVisible = item.IsVisible;
      Order = item.Order;
      Section = item.Section;
    }

    public ToolbarItem ToToolbarItem()
    {
      return new ToolbarItem
      {
        Id = Id,
        Label = Label,
        Icon = Icon,
        IsVisible = IsVisible,
        Order = Order,
        Section = Section
      };
    }
  }

  public class TextInputDialog : ContentDialog
  {
    public string InputText { get; private set; } = string.Empty;
    private TextBox _inputTextBox;

    public TextInputDialog(string title, string message, string defaultValue = "")
    {
      Title = title;
      PrimaryButtonText = "OK";
      SecondaryButtonText = "Cancel";
      DefaultButton = ContentDialogButton.Primary;

      var stackPanel = new StackPanel { Spacing = 12 };
      stackPanel.Children.Add(new TextBlock { Text = message, TextWrapping = Microsoft.UI.Xaml.TextWrapping.Wrap });

      _inputTextBox = new TextBox
      {
        Text = defaultValue,
        HorizontalAlignment = Microsoft.UI.Xaml.HorizontalAlignment.Stretch
      };
      stackPanel.Children.Add(_inputTextBox);

      Content = stackPanel;
      PrimaryButtonClick += (_, _) => InputText = _inputTextBox.Text;
    }
  }
}