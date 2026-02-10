using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using System;
using System.Threading.Tasks;
using VoiceStudio.App.ViewModels;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Tests.ViewModels
{
    /// <summary>
    /// Unit tests for VideoGenViewModel and related model classes.
    /// Note: VideoGenViewModel requires a WinUI DispatcherQueue that cannot be mocked in unit tests.
    /// These tests focus on the testable model classes used by the ViewModel.
    /// </summary>
    [TestClass]
    public class VideoGenViewModelTests : ViewModelTestBase
    {
        #region GeneratedVideo Model Tests

        [TestMethod]
        public void GeneratedVideo_DefaultValues_AreEmpty()
        {
            // Arrange & Act
            var video = new GeneratedVideo();

            // Assert
            Assert.AreEqual(string.Empty, video.VideoId);
            Assert.AreEqual(string.Empty, video.VideoUrl);
            Assert.AreEqual(string.Empty, video.Prompt);
            Assert.AreEqual(string.Empty, video.Engine);
            Assert.AreEqual(0, video.Width);
            Assert.AreEqual(0, video.Height);
            Assert.AreEqual(0.0, video.Fps);
            Assert.AreEqual(0.0, video.Duration);
            Assert.IsNull(video.QualityMetrics);
        }

        [TestMethod]
        public void GeneratedVideo_SetProperties_PersistsValues()
        {
            // Arrange & Act
            var video = new GeneratedVideo
            {
                VideoId = "vid-001",
                VideoUrl = "https://storage.example.com/video.mp4",
                Prompt = "A peaceful sunset over the ocean",
                Engine = "stable-video-diffusion",
                Width = 1920,
                Height = 1080,
                Fps = 24.0,
                Duration = 4.0,
                QualityMetrics = "{\"clarity\": 0.95}"
            };

            // Assert
            Assert.AreEqual("vid-001", video.VideoId);
            Assert.AreEqual("https://storage.example.com/video.mp4", video.VideoUrl);
            Assert.AreEqual("A peaceful sunset over the ocean", video.Prompt);
            Assert.AreEqual("stable-video-diffusion", video.Engine);
            Assert.AreEqual(1920, video.Width);
            Assert.AreEqual(1080, video.Height);
            Assert.AreEqual(24.0, video.Fps);
            Assert.AreEqual(4.0, video.Duration);
            Assert.AreEqual("{\"clarity\": 0.95}", video.QualityMetrics);
        }

        [TestMethod]
        public void GeneratedVideo_CommonResolutions_AreSupported()
        {
            // Test common video resolutions
            var resolutions = new[]
            {
                (Width: 1920, Height: 1080, Name: "1080p"),
                (Width: 1280, Height: 720, Name: "720p"),
                (Width: 3840, Height: 2160, Name: "4K"),
                (Width: 512, Height: 512, Name: "Square")
            };

            foreach (var res in resolutions)
            {
                var video = new GeneratedVideo
                {
                    Width = res.Width,
                    Height = res.Height
                };

                Assert.AreEqual(res.Width, video.Width, $"{res.Name} width mismatch");
                Assert.AreEqual(res.Height, video.Height, $"{res.Name} height mismatch");
            }
        }

        [TestMethod]
        public void GeneratedVideo_TypicalFrameRates_AreSupported()
        {
            // Test common frame rates
            var frameRates = new[] { 24.0, 25.0, 29.97, 30.0, 60.0 };

            foreach (var fps in frameRates)
            {
                var video = new GeneratedVideo { Fps = fps };
                Assert.AreEqual(fps, video.Fps, $"Frame rate {fps} not persisted correctly");
            }
        }

        #endregion

        #region VideoQualityPreset Model Tests

        [TestMethod]
        public void VideoQualityPreset_DefaultValues_AreCorrect()
        {
            // Arrange & Act
            var preset = new VideoQualityPreset();

            // Assert
            Assert.AreEqual(string.Empty, preset.Id);
            Assert.AreEqual(string.Empty, preset.Name);
            Assert.AreEqual(string.Empty, preset.Description);
            Assert.AreEqual(0, preset.Width);
            Assert.AreEqual(0, preset.Height);
            Assert.AreEqual(0.0, preset.Fps);
            Assert.AreEqual(0.0, preset.Bitrate);
            Assert.AreEqual("H.264", preset.Codec);  // Default codec
        }

        [TestMethod]
        public void VideoQualityPreset_SetProperties_PersistsValues()
        {
            // Arrange & Act
            var preset = new VideoQualityPreset
            {
                Id = "preset-hd",
                Name = "HD 1080p",
                Description = "High definition 1080p video",
                Width = 1920,
                Height = 1080,
                Fps = 30.0,
                Bitrate = 8000000,  // 8 Mbps
                Codec = "H.265"
            };

            // Assert
            Assert.AreEqual("preset-hd", preset.Id);
            Assert.AreEqual("HD 1080p", preset.Name);
            Assert.AreEqual("High definition 1080p video", preset.Description);
            Assert.AreEqual(1920, preset.Width);
            Assert.AreEqual(1080, preset.Height);
            Assert.AreEqual(30.0, preset.Fps);
            Assert.AreEqual(8000000, preset.Bitrate);
            Assert.AreEqual("H.265", preset.Codec);
        }

        [TestMethod]
        public void VideoQualityPreset_CommonPresets_CanBeCreated()
        {
            // Test creating common preset configurations
            var presets = new[]
            {
                new VideoQualityPreset { Name = "Low", Width = 640, Height = 360, Bitrate = 1000000 },
                new VideoQualityPreset { Name = "Medium", Width = 1280, Height = 720, Bitrate = 4000000 },
                new VideoQualityPreset { Name = "High", Width = 1920, Height = 1080, Bitrate = 8000000 },
                new VideoQualityPreset { Name = "Ultra", Width = 3840, Height = 2160, Bitrate = 20000000 }
            };

            Assert.AreEqual(4, presets.Length);
            Assert.AreEqual("Low", presets[0].Name);
            Assert.AreEqual("Ultra", presets[3].Name);
        }

        [TestMethod]
        public void VideoQualityPreset_SupportedCodecs_AreValid()
        {
            // Test various codec values
            var codecs = new[] { "H.264", "H.265", "VP9", "AV1" };

            foreach (var codec in codecs)
            {
                var preset = new VideoQualityPreset { Codec = codec };
                Assert.AreEqual(codec, preset.Codec);
            }
        }

        #endregion

        #region Edge Cases

        [TestMethod]
        public void GeneratedVideo_ZeroDuration_IsValid()
        {
            // Zero duration might indicate an image or still frame
            var video = new GeneratedVideo { Duration = 0.0 };
            Assert.AreEqual(0.0, video.Duration);
        }

        [TestMethod]
        public void GeneratedVideo_NullQualityMetrics_IsValid()
        {
            // Quality metrics may not always be present
            var video = new GeneratedVideo { QualityMetrics = null };
            Assert.IsNull(video.QualityMetrics);
        }

        [TestMethod]
        public void VideoQualityPreset_ZeroBitrate_IsValid()
        {
            // Zero bitrate might indicate variable/auto bitrate
            var preset = new VideoQualityPreset { Bitrate = 0.0 };
            Assert.AreEqual(0.0, preset.Bitrate);
        }

        #endregion
    }
}