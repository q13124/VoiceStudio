using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Controls.Primitives;
using Microsoft.UI.Xaml.Input;
using System.Collections.ObjectModel;
using System.Linq;
using Windows.Foundation;
using Windows.ApplicationModel.DataTransfer;

namespace VoiceStudio.App.Controls
{
  public sealed partial class PanelStack : UserControl
  {
    public static readonly DependencyProperty PanelsProperty =
        DependencyProperty.Register(
            nameof(Panels),
            typeof(ObservableCollection<PanelStackItem>),
            typeof(PanelStack),
            new PropertyMetadata(new ObservableCollection<PanelStackItem>(), OnPanelsChanged));

    public static readonly DependencyProperty ActivePanelIdProperty =
        DependencyProperty.Register(
            nameof(ActivePanelId),
            typeof(string),
            typeof(PanelStack),
            new PropertyMetadata(string.Empty, OnActivePanelChanged));

    public static readonly DependencyProperty HasMultiplePanelsProperty =
        DependencyProperty.Register(
            nameof(HasMultiplePanels),
            typeof(bool),
            typeof(PanelStack),
            new PropertyMetadata(false));

    public ObservableCollection<PanelStackItem> Panels
    {
      get => (ObservableCollection<PanelStackItem>)GetValue(PanelsProperty);
      set => SetValue(PanelsProperty, value);
    }

    public string ActivePanelId
    {
      get => (string)GetValue(ActivePanelIdProperty);
      set => SetValue(ActivePanelIdProperty, value);
    }

    public bool HasMultiplePanels
    {
      get => (bool)GetValue(HasMultiplePanelsProperty);
      private set => SetValue(HasMultiplePanelsProperty, value);
    }

    private PanelStackItem? _draggedItem;
    private int _dragStartIndex = -1;

    public PanelStack()
    {
      this.InitializeComponent();
      Panels = new ObservableCollection<PanelStackItem>();
      Panels.CollectionChanged += Panels_CollectionChanged;
    }

    private static void OnPanelsChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
      if (d is PanelStack stack)
      {
        if (e.OldValue is ObservableCollection<PanelStackItem> oldCollection)
        {
          oldCollection.CollectionChanged -= stack.Panels_CollectionChanged;
        }
        if (e.NewValue is ObservableCollection<PanelStackItem> newCollection)
        {
          newCollection.CollectionChanged += stack.Panels_CollectionChanged;
        }
        stack.UpdateHasMultiplePanels();
        stack.RebuildTabs();
      }
    }

