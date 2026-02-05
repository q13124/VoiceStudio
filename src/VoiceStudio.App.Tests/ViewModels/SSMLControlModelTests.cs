using Microsoft.VisualStudio.TestTools.UnitTesting;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Tests.ViewModels
{
    [TestClass]
    public class SSMLControlModelTests
    {
        #region SSMLDocument Model Tests

        [TestMethod]
        public void SSMLDocument_DefaultValues()
        {
            var doc = new SSMLDocument();

            Assert.AreEqual(string.Empty, doc.Id);
            Assert.AreEqual(string.Empty, doc.Name);
            Assert.AreEqual(string.Empty, doc.Content);
            Assert.IsNull(doc.ProfileId);
            Assert.IsNull(doc.ProjectId);
            Assert.AreEqual(string.Empty, doc.Created);
            Assert.AreEqual(string.Empty, doc.Modified);
        }

        [TestMethod]
        public void SSMLDocument_PropertiesSetCorrectly()
        {
            var doc = new SSMLDocument
            {
                Id = "doc123",
                Name = "My SSML Document",
                Content = "<speak>Hello world</speak>",
                ProfileId = "profile456",
                ProjectId = "project789",
                Created = "2026-01-01",
                Modified = "2026-01-15"
            };

            Assert.AreEqual("doc123", doc.Id);
            Assert.AreEqual("My SSML Document", doc.Name);
            Assert.AreEqual("<speak>Hello world</speak>", doc.Content);
            Assert.AreEqual("profile456", doc.ProfileId);
            Assert.AreEqual("project789", doc.ProjectId);
            Assert.AreEqual("2026-01-01", doc.Created);
            Assert.AreEqual("2026-01-15", doc.Modified);
        }

        [TestMethod]
        public void SSMLDocument_NullablePropertiesAllowNull()
        {
            var doc = new SSMLDocument
            {
                Id = "doc1",
                Name = "Test",
                Content = "<speak/>",
                ProfileId = null,
                ProjectId = null
            };

            Assert.IsNull(doc.ProfileId);
            Assert.IsNull(doc.ProjectId);
        }

        #endregion

        #region SSMLDocumentItem Model Tests

        [TestMethod]
        public void SSMLDocumentItem_CreatedFromSSMLDocument()
        {
            var doc = new SSMLDocument
            {
                Id = "d1",
                Name = "Test Document",
                Content = "<speak>Test content</speak>",
                ProfileId = "p1",
                ProjectId = "proj1",
                Created = "2026-01-01",
                Modified = "2026-01-02"
            };

            var item = new SSMLDocumentItem(doc);

            Assert.AreEqual("d1", item.Id);
            Assert.AreEqual("Test Document", item.Name);
            Assert.AreEqual("<speak>Test content</speak>", item.Content);
            Assert.AreEqual("p1", item.ProfileId);
            Assert.AreEqual("proj1", item.ProjectId);
            Assert.AreEqual("2026-01-01", item.Created);
            Assert.AreEqual("2026-01-02", item.Modified);
        }

        [TestMethod]
        public void SSMLDocumentItem_UpdateFrom_UpdatesProperties()
        {
            var original = new SSMLDocument
            {
                Id = "d1",
                Name = "Original",
                Content = "<speak>Original</speak>",
                ProfileId = "old_profile",
                Modified = "2026-01-01"
            };
            var item = new SSMLDocumentItem(original);

            var updated = new SSMLDocument
            {
                Name = "Updated",
                Content = "<speak>Updated content</speak>",
                ProfileId = "new_profile",
                Modified = "2026-02-01"
            };
            item.UpdateFrom(updated);

            Assert.AreEqual("Updated", item.Name);
            Assert.AreEqual("<speak>Updated content</speak>", item.Content);
            Assert.AreEqual("new_profile", item.ProfileId);
            Assert.AreEqual("2026-02-01", item.Modified);
            // Id should remain unchanged
            Assert.AreEqual("d1", item.Id);
        }

        [TestMethod]
        public void SSMLDocumentItem_NullablePropertiesAllowNull()
        {
            var doc = new SSMLDocument
            {
                Id = "d1",
                Name = "Test",
                Content = "<speak/>",
                ProfileId = null,
                ProjectId = null
            };

            var item = new SSMLDocumentItem(doc);

            Assert.IsNull(item.ProfileId);
            Assert.IsNull(item.ProjectId);
        }

        [TestMethod]
        public void SSMLDocumentItem_UpdateFrom_CanSetProfileToNull()
        {
            var original = new SSMLDocument
            {
                Id = "d1",
                Name = "Test",
                Content = "<speak/>",
                ProfileId = "some_profile"
            };
            var item = new SSMLDocumentItem(original);

            var updated = new SSMLDocument
            {
                Name = "Updated",
                Content = "<speak>New</speak>",
                ProfileId = null
            };
            item.UpdateFrom(updated);

            Assert.IsNull(item.ProfileId);
        }

        #endregion
    }
}
