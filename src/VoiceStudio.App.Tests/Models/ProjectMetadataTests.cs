using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Collections.Generic;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Tests.Models;

[TestClass]
public class ProjectMetadataTests
{
    #region Default Values Tests

    [TestMethod]
    public void DefaultValues_IdIsEmpty()
    {
        var metadata = new ProjectMetadata();
        Assert.AreEqual(string.Empty, metadata.Id);
    }

    [TestMethod]
    public void DefaultValues_NameIsEmpty()
    {
        var metadata = new ProjectMetadata();
        Assert.AreEqual(string.Empty, metadata.Name);
    }

    [TestMethod]
    public void DefaultValues_DescriptionIsNull()
    {
        var metadata = new ProjectMetadata();
        Assert.IsNull(metadata.Description);
    }

    [TestMethod]
    public void DefaultValues_ThumbnailPathIsNull()
    {
        var metadata = new ProjectMetadata();
        Assert.IsNull(metadata.ThumbnailPath);
    }

    [TestMethod]
    public void DefaultValues_SizeBytesIsZero()
    {
        var metadata = new ProjectMetadata();
        Assert.AreEqual(0L, metadata.SizeBytes);
    }

    [TestMethod]
    public void DefaultValues_TrackCountIsZero()
    {
        var metadata = new ProjectMetadata();
        Assert.AreEqual(0, metadata.TrackCount);
    }

    [TestMethod]
    public void DefaultValues_ProfileCountIsZero()
    {
        var metadata = new ProjectMetadata();
        Assert.AreEqual(0, metadata.ProfileCount);
    }

    [TestMethod]
    public void DefaultValues_TagsIsNull()
    {
        var metadata = new ProjectMetadata();
        Assert.IsNull(metadata.Tags);
    }

    #endregion

    #region Property Set/Get Tests

    [TestMethod]
    public void Id_CanBeSet()
    {
        var metadata = new ProjectMetadata { Id = "project-123" };
        Assert.AreEqual("project-123", metadata.Id);
    }

    [TestMethod]
    public void Name_CanBeSet()
    {
        var metadata = new ProjectMetadata { Name = "My Project" };
        Assert.AreEqual("My Project", metadata.Name);
    }

    [TestMethod]
    public void Description_CanBeSet()
    {
        var metadata = new ProjectMetadata { Description = "A voice synthesis project" };
        Assert.AreEqual("A voice synthesis project", metadata.Description);
    }

    [TestMethod]
    public void Created_CanBeSet()
    {
        var date = new DateTime(2025, 6, 15, 10, 30, 0);
        var metadata = new ProjectMetadata { Created = date };
        Assert.AreEqual(date, metadata.Created);
    }

    [TestMethod]
    public void Modified_CanBeSet()
    {
        var date = new DateTime(2025, 6, 20, 14, 45, 0);
        var metadata = new ProjectMetadata { Modified = date };
        Assert.AreEqual(date, metadata.Modified);
    }

    [TestMethod]
    public void ThumbnailPath_CanBeSet()
    {
        var metadata = new ProjectMetadata { ThumbnailPath = "thumbnails/project1.png" };
        Assert.AreEqual("thumbnails/project1.png", metadata.ThumbnailPath);
    }

    [TestMethod]
    public void SizeBytes_CanBeSet()
    {
        var metadata = new ProjectMetadata { SizeBytes = 1024 * 1024 * 50 }; // 50 MB
        Assert.AreEqual(52428800L, metadata.SizeBytes);
    }

    [TestMethod]
    public void TrackCount_CanBeSet()
    {
        var metadata = new ProjectMetadata { TrackCount = 12 };
        Assert.AreEqual(12, metadata.TrackCount);
    }

    [TestMethod]
    public void ProfileCount_CanBeSet()
    {
        var metadata = new ProjectMetadata { ProfileCount = 3 };
        Assert.AreEqual(3, metadata.ProfileCount);
    }

    [TestMethod]
    public void Tags_CanBeSet()
    {
        var tags = new List<string> { "audiobook", "fiction", "en-US" };
        var metadata = new ProjectMetadata { Tags = tags };

        Assert.IsNotNull(metadata.Tags);
        Assert.AreEqual(3, metadata.Tags.Count);
        CollectionAssert.Contains(metadata.Tags, "audiobook");
        CollectionAssert.Contains(metadata.Tags, "fiction");
        CollectionAssert.Contains(metadata.Tags, "en-US");
    }

    #endregion

    #region Alias Tests

    [TestMethod]
    public void ProjectId_ReadsFromId()
    {
        var metadata = new ProjectMetadata { Id = "test-id" };
        Assert.AreEqual("test-id", metadata.ProjectId);
    }

