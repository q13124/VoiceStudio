using Microsoft.VisualStudio.TestTools.UnitTesting;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Tests.ViewModels
{
    [TestClass]
    public class TagManagerModelTests
    {
        #region Tag Model Tests

        [TestMethod]
        public void Tag_DefaultValues()
        {
            var tag = new Tag();

            Assert.AreEqual(string.Empty, tag.Id);
            Assert.AreEqual(string.Empty, tag.Name);
            Assert.IsNull(tag.Category);
            Assert.IsNull(tag.Color);
            Assert.IsNull(tag.Description);
            Assert.AreEqual(0, tag.UsageCount);
            Assert.AreEqual(string.Empty, tag.Created);
            Assert.AreEqual(string.Empty, tag.Modified);
        }

        [TestMethod]
        public void Tag_PropertiesSetCorrectly()
        {
            var tag = new Tag
            {
                Id = "tag123",
                Name = "Important",
                Category = "Priority",
                Color = "#FF0000",
                Description = "High priority items",
                UsageCount = 25,
                Created = "2026-01-01",
                Modified = "2026-01-10"
            };

            Assert.AreEqual("tag123", tag.Id);
            Assert.AreEqual("Important", tag.Name);
            Assert.AreEqual("Priority", tag.Category);
            Assert.AreEqual("#FF0000", tag.Color);
            Assert.AreEqual("High priority items", tag.Description);
            Assert.AreEqual(25, tag.UsageCount);
            Assert.AreEqual("2026-01-01", tag.Created);
            Assert.AreEqual("2026-01-10", tag.Modified);
        }

        #endregion

        #region TagItem Model Tests

        [TestMethod]
        public void TagItem_CreatedFromTag()
        {
            var tag = new Tag
            {
                Id = "t1",
                Name = "Urgent",
                Category = "Status",
                Color = "#00FF00",
                Description = "Urgent items",
                UsageCount = 50
            };

            var item = new TagItem(tag);

            Assert.AreEqual("t1", item.Id);
            Assert.AreEqual("Urgent", item.Name);
            Assert.AreEqual("Status", item.Category);
            Assert.AreEqual("#00FF00", item.Color);
            Assert.AreEqual("Urgent items", item.Description);
            Assert.AreEqual(50, item.UsageCount);
        }

        [TestMethod]
        public void TagItem_UpdateFrom_UpdatesAllProperties()
        {
            var original = new Tag
            {
                Id = "t1",
                Name = "Original",
                Category = "Cat1",
                Color = "#000000",
                Description = "Original Description",
                UsageCount = 10
            };
            var item = new TagItem(original);

            var updated = new Tag
            {
                Name = "Updated",
                Category = "Cat2",
                Color = "#FFFFFF",
                Description = "Updated Description",
                UsageCount = 20
            };
            item.UpdateFrom(updated);

            Assert.AreEqual("Updated", item.Name);
            Assert.AreEqual("Cat2", item.Category);
            Assert.AreEqual("#FFFFFF", item.Color);
            Assert.AreEqual("Updated Description", item.Description);
            Assert.AreEqual(20, item.UsageCount);
            // Id should not change
            Assert.AreEqual("t1", item.Id);
        }

        [TestMethod]
        public void TagItem_NullablePropertiesAllowNull()
        {
            var tag = new Tag
            {
                Id = "t1",
                Name = "Name",
                Category = null,
                Color = null,
                Description = null
            };

            var item = new TagItem(tag);

            Assert.IsNull(item.Category);
            Assert.IsNull(item.Color);
            Assert.IsNull(item.Description);
        }

        [TestMethod]
        public void TagItem_UsageCountDefaultsToZero()
        {
            var tag = new Tag { Id = "t1", Name = "Test" };
            var item = new TagItem(tag);

            Assert.AreEqual(0, item.UsageCount);
        }

        #endregion
    }
}
