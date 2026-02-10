// Phase 5: Search System
// Task 5.9: Global search functionality

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.App.Features.Search;

/// <summary>
/// Search result types.
/// </summary>
public enum SearchResultType
{
    Project,
    VoiceProfile,
    AudioClip,
    Engine,
    Setting,
    Command,
    Documentation,
    Recent,
}

/// <summary>
/// A single search result.
/// </summary>
public class SearchResult
{
    public string Id { get; set; } = "";
    public string Title { get; set; } = "";
    public string Subtitle { get; set; } = "";
    public SearchResultType Type { get; set; }
    public string? IconGlyph { get; set; }
    public double Score { get; set; }
    public Dictionary<string, string> Metadata { get; set; } = new();
    public Action? NavigateAction { get; set; }
}

/// <summary>
/// Search provider interface.
/// </summary>
public interface ISearchProvider
{
    string Name { get; }
    SearchResultType ResultType { get; }
    int Priority { get; }
    
    Task<IEnumerable<SearchResult>> SearchAsync(
        string query,
        int maxResults,
        CancellationToken cancellationToken);
}

/// <summary>
/// Service for global search across all content.
/// </summary>
public class SearchService
{
    private readonly List<ISearchProvider> _providers = new();
    private readonly List<string> _recentSearches = new();
    private readonly int _maxRecentSearches = 10;
    private CancellationTokenSource? _searchCts;

    public event EventHandler<IEnumerable<SearchResult>>? SearchCompleted;

    /// <summary>
    /// Register a search provider.
    /// </summary>
    public void RegisterProvider(ISearchProvider provider)
    {
        _providers.Add(provider);
        _providers.Sort((a, b) => b.Priority.CompareTo(a.Priority));
    }

    /// <summary>
    /// Perform a search.
    /// </summary>
    public async Task<IEnumerable<SearchResult>> SearchAsync(
        string query,
        int maxResults = 20,
        SearchResultType[]? filterTypes = null)
    {
        // Cancel any existing search
        _searchCts?.Cancel();
        _searchCts = new CancellationTokenSource();
        var token = _searchCts.Token;
        
        if (string.IsNullOrWhiteSpace(query))
        {
            return GetRecentSearchResults();
        }
        
        var results = new List<SearchResult>();
        var tasks = new List<Task<IEnumerable<SearchResult>>>();
        
        // Query all providers
        foreach (var provider in _providers)
        {
            if (filterTypes != null && !filterTypes.Contains(provider.ResultType))
            {
                continue;
            }
            
            tasks.Add(provider.SearchAsync(query, maxResults, token));
        }
        
        try
        {
            await Task.WhenAll(tasks);
            
            foreach (var task in tasks)
            {
                results.AddRange(await task);
            }
        }
        catch (OperationCanceledException)
        {
            return Enumerable.Empty<SearchResult>();
        }
        
        // Sort by score and take top results
        var sortedResults = results
            .OrderByDescending(r => r.Score)
            .Take(maxResults)
            .ToList();
        
        SearchCompleted?.Invoke(this, sortedResults);
        
        // Save to recent searches
        AddToRecentSearches(query);
        
        return sortedResults;
    }

    /// <summary>
    /// Get recent search terms.
    /// </summary>
    public IReadOnlyList<string> GetRecentSearches() => _recentSearches;

    /// <summary>
    /// Clear recent searches.
    /// </summary>
    public void ClearRecentSearches() => _recentSearches.Clear();

    /// <summary>
    /// Get search suggestions based on partial query.
    /// </summary>
    public async Task<IEnumerable<string>> GetSuggestionsAsync(string partialQuery)
    {
        if (string.IsNullOrWhiteSpace(partialQuery))
        {
            return _recentSearches;
        }
        
        var suggestions = new List<string>();
        
        // Add matching recent searches
        suggestions.AddRange(
            _recentSearches.Where(s =>
                s.StartsWith(partialQuery, StringComparison.OrdinalIgnoreCase)));
        
        // Get quick results for suggestions
        var results = await SearchAsync(partialQuery, 5);
        suggestions.AddRange(results.Select(r => r.Title));
        
        return suggestions.Distinct().Take(10);
    }

    private void AddToRecentSearches(string query)
    {
        _recentSearches.Remove(query);
        _recentSearches.Insert(0, query);
        
        while (_recentSearches.Count > _maxRecentSearches)
        {
            _recentSearches.RemoveAt(_recentSearches.Count - 1);
        }
    }

