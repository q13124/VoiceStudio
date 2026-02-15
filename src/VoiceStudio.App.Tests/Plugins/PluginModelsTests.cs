using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Collections.Generic;
using VoiceStudio.Core.Plugins.Models;

namespace VoiceStudio.App.Tests.Plugins;

[TestClass]
public class PluginInfoTests
{
    #region Default Values Tests

    [TestMethod]
    public void DefaultValues_IdIsEmpty()
    {
        var info = new PluginInfo();
        Assert.AreEqual(string.Empty, info.Id);
    }

    [TestMethod]
    public void DefaultValues_NameIsEmpty()
    {
        var info = new PluginInfo();
        Assert.AreEqual(string.Empty, info.Name);
    }

    [TestMethod]
    public void DefaultValues_DescriptionIsEmpty()
    {
        var info = new PluginInfo();
        Assert.AreEqual(string.Empty, info.Description);
    }

    [TestMethod]
    public void DefaultValues_VersionIsOneZeroZero()
    {
        var info = new PluginInfo();
        Assert.AreEqual("1.0.0", info.Version);
    }

    [TestMethod]
    public void DefaultValues_CategoryIsUncategorized()
    {
        var info = new PluginInfo();
        Assert.AreEqual("Uncategorized", info.Category);
    }

    [TestMethod]
    public void DefaultValues_TagsIsEmptyList()
    {
        var info = new PluginInfo();
        Assert.IsNotNull(info.Tags);
        Assert.AreEqual(0, info.Tags.Count);
    }

    [TestMethod]
    public void DefaultValues_DependenciesIsEmptyList()
    {
        var info = new PluginInfo();
        Assert.IsNotNull(info.Dependencies);
        Assert.AreEqual(0, info.Dependencies.Count);
    }

    [TestMethod]
    public void DefaultValues_ScreenshotsIsEmptyList()
    {
        var info = new PluginInfo();
        Assert.IsNotNull(info.Screenshots);
        Assert.AreEqual(0, info.Screenshots.Count);
    }

    [TestMethod]
    public void DefaultValues_IsInstalledIsFalse()
    {
        var info = new PluginInfo();
        Assert.IsFalse(info.IsInstalled);
    }

    [TestMethod]
    public void DefaultValues_IsVerifiedIsFalse()
    {
        var info = new PluginInfo();
        Assert.IsFalse(info.IsVerified);
    }

    #endregion

    #region HasUpdate Computed Property Tests

    [TestMethod]
    public void HasUpdate_WhenNotInstalled_ReturnsFalse()
    {
        var info = new PluginInfo
        {
            IsInstalled = false,
            Version = "2.0.0",
            InstalledVersion = "1.0.0"
        };

        Assert.IsFalse(info.HasUpdate);
    }

    [TestMethod]
    public void HasUpdate_WhenInstalledAndVersionsDiffer_ReturnsTrue()
    {
        var info = new PluginInfo
        {
            IsInstalled = true,
            Version = "2.0.0",
            InstalledVersion = "1.0.0"
        };

        Assert.IsTrue(info.HasUpdate);
    }

    [TestMethod]
    public void HasUpdate_WhenInstalledAndVersionsMatch_ReturnsFalse()
    {
        var info = new PluginInfo
        {
            IsInstalled = true,
            Version = "1.0.0",
            InstalledVersion = "1.0.0"
        };

        Assert.IsFalse(info.HasUpdate);
    }

    [TestMethod]
    public void HasUpdate_WhenInstalledAndInstalledVersionIsNull_ReturnsTrue()
    {
        var info = new PluginInfo
        {
            IsInstalled = true,
            Version = "1.0.0",
            InstalledVersion = null
        };

        Assert.IsTrue(info.HasUpdate);
    }

    #endregion

    #region Property Tests

