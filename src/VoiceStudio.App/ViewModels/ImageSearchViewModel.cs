using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Services;
using VoiceStudio.App.Utilities;

namespace VoiceStudio.App.ViewModels
{
  /// <summary>
  /// ViewModel for the ImageSearchView panel - Image search functionality.
  /// </summary>
  public partial class ImageSearchViewModel : BaseViewModel, IPanelView
  {
    private readonly IBackendClient _backendClient;
    private readonly ToastNotificationService? _toastNotificationService;

    public string PanelId => "image-search";
    public string DisplayName => ResourceHelper.GetString("Panel.ImageSearch.DisplayName", "Image Search");
    public PanelRegion Region => PanelRegion.Center;

    [ObservableProperty]
    private ObservableCollection<ImageSearchResultItem> searchResults = new();

    [ObservableProperty]
    private ImageSearchResultItem? selectedResult;

    [ObservableProperty]
    private ObservableCollection<ImageSourceItem> availableSources = new();

    [ObservableProperty]
    private ObservableCollection<string> availableCategories = new();

    [ObservableProperty]
    private ObservableCollection<string> availableColors = new();

    [ObservableProperty]
    private string searchQuery = string.Empty;

    [ObservableProperty]
    private string? selectedSource;

    [ObservableProperty]
    private string? selectedCategory;

    [ObservableProperty]
    private string? selectedOrientation;

    [ObservableProperty]
    private string? selectedColor;

    [ObservableProperty]
    private int currentPage = 1;

    [ObservableProperty]
    private int totalPages = 1;

    [ObservableProperty]
    private int totalResults;

    [ObservableProperty]
    private int perPage = 20;

    [ObservableProperty]
    private bool isSearching;

    [ObservableProperty]
    private ObservableCollection<string> availableOrientations = new() { "landscape", "portrait", "square" };

    public ImageSearchViewModel(IViewModelContext context, IBackendClient backendClient)
        : base(context)
    {
      _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));

      // Get services (may be null if not initialized)
      try
      {
        _toastNotificationService = ServiceProvider.GetToastNotificationService();
      }
      catch
      {
        // Services may not be initialized yet - that's okay
        _toastNotificationService = null;
      }

      SearchCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("Search");
        await SearchAsync(ct);
      }, () => !IsSearching && !string.IsNullOrWhiteSpace(SearchQuery) && !IsLoading);
      LoadSourcesCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("LoadSources");
        await LoadSourcesAsync(ct);
      }, () => !IsLoading);
      LoadCategoriesCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("LoadCategories");
        await LoadCategoriesAsync(ct);
      }, () => !IsLoading);
      LoadColorsCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("LoadColors");
        await LoadColorsAsync(ct);
      }, () => !IsLoading);
      NextPageCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("NextPage");
        await NextPageAsync(ct);
      }, () => CurrentPage < TotalPages && !IsLoading);
      PreviousPageCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("PreviousPage");
        await PreviousPageAsync(ct);
      }, () => CurrentPage > 1 && !IsLoading);
      RefreshCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("Refresh");
        await RefreshAsync(ct);
      }, () => !IsLoading);
      ClearHistoryCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("ClearHistory");
        await ClearHistoryAsync(ct);
      }, () => !IsLoading);

      // Load initial data
      _ = LoadSourcesAsync(CancellationToken.None);
      _ = LoadCategoriesAsync(CancellationToken.None);
      _ = LoadColorsAsync(CancellationToken.None);
    }

    public IAsyncRelayCommand SearchCommand { get; }
    public IAsyncRelayCommand LoadSourcesCommand { get; }
    public IAsyncRelayCommand LoadCategoriesCommand { get; }
    public IAsyncRelayCommand LoadColorsCommand { get; }
    public IAsyncRelayCommand NextPageCommand { get; }
    public IAsyncRelayCommand PreviousPageCommand { get; }
    public IAsyncRelayCommand RefreshCommand { get; }
    public IAsyncRelayCommand ClearHistoryCommand { get; }

    partial void OnIsSearchingChanged(bool value)
    {
      SearchCommand.NotifyCanExecuteChanged();
    }

    partial void OnSearchQueryChanged(string value)
    {
      SearchCommand.NotifyCanExecuteChanged();
    }

    partial void OnCurrentPageChanged(int value)
    {
      NextPageCommand.NotifyCanExecuteChanged();
      PreviousPageCommand.NotifyCanExecuteChanged();
    }

    partial void OnTotalPagesChanged(int value)
    {
      NextPageCommand.NotifyCanExecuteChanged();
    }

    private async Task SearchAsync(CancellationToken cancellationToken)
    {
      if (string.IsNullOrWhiteSpace(SearchQuery))
      {
        ErrorMessage = ResourceHelper.GetString("ImageSearch.SearchQueryRequired", "Search query is required");
        return;
      }

      IsSearching = true;
      ErrorMessage = null;

      try
      {
        var request = new ImageSearchRequest
        {
          Query = SearchQuery,
          Source = SelectedSource,
          Category = SelectedCategory,
          Orientation = SelectedOrientation,
          Color = SelectedColor,
          Page = CurrentPage,
          PerPage = PerPage
        };

        var response = await _backendClient.SendRequestAsync<ImageSearchRequest, ImageSearchResponse>(
            "/api/image-search/search",
            request,
            System.Net.Http.HttpMethod.Post,
            cancellationToken
        );

        if (response != null)
        {
          SearchResults.Clear();
          foreach (var result in response.Results)
          {
            SearchResults.Add(new ImageSearchResultItem(
                result.ResultId,
                result.ImageUrl,
                result.ThumbnailUrl,
                result.Title,
                result.Description,
                result.Source,
                result.Width,
                result.Height,
                result.FileSize,
                result.License,
                result.Author,
                result.AuthorUrl,
                result.Tags
            ));
          }

          TotalResults = response.Total;
          TotalPages = response.TotalPages;
          CurrentPage = response.Page;

          StatusMessage = ResourceHelper.FormatString("ImageSearch.FoundResults", TotalResults);
          _toastNotificationService?.ShowSuccess(
              ResourceHelper.FormatString("ImageSearch.FoundImages", TotalResults),
              ResourceHelper.GetString("Toast.Title.SearchComplete", "Search Complete"));
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "Search");
        _toastNotificationService?.ShowError(
            ResourceHelper.GetString("Toast.Title.SearchFailed", "Search Failed"),
            ex.Message);
      }
      finally
      {
        IsSearching = false;
      }
    }

    private async Task LoadSourcesAsync(CancellationToken cancellationToken)
    {
      try
      {
        var sources = await _backendClient.SendRequestAsync<object, ImageSource[]>(
            "/api/image-search/sources",
            null,
            System.Net.Http.HttpMethod.Get,
            cancellationToken
        );

        if (sources != null)
        {
          AvailableSources.Clear();
          foreach (var source in sources)
          {
            AvailableSources.Add(new ImageSourceItem(
                source.SourceId,
                source.Name,
                source.Description,
                source.RequiresApiKey,
                source.IsAvailable
            ));
          }
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "LoadSources");
        ErrorMessage = ResourceHelper.FormatString("ImageSearch.LoadSourcesFailed", ex.Message);
      }
    }

    private async Task LoadCategoriesAsync(CancellationToken cancellationToken)
    {
      try
      {
        var categories = await _backendClient.SendRequestAsync<object, string[]>(
            "/api/image-search/categories",
            null,
            System.Net.Http.HttpMethod.Get,
            cancellationToken
        );

        if (categories != null)
        {
          AvailableCategories.Clear();
          foreach (var category in categories)
          {
            AvailableCategories.Add(category);
          }
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "LoadCategories");
      }
    }

    private async Task LoadColorsAsync(CancellationToken cancellationToken)
    {
      try
      {
        var colors = await _backendClient.SendRequestAsync<object, string[]>(
            "/api/image-search/colors",
            null,
            System.Net.Http.HttpMethod.Get,
            cancellationToken
        );

        if (colors != null)
        {
          AvailableColors.Clear();
          foreach (var color in colors)
          {
            AvailableColors.Add(color);
          }
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "LoadColors");
        ErrorMessage = ResourceHelper.FormatString("ImageSearch.LoadColorsFailed", ex.Message);
      }
    }

    private async Task NextPageAsync(CancellationToken cancellationToken)
    {
      if (CurrentPage < TotalPages)
      {
        CurrentPage++;
        await SearchAsync(cancellationToken);
      }
    }

    private async Task PreviousPageAsync(CancellationToken cancellationToken)
    {
      if (CurrentPage > 1)
      {
        CurrentPage--;
        await SearchAsync(cancellationToken);
      }
    }

    private async Task RefreshAsync(CancellationToken cancellationToken)
    {
      await LoadSourcesAsync(cancellationToken);
      await LoadCategoriesAsync(cancellationToken);
      await LoadColorsAsync(cancellationToken);
      if (!string.IsNullOrWhiteSpace(SearchQuery))
      {
        await SearchAsync(cancellationToken);
      }
      StatusMessage = ResourceHelper.GetString("ImageSearch.Refreshed", "Refreshed");
    }

    private async Task ClearHistoryAsync(CancellationToken cancellationToken)
    {
      try
      {
        await _backendClient.SendRequestAsync<object, object>(
            "/api/image-search/history",
            null,
            System.Net.Http.HttpMethod.Delete,
            cancellationToken
        );

        StatusMessage = ResourceHelper.GetString("ImageSearch.SearchHistoryCleared", "Search history cleared");
        _toastNotificationService?.ShowSuccess(
            ResourceHelper.GetString("ImageSearch.SearchHistoryClearedDetail", "Search history cleared"),
            ResourceHelper.GetString("Toast.Title.HistoryCleared", "History Cleared"));
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "ClearHistory");
        _toastNotificationService?.ShowError(
            ResourceHelper.GetString("Toast.Title.ClearFailed", "Clear Failed"),
            ex.Message);
      }
    }

    // Request models
    private class ImageSearchRequest
    {
      public string Query { get; set; } = string.Empty;
      public string? Source { get; set; }
      public string? Category { get; set; }
      public string? Orientation { get; set; }
      public string? Color { get; set; }
      public int Page { get; set; } = 1;
      public int PerPage { get; set; } = 20;
    }

    private class ImageSearchResponse
    {
      public ImageSearchResult[] Results { get; set; } = Array.Empty<ImageSearchResult>();
      public int Total { get; set; }
      public int Page { get; set; }
      public int PerPage { get; set; }
      public int TotalPages { get; set; }
      public string Query { get; set; } = string.Empty;
      public string? Source { get; set; }
    }

    private class ImageSearchResult
    {
      public string ResultId { get; set; } = string.Empty;
      public string ImageUrl { get; set; } = string.Empty;
      public string? ThumbnailUrl { get; set; }
      public string Title { get; set; } = string.Empty;
      public string? Description { get; set; }
      public string Source { get; set; } = string.Empty;
      public int Width { get; set; }
      public int Height { get; set; }
      public int? FileSize { get; set; }
      public string? License { get; set; }
      public string? Author { get; set; }
      public string? AuthorUrl { get; set; }
      public string[] Tags { get; set; } = Array.Empty<string>();
    }

    private class ImageSource
    {
      public string SourceId { get; set; } = string.Empty;
      public string Name { get; set; } = string.Empty;
      public string Description { get; set; } = string.Empty;
      public bool RequiresApiKey { get; set; }
      public bool IsAvailable { get; set; }
    }
  }

  // Data models
  public class ImageSearchResultItem : ObservableObject
  {
    public string ResultId { get; set; }
    public string ImageUrl { get; set; }
    public string? ThumbnailUrl { get; set; }
    public string Title { get; set; }
    public string? Description { get; set; }
    public string Source { get; set; }
    public int Width { get; set; }
    public int Height { get; set; }
    public int? FileSize { get; set; }
    public string? License { get; set; }
    public string? Author { get; set; }
    public string? AuthorUrl { get; set; }
    public string[] Tags { get; set; }

    public string DimensionsDisplay => $"{Width} × {Height}";
    public string FileSizeDisplay => FileSize.HasValue ? FormatFileSize(FileSize.Value) : ResourceHelper.GetString("ImageSearch.Unknown", "Unknown");
    public string TagsDisplay => Tags?.Length > 0 ? string.Join(", ", Tags) : "No tags";

    public ImageSearchResultItem(string resultId, string imageUrl, string? thumbnailUrl, string title, string? description, string source, int width, int height, int? fileSize, string? license, string? author, string? authorUrl, string[] tags)
    {
      ResultId = resultId;
      ImageUrl = imageUrl;
      ThumbnailUrl = thumbnailUrl;
      Title = title;
      Description = description;
      Source = source;
      Width = width;
      Height = height;
      FileSize = fileSize;
      License = license;
      Author = author;
      AuthorUrl = authorUrl;
      Tags = tags ?? Array.Empty<string>();
    }

    private static string FormatFileSize(long bytes)
    {
      string[] sizes = { "B", "KB", "MB", "GB" };
      double len = bytes;
      int order = 0;
      while (len >= 1024 && order < sizes.Length - 1)
      {
        order++;
        len /= 1024;
      }
      return $"{len:0.##} {sizes[order]}";
    }
  }

  public class ImageSourceItem : ObservableObject
  {
    public string SourceId { get; set; }
    public string Name { get; set; }
    public string Description { get; set; }
    public bool RequiresApiKey { get; set; }
    public bool IsAvailable { get; set; }

    public string DisplayName => Name + (RequiresApiKey ? " (API Key Required)" : "");

    public ImageSourceItem(string sourceId, string name, string description, bool requiresApiKey, bool isAvailable)
    {
      SourceId = sourceId;
      Name = name;
      Description = description;
      RequiresApiKey = requiresApiKey;
      IsAvailable = isAvailable;
    }
  }
}