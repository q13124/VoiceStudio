using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Collections.Generic;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Tests.ViewModels
{
    /// <summary>
    /// Unit tests for Spectrogram related model classes.
    /// Note: SpectrogramViewModel requires a WinUI DispatcherQueue that cannot be mocked in unit tests.
    /// These tests focus on the testable model classes used by the ViewModel.
    /// </summary>
    [TestClass]
    public class SpectrogramModelTests
    {
        #region SpectrogramData Model Tests

        [TestMethod]
        public void SpectrogramData_DefaultConstructor_InitializesDefaults()
        {
            // Arrange & Act
            var data = new SpectrogramData();

            // Assert
            Assert.AreEqual(string.Empty, data.AudioId);
            Assert.AreEqual(0, data.SampleRate);
            Assert.AreEqual(0.0, data.Duration);
            Assert.IsNotNull(data.Frames);
            Assert.AreEqual(0, data.Frames.Count);
            Assert.AreEqual(0.0, data.FrequencyResolution);
            Assert.AreEqual(0.0, data.TimeResolution);
            Assert.IsNotNull(data.Config);
        }

        [TestMethod]
        public void SpectrogramData_SetProperties_PersistsValues()
        {
            // Arrange & Act
            var data = new SpectrogramData
            {
                AudioId = "audio-123",
                SampleRate = 44100,
                Duration = 3.5,
                FrequencyResolution = 10.5,
                TimeResolution = 0.023
            };

            // Assert
            Assert.AreEqual("audio-123", data.AudioId);
            Assert.AreEqual(44100, data.SampleRate);
            Assert.AreEqual(3.5, data.Duration, 0.001);
            Assert.AreEqual(10.5, data.FrequencyResolution, 0.001);
            Assert.AreEqual(0.023, data.TimeResolution, 0.001);
        }

        [TestMethod]
        public void SpectrogramData_Frames_CanBePopulated()
        {
            // Arrange
            var data = new SpectrogramData();

            // Act
            data.Frames.Add(new SpectrogramFrame { Time = 0.0 });
            data.Frames.Add(new SpectrogramFrame { Time = 0.5 });
            data.Frames.Add(new SpectrogramFrame { Time = 1.0 });

            // Assert
            Assert.AreEqual(3, data.Frames.Count);
            Assert.AreEqual(0.0, data.Frames[0].Time);
            Assert.AreEqual(0.5, data.Frames[1].Time);
            Assert.AreEqual(1.0, data.Frames[2].Time);
        }

        #endregion

        #region SpectrogramFrame Model Tests

        [TestMethod]
        public void SpectrogramFrame_DefaultConstructor_InitializesDefaults()
        {
            // Arrange & Act
            var frame = new SpectrogramFrame();

            // Assert
            Assert.AreEqual(0.0, frame.Time);
            Assert.IsNotNull(frame.Frequencies);
            Assert.IsNotNull(frame.Magnitudes);
            Assert.AreEqual(0, frame.Frequencies.Count);
            Assert.AreEqual(0, frame.Magnitudes.Count);
            Assert.IsNull(frame.Phases);
        }

        [TestMethod]
        public void SpectrogramFrame_SetProperties_PersistsValues()
        {
            // Arrange & Act
            var frame = new SpectrogramFrame
            {
                Time = 1.25,
                Frequencies = new List<double> { 20.0, 100.0, 500.0, 2000.0, 8000.0 },
                Magnitudes = new List<double> { -60.0, -40.0, -30.0, -45.0, -55.0 },
                Phases = new List<double> { 0.1, 0.2, 0.3, 0.4, 0.5 }
            };

            // Assert
            Assert.AreEqual(1.25, frame.Time, 0.001);
            Assert.AreEqual(5, frame.Frequencies.Count);
            Assert.AreEqual(5, frame.Magnitudes.Count);
            Assert.IsNotNull(frame.Phases);
            Assert.AreEqual(5, frame.Phases.Count);
        }

        [TestMethod]
        public void SpectrogramFrame_Frequencies_CanContainNyquistRange()
        {
            // Arrange - Typical frequency range up to Nyquist (22050 Hz for 44100 sample rate)
            var frame = new SpectrogramFrame
            {
                Frequencies = new List<double> { 20.0, 100.0, 1000.0, 5000.0, 10000.0, 20000.0, 22050.0 }
            };

            // Assert
            Assert.AreEqual(7, frame.Frequencies.Count);
            Assert.AreEqual(20.0, frame.Frequencies[0]);
            Assert.AreEqual(22050.0, frame.Frequencies[6]);
        }

        #endregion

        #region SpectrogramConfig Model Tests

        [TestMethod]
        public void SpectrogramConfig_DefaultConstructor_InitializesDefaults()
        {
            // Arrange & Act
            var config = new SpectrogramConfig();

            // Assert
            Assert.AreEqual(string.Empty, config.AudioId);
            Assert.AreEqual(0, config.WindowSize);
            Assert.AreEqual(0, config.HopLength);
            Assert.AreEqual(0, config.NFft);
            Assert.IsNull(config.FrequencyRange);
            Assert.IsNull(config.TimeRange);
            Assert.AreEqual("viridis", config.ColorScheme);
            Assert.IsNull(config.ColormapRange);
            Assert.IsFalse(config.ShowPhase);
            Assert.IsFalse(config.ShowMagnitude);
            Assert.IsFalse(config.LogScale);
        }

        [TestMethod]
        public void SpectrogramConfig_SetProperties_PersistsValues()
        {
            // Arrange & Act
            var config = new SpectrogramConfig
            {
                AudioId = "audio-456",
                WindowSize = 2048,
                HopLength = 512,
                NFft = 4096,
                ColorScheme = "plasma",
                ShowPhase = true,
                ShowMagnitude = true,
                LogScale = true,
                FrequencyRange = new Dictionary<string, double> { { "min", 20.0 }, { "max", 8000.0 } },
                TimeRange = new Dictionary<string, double> { { "start", 0.0 }, { "end", 5.0 } },
                ColormapRange = new Dictionary<string, double> { { "min", -80.0 }, { "max", 0.0 } }
            };

            // Assert
            Assert.AreEqual("audio-456", config.AudioId);
            Assert.AreEqual(2048, config.WindowSize);
            Assert.AreEqual(512, config.HopLength);
            Assert.AreEqual(4096, config.NFft);
            Assert.AreEqual("plasma", config.ColorScheme);
            Assert.IsTrue(config.ShowPhase);
            Assert.IsTrue(config.ShowMagnitude);
            Assert.IsTrue(config.LogScale);
            Assert.IsNotNull(config.FrequencyRange);
            Assert.AreEqual(20.0, config.FrequencyRange["min"]);
            Assert.AreEqual(8000.0, config.FrequencyRange["max"]);
        }

        [TestMethod]
        public void SpectrogramConfig_ColorScheme_DefaultIsViridis()
        {
            // Arrange & Act
            var config = new SpectrogramConfig();

            // Assert
            Assert.AreEqual("viridis", config.ColorScheme);
        }

        [TestMethod]
        public void SpectrogramConfig_ColorScheme_CanBeChanged()
        {
            // Arrange
            var config = new SpectrogramConfig();

            // Act
            config.ColorScheme = "magma";

            // Assert
            Assert.AreEqual("magma", config.ColorScheme);
        }

        #endregion

        #region ColorSchemeInfo Model Tests

        [TestMethod]
        public void ColorSchemeInfo_DefaultConstructor_InitializesEmptyStrings()
        {
            // Arrange & Act
            var info = new ColorSchemeInfo();

            // Assert
            Assert.AreEqual(string.Empty, info.Id);
            Assert.AreEqual(string.Empty, info.Name);
            Assert.AreEqual(string.Empty, info.Description);
        }

        [TestMethod]
        public void ColorSchemeInfo_SetProperties_PersistsValues()
        {
            // Arrange & Act
            var info = new ColorSchemeInfo
            {
                Id = "viridis",
                Name = "Viridis",
                Description = "Perceptually uniform colormap"
            };

            // Assert
            Assert.AreEqual("viridis", info.Id);
            Assert.AreEqual("Viridis", info.Name);
            Assert.AreEqual("Perceptually uniform colormap", info.Description);
        }

        [TestMethod]
        public void ColorSchemeInfo_CommonColorSchemes_AreValid()
        {
            // Arrange & Act
            var schemes = new[]
            {
                new ColorSchemeInfo { Id = "viridis", Name = "Viridis", Description = "Perceptually uniform" },
                new ColorSchemeInfo { Id = "plasma", Name = "Plasma", Description = "High contrast warm" },
                new ColorSchemeInfo { Id = "magma", Name = "Magma", Description = "Dark to bright" },
                new ColorSchemeInfo { Id = "inferno", Name = "Inferno", Description = "Hot colors" },
                new ColorSchemeInfo { Id = "grayscale", Name = "Grayscale", Description = "Black to white" }
            };

            // Assert
            foreach (var scheme in schemes)
            {
                Assert.IsFalse(string.IsNullOrEmpty(scheme.Id));
                Assert.IsFalse(string.IsNullOrEmpty(scheme.Name));
                Assert.IsFalse(string.IsNullOrEmpty(scheme.Description));
            }
            Assert.AreEqual(5, schemes.Length);
        }

        #endregion

        #region SpectrogramDataItem Model Tests

        [TestMethod]
        public void SpectrogramDataItem_Constructor_CopiesFromSpectrogramData()
        {
            // Arrange
            var sourceData = new SpectrogramData
            {
                AudioId = "source-audio",
                SampleRate = 48000,
                Duration = 2.5,
                FrequencyResolution = 23.4,
                TimeResolution = 0.01
            };
            sourceData.Frames.Add(new SpectrogramFrame { Time = 0.0 });
            sourceData.Frames.Add(new SpectrogramFrame { Time = 0.5 });

            // Act
            var item = new SpectrogramDataItem(sourceData);

            // Assert
            Assert.AreEqual("source-audio", item.AudioId);
            Assert.AreEqual(48000, item.SampleRate);
            Assert.AreEqual(2.5, item.Duration, 0.001);
            Assert.AreEqual(23.4, item.FrequencyResolution, 0.001);
            Assert.AreEqual(0.01, item.TimeResolution, 0.001);
            Assert.AreEqual(2, item.FrameCount);
        }

        [TestMethod]
        public void SpectrogramDataItem_FrameCount_ReturnsCorrectCount()
        {
            // Arrange
            var sourceData = new SpectrogramData();
            for (int i = 0; i < 100; i++)
            {
                sourceData.Frames.Add(new SpectrogramFrame { Time = i * 0.01 });
            }

            // Act
            var item = new SpectrogramDataItem(sourceData);

            // Assert
            Assert.AreEqual(100, item.FrameCount);
        }

        [TestMethod]
        public void SpectrogramDataItem_FrameCount_WithNullFrames_ReturnsZero()
        {
            // Arrange
            var sourceData = new SpectrogramData();
            var item = new SpectrogramDataItem(sourceData);

            // Act - Frames list is empty but not null
            item.Frames = null!;

            // Assert
            Assert.AreEqual(0, item.FrameCount);
        }

        #endregion

        #region Edge Cases

        [TestMethod]
        public void SpectrogramData_ZeroSampleRate_IsAllowed()
        {
            // Arrange & Act
            var data = new SpectrogramData { SampleRate = 0 };

            // Assert
            Assert.AreEqual(0, data.SampleRate);
        }

        [TestMethod]
        public void SpectrogramData_NegativeDuration_IsAllowed()
        {
            // Arrange & Act - The model doesn't validate, caller's responsibility
            var data = new SpectrogramData { Duration = -1.0 };

            // Assert
            Assert.AreEqual(-1.0, data.Duration);
        }

        [TestMethod]
        public void SpectrogramConfig_LargeNFft_IsAllowed()
        {
            // Arrange & Act
            var config = new SpectrogramConfig { NFft = 16384 };

            // Assert
            Assert.AreEqual(16384, config.NFft);
        }

        #endregion
    }
}
