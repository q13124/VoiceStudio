using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Collections.Generic;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Tests.ViewModels
{
    /// <summary>
    /// Unit tests for QualityDashboard related model classes.
    /// Note: QualityDashboardViewModel requires a WinUI DispatcherQueue that cannot be mocked in unit tests.
    /// These tests focus on the testable model classes used by the ViewModel.
    /// </summary>
    [TestClass]
    public class QualityDashboardModelTests
    {
        #region QualityOverview Model Tests

        [TestMethod]
        public void QualityOverview_DefaultConstructor_InitializesProperties()
        {
            // Arrange & Act
            var overview = new QualityOverview();

            // Assert
            Assert.AreEqual(0, overview.AverageMosScore);
            Assert.AreEqual(0, overview.AverageSimilarity);
            Assert.AreEqual(0, overview.AverageNaturalness);
            Assert.AreEqual(0, overview.TotalSamples);
            Assert.IsNotNull(overview.QualityDistribution);
        }

        [TestMethod]
        public void QualityOverview_AverageMosScoreDisplay_FormatsCorrectly()
        {
            // Arrange
            var overview = new QualityOverview { AverageMosScore = 4.25 };

            // Assert
            Assert.AreEqual("4.25/5.0", overview.AverageMosScoreDisplay);
        }

        [TestMethod]
        public void QualityOverview_AverageMosScoreDisplay_WithZero_FormatsCorrectly()
        {
            // Arrange
            var overview = new QualityOverview { AverageMosScore = 0 };

            // Assert
            Assert.AreEqual("0.00/5.0", overview.AverageMosScoreDisplay);
        }

        [TestMethod]
        public void QualityOverview_AverageMosScoreDisplay_WithMaxValue_FormatsCorrectly()
        {
            // Arrange
            var overview = new QualityOverview { AverageMosScore = 5.0 };

            // Assert
            Assert.AreEqual("5.00/5.0", overview.AverageMosScoreDisplay);
        }

        [TestMethod]
        public void QualityOverview_AverageSimilarityDisplay_FormatsAsPercentage()
        {
            // Arrange
            var overview = new QualityOverview { AverageSimilarity = 0.85 };

            // Assert
            StringAssert.Contains(overview.AverageSimilarityDisplay, "85");
        }

        [TestMethod]
        public void QualityOverview_AverageNaturalnessDisplay_FormatsAsPercentage()
        {
            // Arrange
            var overview = new QualityOverview { AverageNaturalness = 0.90 };

            // Assert
            StringAssert.Contains(overview.AverageNaturalnessDisplay, "90");
        }

        #endregion

        #region QualityDistributionItem Model Tests

        [TestMethod]
        public void QualityDistributionItem_DefaultConstructor_InitializesProperties()
        {
            // Arrange & Act
            var item = new QualityDistributionItem();

            // Assert
            Assert.AreEqual(string.Empty, item.Range);
            Assert.AreEqual(0, item.Count);
            Assert.AreEqual(0, item.TotalSamples);
        }

        [TestMethod]
        public void QualityDistributionItem_ParameterizedConstructor_SetsProperties()
        {
            // Arrange & Act
            var item = new QualityDistributionItem("3.0-4.0", 50, 100);

            // Assert
            Assert.AreEqual("3.0-4.0", item.Range);
            Assert.AreEqual(50, item.Count);
            Assert.AreEqual(100, item.TotalSamples);
        }

        [TestMethod]
        public void QualityDistributionItem_CountDisplay_ReturnsCountAsString()
        {
            // Arrange
            var item = new QualityDistributionItem("3.0-4.0", 42, 100);

            // Assert
            Assert.AreEqual("42", item.CountDisplay);
        }

        [TestMethod]
        public void QualityDistributionItem_PercentageDisplay_CalculatesCorrectly()
        {
            // Arrange
            var item = new QualityDistributionItem("3.0-4.0", 25, 100);

            // Assert
            Assert.AreEqual("25.0", item.PercentageDisplay);
        }

        [TestMethod]
        public void QualityDistributionItem_PercentageDisplay_WhenZeroTotal_ReturnsZero()
        {
            // Arrange
            var item = new QualityDistributionItem("3.0-4.0", 25, 0);

            // Assert
            Assert.AreEqual("0.0", item.PercentageDisplay);
        }

        [TestMethod]
        public void QualityDistributionItem_PercentageDisplay_WithLargeValues_CalculatesCorrectly()
        {
            // Arrange
            var item = new QualityDistributionItem("4.0-5.0", 750, 1000);

            // Assert
            Assert.AreEqual("75.0", item.PercentageDisplay);
        }

        [TestMethod]
        public void QualityDistributionItem_PercentageDisplay_WithSmallFraction_RoundsCorrectly()
        {
            // Arrange
            var item = new QualityDistributionItem("2.0-3.0", 1, 3);

            // Assert
            // 1/3 = 33.333...%
            Assert.AreEqual("33.3", item.PercentageDisplay);
        }

        #endregion

        #region QualityPresetItem Model Tests

        [TestMethod]
        public void QualityPresetItem_Constructor_SetsProperties()
        {
            // Arrange
            var targetMetrics = new Dictionary<string, double>
            {
                { "mos_score", 4.0 },
                { "similarity", 0.8 }
            };
            var parameters = new Dictionary<string, object>
            {
                { "quality_tier", "high" }
            };

            // Act
            var item = new QualityPresetItem("Standard", "Standard quality preset", targetMetrics, parameters);

            // Assert
            Assert.AreEqual("Standard", item.Name);
            Assert.AreEqual("Standard quality preset", item.Description);
            Assert.AreEqual(2, item.TargetMetrics.Count);
            Assert.AreEqual(1, item.Parameters.Count);
        }

        [TestMethod]
        public void QualityPresetItem_TargetMetricsDisplay_FormatsCorrectly()
        {
            // Arrange
            var targetMetrics = new Dictionary<string, double>
            {
                { "mos_score", 4.5 }
            };
            var parameters = new Dictionary<string, object>();

            // Act
            var item = new QualityPresetItem("Test", "Test", targetMetrics, parameters);

            // Assert
            StringAssert.Contains(item.TargetMetricsDisplay, "mos_score");
            StringAssert.Contains(item.TargetMetricsDisplay, "4.50");
        }

        [TestMethod]
        public void QualityPresetItem_TargetMetricsDisplay_WithMultipleMetrics_FormatsAll()
        {
            // Arrange
            var targetMetrics = new Dictionary<string, double>
            {
                { "mos_score", 4.0 },
                { "similarity", 0.85 }
            };
            var parameters = new Dictionary<string, object>();

            // Act
            var item = new QualityPresetItem("Multi", "Multi", targetMetrics, parameters);

            // Assert
            StringAssert.Contains(item.TargetMetricsDisplay, "mos_score");
            StringAssert.Contains(item.TargetMetricsDisplay, "similarity");
        }

        [TestMethod]
        public void QualityPresetItem_TargetMetricsDisplay_WithEmptyMetrics_ReturnsEmpty()
        {
            // Arrange
            var targetMetrics = new Dictionary<string, double>();
            var parameters = new Dictionary<string, object>();

            // Act
            var item = new QualityPresetItem("Empty", "Empty", targetMetrics, parameters);

            // Assert
            Assert.AreEqual(string.Empty, item.TargetMetricsDisplay);
        }

        #endregion
    }
}
