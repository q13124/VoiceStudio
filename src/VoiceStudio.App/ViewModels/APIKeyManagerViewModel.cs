using System;
using System.Collections.Specialized;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.UI.Xaml;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Utilities;

namespace VoiceStudio.App.ViewModels
{
    /// <summary>
    /// ViewModel for the APIKeyManagerView panel - API key management.
    /// </summary>
    public partial class APIKeyManagerViewModel : BaseViewModel, IPanelView
    {
        private readonly IBackendClient _backendClient;
        private ObservableCollection<APIKeyItem>? _apiKeysHooked;

        public string PanelId => "api-key-manager";
        public string DisplayName => ResourceHelper.GetString("Panel.APIKeyManager.DisplayName", "API Key Manager");
        public PanelRegion Region => PanelRegion.Center;

        [ObservableProperty]
        private ObservableCollection<APIKeyItem> apiKeys = new();

        [ObservableProperty]
        private APIKeyItem? selectedKey;

        [ObservableProperty]
        private ObservableCollection<string> supportedServices = new();

        [ObservableProperty]
        private string? newServiceName;

        [ObservableProperty]
        private string? newKeyValue;

        [ObservableProperty]
        private string? newDescription;

        [ObservableProperty]
        private bool isCreatingKey;

        [ObservableProperty]
        private bool showKeyValue;

        public Visibility ErrorMessageVisibility =>
            string.IsNullOrWhiteSpace(ErrorMessage) ? Visibility.Collapsed : Visibility.Visible;

        public Visibility EmptyStateVisibility =>
            ApiKeys.Count == 0 ? Visibility.Visible : Visibility.Collapsed;

        public Visibility SelectedKeyVisibility =>
            SelectedKey != null ? Visibility.Visible : Visibility.Collapsed;

        public APIKeyManagerViewModel(IViewModelContext context, IBackendClient backendClient)
            : base(context)
        {
            _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));

            LoadKeysCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("LoadKeys");
                await LoadKeysAsync(ct);
            });
            CreateKeyCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("CreateKey");
                await CreateKeyAsync(ct);
            }, () => !IsCreatingKey && !string.IsNullOrWhiteSpace(NewServiceName) && !string.IsNullOrWhiteSpace(NewKeyValue));
            UpdateKeyCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("UpdateKey");
                await UpdateKeyAsync(ct);
            }, () => SelectedKey != null);
            DeleteKeyCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("DeleteKey");
                await DeleteKeyAsync(ct);
            }, () => SelectedKey != null);
            ValidateKeyCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("ValidateKey");
                await ValidateKeyAsync(ct);
            }, () => SelectedKey != null);
            RefreshCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("Refresh");
                await RefreshAsync(ct);
            });
            LoadServicesCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("LoadServices");
                await LoadServicesAsync(ct);
            });

            // Load initial data
            _ = LoadKeysAsync(CancellationToken.None);
            _ = LoadServicesAsync(CancellationToken.None);

            HookApiKeysCollection(ApiKeys);

            PropertyChanged += (_, e) =>
            {
                if (string.Equals(e.PropertyName, nameof(ErrorMessage), StringComparison.Ordinal))
                {
                    OnPropertyChanged(nameof(ErrorMessageVisibility));
                }
            };
        }

        public IAsyncRelayCommand LoadKeysCommand { get; }
        public IAsyncRelayCommand CreateKeyCommand { get; }
        public IAsyncRelayCommand UpdateKeyCommand { get; }
        public IAsyncRelayCommand DeleteKeyCommand { get; }
        public IAsyncRelayCommand ValidateKeyCommand { get; }
        public IAsyncRelayCommand RefreshCommand { get; }
        public IAsyncRelayCommand LoadServicesCommand { get; }

        partial void OnIsCreatingKeyChanged(bool value)
        {
            CreateKeyCommand.NotifyCanExecuteChanged();
        }

        partial void OnNewServiceNameChanged(string? value)
        {
            CreateKeyCommand.NotifyCanExecuteChanged();
        }

        partial void OnNewKeyValueChanged(string? value)
        {
            CreateKeyCommand.NotifyCanExecuteChanged();
        }

        partial void OnSelectedKeyChanged(APIKeyItem? value)
        {
            UpdateKeyCommand.NotifyCanExecuteChanged();
            DeleteKeyCommand.NotifyCanExecuteChanged();
            ValidateKeyCommand.NotifyCanExecuteChanged();
            OnPropertyChanged(nameof(SelectedKeyVisibility));
        }

        partial void OnApiKeysChanged(ObservableCollection<APIKeyItem> value)
        {
            HookApiKeysCollection(value);
            OnPropertyChanged(nameof(EmptyStateVisibility));
        }

        private void HookApiKeysCollection(ObservableCollection<APIKeyItem> collection)
        {
            if (ReferenceEquals(_apiKeysHooked, collection))
            {
                return;
            }

            if (_apiKeysHooked != null)
            {
                _apiKeysHooked.CollectionChanged -= ApiKeys_CollectionChanged;
            }

            _apiKeysHooked = collection;
            _apiKeysHooked.CollectionChanged += ApiKeys_CollectionChanged;
        }

        private void ApiKeys_CollectionChanged(object? sender, NotifyCollectionChangedEventArgs e)
        {
            OnPropertyChanged(nameof(EmptyStateVisibility));
        }

        private async Task LoadKeysAsync(CancellationToken cancellationToken)
        {
            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var keys = await _backendClient.SendRequestAsync<object, APIKeyResponse[]>(
                    "/api/api-keys",
                    null,
                    System.Net.Http.HttpMethod.Get,
                    cancellationToken
                );

                if (keys != null)
                {
                    ApiKeys.Clear();
                    foreach (var key in keys)
                    {
                        ApiKeys.Add(new APIKeyItem(
                            key.KeyId,
                            key.ServiceName,
                            key.KeyValueMasked,
                            key.Description,
                            key.CreatedAt,
                            key.LastUsed,
                            key.IsActive,
                            key.UsageCount
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
                ErrorMessage = $"Failed to load API keys: {ex.Message}";
                await HandleErrorAsync(ex, "LoadKeys");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task CreateKeyAsync(CancellationToken cancellationToken)
        {
            if (string.IsNullOrWhiteSpace(NewServiceName) || string.IsNullOrWhiteSpace(NewKeyValue))
            {
                ErrorMessage = ResourceHelper.GetString("APIKeyManager.ServiceNameAndKeyRequired", "Service name and key value are required");
                return;
            }

            IsCreatingKey = true;
            ErrorMessage = null;

            try
            {
                var request = new APIKeyCreateRequest
                {
                    ServiceName = NewServiceName,
                    KeyValue = NewKeyValue,
                    Description = NewDescription
                };

                var key = await _backendClient.SendRequestAsync<APIKeyCreateRequest, APIKeyResponse>(
                    "/api/api-keys",
                    request,
                    System.Net.Http.HttpMethod.Post,
                    cancellationToken
                );

                if (key != null)
                {
                    ApiKeys.Add(new APIKeyItem(
                        key.KeyId,
                        key.ServiceName,
                        key.KeyValueMasked,
                        key.Description,
                        key.CreatedAt,
                        key.LastUsed,
                        key.IsActive,
                        key.UsageCount
                    ));
                    ApiKeys = new ObservableCollection<APIKeyItem>(ApiKeys.OrderBy(k => k.ServiceName));

                    // Clear form
                    NewServiceName = null;
                    NewKeyValue = null;
                    NewDescription = null;

                    StatusMessage = $"API key for {key.ServiceName} created successfully";
                }
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("APIKeyManager.CreateKeyFailed", ex.Message);
                await HandleErrorAsync(ex, "CreateKey");
            }
            finally
            {
                IsCreatingKey = false;
            }
        }

        private async Task UpdateKeyAsync(CancellationToken cancellationToken)
        {
            if (SelectedKey == null)
            {
                return;
            }

            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var request = new APIKeyUpdateRequest
                {
                    Description = SelectedKey.Description,
                    IsActive = SelectedKey.IsActive
                };

                var key = await _backendClient.SendRequestAsync<APIKeyUpdateRequest, APIKeyResponse>(
                    $"/api/api-keys/{Uri.EscapeDataString(SelectedKey.KeyId)}",
                    request,
                    System.Net.Http.HttpMethod.Put,
                    cancellationToken
                );

                if (key != null)
                {
                    var index = ApiKeys.IndexOf(SelectedKey);
                    if (index >= 0)
                    {
                        ApiKeys[index] = new APIKeyItem(
                            key.KeyId,
                            key.ServiceName,
                            key.KeyValueMasked,
                            key.Description,
                            key.CreatedAt,
                            key.LastUsed,
                            key.IsActive,
                            key.UsageCount
                        );
                    }

                    StatusMessage = ResourceHelper.GetString("APIKeyManager.KeyUpdatedSuccess", "API key updated successfully");
                }
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                ErrorMessage = $"Failed to update API key: {ex.Message}";
                await HandleErrorAsync(ex, "UpdateKey");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task DeleteKeyAsync(CancellationToken cancellationToken)
        {
            if (SelectedKey == null)
            {
                return;
            }

            IsLoading = true;
            ErrorMessage = null;

            try
            {
                await _backendClient.SendRequestAsync<object, object>(
                    $"/api/api-keys/{Uri.EscapeDataString(SelectedKey.KeyId)}",
                    null,
                    System.Net.Http.HttpMethod.Delete,
                    cancellationToken
                );

                ApiKeys.Remove(SelectedKey);
                SelectedKey = null;

                StatusMessage = ResourceHelper.GetString("APIKeyManager.KeyDeletedSuccess", "API key deleted successfully");
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("APIKeyManager.DeleteKeyFailed", ex.Message);
                await HandleErrorAsync(ex, "DeleteKey");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task ValidateKeyAsync(CancellationToken cancellationToken)
        {
            if (SelectedKey == null)
            {
                return;
            }

            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var result = await _backendClient.SendRequestAsync<object, APIKeyValidationResult>(
                    $"/api/api-keys/{Uri.EscapeDataString(SelectedKey.KeyId)}/validate",
                    null,
                    System.Net.Http.HttpMethod.Post,
                    cancellationToken
                );

                if (result != null)
                {
                    if (result.Valid)
                    {
                        StatusMessage = result.Message ?? "API key is valid";
                        // Refresh to update last_used
                        await LoadKeysAsync(cancellationToken);
                    }
                    else
                    {
                        ErrorMessage = result.Message ?? ResourceHelper.GetString("APIKeyManager.ValidationFailed", "API key validation failed");
                    }
                }
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                ErrorMessage = $"Failed to validate API key: {ex.Message}";
                await HandleErrorAsync(ex, "ValidateKey");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task RefreshAsync(CancellationToken cancellationToken)
        {
            await LoadKeysAsync(cancellationToken);
            await LoadServicesAsync(cancellationToken);
            StatusMessage = ResourceHelper.GetString("APIKeyManager.Refreshed", "Refreshed");
        }

        private async Task LoadServicesAsync(CancellationToken cancellationToken)
        {
            try
            {
                var services = await _backendClient.SendRequestAsync<object, string[]>(
                    "/api/api-keys/services/list",
                    null,
                    System.Net.Http.HttpMethod.Get,
                    cancellationToken
                );

                if (services != null)
                {
                    SupportedServices.Clear();
                    foreach (var service in services)
                    {
                        SupportedServices.Add(service);
                    }
                }
            }
            catch (Exception ex)
            {
                ErrorMessage = $"Failed to load supported services: {ex.Message}";
            }
        }

        // Request models
        private class APIKeyCreateRequest
        {
            public string ServiceName { get; set; } = string.Empty;
            public string KeyValue { get; set; } = string.Empty;
            public string? Description { get; set; }
        }

        private class APIKeyUpdateRequest
        {
            public string? KeyValue { get; set; }
            public string? Description { get; set; }
            public bool? IsActive { get; set; }
        }

        private class APIKeyResponse
        {
            public string KeyId { get; set; } = string.Empty;
            public string ServiceName { get; set; } = string.Empty;
            public string KeyValueMasked { get; set; } = string.Empty;
            public string? Description { get; set; }
            public string CreatedAt { get; set; } = string.Empty;
            public string? LastUsed { get; set; }
            public bool IsActive { get; set; }
            public int UsageCount { get; set; }
        }

        private class APIKeyValidationResult
        {
            public bool Valid { get; set; }
            public string? Message { get; set; }
            public string? LastUsed { get; set; }
        }
    }

    // Data model
    public class APIKeyItem : ObservableObject
    {
        public string KeyId { get; set; }
        public string ServiceName { get; set; }
        public string KeyValueMasked { get; set; }
        public string? Description { get; set; }
        public string CreatedAt { get; set; }
        public string? LastUsed { get; set; }
        public bool IsActive { get; set; }
        public int UsageCount { get; set; }

        public string StatusDisplay => IsActive ? ResourceHelper.GetString("APIKeyManager.StatusActive", "Active") : ResourceHelper.GetString("APIKeyManager.StatusInactive", "Inactive");
        public string CreatedAtDisplay => FormatDateTime(CreatedAt);
        public string LastUsedDisplay => LastUsed != null ? FormatDateTime(LastUsed) : ResourceHelper.GetString("APIKeyManager.Never", "Never");
        public Visibility DescriptionVisibility => string.IsNullOrWhiteSpace(Description) ? Visibility.Collapsed : Visibility.Visible;

        public APIKeyItem(string keyId, string serviceName, string keyValueMasked, string? description, string createdAt, string? lastUsed, bool isActive, int usageCount)
        {
            KeyId = keyId;
            ServiceName = serviceName;
            KeyValueMasked = keyValueMasked;
            Description = description;
            CreatedAt = createdAt;
            LastUsed = lastUsed;
            IsActive = isActive;
            UsageCount = usageCount;
        }

        private static string FormatDateTime(string isoString)
        {
            if (DateTime.TryParse(isoString, out var dateTime))
            {
                return dateTime.ToString("yyyy-MM-dd HH:mm");
            }
            return isoString;
        }
    }
}

