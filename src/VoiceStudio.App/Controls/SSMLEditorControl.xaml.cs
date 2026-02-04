using Microsoft.UI.Text;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Controls.Primitives;
using Microsoft.UI.Xaml.Input;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text.RegularExpressions;
using Windows.System;
using Windows.UI;

namespace VoiceStudio.App.Controls
{
  public sealed partial class SSMLEditorControl : UserControl
  {
    public static readonly DependencyProperty TextProperty =
        DependencyProperty.Register(
            nameof(Text),
            typeof(string),
            typeof(SSMLEditorControl),
            new PropertyMetadata(string.Empty, OnTextChanged));

    public static readonly DependencyProperty ShowLineNumbersProperty =
        DependencyProperty.Register(
            nameof(ShowLineNumbers),
            typeof(bool),
            typeof(SSMLEditorControl),
            new PropertyMetadata(true));

    public static readonly DependencyProperty ShowStatusBarProperty =
        DependencyProperty.Register(
            nameof(ShowStatusBar),
            typeof(bool),
            typeof(SSMLEditorControl),
            new PropertyMetadata(true));

    public static readonly DependencyProperty StatusMessageProperty =
        DependencyProperty.Register(
            nameof(StatusMessage),
            typeof(string),
            typeof(SSMLEditorControl),
            new PropertyMetadata(string.Empty));

    public static readonly DependencyProperty ValidationErrorsProperty =
        DependencyProperty.Register(
            nameof(ValidationErrors),
            typeof(ObservableCollection<SSMLError>),
            typeof(SSMLEditorControl),
            new PropertyMetadata(new ObservableCollection<SSMLError>(), OnValidationErrorsChanged));

    public string Text
    {
      get => (string)GetValue(TextProperty);
      set => SetValue(TextProperty, value);
    }

    public bool ShowLineNumbers
    {
      get => (bool)GetValue(ShowLineNumbersProperty);
      set => SetValue(ShowLineNumbersProperty, value);
    }

    public bool ShowStatusBar
    {
      get => (bool)GetValue(ShowStatusBarProperty);
      set => SetValue(ShowStatusBarProperty, value);
    }

    // XAML compiler stability: avoid bool->Visibility x:Bind.
    public Visibility LineNumbersVisibility => ShowLineNumbers ? Visibility.Visible : Visibility.Collapsed;
    public Visibility StatusBarVisibility => ShowStatusBar ? Visibility.Visible : Visibility.Collapsed;

    public string StatusMessage
    {
      get => (string)GetValue(StatusMessageProperty);
      set => SetValue(StatusMessageProperty, value);
    }

    public ObservableCollection<SSMLError> ValidationErrors
    {
      get => (ObservableCollection<SSMLError>)GetValue(ValidationErrorsProperty);
      set => SetValue(ValidationErrorsProperty, value);
    }

    public ObservableCollection<AutoCompleteItem> AutoCompleteItems { get; } = new();
    public int LineCount { get; private set; }
    public int ColumnCount { get; private set; }

    private bool _isUpdatingText;
    private bool _isApplyingSyntaxHighlighting;
    private string _lastText = string.Empty;
    private readonly List<SSMLTagInfo> _ssmlTags = new()
        {
            new SSMLTagInfo { Tag = "speak", Description = "Root element for SSML" },
            new SSMLTagInfo { Tag = "p", Description = "Paragraph" },
            new SSMLTagInfo { Tag = "s", Description = "Sentence" },
            new SSMLTagInfo { Tag = "break", Description = "Pause or break" },
            new SSMLTagInfo { Tag = "prosody", Description = "Prosody (rate, pitch, volume)" },
            new SSMLTagInfo { Tag = "emphasis", Description = "Emphasis" },
            new SSMLTagInfo { Tag = "say-as", Description = "Say as (interpret-as)" },
            new SSMLTagInfo { Tag = "phoneme", Description = "Phonetic pronunciation" },
            new SSMLTagInfo { Tag = "sub", Description = "Substitute text" },
            new SSMLTagInfo { Tag = "audio", Description = "Audio reference" },
            new SSMLTagInfo { Tag = "mark", Description = "Bookmark" },
        };

