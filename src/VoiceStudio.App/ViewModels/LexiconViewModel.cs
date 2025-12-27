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
using VoiceStudio.App.Services.UndoableActions;
using VoiceStudio.App.Utilities;
using LexiconModel = VoiceStudio.App.ViewModels.LexiconViewModel.Lexicon;
using LexiconEntryModel = VoiceStudio.App.ViewModels.LexiconViewModel.LexiconEntry;
using LexiconSearchResponseModel = VoiceStudio.App.ViewModels.LexiconViewModel.LexiconSearchResponse;
using LexiconSearchResultModel = VoiceStudio.App.ViewModels.LexiconViewModel.LexiconSearchResult;

namespace VoiceStudio.App.ViewModels
{
    /// <summary>
    /// ViewModel for the LexiconView panel - Pronunciation lexicon management.
    /// </summary>
    public partial class LexiconViewModel : BaseViewModel, IPanelView
    {
        private readonly IBackendClient _backendClient;
        private readonly UndoRedoService? _undoRedoService;

        public string PanelId => "lexicon";
        public string DisplayName => ResourceHelper.GetString("Panel.Lexicon.DisplayName", "Pronunciation Lexicon");
        public PanelRegion Region => PanelRegion.Center;

        [ObservableProperty]
        private ObservableCollection<LexiconItem> lexicons = new();

        [ObservableProperty]
        private LexiconItem? selectedLexicon;

        [ObservableProperty]
        private ObservableCollection<LexiconEntryItem> entries = new();

        [ObservableProperty]
        private LexiconEntryItem? selectedEntry;

        [ObservableProperty]
        private string newLexiconName = string.Empty;

        [ObservableProperty]
        private string newLexiconLanguage = "en";

        [ObservableProperty]
        private string? newLexiconDescription;

        [ObservableProperty]
        private string newEntryWord = string.Empty;

        [ObservableProperty]
        private string newEntryPronunciation = string.Empty;

        [ObservableProperty]
        private string? newEntryPartOfSpeech;

        [ObservableProperty]
        private string? newEntryNotes;

        [ObservableProperty]
        private string searchQuery = string.Empty;

        [ObservableProperty]
        private ObservableCollection<LexiconSearchResultItem> searchResults = new();

        public LexiconViewModel(IBackendClient backendClient)
        {
            _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));

            // Get undo/redo service (may be null if not initialized)
            try
            {
                _undoRedoService = ServiceProvider.GetUndoRedoService();
            }
            catch
            {
                // Service may not be initialized yet - that's okay
                _undoRedoService = null;
            }

            LoadLexiconsCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("LoadLexicons");
                await LoadLexiconsAsync(ct);
            }, () => !IsLoading);
            CreateLexiconCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("CreateLexicon");
                await CreateLexiconAsync(ct);
            }, () => !string.IsNullOrWhiteSpace(NewLexiconName) && !IsLoading);
            UpdateLexiconCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("UpdateLexicon");
                await UpdateLexiconAsync(ct);
            }, () => !IsLoading);
            DeleteLexiconCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("DeleteLexicon");
                await DeleteLexiconAsync(ct);
            }, () => !IsLoading);
            LoadEntriesCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("LoadEntries");
                await LoadEntriesAsync(ct);
            }, () => !IsLoading);
            CreateEntryCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("CreateEntry");
                await CreateEntryAsync(ct);
            }, () => !IsLoading);
            UpdateEntryCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("UpdateEntry");
                await UpdateEntryAsync(ct);
            }, () => !IsLoading);
            DeleteEntryCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("DeleteEntry");
                await DeleteEntryAsync(ct);
            }, () => !IsLoading);
            SearchEntriesCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("SearchEntries");
                await SearchEntriesAsync(ct);
            }, () => !IsLoading);
            RefreshCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("Refresh");
                await RefreshAsync(ct);
            }, () => !IsLoading);

            // Load initial data
            _ = LoadLexiconsAsync(CancellationToken.None);
        }

        public IAsyncRelayCommand LoadLexiconsCommand { get; }
        public IAsyncRelayCommand CreateLexiconCommand { get; }
        public IAsyncRelayCommand UpdateLexiconCommand { get; }
        public IAsyncRelayCommand DeleteLexiconCommand { get; }
        public IAsyncRelayCommand LoadEntriesCommand { get; }
        public IAsyncRelayCommand CreateEntryCommand { get; }
        public IAsyncRelayCommand UpdateEntryCommand { get; }
        public IAsyncRelayCommand DeleteEntryCommand { get; }
        public IAsyncRelayCommand SearchEntriesCommand { get; }
        public IAsyncRelayCommand RefreshCommand { get; }

        partial void OnSelectedLexiconChanged(LexiconItem? value)
        {
            if (value != null)
            {
                _ = LoadEntriesAsync(CancellationToken.None);
            }
            else
            {
                Entries.Clear();
            }
        }

        private async Task LoadLexiconsAsync(CancellationToken cancellationToken)
        {
            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var lexicons = await _backendClient.SendRequestAsync<object, Lexicon[]>(
                    "/api/lexicon/lexicons",
                    null,
                    System.Net.Http.HttpMethod.Get,
                    cancellationToken
                );

                if (lexicons != null)
                {
                    Lexicons.Clear();
                    foreach (var lexicon in lexicons)
                    {
                        Lexicons.Add(new LexiconItem(lexicon));
                    }
                }
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                await HandleErrorAsync(ex, "LoadLexicons");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task CreateLexiconAsync(CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(NewLexiconName))
            {
                ErrorMessage = ResourceHelper.GetString("Lexicon.LexiconNameRequired", "Lexicon name is required");
                return;
            }

            try
            {
                IsLoading = true;
                ErrorMessage = null;

                var request = new
                {
                    name = NewLexiconName,
                    language = NewLexiconLanguage,
                    description = NewLexiconDescription
                };

                var lexicon = await _backendClient.SendRequestAsync<object, Lexicon>(
                    "/api/lexicon/lexicons",
                    request
                );

                if (lexicon != null)
                {
                    var lexiconItem = new LexiconItem(lexicon);
                    Lexicons.Add(lexiconItem);
                    SelectedLexicon = lexiconItem;
                    NewLexiconName = string.Empty;
                    NewLexiconDescription = null;

                    // Register undo action
                    if (_undoRedoService != null)
                    {
                        var action = new CreateLexiconAction(
                            Lexicons,
                            _backendClient,
                            lexiconItem,
                            onUndo: (l) =>
                            {
                                if (SelectedLexicon?.LexiconId == l.LexiconId)
                                {
                                    SelectedLexicon = Lexicons.FirstOrDefault();
                                    Entries.Clear();
                                }
                            },
                            onRedo: (l) =>
                            {
                                SelectedLexicon = l;
                            });
                        _undoRedoService.RegisterAction(action);
                    }

                    StatusMessage = ResourceHelper.GetString("Lexicon.LexiconCreated", "Lexicon created");
                }
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("Lexicon.CreateLexiconFailed", ex.Message);
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task UpdateLexiconAsync(CancellationToken cancellationToken)
        {
            if (SelectedLexicon == null)
            {
                ErrorMessage = ResourceHelper.GetString("Lexicon.NoLexiconSelected", "No lexicon selected");
                return;
            }

            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var request = new
                {
                    name = SelectedLexicon.Name,
                    language = SelectedLexicon.Language,
                    description = SelectedLexicon.Description
                };

                var lexicon = await _backendClient.SendRequestAsync<object, Lexicon>(
                    $"/api/lexicon/lexicons/{Uri.EscapeDataString(SelectedLexicon.LexiconId)}",
                    request,
                    System.Net.Http.HttpMethod.Put,
                    cancellationToken
                );

                if (lexicon != null)
                {
                    var index = Lexicons.IndexOf(SelectedLexicon);
                    var updatedItem = new LexiconItem(lexicon);
                    Lexicons[index] = updatedItem;
                    SelectedLexicon = updatedItem;
                    StatusMessage = ResourceHelper.GetString("Lexicon.LexiconUpdated", "Lexicon updated");
                }
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                await HandleErrorAsync(ex, "UpdateLexicon");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task DeleteLexiconAsync(CancellationToken cancellationToken = default)
        {
            if (SelectedLexicon == null)
            {
                ErrorMessage = ResourceHelper.GetString("Lexicon.NoLexiconSelected", "No lexicon selected");
                return;
            }

            try
            {
                IsLoading = true;
                ErrorMessage = null;

                await _backendClient.SendRequestAsync<object, object>(
                    $"/api/lexicon/lexicons/{Uri.EscapeDataString(SelectedLexicon.LexiconId)}",
                    null,
                    System.Net.Http.HttpMethod.Delete,
                    cancellationToken
                );

                var lexiconToDelete = SelectedLexicon;
                var originalIndex = Lexicons.IndexOf(lexiconToDelete);
                var wasSelected = SelectedLexicon != null;
                Lexicons.Remove(lexiconToDelete);
                SelectedLexicon = null;
                Entries.Clear();

                // Register undo action
                if (_undoRedoService != null && lexiconToDelete != null)
                {
                    var action = new DeleteLexiconAction(
                        Lexicons,
                        _backendClient,
                        lexiconToDelete,
                        originalIndex,
                        onUndo: (l) =>
                        {
                            SelectedLexicon = l;
                        },
                        onRedo: (l) =>
                        {
                            if (SelectedLexicon?.LexiconId == l.LexiconId)
                            {
                                SelectedLexicon = null;
                                Entries.Clear();
                            }
                        });
                    _undoRedoService.RegisterAction(action);
                }

                StatusMessage = ResourceHelper.GetString("Lexicon.LexiconDeleted", "Lexicon deleted");
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("Lexicon.DeleteLexiconFailed", ex.Message);
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task LoadEntriesAsync(CancellationToken cancellationToken)
        {
            if (SelectedLexicon == null)
            {
                return;
            }

            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var entries = await _backendClient.SendRequestAsync<object, LexiconEntry[]>(
                    $"/api/lexicon/lexicons/{Uri.EscapeDataString(SelectedLexicon.LexiconId)}/entries",
                    null,
                    System.Net.Http.HttpMethod.Get,
                    cancellationToken
                );

                if (entries != null)
                {
                    Entries.Clear();
                    foreach (var entry in entries)
                    {
                        Entries.Add(new LexiconEntryItem(entry));
                    }
                }
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                await HandleErrorAsync(ex, "LoadEntries");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task CreateEntryAsync(CancellationToken cancellationToken = default)
        {
            if (SelectedLexicon == null)
            {
                ErrorMessage = ResourceHelper.GetString("Lexicon.NoLexiconSelected", "No lexicon selected");
                return;
            }

            if (string.IsNullOrWhiteSpace(NewEntryWord) || string.IsNullOrWhiteSpace(NewEntryPronunciation))
            {
                ErrorMessage = ResourceHelper.GetString("Lexicon.WordAndPronunciationRequired", "Word and pronunciation are required");
                return;
            }

            try
            {
                IsLoading = true;
                ErrorMessage = null;

                var request = new
                {
                    word = NewEntryWord,
                    pronunciation = NewEntryPronunciation,
                    part_of_speech = NewEntryPartOfSpeech,
                    notes = NewEntryNotes
                };

                var entry = await _backendClient.SendRequestAsync<object, LexiconEntry>(
                    $"/api/lexicon/lexicons/{Uri.EscapeDataString(SelectedLexicon.LexiconId)}/entries",
                    request,
                    System.Net.Http.HttpMethod.Post,
                    cancellationToken
                );

                if (entry != null)
                {
                    var entryItem = new LexiconEntryItem(entry);
                    Entries.Add(entryItem);
                    NewEntryWord = string.Empty;
                    NewEntryPronunciation = string.Empty;
                    NewEntryPartOfSpeech = null;
                    NewEntryNotes = null;

                    // Register undo action
                    if (_undoRedoService != null && SelectedLexicon != null)
                    {
                        var action = new CreateLexiconEntryAction(
                            Entries,
                            _backendClient,
                            SelectedLexicon.LexiconId,
                            entryItem,
                            onUndo: (e) =>
                            {
                                if (SelectedEntry?.Word == e.Word)
                                {
                                    SelectedEntry = Entries.FirstOrDefault();
                                }
                            },
                            onRedo: (e) =>
                            {
                                SelectedEntry = e;
                            });
                        _undoRedoService.RegisterAction(action);
                    }

                    StatusMessage = ResourceHelper.GetString("Lexicon.EntryCreated", "Entry created");
                }
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("Lexicon.CreateEntryFailed", ex.Message);
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task UpdateEntryAsync(CancellationToken cancellationToken)
        {
            if (SelectedEntry == null || SelectedLexicon == null)
            {
                ErrorMessage = ResourceHelper.GetString("Lexicon.NoEntrySelected", "No entry selected");
                return;
            }

            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var request = new
                {
                    word = SelectedEntry.Word,
                    pronunciation = SelectedEntry.Pronunciation,
                    part_of_speech = SelectedEntry.PartOfSpeech,
                    notes = SelectedEntry.Notes
                };

                var entry = await _backendClient.SendRequestAsync<object, LexiconEntry>(
                    $"/api/lexicon/lexicons/{Uri.EscapeDataString(SelectedLexicon.LexiconId)}/entries/{Uri.EscapeDataString(SelectedEntry.Word)}",
                    request,
                    System.Net.Http.HttpMethod.Put,
                    cancellationToken
                );

                if (entry != null)
                {
                    var index = Entries.IndexOf(SelectedEntry);
                    var updatedItem = new LexiconEntryItem(entry);
                    Entries[index] = updatedItem;
                    SelectedEntry = updatedItem;
                    StatusMessage = ResourceHelper.GetString("Lexicon.EntryUpdated", "Entry updated");
                }
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                await HandleErrorAsync(ex, "UpdateEntry");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task DeleteEntryAsync(CancellationToken cancellationToken = default)
        {
            if (SelectedEntry == null || SelectedLexicon == null)
            {
                ErrorMessage = ResourceHelper.GetString("Lexicon.NoEntrySelected", "No entry selected");
                return;
            }

            try
            {
                IsLoading = true;
                ErrorMessage = null;

                await _backendClient.SendRequestAsync<object, object>(
                    $"/api/lexicon/lexicons/{Uri.EscapeDataString(SelectedLexicon.LexiconId)}/entries/{Uri.EscapeDataString(SelectedEntry.Word)}",
                    null,
                    System.Net.Http.HttpMethod.Delete,
                    cancellationToken
                );

                var entryToDelete = SelectedEntry;
                var originalIndex = Entries.IndexOf(entryToDelete);
                Entries.Remove(entryToDelete);
                SelectedEntry = null;

                // Register undo action
                if (_undoRedoService != null && entryToDelete != null && SelectedLexicon != null)
                {
                    var action = new DeleteLexiconEntryAction(
                        Entries,
                        _backendClient,
                        SelectedLexicon.LexiconId,
                        entryToDelete,
                        originalIndex,
                        onUndo: (e) =>
                        {
                            SelectedEntry = e;
                        },
                        onRedo: (e) =>
                        {
                            if (SelectedEntry?.Word == e.Word)
                            {
                                SelectedEntry = null;
                            }
                        });
                    _undoRedoService.RegisterAction(action);
                }

                StatusMessage = ResourceHelper.GetString("Lexicon.EntryDeleted", "Entry deleted");
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("Lexicon.DeleteEntryFailed", ex.Message);
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task SearchEntriesAsync(CancellationToken cancellationToken)
        {
            if (string.IsNullOrWhiteSpace(SearchQuery))
            {
                ErrorMessage = ResourceHelper.GetString("Lexicon.SearchQueryRequired", "Search query is required");
                return;
            }

            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var request = new
                {
                    query = SearchQuery
                };

                var response = await _backendClient.SendRequestAsync<object, LexiconSearchResponse>(
                    "/api/lexicon/search",
                    request,
                    System.Net.Http.HttpMethod.Post,
                    cancellationToken
                );

                if (response != null)
                {
                    SearchResults.Clear();
                    foreach (var result in response.Results)
                    {
                        SearchResults.Add(new LexiconSearchResultItem(result));
                    }
                    StatusMessage = ResourceHelper.FormatString("Lexicon.SearchResultsFound", SearchResults.Count);
                }
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                await HandleErrorAsync(ex, "SearchEntries");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task RefreshAsync(CancellationToken cancellationToken)
        {
            await LoadLexiconsAsync(cancellationToken);
            if (SelectedLexicon != null)
            {
                await LoadEntriesAsync(cancellationToken);
            }
            StatusMessage = ResourceHelper.GetString("Lexicon.Refreshed", "Refreshed");
        }

        // Response models
        public class Lexicon
        {
            public string LexiconId { get; set; } = string.Empty;
            public string Name { get; set; } = string.Empty;
            public string Language { get; set; } = "en";
            public string? Description { get; set; }
            public int EntryCount { get; set; }
            public string Created { get; set; } = string.Empty;
            public string Modified { get; set; } = string.Empty;
        }

        public class LexiconEntry
        {
            public string Word { get; set; } = string.Empty;
            public string Pronunciation { get; set; } = string.Empty;
            public string? PartOfSpeech { get; set; }
            public string Language { get; set; } = "en";
            public string? Notes { get; set; }
        }

        public class LexiconSearchResponse
        {
            public LexiconSearchResult[] Results { get; set; } = Array.Empty<LexiconSearchResult>();
            public int Count { get; set; }
        }

        public class LexiconSearchResult
        {
            public string LexiconId { get; set; } = string.Empty;
            public string LexiconName { get; set; } = string.Empty;
            public LexiconEntry Entry { get; set; } = new();
        }
    }

    // Data models
    public class LexiconItem : ObservableObject
    {
        public string LexiconId { get; set; }
        public string Name { get; set; }
        public string Language { get; set; }
        public string? Description { get; set; }
        public int EntryCount { get; set; }
        public string Created { get; set; }
        public string Modified { get; set; }
        public string EntryCountDisplay => ResourceHelper.FormatString("Lexicon.EntryCountDisplay", EntryCount);

        public LexiconItem(LexiconModel lexicon)
        {
            LexiconId = lexicon.LexiconId;
            Name = lexicon.Name;
            Language = lexicon.Language;
            Description = lexicon.Description;
            EntryCount = lexicon.EntryCount;
            Created = lexicon.Created;
            Modified = lexicon.Modified;
        }
    }

    public class LexiconEntryItem : ObservableObject
    {
        public string Word { get; set; }
        public string Pronunciation { get; set; }
        public string? PartOfSpeech { get; set; }
        public string Language { get; set; }
        public string? Notes { get; set; }
        public string PartOfSpeechDisplay => PartOfSpeech ?? "N/A";

        public LexiconEntryItem(LexiconEntryModel entry)
        {
            Word = entry.Word;
            Pronunciation = entry.Pronunciation;
            PartOfSpeech = entry.PartOfSpeech;
            Language = entry.Language;
            Notes = entry.Notes;
        }
    }

    public class LexiconSearchResultItem : ObservableObject
    {
        public string LexiconId { get; set; }
        public string LexiconName { get; set; }
        public LexiconEntryItem Entry { get; set; }

        public LexiconSearchResultItem(LexiconSearchResultModel result)
        {
            LexiconId = result.LexiconId;
            LexiconName = result.LexiconName;
            Entry = new LexiconEntryItem(result.Entry);
        }
    }
}


