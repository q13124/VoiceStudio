using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using VoiceStudio.App.ViewModels;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Tests.ViewModels
{
    /// <summary>
    /// Unit tests for QualityControlViewModel and related model classes.
    /// Note: QualityControlViewModel requires a WinUI DispatcherQueue that cannot be mocked in unit tests.
    /// These tests focus on the testable model classes used by the ViewModel.
    /// </summary>
    [TestClass]
    public class QualityControlViewModelTests : ViewModelTestBase
    {
        #region QualityPresetInfo Model Tests

        [TestMethod]
        public void QualityPresetInfo_DefaultValues_AreEmpty()
        {
            // Arrange & Act
            var preset = new QualityPresetInfo();

            // Assert
            Assert.AreEqual(string.Empty, preset.Name);
            Assert.AreEqual(string.Empty, preset.Description);
            Assert.IsNotNull(preset.TargetMetrics);
            Assert.AreEqual(0, preset.TargetMetrics.Count);
            Assert.IsNotNull(preset.Parameters);
            Assert.AreEqual(0, preset.Parameters.Count);
        }

        [TestMethod]
        public void QualityPresetInfo_SetProperties_PersistsValues()
        {
            // Arrange & Act
            var preset = new QualityPresetInfo
            {
                Name = "Professional",
                Description = "High quality professional output",
                TargetMetrics = new Dictionary<string, double>
                {
                    ["mos_score"] = 4.0,
                    ["similarity"] = 0.85
                },
                Parameters = new Dictionary<string, object>
                {
                    ["sample_rate"] = 44100,
                    ["use_enhancement"] = true
                }
            };

            // Assert
            Assert.AreEqual("Professional", preset.Name);
            Assert.AreEqual("High quality professional output", preset.Description);
            Assert.AreEqual(2, preset.TargetMetrics.Count);
            Assert.AreEqual(4.0, preset.TargetMetrics["mos_score"]);
            Assert.AreEqual(0.85, preset.TargetMetrics["similarity"]);
            Assert.AreEqual(2, preset.Parameters.Count);
        }

        [TestMethod]
        public void QualityPresetInfo_TargetMetrics_CanBeModified()
        {
            // Arrange
            var preset = new QualityPresetInfo
            {
                Name = "Test",
                TargetMetrics = new Dictionary<string, double>()
            };

            // Act
            preset.TargetMetrics["naturalness"] = 0.9;
            preset.TargetMetrics["snr_db"] = 30.0;

            // Assert
            Assert.AreEqual(2, preset.TargetMetrics.Count);
            Assert.AreEqual(0.9, preset.TargetMetrics["naturalness"]);
            Assert.AreEqual(30.0, preset.TargetMetrics["snr_db"]);
        }

        #endregion

        #region QualityAnalysisRequest Model Tests

        [TestMethod]
        public void QualityAnalysisRequest_DefaultValues_AreCorrect()
        {
            // Arrange & Act
            var request = new QualityAnalysisRequest();

            // Assert
            Assert.IsNull(request.MosScore);
            Assert.IsNull(request.Similarity);
            Assert.IsNull(request.Naturalness);
            Assert.IsNull(request.SnrDb);
            Assert.AreEqual("standard", request.TargetTier);
        }

        [TestMethod]
        public void QualityAnalysisRequest_SetProperties_PersistsValues()
        {
            // Arrange & Act
            var request = new QualityAnalysisRequest
            {
                MosScore = 4.5,
                Similarity = 0.92,
                Naturalness = 0.88,
                SnrDb = 35.0,
                TargetTier = "professional"
            };

            // Assert
            Assert.AreEqual(4.5, request.MosScore);
            Assert.AreEqual(0.92, request.Similarity);
            Assert.AreEqual(0.88, request.Naturalness);
            Assert.AreEqual(35.0, request.SnrDb);
            Assert.AreEqual("professional", request.TargetTier);
        }

        [TestMethod]
        public void QualityAnalysisRequest_PartialValues_AllowsNulls()
        {
            // Arrange & Act - only set MOS score
            var request = new QualityAnalysisRequest
            {
                MosScore = 4.0,
                TargetTier = "broadcast"
            };

            // Assert
            Assert.AreEqual(4.0, request.MosScore);
            Assert.IsNull(request.Similarity);
            Assert.IsNull(request.Naturalness);
            Assert.IsNull(request.SnrDb);
            Assert.AreEqual("broadcast", request.TargetTier);
        }

        #endregion

        #region Quality Tier Tests

        [TestMethod]
        public void QualityTiers_ValidTiers_AreRecognized()
        {
            // Valid tiers used in the quality control system
            var validTiers = new[] { "standard", "professional", "broadcast", "studio" };

            foreach (var tier in validTiers)
            {
                var request = new QualityAnalysisRequest { TargetTier = tier };
                Assert.AreEqual(tier, request.TargetTier);
            }
        }

        #endregion

        #region Edge Cases

        [TestMethod]
        public void QualityPresetInfo_EmptyName_AllowsEmptyString()
        {
            // Arrange & Act
            var preset = new QualityPresetInfo { Name = "" };

            // Assert
            Assert.AreEqual(string.Empty, preset.Name);
        }

        [TestMethod]
        public void QualityPresetInfo_EmptyDescription_AllowsEmptyString()
        {
            // Arrange & Act
            var preset = new QualityPresetInfo { Description = "" };

            // Assert
            Assert.AreEqual(string.Empty, preset.Description);
        }

        [TestMethod]
        public void QualityAnalysisRequest_ZeroValues_AreValid()
        {
            // Zero is a valid (if unusual) score
            var request = new QualityAnalysisRequest
            {
                MosScore = 0.0,
                Similarity = 0.0,
                Naturalness = 0.0,
                SnrDb = 0.0
            };

            Assert.AreEqual(0.0, request.MosScore);
            Assert.AreEqual(0.0, request.Similarity);
            Assert.AreEqual(0.0, request.Naturalness);
            Assert.AreEqual(0.0, request.SnrDb);
        }

        [TestMethod]
        public void QualityAnalysisRequest_NegativeSnr_IsValid()
        {
            // Negative SNR is valid (signal weaker than noise)
            var request = new QualityAnalysisRequest { SnrDb = -5.0 };

            Assert.AreEqual(-5.0, request.SnrDb);
        }

        #endregion
    }
}