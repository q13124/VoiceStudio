using System.Collections.ObjectModel;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;

namespace VoiceStudio.App.Controls;

public sealed partial class HelpOverlay : UserControl
{
    public static readonly DependencyProperty IsVisibleProperty =
        DependencyProperty.Register(
            nameof(IsVisible),
            typeof(bool),
            typeof(HelpOverlay),
            new PropertyMetadata(false, OnIsVisibleChanged));

    public static readonly DependencyProperty TitleProperty =
        DependencyProperty.Register(
            nameof(Title),
            typeof(string),
            typeof(HelpOverlay),
            new PropertyMetadata("Help"));

    public static readonly DependencyProperty HelpTextProperty =
        DependencyProperty.Register(
            nameof(HelpText),
            typeof(string),
            typeof(HelpOverlay),
            new PropertyMetadata(string.Empty));

    public static readonly DependencyProperty ShortcutsProperty =
        DependencyProperty.Register(
            nameof(Shortcuts),
            typeof(ObservableCollection<KeyboardShortcut>),
            typeof(HelpOverlay),
            new PropertyMetadata(new ObservableCollection<KeyboardShortcut>()));

    public static readonly DependencyProperty TipsProperty =
        DependencyProperty.Register(
            nameof(Tips),
            typeof(ObservableCollection<string>),
            typeof(HelpOverlay),
            new PropertyMetadata(new ObservableCollection<string>()));

    public bool IsVisible
    {
        get => (bool)GetValue(IsVisibleProperty);
        set => SetValue(IsVisibleProperty, value);
    }

    public string Title
    {
        get => (string)GetValue(TitleProperty);
        set => SetValue(TitleProperty, value);
    }

    public string HelpText
    {
        get => (string)GetValue(HelpTextProperty);
        set => SetValue(HelpTextProperty, value);
    }

    public ObservableCollection<KeyboardShortcut> Shortcuts
    {
        get => (ObservableCollection<KeyboardShortcut>)GetValue(ShortcutsProperty);
        set => SetValue(ShortcutsProperty, value);
    }

    public ObservableCollection<string> Tips
    {
        get => (ObservableCollection<string>)GetValue(TipsProperty);
        set => SetValue(TipsProperty, value);
    }

    public bool HasShortcuts => Shortcuts != null && Shortcuts.Count > 0;
    public bool HasTips => Tips != null && Tips.Count > 0;

    public HelpOverlay()
    {
        this.InitializeComponent();
        this.KeyDown += HelpOverlay_KeyDown;
    }

    private static void OnIsVisibleChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        if (d is HelpOverlay overlay)
        {
            overlay.Visibility = overlay.IsVisible ? Visibility.Visible : Visibility.Collapsed;
        }
    }

    private void HelpOverlay_KeyDown(object sender, KeyRoutedEventArgs e)
    {
        if (e.Key == Windows.System.VirtualKey.Escape && IsVisible)
        {
            Close();
            e.Handled = true;
        }
    }

    private void CloseButton_Click(object sender, RoutedEventArgs e)
    {
        Close();
    }

    public void Close()
    {
        IsVisible = false;
    }

    public void Hide()
    {
        Close();
    }

    public bool IsOpen => IsVisible;

    public void Show()
    {
        IsVisible = true;
    }
}

public class KeyboardShortcut
{
    public string Key { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
}

