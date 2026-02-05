using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Collections.Generic;
using System.Linq;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Tests.ViewModels
{
    [TestClass]
    public class SceneBuilderModelTests
    {
        #region Scene Model Tests

        [TestMethod]
        public void Scene_DefaultValues()
        {
            var scene = new Scene();

            Assert.AreEqual(string.Empty, scene.Id);
            Assert.AreEqual(string.Empty, scene.Name);
            Assert.IsNull(scene.Description);
            Assert.AreEqual(string.Empty, scene.ProjectId);
            Assert.IsNotNull(scene.Tracks);
            Assert.AreEqual(0, scene.Tracks.Count);
            Assert.IsNotNull(scene.MasterEffects);
            Assert.AreEqual(0, scene.MasterEffects.Count);
            Assert.AreEqual(0.0, scene.Duration);
            Assert.AreEqual(string.Empty, scene.Created);
            Assert.AreEqual(string.Empty, scene.Modified);
            Assert.IsNotNull(scene.Tags);
            Assert.AreEqual(0, scene.Tags.Count);
        }

        [TestMethod]
        public void Scene_PropertiesSetCorrectly()
        {
            var tracks = new List<SceneTrack> { new SceneTrack { Id = "t1" } };
            var effects = new List<Dictionary<string, object>> { new Dictionary<string, object> { { "type", "reverb" } } };
            var tags = new List<string> { "music", "voice" };

            var scene = new Scene
            {
                Id = "scene123",
                Name = "Main Scene",
                Description = "Primary scene",
                ProjectId = "project456",
                Tracks = tracks,
                MasterEffects = effects,
                Duration = 120.5,
                Created = "2026-01-01",
                Modified = "2026-01-15",
                Tags = tags
            };

            Assert.AreEqual("scene123", scene.Id);
            Assert.AreEqual("Main Scene", scene.Name);
            Assert.AreEqual("Primary scene", scene.Description);
            Assert.AreEqual("project456", scene.ProjectId);
            Assert.AreSame(tracks, scene.Tracks);
            Assert.AreSame(effects, scene.MasterEffects);
            Assert.AreEqual(120.5, scene.Duration);
            Assert.AreEqual("2026-01-01", scene.Created);
            Assert.AreEqual("2026-01-15", scene.Modified);
            Assert.AreSame(tags, scene.Tags);
        }

        #endregion

        #region SceneTrack Model Tests

        [TestMethod]
        public void SceneTrack_DefaultValues()
        {
            var track = new SceneTrack();

            Assert.AreEqual(string.Empty, track.Id);
            Assert.AreEqual(string.Empty, track.Name);
            Assert.AreEqual(0, track.TrackNumber);
            Assert.IsNotNull(track.Clips);
            Assert.AreEqual(0, track.Clips.Count);
            Assert.IsNotNull(track.Effects);
            Assert.AreEqual(0, track.Effects.Count);
            Assert.IsNotNull(track.Automation);
            Assert.AreEqual(0, track.Automation.Count);
        }

        [TestMethod]
        public void SceneTrack_PropertiesSetCorrectly()
        {
            var clips = new List<Dictionary<string, object>> { new Dictionary<string, object> { { "start", 0.0 } } };
            var effects = new List<Dictionary<string, object>> { new Dictionary<string, object> { { "type", "eq" } } };
            var automation = new List<Dictionary<string, object>> { new Dictionary<string, object> { { "param", "volume" } } };

            var track = new SceneTrack
            {
                Id = "track1",
                Name = "Vocal Track",
                TrackNumber = 1,
                Clips = clips,
                Effects = effects,
                Automation = automation
            };

            Assert.AreEqual("track1", track.Id);
            Assert.AreEqual("Vocal Track", track.Name);
            Assert.AreEqual(1, track.TrackNumber);
            Assert.AreSame(clips, track.Clips);
            Assert.AreSame(effects, track.Effects);
            Assert.AreSame(automation, track.Automation);
        }

        #endregion

        #region SceneItem Model Tests

        [TestMethod]
        public void SceneItem_CreatedFromScene()
        {
            var scene = new Scene
            {
                Id = "s1",
                Name = "Test Scene",
                Description = "Test description",
                ProjectId = "p1",
                Tracks = new List<SceneTrack> { new SceneTrack { Id = "t1" } },
                MasterEffects = new List<Dictionary<string, object>> { new Dictionary<string, object> { { "x", 1 } } },
                Duration = 60.0,
                Created = "2026-01-01",
                Modified = "2026-01-02",
                Tags = new List<string> { "tag1" }
            };

            var item = new SceneItem(scene);

            Assert.AreEqual("s1", item.Id);
            Assert.AreEqual("Test Scene", item.Name);
            Assert.AreEqual("Test description", item.Description);
            Assert.AreEqual("p1", item.ProjectId);
            Assert.AreEqual(1, item.Tracks.Count);
            Assert.AreEqual(1, item.MasterEffects.Count);
            Assert.AreEqual(60.0, item.Duration);
            Assert.AreEqual("2026-01-01", item.Created);
            Assert.AreEqual("2026-01-02", item.Modified);
            Assert.AreEqual(1, item.Tags.Count);
        }

        [TestMethod]
        public void SceneItem_TrackCount_ReturnsCorrectCount()
        {
            var scene = new Scene
            {
                Tracks = new List<SceneTrack>
                {
                    new SceneTrack { Id = "t1" },
                    new SceneTrack { Id = "t2" },
                    new SceneTrack { Id = "t3" }
                }
            };
            var item = new SceneItem(scene);

            Assert.AreEqual(3, item.TrackCount);
        }

        [TestMethod]
        public void SceneItem_TrackCount_ZeroWhenEmpty()
        {
            var scene = new Scene { Tracks = new List<SceneTrack>() };
            var item = new SceneItem(scene);

            Assert.AreEqual(0, item.TrackCount);
        }

        [TestMethod]
        public void SceneItem_EffectCount_ReturnsCorrectCount()
        {
            var scene = new Scene
            {
                MasterEffects = new List<Dictionary<string, object>>
                {
                    new Dictionary<string, object> { { "e1", 1 } },
                    new Dictionary<string, object> { { "e2", 2 } }
                }
            };
            var item = new SceneItem(scene);

            Assert.AreEqual(2, item.EffectCount);
        }

        [TestMethod]
        public void SceneItem_UpdateFrom_UpdatesProperties()
        {
            var original = new Scene
            {
                Id = "s1",
                Name = "Original",
                Description = "Original desc",
                Duration = 30.0,
                Tags = new List<string> { "old" }
            };
            var item = new SceneItem(original);

            var updated = new Scene
            {
                Name = "Updated",
                Description = "Updated desc",
                Duration = 90.0,
                Tags = new List<string> { "new1", "new2" },
                Modified = "2026-02-01"
            };
            item.UpdateFrom(updated);

            Assert.AreEqual("Updated", item.Name);
            Assert.AreEqual("Updated desc", item.Description);
            Assert.AreEqual(90.0, item.Duration);
            Assert.AreEqual(2, item.Tags.Count);
            Assert.AreEqual("2026-02-01", item.Modified);
            // Id should not change
            Assert.AreEqual("s1", item.Id);
        }

        #endregion

        #region SceneTrackItem Model Tests

        [TestMethod]
        public void SceneTrackItem_CreatedFromSceneTrack()
        {
            var track = new SceneTrack
            {
                Id = "t1",
                Name = "Track 1",
                TrackNumber = 1,
                Clips = new List<Dictionary<string, object>> { new Dictionary<string, object> { { "c", 1 } } },
                Effects = new List<Dictionary<string, object>> { new Dictionary<string, object> { { "e", 1 } } },
                Automation = new List<Dictionary<string, object>> { new Dictionary<string, object> { { "a", 1 } } }
            };

            var item = new SceneTrackItem(track);

            Assert.AreEqual("t1", item.Id);
            Assert.AreEqual("Track 1", item.Name);
            Assert.AreEqual(1, item.TrackNumber);
            Assert.AreEqual(1, item.Clips.Count);
            Assert.AreEqual(1, item.Effects.Count);
            Assert.AreEqual(1, item.Automation.Count);
        }

        [TestMethod]
        public void SceneTrackItem_ClipCount_ReturnsCorrectCount()
        {
            var track = new SceneTrack
            {
                Clips = new List<Dictionary<string, object>>
                {
                    new Dictionary<string, object>(),
                    new Dictionary<string, object>(),
                    new Dictionary<string, object>(),
                    new Dictionary<string, object>()
                }
            };
            var item = new SceneTrackItem(track);

            Assert.AreEqual(4, item.ClipCount);
        }

        [TestMethod]
        public void SceneTrackItem_ClipCount_ZeroWhenEmpty()
        {
            var track = new SceneTrack { Clips = new List<Dictionary<string, object>>() };
            var item = new SceneTrackItem(track);

            Assert.AreEqual(0, item.ClipCount);
        }

        #endregion
    }
}
