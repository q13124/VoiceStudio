using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Collections.Generic;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Tests.ViewModels
{
    /// <summary>
    /// Unit tests for VoiceCloningWizard related model classes.
    /// Note: VoiceCloningWizardViewModel requires a WinUI DispatcherQueue that cannot be mocked in unit tests.
    /// These tests focus on the testable model classes used by the ViewModel.
    /// </summary>
    [TestClass]
    public class VoiceCloningWizardModelTests
    {
        #region QualityCandidateItem Model Tests

        [TestMethod]
        public void QualityCandidateItem_DefaultValues_AreNull()
        {
            // Arrange & Act
            var item = new QualityCandidateItem();

            // Assert
            Assert.IsNull(item.Label);
            Assert.IsNull(item.Score);
            Assert.IsNull(item.Device);
            Assert.IsNull(item.Metrics);
            Assert.IsNull(item.ReferenceAudio);
            Assert.IsNull(item.Selected);
        }

        [TestMethod]
        public void QualityCandidateItem_SetProperties_PersistsValues()
        {
            // Arrange & Act
            var item = new QualityCandidateItem
            {
                Label = "Candidate 1",
                Score = 0.95,
                Device = "GPU",
                ReferenceAudio = "audio_001.wav",
                Selected = true
            };

            // Assert
            Assert.AreEqual("Candidate 1", item.Label);
            Assert.AreEqual(0.95, item.Score);
            Assert.AreEqual("GPU", item.Device);
            Assert.AreEqual("audio_001.wav", item.ReferenceAudio);
            Assert.IsTrue(item.Selected.Value);
        }

        [TestMethod]
        public void QualityCandidateItem_LabelDisplay_WithLabel_ReturnsLabel()
        {
            // Arrange
            var item = new QualityCandidateItem { Label = "Best Match" };

            // Assert
            Assert.AreEqual("Best Match", item.LabelDisplay);
        }

        [TestMethod]
        public void QualityCandidateItem_LabelDisplay_WithEmptyLabel_ReturnsCandidateFallback()
        {
            // Arrange
            var item = new QualityCandidateItem { Label = "" };

            // Assert
            Assert.AreEqual("Candidate", item.LabelDisplay);
        }

        [TestMethod]
        public void QualityCandidateItem_LabelDisplay_WithNullLabel_ReturnsCandidateFallback()
        {
            // Arrange
            var item = new QualityCandidateItem { Label = null };

            // Assert
            Assert.AreEqual("Candidate", item.LabelDisplay);
        }

        [TestMethod]
        public void QualityCandidateItem_ScoreDisplay_WithScore_FormatsCorrectly()
        {
            // Arrange
            var item = new QualityCandidateItem { Score = 0.875 };

            // Assert
            Assert.AreEqual("0.875", item.ScoreDisplay);
        }

        [TestMethod]
        public void QualityCandidateItem_ScoreDisplay_WithNullScore_ReturnsNA()
        {
            // Arrange
            var item = new QualityCandidateItem { Score = null };

            // Assert
            Assert.AreEqual("N/A", item.ScoreDisplay);
        }

        [TestMethod]
        public void QualityCandidateItem_DeviceDisplay_WithDevice_ReturnsDevice()
        {
            // Arrange
            var item = new QualityCandidateItem { Device = "CUDA:0" };

            // Assert
            Assert.AreEqual("CUDA:0", item.DeviceDisplay);
        }

        [TestMethod]
        public void QualityCandidateItem_DeviceDisplay_WithNullDevice_ReturnsNA()
        {
            // Arrange
            var item = new QualityCandidateItem { Device = null };

            // Assert
            Assert.AreEqual("N/A", item.DeviceDisplay);
        }

        [TestMethod]
        public void QualityCandidateItem_SelectedDisplay_WhenTrue_ReturnsSelected()
        {
            // Arrange
            var item = new QualityCandidateItem { Selected = true };

            // Assert
            Assert.AreEqual("Selected", item.SelectedDisplay);
        }

        [TestMethod]
        public void QualityCandidateItem_SelectedDisplay_WhenFalse_ReturnsNotSelected()
        {
            // Arrange
            var item = new QualityCandidateItem { Selected = false };

            // Assert
            Assert.AreEqual("Not selected", item.SelectedDisplay);
        }

        [TestMethod]
        public void QualityCandidateItem_SelectedDisplay_WhenNull_ReturnsUnknown()
        {
            // Arrange
            var item = new QualityCandidateItem { Selected = null };

            // Assert
            Assert.AreEqual("Unknown", item.SelectedDisplay);
        }

        [TestMethod]
        public void QualityCandidateItem_FromDictionary_WithValidData_CreatesItem()
        {
            // Arrange
            var dict = new Dictionary<string, object>
            {
                { "label", "Test Candidate" },
                { "score", 0.92 },
                { "device", "GPU:0" },
                { "reference_audio", "test.wav" },
                { "selected", true }
            };

            // Act
            var item = QualityCandidateItem.FromDictionary(dict);

            // Assert
            Assert.IsNotNull(item);
            Assert.AreEqual("Test Candidate", item.Label);
            Assert.AreEqual(0.92, item.Score);
            Assert.AreEqual("GPU:0", item.Device);
            Assert.AreEqual("test.wav", item.ReferenceAudio);
            Assert.IsTrue(item.Selected.GetValueOrDefault());
        }

        [TestMethod]
        public void QualityCandidateItem_FromDictionary_WithAlternativeKeys_CreatesItem()
        {
            // Arrange - test fallback from "label" to "name"
            var dict = new Dictionary<string, object>
            {
                { "name", "Alternate Name" },
                { "mos", 4.5 },
                { "device_name", "NVIDIA RTX" }
            };

            // Act
            var item = QualityCandidateItem.FromDictionary(dict);

            // Assert
            Assert.IsNotNull(item);
            Assert.AreEqual("Alternate Name", item.Label);
            Assert.AreEqual(4.5, item.Score);
            Assert.AreEqual("NVIDIA RTX", item.Device);
        }

        [TestMethod]
        public void QualityCandidateItem_FromDictionary_WithCandidateFallback_UsesCandidate()
        {
            // Arrange
            var dict = new Dictionary<string, object>
            {
                { "candidate", "Candidate 3" }
            };

            // Act
            var item = QualityCandidateItem.FromDictionary(dict);

            // Assert
            Assert.IsNotNull(item);
            Assert.AreEqual("Candidate 3", item.Label);
        }

        [TestMethod]
        public void QualityCandidateItem_FromDictionary_WithEmptyDict_CreatesItemWithNulls()
        {
            // Arrange
            var dict = new Dictionary<string, object>();

            // Act
            var item = QualityCandidateItem.FromDictionary(dict);

            // Assert
            Assert.IsNotNull(item);
            Assert.IsNull(item.Label);
            Assert.IsNull(item.Score);
            Assert.IsNull(item.Device);
        }

        #endregion

        #region CandidateMetricDto Model Tests

        [TestMethod]
        public void CandidateMetricDto_DefaultValues_AreNullOrDefaults()
        {
            // Arrange & Act
            var dto = new CandidateMetricDto();

            // Assert
            Assert.IsNull(dto.ReferenceAudio);
            Assert.IsNull(dto.Metrics);
            Assert.IsNull(dto.Score);
            Assert.IsNull(dto.Selected);
            Assert.IsNull(dto.Device);
        }

        [TestMethod]
        public void CandidateMetricDto_SetProperties_PersistsValues()
        {
            // Arrange & Act
            var dto = new CandidateMetricDto
            {
                ReferenceAudio = "ref.wav",
                Score = 0.88,
                Selected = true,
                Device = "cuda:0",
                Metrics = new Dictionary<string, object>
                {
                    { "mos_score", 4.2 },
                    { "similarity", 0.95 }
                }
            };

            // Assert
            Assert.AreEqual("ref.wav", dto.ReferenceAudio);
            Assert.AreEqual(0.88, dto.Score);
            Assert.IsTrue(dto.Selected.Value);
            Assert.AreEqual("cuda:0", dto.Device);
            Assert.IsNotNull(dto.Metrics);
            Assert.AreEqual(2, dto.Metrics.Count);
        }

        [TestMethod]
        public void CandidateMetricDto_ToDictionary_ConvertsCorrectly()
        {
            // Arrange
            var dto = new CandidateMetricDto
            {
                ReferenceAudio = "test.wav",
                Score = 0.75,
                Selected = false,
                Device = "cpu"
            };

            // Act
            var dict = dto.ToDictionary();

            // Assert
            Assert.AreEqual("test.wav", dict["reference_audio"]);
            Assert.AreEqual(0.75, dict["score"]);
            Assert.AreEqual(false, dict["selected"]);
            Assert.AreEqual("cpu", dict["device"]);
        }

        [TestMethod]
        public void CandidateMetricDto_ToDictionary_WithNulls_UsesDefaults()
        {
            // Arrange
            var dto = new CandidateMetricDto();

            // Act
            var dict = dto.ToDictionary();

            // Assert
            Assert.AreEqual(string.Empty, dict["reference_audio"]);
            Assert.AreEqual(0.0, dict["score"]);
            Assert.AreEqual(false, dict["selected"]);
            Assert.AreEqual(string.Empty, dict["device"]);
            Assert.IsInstanceOfType(dict["metrics"], typeof(Dictionary<string, object>));
        }

        #endregion

        #region Edge Cases and Boundary Tests

        [TestMethod]
        public void QualityCandidateItem_ScoreDisplay_WithZeroScore_FormatsCorrectly()
        {
            // Arrange
            var item = new QualityCandidateItem { Score = 0.0 };

            // Assert
            Assert.AreEqual("0.000", item.ScoreDisplay);
        }

        [TestMethod]
        public void QualityCandidateItem_ScoreDisplay_WithOneScore_FormatsCorrectly()
        {
            // Arrange
            var item = new QualityCandidateItem { Score = 1.0 };

            // Assert
            Assert.AreEqual("1.000", item.ScoreDisplay);
        }

        [TestMethod]
        public void QualityCandidateItem_ScoreDisplay_WithHighPrecision_TruncatesTo3Decimals()
        {
            // Arrange
            var item = new QualityCandidateItem { Score = 0.123456789 };

            // Assert
            Assert.AreEqual("0.123", item.ScoreDisplay);
        }

        [TestMethod]
        public void QualityCandidateItem_DeviceDisplay_WithWhitespaceDevice_ReturnsNA()
        {
            // Arrange
            var item = new QualityCandidateItem { Device = "   " };

            // Assert
            Assert.AreEqual("N/A", item.DeviceDisplay);
        }

        [TestMethod]
        public void QualityCandidateItem_LabelDisplay_WithWhitespaceLabel_ReturnsCandidateFallback()
        {
            // Arrange
            var item = new QualityCandidateItem { Label = "   " };

            // Assert
            Assert.AreEqual("Candidate", item.LabelDisplay);
        }

        #endregion
    }
}
