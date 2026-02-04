using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Printing;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading.Tasks;
using VoiceStudio.App.Services;
using Windows.System;
using Windows.Foundation;
using Windows.Storage;
using Windows.Storage.Pickers;
using Windows.Graphics.Printing;
using Windows.Graphics.Printing.OptionDetails;
using Windows.UI.Core;
using KeyboardShortcut = VoiceStudio.App.Services.KeyboardShortcut;

namespace VoiceStudio.App.Views
{
  /// <summary>
  /// Keyboard shortcuts cheat sheet view.
  /// Implements IDEA 29: Keyboard Shortcut Cheat Sheet.
  /// </summary>
  public sealed partial class KeyboardShortcutsView : UserControl
  {
    private readonly KeyboardShortcutService _shortcutService;
    private readonly ObservableCollection<ShortcutViewModel> _allShortcuts = new();
    private readonly ObservableCollection<ShortcutViewModel> _filteredShortcuts = new();
    private PrintDocument? _printDocument;
    private IPrintDocumentSource? _printDocumentSource;

    public KeyboardShortcutsView()
    {
      this.InitializeComponent();
      _shortcutService = ServiceProvider.TryGetKeyboardShortcutService() ?? new KeyboardShortcutService();
      LoadShortcuts();
    }

    private void LoadShortcuts()
    {
      _allShortcuts.Clear();
      _filteredShortcuts.Clear();

      var shortcuts = _shortcutService.GetAllShortcuts().ToList();

      // Group shortcuts by category
      var categorized = CategorizeShortcuts(shortcuts);

      foreach (var category in categorized.Keys.OrderBy(k => k))
      {
        foreach (var shortcut in categorized[category].OrderBy(s => s.Description))
        {
          var viewModel = new ShortcutViewModel
          {
            Id = shortcut.Id,
            Description = shortcut.Description ?? shortcut.Id,
            Category = category,
            DisplayText = _shortcutService.GetShortcutDisplayText(shortcut.Id) ?? FormatShortcut(shortcut),
            Key = shortcut.Key,
            Modifiers = shortcut.Modifiers
          };

          _allShortcuts.Add(viewModel);
          _filteredShortcuts.Add(viewModel);
        }
      }

      ShortcutsItemsControl.ItemsSource = _filteredShortcuts;
    }

    private Dictionary<string, List<KeyboardShortcut>> CategorizeShortcuts(List<KeyboardShortcut> shortcuts)
    {
      var categories = new Dictionary<string, List<KeyboardShortcut>>();

      foreach (var shortcut in shortcuts)
      {
        var category = DetermineCategory(shortcut);
        if (!categories.ContainsKey(category))
        {
          categories[category] = new List<KeyboardShortcut>();
        }
        categories[category].Add(shortcut);
      }

      return categories;
    }

    private string DetermineCategory(KeyboardShortcut shortcut)
    {
      // Categorize based on description or ID
      var id = shortcut.Id.ToLower();
      var desc = (shortcut.Description ?? "").ToLower();

      if (id.Contains("file") || desc.Contains("file") || desc.Contains("open") || desc.Contains("save") || desc.Contains("new"))
        return "File";
      if (id.Contains("edit") || desc.Contains("edit") || desc.Contains("cut") || desc.Contains("copy") || desc.Contains("paste") || desc.Contains("undo") || desc.Contains("redo"))
        return "Edit";
      if (id.Contains("view") || desc.Contains("view") || desc.Contains("toggle") || desc.Contains("show") || desc.Contains("hide"))
        return "View";
      if (id.Contains("playback") || desc.Contains("play") || desc.Contains("stop") || desc.Contains("record") || desc.Contains("pause"))
        return "Playback";
      if (id.Contains("panel") || desc.Contains("panel") || desc.Contains("profiles") || desc.Contains("timeline") || desc.Contains("mixer"))
        return "Panels";
      if (id.Contains("search") || desc.Contains("search") || desc.Contains("find") || desc.Contains("command"))
        return "Navigation";
      if (id.Contains("help") || desc.Contains("help") || desc.Contains("shortcut"))
        return "Help";

      return "General";
    }

