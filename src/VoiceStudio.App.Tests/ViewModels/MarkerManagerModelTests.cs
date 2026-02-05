using Microsoft.VisualStudio.TestTools.UnitTesting;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Tests.ViewModels
{
    [TestClass]
    public class MarkerManagerModelTests
    {
        #region Marker Model Tests

        [TestMethod]
        public void Marker_DefaultValues()
        {
            var marker = new Marker();

            Assert.AreEqual(string.Empty, marker.Id);
            Assert.AreEqual(string.Empty, marker.Name);
            Assert.AreEqual(0.0, marker.Time);
            Assert.AreEqual("#00FFFF", marker.Color);
            Assert.IsNull(marker.Category);
            Assert.IsNull(marker.Description);
            Assert.AreEqual(string.Empty, marker.ProjectId);
            Assert.AreEqual(string.Empty, marker.Created);
            Assert.AreEqual(string.Empty, marker.Modified);
        }

        [TestMethod]
        public void Marker_PropertiesSetCorrectly()
        {
            var marker = new Marker
            {
                Id = "marker123",
                Name = "Intro Start",
                Time = 5.5,
                Color = "#FF0000",
                Category = "Section",
                Description = "Beginning of intro",
                ProjectId = "project456",
                Created = "2026-01-01",
                Modified = "2026-01-02"
            };

            Assert.AreEqual("marker123", marker.Id);
            Assert.AreEqual("Intro Start", marker.Name);
            Assert.AreEqual(5.5, marker.Time);
            Assert.AreEqual("#FF0000", marker.Color);
            Assert.AreEqual("Section", marker.Category);
            Assert.AreEqual("Beginning of intro", marker.Description);
            Assert.AreEqual("project456", marker.ProjectId);
            Assert.AreEqual("2026-01-01", marker.Created);
            Assert.AreEqual("2026-01-02", marker.Modified);
        }

        #endregion

        #region MarkerItem Model Tests

        [TestMethod]
        public void MarkerItem_CreatedFromMarker()
        {
            var marker = new Marker
            {
                Id = "m1",
                Name = "Chorus",
                Time = 30.25,
                Color = "#00FF00",
                Category = "Music",
                Description = "Chorus section",
                ProjectId = "p1",
                Created = "2026-01-01",
                Modified = "2026-01-02"
            };

            var item = new MarkerItem(marker);

            Assert.AreEqual("m1", item.Id);
            Assert.AreEqual("Chorus", item.Name);
            Assert.AreEqual(30.25, item.Time);
            Assert.AreEqual("#00FF00", item.Color);
            Assert.AreEqual("Music", item.Category);
            Assert.AreEqual("Chorus section", item.Description);
            Assert.AreEqual("p1", item.ProjectId);
            Assert.AreEqual("2026-01-01", item.Created);
            Assert.AreEqual("2026-01-02", item.Modified);
        }

        [TestMethod]
        public void MarkerItem_TimeDisplay_FormatsCorrectly()
        {
            var marker = new Marker { Time = 5.5 };
            var item = new MarkerItem(marker);

            Assert.AreEqual("5.50s", item.TimeDisplay);
        }

        [TestMethod]
        public void MarkerItem_TimeDisplay_ZeroTime()
        {
            var marker = new Marker { Time = 0 };
            var item = new MarkerItem(marker);

            Assert.AreEqual("0.00s", item.TimeDisplay);
        }

        [TestMethod]
        public void MarkerItem_TimeDisplay_LongTime()
        {
            var marker = new Marker { Time = 125.75 };
            var item = new MarkerItem(marker);

            Assert.AreEqual("125.75s", item.TimeDisplay);
        }

        [TestMethod]
        public void MarkerItem_UpdateFrom_UpdatesProperties()
        {
            var original = new Marker
            {
                Id = "m1",
                Name = "Original",
                Time = 10.0,
                Color = "#000000",
                Category = "Old",
                Description = "Old desc"
            };
            var item = new MarkerItem(original);

            var updated = new Marker
            {
                Name = "Updated",
                Time = 20.0,
                Color = "#FFFFFF",
                Category = "New",
                Description = "New desc"
            };
            item.UpdateFrom(updated);

            Assert.AreEqual("Updated", item.Name);
            Assert.AreEqual(20.0, item.Time);
            Assert.AreEqual("#FFFFFF", item.Color);
            Assert.AreEqual("New", item.Category);
            Assert.AreEqual("New desc", item.Description);
            // Id should remain unchanged
            Assert.AreEqual("m1", item.Id);
        }

        [TestMethod]
        public void MarkerItem_NullablePropertiesAllowNull()
        {
            var marker = new Marker
            {
                Id = "m1",
                Name = "Name",
                Category = null,
                Description = null
            };

            var item = new MarkerItem(marker);

            Assert.IsNull(item.Category);
            Assert.IsNull(item.Description);
        }

        #endregion
    }
}