    private static void OnActivePanelChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
      if (d is PanelStack stack)
      {
        stack.UpdateActiveContent();
      }
    }

    private void Panels_CollectionChanged(object? sender, System.Collections.Specialized.NotifyCollectionChangedEventArgs e)
    {
      UpdateHasMultiplePanels();
      RebuildTabs();
    }

    private void UpdateHasMultiplePanels()
    {
      HasMultiplePanels = Panels.Count > 1;
    }

    private void RebuildTabs()
    {
      TabBar.Children.Clear();

      for (int i = 0; i < Panels.Count; i++)
      {
        var panel = Panels[i];
        var tabContainer = CreateTabContainer(panel, i);
        TabBar.Children.Add(tabContainer);
      }

      UpdateActiveContent();
    }

    private Border CreateTabContainer(PanelStackItem panel, int index)
    {
      var container = new Border
      {
        Tag = panel.PanelId,
        Margin = new Thickness(4, 4, 0, 4),
        Padding = new Thickness(0),
        CornerRadius = new CornerRadius(4, 4, 0, 0),
        Background = panel.PanelId == ActivePanelId
              ? new Microsoft.UI.Xaml.Media.SolidColorBrush(Microsoft.UI.Colors.Transparent)
              : new Microsoft.UI.Xaml.Media.SolidColorBrush(Microsoft.UI.Colors.Transparent),
        BorderBrush = panel.PanelId == ActivePanelId
              ? new Microsoft.UI.Xaml.Media.SolidColorBrush(Windows.UI.Color.FromArgb(255, 0, 183, 194)) // VSQ.Accent.Cyan
              : new Microsoft.UI.Xaml.Media.SolidColorBrush(Microsoft.UI.Colors.Transparent),
        BorderThickness = panel.PanelId == ActivePanelId ? new Thickness(0, 0, 0, 2) : new Thickness(0),
        MinWidth = 100
      };

      var stackPanel = new StackPanel
      {
        Orientation = Orientation.Horizontal,
        Spacing = 4,
        Padding = new Thickness(12, 6, 8, 6)
      };

      var tabButton = new ToggleButton
      {
        Content = panel.DisplayName,
        Tag = panel.PanelId,
        IsChecked = panel.PanelId == ActivePanelId,
        HorizontalAlignment = HorizontalAlignment.Stretch,
        HorizontalContentAlignment = HorizontalAlignment.Left,
        Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(Microsoft.UI.Colors.Transparent),
        BorderThickness = new Thickness(0),
        Padding = new Thickness(0)
      };

      tabButton.Click += (s, e) =>
      {
        if (s is ToggleButton btn && btn.Tag is string panelId)
        {
          ActivePanelId = panelId;
        }
      };

      // Close button
      var closeButton = new Button
      {
        Content = "×",
        Width = 20,
        Height = 20,
        Padding = new Thickness(0),
        FontSize = 16,
        Tag = panel.PanelId,
        Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(Microsoft.UI.Colors.Transparent),
        BorderThickness = new Thickness(0),
        HorizontalAlignment = HorizontalAlignment.Center,
        VerticalAlignment = VerticalAlignment.Center,
        Opacity = 0.6
      };

      closeButton.Click += CloseButton_Click;
      closeButton.PointerEntered += (s, e) => { if (s is Button btn) btn.Opacity = 1.0; };
      closeButton.PointerExited += (s, e) => { if (s is Button btn) btn.Opacity = 0.6; };

      stackPanel.Children.Add(tabButton);
      stackPanel.Children.Add(closeButton);

      container.Child = stackPanel;

      // Drag-and-drop support
      container.CanDrag = true;
      container.DragStarting += (s, e) => Tab_DragStarting(s, e, panel, index);
      container.DragOver += Tab_DragOver;
      container.Drop += (s, e) => Tab_Drop(s, e, index);

      return container;
    }

    private void Tab_DragStarting(object sender, DragStartingEventArgs e, PanelStackItem panel, int index)
    {
      _draggedItem = panel;
      _dragStartIndex = index;
      e.Data.Properties.Add("PanelId", panel.PanelId);
      e.Data.Properties.Add("SourceIndex", index);
    }

    private void Tab_DragOver(object sender, DragEventArgs e)
    {
      e.AcceptedOperation = DataPackageOperation.Move;
      e.DragUIOverride.IsGlyphVisible = false;
      e.DragUIOverride.IsContentVisible = false;
      e.DragUIOverride.IsCaptionVisible = false;

      if (sender is Border border)
      {
        border.Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(
            Windows.UI.Color.FromArgb(50, 0, 183, 194));
      }
    }

    private void Tab_Drop(object sender, DragEventArgs e, int targetIndex)
    {
      if (sender is Border border)
      {
        border.Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(Microsoft.UI.Colors.Transparent);
      }

      if (_draggedItem == null || _dragStartIndex < 0)
        return;

      if (e.Data.Properties.TryGetValue("SourceIndex", out var sourceIndexObj) &&
          sourceIndexObj is int sourceIndex)
      {
        if (sourceIndex != targetIndex)
        {
          Panels.Move(sourceIndex, targetIndex);

          // If we moved the active panel, update ActivePanelId to maintain selection
          if (_draggedItem.PanelId == ActivePanelId)
          {
            ActivePanelId = _draggedItem.PanelId;
          }
        }
      }

      _draggedItem = null;
      _dragStartIndex = -1;
    }

    private void CloseButton_Click(object sender, RoutedEventArgs e)
    {
      if (sender is Button btn && btn.Tag is string panelId)
      {
        var panelToRemove = Panels.FirstOrDefault(p => p.PanelId == panelId);
        if (panelToRemove != null)
        {
          // If closing the active panel, switch to another panel first
          if (panelId == ActivePanelId)
          {
            var index = Panels.IndexOf(panelToRemove);
            if (index > 0)
            {
              ActivePanelId = Panels[index - 1].PanelId;
            }
            else if (Panels.Count > 1)
            {
              ActivePanelId = Panels[1].PanelId;
            }
          }

          Panels.Remove(panelToRemove);

          // If no panels remain, raise event or handle empty state
          if (Panels.Count == 0)
          {
            ActivePanelId = string.Empty;
            ContentPresenter.Content = null;
          }
        }
      }
    }

    private void UpdateActiveContent()
    {
      var activePanel = Panels.FirstOrDefault(p => p.PanelId == ActivePanelId);
      if (activePanel != null)
      {
        ContentPresenter.Content = activePanel.Content;
      }
      else if (Panels.Count > 0)
      {
        // Default to first panel if active not found
        ActivePanelId = Panels[0].PanelId;
      }
      else
      {
        ContentPresenter.Content = null;
      }

      // Update tab button states and borders
      foreach (var child in TabBar.Children)
      {
        if (child is Border border && border.Tag is string panelId)
        {
          bool isActive = panelId == ActivePanelId;
          border.BorderBrush = isActive
              ? new Microsoft.UI.Xaml.Media.SolidColorBrush(Windows.UI.Color.FromArgb(255, 0, 183, 194))
              : new Microsoft.UI.Xaml.Media.SolidColorBrush(Microsoft.UI.Colors.Transparent);
          border.BorderThickness = isActive ? new Thickness(0, 0, 0, 2) : new Thickness(0);

          if (border.Child is StackPanel stackPanel &&
              stackPanel.Children.Count > 0 &&
              stackPanel.Children[0] is ToggleButton btn)
          {
            btn.IsChecked = isActive;
          }
        }
      }
    }

    /// <summary>
    /// Adds a panel to the stack.
    /// </summary>
    public void AddPanel(PanelStackItem panel)
    {
      if (!Panels.Any(p => p.PanelId == panel.PanelId))
      {
        Panels.Add(panel);
        ActivePanelId = panel.PanelId;
      }
      else
      {
        // Panel already exists, just switch to it
        ActivePanelId = panel.PanelId;
      }
    }

    /// <summary>
    /// Removes a panel from the stack.
    /// </summary>
    public void RemovePanel(string panelId)
    {
      var panel = Panels.FirstOrDefault(p => p.PanelId == panelId);
      if (panel != null)
      {
        if (panelId == ActivePanelId)
        {
          var index = Panels.IndexOf(panel);
          if (index > 0)
          {
            ActivePanelId = Panels[index - 1].PanelId;
          }
          else if (Panels.Count > 1)
          {
            ActivePanelId = Panels[1].PanelId;
          }
        }

        Panels.Remove(panel);
      }
    }
  }

  public class PanelStackItem
  {
    public string PanelId { get; set; } = string.Empty;
    public string DisplayName { get; set; } = string.Empty;
    public UIElement Content { get; set; } = null!;
  }
}