    private string FormatShortcut(KeyboardShortcut shortcut)
    {
      var parts = new List<string>();
      if (shortcut.Modifiers.HasFlag(VirtualKeyModifiers.Control))
        parts.Add("Ctrl");
      if (shortcut.Modifiers.HasFlag(VirtualKeyModifiers.Shift))
        parts.Add("Shift");
      if (shortcut.Modifiers.HasFlag(VirtualKeyModifiers.Menu))
        parts.Add("Alt");

      parts.Add(shortcut.Key.ToString());

      return string.Join(" + ", parts);
    }

    private void SearchBox_TextChanged(object _, TextChangedEventArgs __)
    {
      var searchText = SearchBox.Text?.ToLower() ?? "";

      _filteredShortcuts.Clear();

      if (string.IsNullOrWhiteSpace(searchText))
      {
        foreach (var shortcut in _allShortcuts)
        {
          _filteredShortcuts.Add(shortcut);
        }
      }
      else
      {
        foreach (var shortcut in _allShortcuts)
        {
          if (shortcut.Description.ToLower().Contains(searchText) ||
              shortcut.Category.ToLower().Contains(searchText) ||
              shortcut.DisplayText.ToLower().Contains(searchText))
          {
            _filteredShortcuts.Add(shortcut);
          }
        }
      }
    }

    private async void PrintButton_Click(object _, RoutedEventArgs __)
    {
      try
      {
        // Check if printing is supported
        var printManager = PrintManager.GetForCurrentView();
        if (printManager == null)
        {
          var errorDialog = new ContentDialog
          {
            Title = "Print Not Available",
            Content = "Printing is not available on this system.",
            CloseButtonText = "OK",
            XamlRoot = this.XamlRoot
          };
          await errorDialog.ShowAsync();
          return;
        }

        // Create print document
        _printDocument = new PrintDocument();
        _printDocumentSource = _printDocument.DocumentSource;
        _printDocument.Paginate += OnPrintDocumentPaginate;
        _printDocument.GetPreviewPage += OnPrintDocumentGetPreviewPage;
        _printDocument.AddPages += OnPrintDocumentAddPages;

        // Show print UI
        var printTaskRequestedHandler = new TypedEventHandler<PrintManager, PrintTaskRequestedEventArgs>((_, args) =>
        {
          var printTask = args.Request.CreatePrintTask("VoiceStudio Keyboard Shortcuts", (sourceRequested) => sourceRequested.SetSource(_printDocumentSource!));

          // Set print options
          printTask.Options.DisplayedOptions.Clear();
          printTask.Options.DisplayedOptions.Add(StandardPrintTaskOptions.Copies);
          printTask.Options.DisplayedOptions.Add(StandardPrintTaskOptions.Orientation);
          printTask.Options.DisplayedOptions.Add(StandardPrintTaskOptions.MediaSize);
        });

        printManager.PrintTaskRequested += printTaskRequestedHandler;

        try
        {
          await PrintManager.ShowPrintUIAsync();
        }
        finally
        {
          printManager.PrintTaskRequested -= printTaskRequestedHandler;
        }
      }
      catch (Exception ex)
      {
        var errorDialog = new ContentDialog
        {
          Title = "Print Error",
          Content = $"Failed to print: {ex.Message}",
          CloseButtonText = "OK",
          XamlRoot = this.XamlRoot
        };
        await errorDialog.ShowAsync();
      }
    }

    private void OnPrintDocumentPaginate(object sender, PaginateEventArgs e)
    {
      // Print document is ready
      _printDocument?.InvalidatePreview();
    }

    private void OnPrintDocumentGetPreviewPage(object sender, GetPreviewPageEventArgs e)
    {
      // Provide preview page
      _printDocument?.SetPreviewPage(e.PageNumber, CreatePrintPage());
    }

    private void OnPrintDocumentAddPages(object sender, AddPagesEventArgs e)
    {
      // Add pages to print
      _printDocument?.AddPage(CreatePrintPage());
      _printDocument?.AddPagesComplete();
    }

