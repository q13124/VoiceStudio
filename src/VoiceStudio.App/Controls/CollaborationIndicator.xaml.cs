using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using System;
using System.Linq;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Controls
{
  /// <summary>
  /// Collaboration indicator control showing active users.
  /// Implements IDEA 25: Real-Time Collaboration Indicators.
  /// </summary>
  public sealed partial class CollaborationIndicator : UserControl
  {
    private CollaborationService? _collaborationService;
    private readonly StackPanel _rootPanel = new();
    private readonly StackPanel _userListPanel = new();
    private readonly TextBlock _emptyStateText = new();

    /// <summary>
    /// Event raised when the user requests to close the indicator panel.
    /// </summary>
    public event EventHandler? CloseRequested;

    public CollaborationIndicator()
    {
      InitializeComponent();
      _rootPanel.Spacing = 6;

      // Header row with title and close button
      var headerRow = new Grid();
      headerRow.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
      headerRow.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });

      var header = new TextBlock
      {
        Text = "Active Collaborators",
        FontWeight = Microsoft.UI.Text.FontWeights.SemiBold,
        VerticalAlignment = VerticalAlignment.Center
      };
      Grid.SetColumn(header, 0);
      headerRow.Children.Add(header);

      var closeButton = new Button
      {
        Content = new FontIcon
        {
          Glyph = "\uE711", // Close icon
          FontSize = 12,
          FontFamily = new FontFamily("Segoe Fluent Icons")
        },
        Padding = new Thickness(4),
        Background = new SolidColorBrush(Microsoft.UI.Colors.Transparent),
        BorderThickness = new Thickness(0)
      };
      ToolTipService.SetToolTip(closeButton, "Close");
      closeButton.Click += CloseButton_Click;
      Grid.SetColumn(closeButton, 1);
      headerRow.Children.Add(closeButton);

      _emptyStateText.Text = "No collaborators connected";
      _emptyStateText.Opacity = 0.6;
      _emptyStateText.Foreground = new SolidColorBrush(Microsoft.UI.Colors.Gray);

      _rootPanel.Children.Add(headerRow);
      _rootPanel.Children.Add(_emptyStateText);
      _rootPanel.Children.Add(_userListPanel);

      Content = _rootPanel;

      Loaded += CollaborationIndicator_Loaded;
    }

    private void CloseButton_Click(object sender, RoutedEventArgs e)
    {
      CloseRequested?.Invoke(this, EventArgs.Empty);
    }

    private void CollaborationIndicator_Loaded(object _, RoutedEventArgs e)
    {
      _collaborationService = Services.ServiceProvider.TryGetCollaborationService();
      if (_collaborationService != null)
      {
        _collaborationService.UserJoined += CollaborationService_UserJoined;
        _collaborationService.UserLeft += CollaborationService_UserLeft;
        UpdateUserList();
      }
    }

    private void CollaborationService_UserJoined(object? sender, ActiveUserEventArgs e)
    {
      this.DispatcherQueue.TryEnqueue(() => UpdateUserList());
    }

    private void CollaborationService_UserLeft(object? sender, ActiveUserEventArgs e)
    {
      this.DispatcherQueue.TryEnqueue(() => UpdateUserList());
    }

    private void UpdateUserList()
    {
      if (_collaborationService == null)
        return;

      _userListPanel.Children.Clear();

      var users = _collaborationService.ActiveUsers.ToList();
      if (users.Count == 0)
      {
        _emptyStateText.Visibility = Visibility.Visible;
        return;
      }

      _emptyStateText.Visibility = Visibility.Collapsed;
      foreach (var user in users)
      {
        var userRow = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 6 };
        var colorIndicator = new Border
        {
          Width = 8,
          Height = 8,
          CornerRadius = new CornerRadius(4),
          Background = new SolidColorBrush(ParseColor(user.Color))
        };
        var nameBlock = new TextBlock
        {
          Text = user.UserName,
          VerticalAlignment = VerticalAlignment.Center
        };
        userRow.Children.Add(colorIndicator);
        userRow.Children.Add(nameBlock);
        _userListPanel.Children.Add(userRow);
      }
    }

    private static Windows.UI.Color ParseColor(string? hex)
    {
      if (string.IsNullOrWhiteSpace(hex) || !hex.StartsWith("#"))
        return Microsoft.UI.Colors.Cyan;

      var value = hex.TrimStart('#');
      if (value.Length == 6)
      {
        value = "FF" + value;
      }

      if (value.Length != 8)
        return Microsoft.UI.Colors.Cyan;

      if (byte.TryParse(value.Substring(0, 2), System.Globalization.NumberStyles.HexNumber, null, out var a) &&
          byte.TryParse(value.Substring(2, 2), System.Globalization.NumberStyles.HexNumber, null, out var r) &&
          byte.TryParse(value.Substring(4, 2), System.Globalization.NumberStyles.HexNumber, null, out var g) &&
          byte.TryParse(value.Substring(6, 2), System.Globalization.NumberStyles.HexNumber, null, out var b))
      {
        return Windows.UI.Color.FromArgb(a, r, g, b);
      }

      return Microsoft.UI.Colors.Cyan;
    }
  }
}