    [TestMethod]
    public void AllPropertiesCanBeSet()
    {
        var published = new DateTime(2025, 1, 1);
        var updated = new DateTime(2025, 6, 1);

        var info = new PluginInfo
        {
            Id = "com.example.plugin",
            Name = "Example Plugin",
            Description = "A test plugin",
            LongDescription = "Full description with markdown",
            Version = "2.1.0",
            Author = "Test Author",
            IconUrl = "https://example.com/icon.png",
            Category = "Voice Effects",
            Tags = new List<string> { "effects", "reverb" },
            MinimumAppVersion = "3.0.0",
            License = "MIT",
            HomepageUrl = "https://example.com",
            DownloadUrl = "https://example.com/plugin.zip",
            DownloadSize = 1024 * 1024,
            DownloadCount = 5000,
            Rating = 4.5,
            RatingCount = 100,
            PublishedDate = published,
            LastUpdated = updated,
            IsVerified = true,
            IsInstalled = true,
            InstalledVersion = "2.0.0",
            Screenshots = new List<string> { "screenshot1.png", "screenshot2.png" }
        };

        Assert.AreEqual("com.example.plugin", info.Id);
        Assert.AreEqual("Example Plugin", info.Name);
        Assert.AreEqual("A test plugin", info.Description);
        Assert.AreEqual("Full description with markdown", info.LongDescription);
        Assert.AreEqual("2.1.0", info.Version);
        Assert.AreEqual("Test Author", info.Author);
        Assert.AreEqual("https://example.com/icon.png", info.IconUrl);
        Assert.AreEqual("Voice Effects", info.Category);
        Assert.AreEqual(2, info.Tags.Count);
        Assert.AreEqual("3.0.0", info.MinimumAppVersion);
        Assert.AreEqual("MIT", info.License);
        Assert.AreEqual("https://example.com", info.HomepageUrl);
        Assert.AreEqual("https://example.com/plugin.zip", info.DownloadUrl);
        Assert.AreEqual(1048576L, info.DownloadSize);
        Assert.AreEqual(5000, info.DownloadCount);
        Assert.AreEqual(4.5, info.Rating);
        Assert.AreEqual(100, info.RatingCount);
        Assert.AreEqual(published, info.PublishedDate);
        Assert.AreEqual(updated, info.LastUpdated);
        Assert.IsTrue(info.IsVerified);
        Assert.IsTrue(info.IsInstalled);
        Assert.AreEqual("2.0.0", info.InstalledVersion);
        Assert.AreEqual(2, info.Screenshots.Count);
        Assert.IsTrue(info.HasUpdate);
    }

    #endregion
}

[TestClass]
public class PluginDependencyTests
{
    [TestMethod]
    public void DefaultValues_PluginIdIsEmpty()
    {
        var dep = new PluginDependency();
        Assert.AreEqual(string.Empty, dep.PluginId);
    }

    [TestMethod]
    public void DefaultValues_MinVersionIsNull()
    {
        var dep = new PluginDependency();
        Assert.IsNull(dep.MinVersion);
    }

    [TestMethod]
    public void DefaultValues_IsOptionalIsFalse()
    {
        var dep = new PluginDependency();
        Assert.IsFalse(dep.IsOptional);
    }

    [TestMethod]
    public void AllPropertiesCanBeSet()
    {
        var dep = new PluginDependency
        {
            PluginId = "com.example.core",
            MinVersion = "1.0.0",
            IsOptional = true
        };

        Assert.AreEqual("com.example.core", dep.PluginId);
        Assert.AreEqual("1.0.0", dep.MinVersion);
        Assert.IsTrue(dep.IsOptional);
    }
}

[TestClass]
public class PluginVersionTests
{
    [TestMethod]
    public void DefaultValues_VersionIsEmpty()
    {
        var ver = new PluginVersion();
        Assert.AreEqual(string.Empty, ver.Version);
    }

    [TestMethod]
    public void DefaultValues_ReleaseDateIsDefault()
    {
        var ver = new PluginVersion();
        Assert.AreEqual(default(DateTime), ver.ReleaseDate);
    }

    [TestMethod]
    public void AllPropertiesCanBeSet()
    {
        var releaseDate = new DateTime(2025, 3, 15);

        var ver = new PluginVersion
        {
            Version = "2.0.0",
            ReleaseDate = releaseDate,
            ReleaseNotes = "Major update with new features",
            DownloadUrl = "https://example.com/v2.zip",
            DownloadSize = 2048000
        };

        Assert.AreEqual("2.0.0", ver.Version);
        Assert.AreEqual(releaseDate, ver.ReleaseDate);
        Assert.AreEqual("Major update with new features", ver.ReleaseNotes);
        Assert.AreEqual("https://example.com/v2.zip", ver.DownloadUrl);
        Assert.AreEqual(2048000L, ver.DownloadSize);
    }
}