    private IEnumerable<SearchResult> GetRecentSearchResults()
    {
        return _recentSearches.Select(s => new SearchResult
        {
            Id = $"recent_{s}",
            Title = s,
            Subtitle = "Recent search",
            Type = SearchResultType.Recent,
            IconGlyph = "\uE81C",
            Score = 0,
        });
    }
}

/// <summary>
/// Command search provider.
/// </summary>
public class CommandSearchProvider : ISearchProvider
{
    private readonly PowerUser.ShortcutManager _shortcutManager;

    public CommandSearchProvider(PowerUser.ShortcutManager shortcutManager)
    {
        _shortcutManager = shortcutManager;
    }

    public string Name => "Commands";
    public SearchResultType ResultType => SearchResultType.Command;
    public int Priority => 100;

    public Task<IEnumerable<SearchResult>> SearchAsync(
        string query,
        int maxResults,
        CancellationToken cancellationToken)
    {
        var results = new List<SearchResult>();
        var queryLower = query.ToLowerInvariant();
        
        foreach (var command in _shortcutManager.GetCommands())
        {
            var nameLower = command.Name.ToLowerInvariant();
            var descLower = command.Description.ToLowerInvariant();
            
            double score = 0;
            
            if (nameLower.StartsWith(queryLower))
            {
                score = 1.0;
            }
            else if (nameLower.Contains(queryLower))
            {
                score = 0.8;
            }
            else if (descLower.Contains(queryLower))
            {
                score = 0.5;
            }
            
            if (score > 0)
            {
                results.Add(new SearchResult
                {
                    Id = command.Id,
                    Title = command.Name,
                    Subtitle = command.Description,
                    Type = SearchResultType.Command,
                    IconGlyph = command.IconGlyph ?? "\uE756",
                    Score = score,
                    NavigateAction = async () =>
                    {
                        if (command.ExecuteAsync != null)
                        {
                            await command.ExecuteAsync();
                        }
                    },
                });
            }
        }
        
        return Task.FromResult<IEnumerable<SearchResult>>(
            results.OrderByDescending(r => r.Score).Take(maxResults));
    }
}

/// <summary>
/// Settings search provider.
/// </summary>
public class SettingsSearchProvider : ISearchProvider
{
    private readonly List<(string Id, string Name, string Description, string Category)> _settings;

    public SettingsSearchProvider()
    {
        _settings = new List<(string, string, string, string)>
        {
            ("theme", "Theme", "Change application theme", "Appearance"),
            ("language", "Language", "Change application language", "General"),
            ("autosave", "Auto Save", "Configure auto save settings", "General"),
            ("audio_device", "Audio Device", "Select audio input/output devices", "Audio"),
            ("sample_rate", "Sample Rate", "Set audio sample rate", "Audio"),
            ("engine", "Default Engine", "Set default synthesis engine", "Synthesis"),
            ("accessibility", "Accessibility", "Configure accessibility options", "Accessibility"),
            ("shortcuts", "Keyboard Shortcuts", "Customize keyboard shortcuts", "Keyboard"),
        };
    }

    public string Name => "Settings";
    public SearchResultType ResultType => SearchResultType.Setting;
    public int Priority => 80;

    public Task<IEnumerable<SearchResult>> SearchAsync(
        string query,
        int maxResults,
        CancellationToken cancellationToken)
    {
        var results = new List<SearchResult>();
        var queryLower = query.ToLowerInvariant();
        
        foreach (var setting in _settings)
        {
            var nameLower = setting.Name.ToLowerInvariant();
            var descLower = setting.Description.ToLowerInvariant();
            var categoryLower = setting.Category.ToLowerInvariant();
            
            double score = 0;
            
            if (nameLower.StartsWith(queryLower))
            {
                score = 1.0;
            }
            else if (nameLower.Contains(queryLower))
            {
                score = 0.8;
            }
            else if (descLower.Contains(queryLower) || categoryLower.Contains(queryLower))
            {
                score = 0.5;
            }
            
            if (score > 0)
            {
                results.Add(new SearchResult
                {
                    Id = $"setting_{setting.Id}",
                    Title = setting.Name,
                    Subtitle = $"{setting.Category} > {setting.Description}",
                    Type = SearchResultType.Setting,
                    IconGlyph = "\uE713",
                    Score = score,
                    Metadata = { ["Category"] = setting.Category },
                });
            }
        }
        
        return Task.FromResult<IEnumerable<SearchResult>>(
            results.OrderByDescending(r => r.Score).Take(maxResults));
    }
}
