using Microsoft.VisualStudio.TestTools.UnitTesting;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Tests.ViewModels
{
    [TestClass]
    public class ProfileComparisonModelTests
    {
        #region ProfileComparisonData Model Tests

        [TestMethod]
        public void ProfileComparisonData_DefaultValues()
        {
            var data = new ProfileComparisonData();

            Assert.IsNull(data.ProfileA);
            Assert.IsNull(data.ProfileB);
            Assert.IsNull(data.QualityMetricsA);
            Assert.IsNull(data.QualityMetricsB);
            Assert.AreEqual(0.0, data.QualityScoreA);
            Assert.AreEqual(0.0, data.QualityScoreB);
            Assert.IsNull(data.AudioUrlA);
            Assert.IsNull(data.AudioUrlB);
        }

        [TestMethod]
        public void ProfileComparisonData_QualityScoreADisplay_FormatsCorrectly()
        {
            var data = new ProfileComparisonData { QualityScoreA = 3.75 };
            Assert.AreEqual("3.75/5.0", data.QualityScoreADisplay);
        }

        [TestMethod]
        public void ProfileComparisonData_QualityScoreADisplay_Zero()
        {
            var data = new ProfileComparisonData { QualityScoreA = 0 };
            Assert.AreEqual("0.00/5.0", data.QualityScoreADisplay);
        }

        [TestMethod]
        public void ProfileComparisonData_QualityScoreBDisplay_FormatsCorrectly()
        {
            var data = new ProfileComparisonData { QualityScoreB = 4.25 };
            Assert.AreEqual("4.25/5.0", data.QualityScoreBDisplay);
        }

        [TestMethod]
        public void ProfileComparisonData_QualityScoreDifference_Positive()
        {
            var data = new ProfileComparisonData
            {
                QualityScoreA = 4.0,
                QualityScoreB = 3.5
            };
            Assert.AreEqual("+0.50", data.QualityScoreDifference);
        }

        [TestMethod]
        public void ProfileComparisonData_QualityScoreDifference_Negative()
        {
            var data = new ProfileComparisonData
            {
                QualityScoreA = 3.0,
                QualityScoreB = 4.0
            };
            Assert.AreEqual("-1.00", data.QualityScoreDifference);
        }

        [TestMethod]
        public void ProfileComparisonData_QualityScoreDifference_Zero()
        {
            var data = new ProfileComparisonData
            {
                QualityScoreA = 3.5,
                QualityScoreB = 3.5
            };
            Assert.AreEqual("0.00", data.QualityScoreDifference);
        }

        [TestMethod]
        public void ProfileComparisonData_ProfileAIsBetter_TrueWhenHigher()
        {
            var data = new ProfileComparisonData
            {
                QualityScoreA = 4.5,
                QualityScoreB = 3.5
            };
            Assert.IsTrue(data.ProfileAIsBetter);
            Assert.IsFalse(data.ProfileBIsBetter);
        }

        [TestMethod]
        public void ProfileComparisonData_ProfileBIsBetter_TrueWhenHigher()
        {
            var data = new ProfileComparisonData
            {
                QualityScoreA = 3.0,
                QualityScoreB = 4.0
            };
            Assert.IsFalse(data.ProfileAIsBetter);
            Assert.IsTrue(data.ProfileBIsBetter);
        }

        [TestMethod]
        public void ProfileComparisonData_NeitherBetter_WhenEqual()
        {
            var data = new ProfileComparisonData
            {
                QualityScoreA = 3.5,
                QualityScoreB = 3.5
            };
            Assert.IsFalse(data.ProfileAIsBetter);
            Assert.IsFalse(data.ProfileBIsBetter);
        }

        [TestMethod]
        public void ProfileComparisonData_MetricsNull_DisplayPropertiesReturnNull()
        {
            var data = new ProfileComparisonData
            {
                QualityMetricsA = null,
                QualityMetricsB = null
            };

            Assert.IsNull(data.MosScoreA);
            Assert.IsNull(data.MosScoreB);
            Assert.IsNull(data.SimilarityA);
            Assert.IsNull(data.SimilarityB);
            Assert.IsNull(data.NaturalnessA);
            Assert.IsNull(data.NaturalnessB);
            Assert.IsNull(data.SnrDbA);
            Assert.IsNull(data.SnrDbB);
        }

        #endregion
    }
}
