using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.App.UseCases
{
  /// <summary>
  /// Use case for audio library operations including folders, files, and search.
  /// Encapsulates business logic previously scattered in LibraryViewModel.
  /// </summary>
  public interface ILibraryUseCase
  {
    /// <summary>
    /// List all root-level library folders.
    /// </summary>
    Task<IReadOnlyList<LibraryFolder>> ListFoldersAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Get contents of a specific folder.
    /// </summary>
    Task<LibraryFolderContents> GetFolderContentsAsync(string folderId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Create a new folder in the library.
    /// </summary>
    Task<LibraryFolder> CreateFolderAsync(string name, string? parentId = null, CancellationToken cancellationToken = default);

    /// <summary>
    /// Rename an existing folder.
    /// </summary>
    Task<LibraryFolder> RenameFolderAsync(string folderId, string newName, CancellationToken cancellationToken = default);

    /// <summary>
    /// Delete a folder and optionally its contents.
    /// </summary>
    Task<bool> DeleteFolderAsync(string folderId, bool deleteContents = false, CancellationToken cancellationToken = default);

    /// <summary>
    /// Import audio files into the library.
    /// </summary>
    Task<IReadOnlyList<LibraryItem>> ImportFilesAsync(IEnumerable<string> filePaths, string? targetFolderId = null, CancellationToken cancellationToken = default);

    /// <summary>
    /// Search the library for items matching the query.
    /// </summary>
    Task<IReadOnlyList<LibraryItem>> SearchAsync(string query, LibrarySearchOptions? options = null, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get metadata for a library item.
    /// </summary>
    Task<LibraryItemMetadata> GetItemMetadataAsync(string itemId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Update metadata for a library item.
    /// </summary>
    Task<LibraryItem> UpdateItemMetadataAsync(string itemId, LibraryItemMetadata metadata, CancellationToken cancellationToken = default);

    /// <summary>
    /// Delete library items.
    /// </summary>
    Task<int> DeleteItemsAsync(IEnumerable<string> itemIds, CancellationToken cancellationToken = default);

    /// <summary>
    /// Move items to a different folder.
    /// </summary>
    Task<int> MoveItemsAsync(IEnumerable<string> itemIds, string targetFolderId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Export library items to a specified path.
    /// </summary>
    Task<string> ExportItemsAsync(IEnumerable<string> itemIds, string exportPath, CancellationToken cancellationToken = default);
  }

  /// <summary>
  /// Options for library search.
  /// </summary>
  public class LibrarySearchOptions
  {
    public string? FolderId { get; set; }
    public string? FileType { get; set; }
    public DateTime? CreatedAfter { get; set; }
    public DateTime? CreatedBefore { get; set; }
    public int? MaxResults { get; set; }
    public string? SortBy { get; set; }
    public bool Descending { get; set; }
  }

  /// <summary>
  /// Contents of a library folder.
  /// </summary>
  public class LibraryFolderContents
  {
    public LibraryFolder Folder { get; set; } = default!;
    public IReadOnlyList<LibraryFolder> Subfolders { get; set; } = new List<LibraryFolder>();
    public IReadOnlyList<LibraryItem> Items { get; set; } = new List<LibraryItem>();
  }

  /// <summary>
  /// Metadata for a library item.
  /// </summary>
  public class LibraryItemMetadata
  {
    public string? Title { get; set; }
    public string? Description { get; set; }
    public List<string>? Tags { get; set; }
    public string? Language { get; set; }
    public string? Speaker { get; set; }
    public double? DurationSeconds { get; set; }
    public int? SampleRate { get; set; }
    public Dictionary<string, object>? CustomProperties { get; set; }
  }

  /// <summary>
  /// Represents a folder in the library.
  /// </summary>
  public class LibraryFolder
  {
    public string Id { get; set; } = "";
    public string Name { get; set; } = "";
    public string? ParentId { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime ModifiedAt { get; set; }
    public int ItemCount { get; set; }
  }

  /// <summary>
  /// Represents an item in the library.
  /// </summary>
  public class LibraryItem
  {
    public string Id { get; set; } = "";
    public string Name { get; set; } = "";
    public string Path { get; set; } = "";
    public string FolderId { get; set; } = "";
    public string FileType { get; set; } = "";
    public long FileSizeBytes { get; set; }
    public double DurationSeconds { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime ModifiedAt { get; set; }
    public List<string>? Tags { get; set; }
  }
}