    [TestMethod]
    public void ProjectId_WritesToId()
    {
        var metadata = new ProjectMetadata { ProjectId = "alias-id" };
        Assert.AreEqual("alias-id", metadata.Id);
    }

    [TestMethod]
    public void CreatedAt_ReadsFromCreated()
    {
        var date = new DateTime(2025, 1, 1, 12, 0, 0);
        var metadata = new ProjectMetadata { Created = date };
        Assert.AreEqual(date, metadata.CreatedAt);
    }

    [TestMethod]
    public void CreatedAt_WritesToCreated()
    {
        var date = new DateTime(2025, 2, 15, 8, 30, 0);
        var metadata = new ProjectMetadata { CreatedAt = date };
        Assert.AreEqual(date, metadata.Created);
    }

    [TestMethod]
    public void ModifiedAt_ReadsFromModified()
    {
        var date = new DateTime(2025, 3, 20, 16, 45, 0);
        var metadata = new ProjectMetadata { Modified = date };
        Assert.AreEqual(date, metadata.ModifiedAt);
    }

    [TestMethod]
    public void ModifiedAt_WritesToModified()
    {
        var date = new DateTime(2025, 4, 10, 9, 15, 0);
        var metadata = new ProjectMetadata { ModifiedAt = date };
        Assert.AreEqual(date, metadata.Modified);
    }

    #endregion

    #region Full Object Tests

    [TestMethod]
    public void FullInitialization_AllPropertiesSet()
    {
        var created = new DateTime(2025, 1, 15, 10, 0, 0);
        var modified = new DateTime(2025, 6, 20, 14, 30, 0);

        var metadata = new ProjectMetadata
        {
            Id = "proj-guid-123",
            Name = "Voice Novel Project",
            Description = "An audiobook production project",
            Created = created,
            Modified = modified,
            ThumbnailPath = "thumbnails/novel.jpg",
            SizeBytes = 1073741824, // 1 GB
            TrackCount = 24,
            ProfileCount = 5,
            Tags = new List<string> { "audiobook", "novel", "production" }
        };

        Assert.AreEqual("proj-guid-123", metadata.Id);
        Assert.AreEqual("Voice Novel Project", metadata.Name);
        Assert.AreEqual("An audiobook production project", metadata.Description);
        Assert.AreEqual(created, metadata.Created);
        Assert.AreEqual(modified, metadata.Modified);
        Assert.AreEqual("thumbnails/novel.jpg", metadata.ThumbnailPath);
        Assert.AreEqual(1073741824L, metadata.SizeBytes);
        Assert.AreEqual(24, metadata.TrackCount);
        Assert.AreEqual(5, metadata.ProfileCount);
        Assert.AreEqual(3, metadata.Tags?.Count);
    }

    #endregion

    #region Typical Usage Tests

    [TestMethod]
    public void TypicalUsage_NewProject()
    {
        var now = DateTime.UtcNow;
        var metadata = new ProjectMetadata
        {
            Id = Guid.NewGuid().ToString(),
            Name = "New Project",
            Created = now,
            Modified = now,
            TrackCount = 0,
            ProfileCount = 0
        };

        Assert.IsFalse(string.IsNullOrEmpty(metadata.Id));
        Assert.AreEqual("New Project", metadata.Name);
        Assert.AreEqual(metadata.Created, metadata.Modified);
    }

    [TestMethod]
    public void TypicalUsage_ProjectList()
    {
        var projects = new List<ProjectMetadata>
        {
            new ProjectMetadata { Id = "1", Name = "Project A", Modified = DateTime.Now.AddDays(-1) },
            new ProjectMetadata { Id = "2", Name = "Project B", Modified = DateTime.Now.AddHours(-2) },
            new ProjectMetadata { Id = "3", Name = "Project C", Modified = DateTime.Now }
        };

        // Sort by most recently modified
        projects.Sort((a, b) => b.Modified.CompareTo(a.Modified));

        Assert.AreEqual("3", projects[0].Id); // Most recent first
        Assert.AreEqual("2", projects[1].Id);
        Assert.AreEqual("1", projects[2].Id);
    }

    [TestMethod]
    public void TypicalUsage_FilterByTags()
    {
        var projects = new List<ProjectMetadata>
        {
            new ProjectMetadata { Id = "1", Name = "Audiobook", Tags = new List<string> { "audiobook", "fiction" } },
            new ProjectMetadata { Id = "2", Name = "Podcast", Tags = new List<string> { "podcast", "interview" } },
            new ProjectMetadata { Id = "3", Name = "Tutorial", Tags = new List<string> { "tutorial", "audiobook" } }
        };

        var audiobookProjects = projects.FindAll(p => p.Tags?.Contains("audiobook") == true);

        Assert.AreEqual(2, audiobookProjects.Count);
    }

    #endregion
}