[TestClass]
public class PluginCategoryTests
{
    [TestMethod]
    public void DefaultValues_IdIsEmpty()
    {
        var cat = new PluginCategory();
        Assert.AreEqual(string.Empty, cat.Id);
    }

    [TestMethod]
    public void DefaultValues_NameIsEmpty()
    {
        var cat = new PluginCategory();
        Assert.AreEqual(string.Empty, cat.Name);
    }

    [TestMethod]
    public void DefaultValues_PluginCountIsZero()
    {
        var cat = new PluginCategory();
        Assert.AreEqual(0, cat.PluginCount);
    }

    [TestMethod]
    public void AllPropertiesCanBeSet()
    {
        var cat = new PluginCategory
        {
            Id = "voice-effects",
            Name = "Voice Effects",
            Description = "Plugins for voice processing",
            IconGlyph = "\uE8D6",
            PluginCount = 15
        };

        Assert.AreEqual("voice-effects", cat.Id);
        Assert.AreEqual("Voice Effects", cat.Name);
        Assert.AreEqual("Plugins for voice processing", cat.Description);
        Assert.AreEqual("\uE8D6", cat.IconGlyph);
        Assert.AreEqual(15, cat.PluginCount);
    }
}

[TestClass]
public class PluginInstallResultTests
{
    [TestMethod]
    public void DefaultValues_SuccessIsFalse()
    {
        var result = new PluginInstallResult();
        Assert.IsFalse(result.Success);
    }

    [TestMethod]
    public void DefaultValues_PluginIsNull()
    {
        var result = new PluginInstallResult();
        Assert.IsNull(result.Plugin);
    }

    [TestMethod]
    public void DefaultValues_RequiresRestartIsFalse()
    {
        var result = new PluginInstallResult();
        Assert.IsFalse(result.RequiresRestart);
    }

    [TestMethod]
    public void DefaultValues_InstalledDependenciesIsEmptyList()
    {
        var result = new PluginInstallResult();
        Assert.IsNotNull(result.InstalledDependencies);
        Assert.AreEqual(0, result.InstalledDependencies.Count);
    }

    [TestMethod]
    public void SuccessfulInstall_AllPropertiesSet()
    {
        var plugin = new PluginInfo { Id = "test", Name = "Test Plugin" };

        var result = new PluginInstallResult
        {
            Success = true,
            Plugin = plugin,
            RequiresRestart = true,
            InstalledDependencies = new List<string> { "dep1", "dep2" }
        };

        Assert.IsTrue(result.Success);
        Assert.IsNotNull(result.Plugin);
        Assert.AreEqual("Test Plugin", result.Plugin.Name);
        Assert.IsTrue(result.RequiresRestart);
        Assert.AreEqual(2, result.InstalledDependencies.Count);
    }

    [TestMethod]
    public void FailedInstall_HasErrorMessage()
    {
        var result = new PluginInstallResult
        {
            Success = false,
            ErrorMessage = "Download failed: network timeout"
        };

        Assert.IsFalse(result.Success);
        Assert.AreEqual("Download failed: network timeout", result.ErrorMessage);
    }
}

[TestClass]
public class PluginInstallProgressTests
{
    [TestMethod]
    public void DefaultValues_PhaseIsPreparing()
    {
        var progress = new PluginInstallProgress();
        Assert.AreEqual(InstallPhase.Preparing, progress.Phase);
    }

    [TestMethod]
    public void DefaultValues_ProgressPercentIsZero()
    {
        var progress = new PluginInstallProgress();
        Assert.AreEqual(0, progress.ProgressPercent);
    }

    [TestMethod]
    public void DefaultValues_StatusMessageIsEmpty()
    {
        var progress = new PluginInstallProgress();
        Assert.AreEqual(string.Empty, progress.StatusMessage);
    }

