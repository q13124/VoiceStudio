using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using VoiceStudio.App.Views.Panels;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Tests.ViewModels
{
    /// <summary>
    /// Unit tests for ImageVideoEnhancementPipelineViewModel and related model classes.
    /// Note: ImageVideoEnhancementPipelineViewModel requires a WinUI DispatcherQueue that cannot be mocked in unit tests.
    /// These tests focus on the testable model classes used by the ViewModel.
    /// </summary>
    [TestClass]
    public class ImageVideoEnhancementPipelineViewModelTests : ViewModelTestBase
    {
        #region EnhancementItem Model Tests

        [TestMethod]
        public void EnhancementItem_DefaultValues_AreEmpty()
        {
            // Arrange & Act
            var item = new EnhancementItem();

            // Assert
            Assert.AreEqual(string.Empty, item.Id);
            Assert.AreEqual(string.Empty, item.Name);
            Assert.AreEqual(string.Empty, item.Description);
        }

        [TestMethod]
        public void EnhancementItem_SetProperties_PersistsValues()
        {
            // Arrange & Act
            var item = new EnhancementItem
            {
                Id = "enhance-001",
                Name = "Noise Reduction",
                Description = "Reduces background noise while preserving voice quality"
            };

            // Assert
            Assert.AreEqual("enhance-001", item.Id);
            Assert.AreEqual("Noise Reduction", item.Name);
            Assert.AreEqual("Reduces background noise while preserving voice quality", item.Description);
        }

        #endregion

        #region PipelineStep Model Tests

        [TestMethod]
        public void PipelineStep_DefaultValues_AreEmpty()
        {
            // Arrange & Act
            var step = new PipelineStep();

            // Assert
            Assert.AreEqual(string.Empty, step.Id);
            Assert.AreEqual(0, step.StepNumber);
            Assert.AreEqual(string.Empty, step.Name);
            Assert.AreEqual(string.Empty, step.Description);
            Assert.AreEqual(string.Empty, step.EnhancementId);
            Assert.IsNotNull(step.Parameters);
            Assert.AreEqual(0, step.Parameters.Count);
        }

        [TestMethod]
        public void PipelineStep_SetProperties_PersistsValues()
        {
            // Arrange & Act
            var step = new PipelineStep
            {
                Id = "step-001",
                StepNumber = 1,
                Name = "Upscale 2x",
                Description = "Upscales image to 2x resolution",
                EnhancementId = "upscale",
                Parameters = new Dictionary<string, object>
                {
                    ["scale"] = 2,
                    ["model"] = "ESRGAN"
                }
            };

            // Assert
            Assert.AreEqual("step-001", step.Id);
            Assert.AreEqual(1, step.StepNumber);
            Assert.AreEqual("Upscale 2x", step.Name);
            Assert.AreEqual("upscale", step.EnhancementId);
            Assert.AreEqual(2, step.Parameters.Count);
        }

        [TestMethod]
        public void PipelineStep_ParametersSummary_FormatsCorrectly()
        {
            // Arrange
            var step = new PipelineStep
            {
                Parameters = new Dictionary<string, object>
                {
                    ["strength"] = 0.5,
                    ["iterations"] = 3
                }
            };

            // Act
            var summary = step.ParametersSummary;

            // Assert
            Assert.IsTrue(summary.Contains("strength: 0.5") || summary.Contains("strength: 0,5"));  // Culture-dependent
            Assert.IsTrue(summary.Contains("iterations: 3"));
            Assert.IsTrue(summary.Contains(", "));
        }

        [TestMethod]
        public void PipelineStep_ParametersSummary_EmptyParameters_ReturnsEmpty()
        {
            // Arrange
            var step = new PipelineStep { Parameters = new Dictionary<string, object>() };

            // Act
            var summary = step.ParametersSummary;

            // Assert
            Assert.AreEqual(string.Empty, summary);
        }

        #endregion

        #region EnhancementPreset Model Tests

        [TestMethod]
        public void EnhancementPreset_DefaultValues_AreCorrect()
        {
            // Arrange & Act
            var preset = new EnhancementPreset();

            // Assert
            Assert.AreEqual(string.Empty, preset.Id);
            Assert.AreEqual(string.Empty, preset.Name);
            Assert.AreEqual(string.Empty, preset.Description);
            Assert.AreEqual("Image", preset.ContentType);  // Default is Image
            Assert.IsNotNull(preset.Steps);
            Assert.AreEqual(0, preset.Steps.Count);
        }

        [TestMethod]
        public void EnhancementPreset_SetProperties_PersistsValues()
        {
            // Arrange & Act
            var preset = new EnhancementPreset
            {
                Id = "preset-hd",
                Name = "HD Quality",
                Description = "Enhance to HD quality",
                ContentType = "Video",
                Steps = new List<string> { "denoise", "upscale", "sharpen" }
            };

            // Assert
            Assert.AreEqual("preset-hd", preset.Id);
            Assert.AreEqual("HD Quality", preset.Name);
            Assert.AreEqual("Video", preset.ContentType);
            Assert.AreEqual(3, preset.Steps.Count);
            CollectionAssert.Contains(preset.Steps, "denoise");
            CollectionAssert.Contains(preset.Steps, "upscale");
            CollectionAssert.Contains(preset.Steps, "sharpen");
        }

        [TestMethod]
        public void EnhancementPreset_ContentTypes_SupportImageAndVideo()
        {
            // Test both content types
            var imagePreset = new EnhancementPreset { ContentType = "Image" };
            var videoPreset = new EnhancementPreset { ContentType = "Video" };

            Assert.AreEqual("Image", imagePreset.ContentType);
            Assert.AreEqual("Video", videoPreset.ContentType);
        }

        #endregion

        #region Edge Cases

        [TestMethod]
        public void PipelineStep_SingleParameter_FormatsWithoutComma()
        {
            // Arrange
            var step = new PipelineStep
            {
                Parameters = new Dictionary<string, object> { ["level"] = 5 }
            };

            // Act
            var summary = step.ParametersSummary;

            // Assert
            Assert.AreEqual("level: 5", summary);
            Assert.IsFalse(summary.Contains(","));
        }

        [TestMethod]
        public void EnhancementPreset_EmptySteps_IsValid()
        {
            // A preset with no steps is valid (might be a template)
            var preset = new EnhancementPreset
            {
                Id = "empty",
                Name = "Empty Preset",
                Steps = new List<string>()
            };

            Assert.AreEqual(0, preset.Steps.Count);
        }

        #endregion
    }
}