    private FrameworkElement CreatePrintPage()
    {
      // Create a printable version of the shortcuts
      var printContent = new StackPanel
      {
        Margin = new Thickness(96, 96, 96, 96) // 1 inch margins
      };

      // Header
      var header = new TextBlock
      {
        Text = "VoiceStudio Keyboard Shortcuts",
        FontSize = 24,
        FontWeight = Microsoft.UI.Text.FontWeights.Bold,
        Margin = new Thickness(0, 0, 0, 12)
      };
      printContent.Children.Add(header);

      var dateText = new TextBlock
      {
        Text = $"Generated: {DateTime.Now:yyyy-MM-dd HH:mm:ss}",
        FontSize = 12,
        Margin = new Thickness(0, 0, 0, 24)
      };
      printContent.Children.Add(dateText);

      // Group shortcuts by category
      var currentCategory = "";
      foreach (var shortcut in _allShortcuts)
      {
        if (shortcut.Category != currentCategory)
        {
          if (!string.IsNullOrEmpty(currentCategory))
          {
            printContent.Children.Add(new TextBlock { Height = 12 }); // Spacing
          }

          var categoryHeader = new TextBlock
          {
            Text = shortcut.Category.ToUpper(),
            FontSize = 16,
            FontWeight = Microsoft.UI.Text.FontWeights.SemiBold,
            Margin = new Thickness(0, 8, 0, 8)
          };
          printContent.Children.Add(categoryHeader);
          currentCategory = shortcut.Category;
        }

        var shortcutPanel = new StackPanel
        {
          Orientation = Orientation.Horizontal,
          Margin = new Thickness(0, 4, 0, 4)
        };

        var descriptionText = new TextBlock
        {
          Text = shortcut.Description,
          FontSize = 12,
          Width = 400,
          TextWrapping = TextWrapping.Wrap
        };
        shortcutPanel.Children.Add(descriptionText);

        var shortcutText = new TextBlock
        {
          Text = shortcut.DisplayText,
          FontSize = 12,
          FontFamily = new Microsoft.UI.Xaml.Media.FontFamily("Consolas"),
          Margin = new Thickness(24, 0, 0, 0)
        };
        shortcutPanel.Children.Add(shortcutText);

        printContent.Children.Add(shortcutPanel);
      }

      return printContent;
    }

    private async void ExportButton_Click(object _, RoutedEventArgs __)
    {
      try
      {
        var picker = new FileSavePicker();
        picker.SuggestedStartLocation = PickerLocationId.DocumentsLibrary;
        picker.FileTypeChoices.Add("Text File", new List<string> { ".txt" });
        picker.SuggestedFileName = "VoiceStudio_Keyboard_Shortcuts";

        var file = await picker.PickSaveFileAsync();
        if (file != null)
        {
          var content = GenerateExportContent();
          await FileIO.WriteTextAsync(file, content);

          var successDialog = new ContentDialog
          {
            Title = "Export Successful",
            Content = $"Shortcuts exported to {file.Name}",
            CloseButtonText = "OK",
            XamlRoot = this.XamlRoot
          };
          await successDialog.ShowAsync();
        }
      }
      catch (Exception ex)
      {
        var errorDialog = new ContentDialog
        {
          Title = "Export Failed",
          Content = $"Error exporting shortcuts: {ex.Message}",
          CloseButtonText = "OK",
          XamlRoot = this.XamlRoot
        };
        await errorDialog.ShowAsync();
      }
    }

    private string GenerateExportContent()
    {
      var content = new System.Text.StringBuilder();
      content.AppendLine("VoiceStudio Keyboard Shortcuts")
        .AppendLine("=".PadRight(50, '='))
        .AppendLine()
        .AppendLine($"Generated: {DateTime.Now:yyyy-MM-dd HH:mm:ss}")
        .AppendLine()
        .AppendLine();

      var currentCategory = "";
      foreach (var shortcut in _allShortcuts)
      {
        if (shortcut.Category != currentCategory)
        {
          if (!string.IsNullOrEmpty(currentCategory))
            content.AppendLine();
          content.AppendLine(shortcut.Category.ToUpper())
            .AppendLine("-".PadRight(50, '-'));
          currentCategory = shortcut.Category;
        }

        content.AppendLine($"{shortcut.Description.PadRight(40)} {shortcut.DisplayText}");
      }

      return content.ToString();
    }
  }

  public class ShortcutViewModel
  {
    public string Id { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Category { get; set; } = string.Empty;
    public string DisplayText { get; set; } = string.Empty;
    public VirtualKey Key { get; set; }
    public VirtualKeyModifiers Modifiers { get; set; }
  }
}