    [TestMethod]
    public void AllPropertiesCanBeSet()
    {
        var progress = new PluginInstallProgress
        {
            Phase = InstallPhase.Downloading,
            ProgressPercent = 45,
            StatusMessage = "Downloading plugin package...",
            BytesDownloaded = 512000,
            TotalBytes = 1024000
        };

        Assert.AreEqual(InstallPhase.Downloading, progress.Phase);
        Assert.AreEqual(45, progress.ProgressPercent);
        Assert.AreEqual("Downloading plugin package...", progress.StatusMessage);
        Assert.AreEqual(512000L, progress.BytesDownloaded);
        Assert.AreEqual(1024000L, progress.TotalBytes);
    }
}

[TestClass]
public class InstallPhaseTests
{
    [TestMethod]
    public void InstallPhase_HasExpectedValues()
    {
        Assert.AreEqual(0, (int)InstallPhase.Preparing);
        Assert.AreEqual(1, (int)InstallPhase.Downloading);
        Assert.AreEqual(2, (int)InstallPhase.Verifying);
        Assert.AreEqual(3, (int)InstallPhase.Extracting);
        Assert.AreEqual(4, (int)InstallPhase.InstallingDependencies);
        Assert.AreEqual(5, (int)InstallPhase.PostInstall);
        Assert.AreEqual(6, (int)InstallPhase.Complete);
        Assert.AreEqual(7, (int)InstallPhase.Failed);
    }

    [TestMethod]
    public void InstallPhase_AllValuesDefined()
    {
        var values = Enum.GetValues<InstallPhase>();
        Assert.AreEqual(8, values.Length);
    }
}

[TestClass]
public class PluginSearchCriteriaTests
{
    [TestMethod]
    public void DefaultValues_SearchTextIsNull()
    {
        var criteria = new PluginSearchCriteria();
        Assert.IsNull(criteria.SearchText);
    }

    [TestMethod]
    public void DefaultValues_SortByIsPopular()
    {
        var criteria = new PluginSearchCriteria();
        Assert.AreEqual(PluginSortOrder.Popular, criteria.SortBy);
    }

    [TestMethod]
    public void DefaultValues_PageIsOne()
    {
        var criteria = new PluginSearchCriteria();
        Assert.AreEqual(1, criteria.Page);
    }

    [TestMethod]
    public void DefaultValues_PageSizeIsTwenty()
    {
        var criteria = new PluginSearchCriteria();
        Assert.AreEqual(20, criteria.PageSize);
    }

    [TestMethod]
    public void DefaultValues_InstalledOnlyIsFalse()
    {
        var criteria = new PluginSearchCriteria();
        Assert.IsFalse(criteria.InstalledOnly);
    }

    [TestMethod]
    public void DefaultValues_UpdatesOnlyIsFalse()
    {
        var criteria = new PluginSearchCriteria();
        Assert.IsFalse(criteria.UpdatesOnly);
    }

    [TestMethod]
    public void AllPropertiesCanBeSet()
    {
        var criteria = new PluginSearchCriteria
        {
            SearchText = "reverb",
            Category = "Voice Effects",
            Tag = "audio",
            InstalledOnly = true,
            UpdatesOnly = true,
            SortBy = PluginSortOrder.Rating,
            Page = 2,
            PageSize = 50
        };

        Assert.AreEqual("reverb", criteria.SearchText);
        Assert.AreEqual("Voice Effects", criteria.Category);
        Assert.AreEqual("audio", criteria.Tag);
        Assert.IsTrue(criteria.InstalledOnly);
        Assert.IsTrue(criteria.UpdatesOnly);
        Assert.AreEqual(PluginSortOrder.Rating, criteria.SortBy);
        Assert.AreEqual(2, criteria.Page);
        Assert.AreEqual(50, criteria.PageSize);
    }
}

[TestClass]
public class PluginSortOrderTests
{
    [TestMethod]
    public void PluginSortOrder_HasExpectedValues()
    {
        Assert.AreEqual(0, (int)PluginSortOrder.Popular);
        Assert.AreEqual(1, (int)PluginSortOrder.Rating);
        Assert.AreEqual(2, (int)PluginSortOrder.RecentlyUpdated);
        Assert.AreEqual(3, (int)PluginSortOrder.Name);
        Assert.AreEqual(4, (int)PluginSortOrder.Newest);
    }

    [TestMethod]
    public void PluginSortOrder_AllValuesDefined()
    {
        var values = Enum.GetValues<PluginSortOrder>();
        Assert.AreEqual(5, values.Length);
    }
}