    public SSMLEditorControl()
    {
      this.InitializeComponent();
      SSMLEditor.Document.SetText(TextSetOptions.None, string.Empty);
      UpdateLineNumbers();
    }

    private static void OnTextChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
      if (d is SSMLEditorControl control && !control._isUpdatingText)
      {
        control._isUpdatingText = true;
        control.SSMLEditor.Document.SetText(TextSetOptions.None, e.NewValue?.ToString() ?? string.Empty);
        control.ApplySyntaxHighlighting();
        control.UpdateLineNumbers();
        control._isUpdatingText = false;
      }
    }

    private static void OnValidationErrorsChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
      if (d is SSMLEditorControl control)
      {
        control.HighlightErrors();
      }
    }

    private void SSMLEditor_TextChanged(object _, RoutedEventArgs __)
    {
      if (_isUpdatingText || _isApplyingSyntaxHighlighting)
        return;

      SSMLEditor.Document.GetText(TextGetOptions.None, out string currentText);
      if (currentText != _lastText)
      {
        _lastText = currentText;
        _isUpdatingText = true;
        Text = currentText;
        _isUpdatingText = false;

        UpdateLineNumbers();
        ApplySyntaxHighlighting();
      }
    }

    private void SSMLEditor_SelectionChanged(object _, RoutedEventArgs __)
    {
      UpdateCursorPosition();
      CheckForAutoComplete();
    }

    private void SSMLEditor_KeyDown(object _, KeyRoutedEventArgs e)
    {
      if (e.Key == VirtualKey.Tab && AutoCompletePopup.IsOpen)
      {
        // Insert selected auto-complete item
        if (AutoCompleteList.SelectedItem is AutoCompleteItem item)
        {
          InsertAutoComplete(item);
          e.Handled = true;
        }
      }
      else if (e.Key == VirtualKey.Escape)
      {
        AutoCompletePopup.IsOpen = false;
      }
    }

    private void SSMLEditor_GotFocus(object _, RoutedEventArgs __)
    {
      // Sync scroll viewers
      EditorScrollViewer.ViewChanged += EditorScrollViewer_ViewChanged;
    }

    private void SSMLEditor_LostFocus(object _, RoutedEventArgs __)
    {
      EditorScrollViewer.ViewChanged -= EditorScrollViewer_ViewChanged;
    }

    private void EditorScrollViewer_ViewChanged(object? _, ScrollViewerViewChangedEventArgs e)
    {
      // Sync line number scroll with editor scroll
      LineNumberScrollViewer.ChangeView(null, EditorScrollViewer.VerticalOffset, null);
    }

    private void AutoCompleteList_ItemClick(object _, ItemClickEventArgs e)
    {
      if (e.ClickedItem is AutoCompleteItem item)
      {
        InsertAutoComplete(item);
      }
    }

    private void AutoCompleteList_KeyDown(object _, KeyRoutedEventArgs e)
    {
      if (e.Key == VirtualKey.Enter && AutoCompleteList.SelectedItem is AutoCompleteItem item)
      {
        InsertAutoComplete(item);
        e.Handled = true;
      }
    }

    private void ApplySyntaxHighlighting()
    {
      if (_isApplyingSyntaxHighlighting)
        return;

      _isApplyingSyntaxHighlighting = true;

      try
      {
        var document = SSMLEditor.Document;
        document.GetText(TextGetOptions.None, out string text);

        // Get current selection to restore it
        document.Selection.GetText(TextGetOptions.None, out string selectedText);
        int selectionStart = document.Selection.StartPosition;
        int selectionEnd = document.Selection.EndPosition;

        // Apply default formatting
        ITextRange range = document.GetRange(0, text.Length);
        range.CharacterFormat.ForegroundColor = Color.FromArgb(255, 255, 255, 255); // White

        // Highlight SSML tags
        var tagPattern = new Regex(@"<(\/?)(\w+)([^>]*)>", RegexOptions.IgnoreCase);
        foreach (Match match in tagPattern.Matches(text))
        {
          int start = match.Index;
          int length = match.Length;
          ITextRange tagRange = document.GetRange(start, start + length);

          // Tag name color (cyan for opening, orange for closing)
          bool isClosing = match.Groups[1].Value == "/";
          tagRange.CharacterFormat.ForegroundColor = isClosing
              ? Color.FromArgb(255, 255, 152, 0) // Orange for closing tags
              : Color.FromArgb(255, 0, 183, 194); // Cyan for opening tags

          // Highlight tag name specifically
          int tagNameStart = match.Index + match.Groups[1].Length + 1;
          int tagNameLength = match.Groups[2].Length;
          ITextRange tagNameRange = document.GetRange(tagNameStart, tagNameStart + tagNameLength);
          tagNameRange.CharacterFormat.ForegroundColor = Color.FromArgb(255, 74, 158, 255); // Blue for tag names
          tagNameRange.CharacterFormat.Weight = FontWeights.SemiBold.Weight;
        }

        // Highlight attributes
        var attrPattern = new Regex(@"(\w+)\s*=\s*[""']([^""']+)[""']", RegexOptions.IgnoreCase);
        var attrMatches = attrPattern.Matches(text);

        foreach (Match match in attrMatches)
        {
          int attrNameStart = match.Index;
          int attrNameLength = match.Groups[1].Length;
          ITextRange attrRange = document.GetRange(attrNameStart, attrNameStart + attrNameLength);
          attrRange.CharacterFormat.ForegroundColor = Color.FromArgb(255, 156, 220, 254); // Light blue for attributes
        }

        // Highlight attribute values
        foreach (Match match in attrMatches)
        {
          int attrValueStart = match.Index + match.Groups[0].Value.IndexOf(match.Groups[2].Value);
          int attrValueLength = match.Groups[2].Length;
          ITextRange valueRange = document.GetRange(attrValueStart, attrValueStart + attrValueLength);
          valueRange.CharacterFormat.ForegroundColor = Color.FromArgb(255, 206, 145, 120); // Light orange for values
        }

        // Restore selection
        document.Selection.SetRange(selectionStart, selectionEnd);
      }
      catch
      {
        // Ignore errors during syntax highlighting
      }
      finally
      {
        _isApplyingSyntaxHighlighting = false;
      }
    }

    private void HighlightErrors()
    {
      if (ValidationErrors == null || ValidationErrors.Count == 0)
        return;

      try
      {
        var document = SSMLEditor.Document;
        document.GetText(TextGetOptions.None, out string text);
        var lines = text.Split('\n');

        foreach (var error in ValidationErrors)
        {
          if (error.LineNumber > 0 && error.LineNumber <= lines.Length)
          {
            int lineStart = 0;
            for (int i = 0; i < error.LineNumber - 1; i++)
            {
              lineStart += lines[i].Length + 1; // +1 for newline
            }

            int lineLength = lines[error.LineNumber - 1].Length;
            ITextRange errorRange = document.GetRange(lineStart, lineStart + lineLength);
            errorRange.CharacterFormat.BackgroundColor = Color.FromArgb(50, 211, 47, 47); // Red background with transparency
            errorRange.CharacterFormat.Underline = UnderlineType.Single;
          }
        }
      }
      catch
      {
        // Ignore errors during error highlighting
      }
    }

    private void UpdateLineNumbers()
    {
      if (!ShowLineNumbers)
        return;

      SSMLEditor.Document.GetText(TextGetOptions.None, out string text);
      var lines = text.Split('\n');
      LineCount = lines.Length;

      var lineNumbers = new System.Text.StringBuilder();
      for (int i = 1; i <= lines.Length; i++)
      {
        lineNumbers.AppendLine(i.ToString());
      }

      LineNumbersText.Text = lineNumbers.ToString();
    }

    private void UpdateCursorPosition()
    {
      try
      {
        var document = SSMLEditor.Document;
        document.GetText(TextGetOptions.None, out string text);
        int position = document.Selection.StartPosition;

        var lines = text.Substring(0, position).Split('\n');
        LineCount = lines.Length;
        ColumnCount = lines.Last().Length + 1;
      }
      catch
      {
        LineCount = 1;
        ColumnCount = 1;
      }
    }

    private void CheckForAutoComplete()
    {
      try
      {
        var document = SSMLEditor.Document;
        document.GetText(TextGetOptions.None, out string text);
        int position = document.Selection.StartPosition;

        // Check if we're typing a tag
        if (position > 0 && text[position - 1] == '<')
        {
          ShowAutoComplete();
        }
        else if (position > 0 && text[position - 1] == ' ')
        {
          // Check if we're in a tag and might need attribute completion
          int tagStart = text.LastIndexOf('<', position - 1);
          if (tagStart >= 0 && tagStart < position)
          {
            string tagContent = text.Substring(tagStart, position - tagStart);
            if (tagContent.Contains(' ') && !tagContent.Contains('>'))
            {
              // We're in a tag, might want attribute suggestions
              ShowAutoComplete();
            }
          }
        }
        else
        {
          AutoCompletePopup.IsOpen = false;
        }
      }
      catch
      {
        AutoCompletePopup.IsOpen = false;
      }
    }

    private void ShowAutoComplete()
    {
      AutoCompleteItems.Clear();

      try
      {
        var document = SSMLEditor.Document;
        document.GetText(TextGetOptions.None, out string text);
        int position = document.Selection.StartPosition;

        // Get current word being typed
        int wordStart = position - 1;
        while (wordStart >= 0 && char.IsLetterOrDigit(text[wordStart]))
        {
          wordStart--;
        }
        wordStart++;

        string currentWord = text.Substring(wordStart, position - wordStart).ToLower();

        // Filter tags based on current word
        foreach (var tag in _ssmlTags)
        {
          if (tag.Tag.ToLower().StartsWith(currentWord))
          {
            AutoCompleteItems.Add(new AutoCompleteItem
            {
              DisplayText = tag.Tag,
              Description = tag.Description,
              InsertText = $"<{tag.Tag}>"
            });
          }
        }

        if (AutoCompleteItems.Count > 0)
        {
          AutoCompleteList.SelectedIndex = 0;
          AutoCompletePopup.IsOpen = true;
        }
      }
      catch
      {
        AutoCompletePopup.IsOpen = false;
      }
    }

    private void InsertAutoComplete(AutoCompleteItem item)
    {
      try
      {
        var document = SSMLEditor.Document;
        document.GetText(TextGetOptions.None, out string text);
        int position = document.Selection.StartPosition;

        // Find the start of the current word
        int wordStart = position - 1;
        while (wordStart >= 0 && char.IsLetterOrDigit(text[wordStart]))
        {
          wordStart--;
        }
        wordStart++;

        // Replace current word with auto-complete text
        document.Selection.SetRange(wordStart, position);
        document.Selection.SetText(TextSetOptions.None, item.InsertText);

        // Move cursor after inserted text
        int newPosition = wordStart + item.InsertText.Length;
        document.Selection.SetRange(newPosition, newPosition);

        AutoCompletePopup.IsOpen = false;
      }
      catch
      {
        AutoCompletePopup.IsOpen = false;
      }
    }
  }

  public class SSMLTagInfo
  {
    public string Tag { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
  }

  public class AutoCompleteItem
  {
    public string DisplayText { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string InsertText { get; set; } = string.Empty;
  }

  public class SSMLError
  {
    public int LineNumber { get; set; }
    public int ColumnNumber { get; set; }
    public string Message { get; set; } = string.Empty;
    public string Severity { get; set; } = "Error"; // Error, Warning
  }
}