[TestClass]
public class PluginSearchResultTests
{
    [TestMethod]
    public void DefaultValues_PluginsIsEmptyList()
    {
        var result = new PluginSearchResult();
        Assert.IsNotNull(result.Plugins);
        Assert.AreEqual(0, result.Plugins.Count);
    }

    [TestMethod]
    public void DefaultValues_TotalCountIsZero()
    {
        var result = new PluginSearchResult();
        Assert.AreEqual(0, result.TotalCount);
    }

    [TestMethod]
    public void DefaultValues_ServiceUnavailableIsFalse()
    {
        var result = new PluginSearchResult();
        Assert.IsFalse(result.ServiceUnavailable);
    }

    #region TotalPages Computed Property Tests

    [TestMethod]
    public void TotalPages_ZeroResults_ReturnsZero()
    {
        var result = new PluginSearchResult
        {
            TotalCount = 0,
            PageSize = 20
        };

        Assert.AreEqual(0, result.TotalPages);
    }

    [TestMethod]
    public void TotalPages_ExactMultiple_ReturnsCorrectPages()
    {
        var result = new PluginSearchResult
        {
            TotalCount = 60,
            PageSize = 20
        };

        Assert.AreEqual(3, result.TotalPages);
    }

    [TestMethod]
    public void TotalPages_PartialPage_RoundsUp()
    {
        var result = new PluginSearchResult
        {
            TotalCount = 61,
            PageSize = 20
        };

        Assert.AreEqual(4, result.TotalPages);
    }

    [TestMethod]
    public void TotalPages_LessThanPageSize_ReturnsOne()
    {
        var result = new PluginSearchResult
        {
            TotalCount = 5,
            PageSize = 20
        };

        Assert.AreEqual(1, result.TotalPages);
    }

    #endregion

    #region HasMore Computed Property Tests

    [TestMethod]
    public void HasMore_OnLastPage_ReturnsFalse()
    {
        var result = new PluginSearchResult
        {
            TotalCount = 40,
            PageSize = 20,
            Page = 2
        };

        Assert.IsFalse(result.HasMore);
    }

    [TestMethod]
    public void HasMore_NotOnLastPage_ReturnsTrue()
    {
        var result = new PluginSearchResult
        {
            TotalCount = 100,
            PageSize = 20,
            Page = 2
        };

        Assert.IsTrue(result.HasMore);
    }

    [TestMethod]
    public void HasMore_OnFirstOfMany_ReturnsTrue()
    {
        var result = new PluginSearchResult
        {
            TotalCount = 100,
            PageSize = 20,
            Page = 1
        };

        Assert.IsTrue(result.HasMore);
    }

    [TestMethod]
    public void HasMore_SinglePage_ReturnsFalse()
    {
        var result = new PluginSearchResult
        {
            TotalCount = 15,
            PageSize = 20,
            Page = 1
        };

        Assert.IsFalse(result.HasMore);
    }

    #endregion

    #region Full Object Tests

    [TestMethod]
    public void FullResult_AllPropertiesSet()
    {
        var plugins = new List<PluginInfo>
        {
            new PluginInfo { Id = "1", Name = "Plugin 1" },
            new PluginInfo { Id = "2", Name = "Plugin 2" }
        };

        var result = new PluginSearchResult
        {
            Plugins = plugins,
            TotalCount = 45,
            Page = 2,
            PageSize = 20
        };

        Assert.AreEqual(2, result.Plugins.Count);
        Assert.AreEqual(45, result.TotalCount);
        Assert.AreEqual(2, result.Page);
        Assert.AreEqual(20, result.PageSize);
        Assert.AreEqual(3, result.TotalPages);
        Assert.IsTrue(result.HasMore);
    }

    [TestMethod]
    public void ServiceUnavailable_Result()
    {
        var result = new PluginSearchResult
        {
            ServiceUnavailable = true,
            ErrorMessage = "Plugin catalog service is offline"
        };

        Assert.IsTrue(result.ServiceUnavailable);
        Assert.AreEqual("Plugin catalog service is offline", result.ErrorMessage);
        Assert.AreEqual(0, result.Plugins.Count);
    }

    #endregion
}
