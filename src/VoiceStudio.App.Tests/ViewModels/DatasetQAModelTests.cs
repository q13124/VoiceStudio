using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Tests.ViewModels
{
    [TestClass]
    public class DatasetQAModelTests
    {
        #region DatasetQAReport Model Tests

        [TestMethod]
        public void DatasetQAReport_DefaultValues()
        {
            var report = new DatasetQAReport();

            Assert.AreEqual(string.Empty, report.DatasetId);
            Assert.AreEqual(0, report.TotalClips);
            Assert.AreEqual(0, report.PassingClips);
            Assert.AreEqual(0, report.FailingClips);
            Assert.AreEqual(0.0, report.AverageQuality);
            Assert.AreEqual(0.0, report.AverageSnr);
            Assert.AreEqual(0.0, report.AverageLufs);
        }

        [TestMethod]
        public void DatasetQAReport_PropertiesSetCorrectly()
        {
            var generatedAt = DateTime.UtcNow;
            var report = new DatasetQAReport
            {
                DatasetId = "dataset123",
                TotalClips = 100,
                PassingClips = 85,
                FailingClips = 15,
                AverageQuality = 4.2,
                AverageSnr = 35.5,
                AverageLufs = -14.0,
                GeneratedAt = generatedAt
            };

            Assert.AreEqual("dataset123", report.DatasetId);
            Assert.AreEqual(100, report.TotalClips);
            Assert.AreEqual(85, report.PassingClips);
            Assert.AreEqual(15, report.FailingClips);
            Assert.AreEqual(4.2, report.AverageQuality);
            Assert.AreEqual(35.5, report.AverageSnr);
            Assert.AreEqual(-14.0, report.AverageLufs);
            Assert.AreEqual(generatedAt, report.GeneratedAt);
        }

        [TestMethod]
        public void DatasetQAReport_PassRateDisplay_CalculatesCorrectly()
        {
            var report = new DatasetQAReport
            {
                TotalClips = 100,
                PassingClips = 85
            };

            Assert.AreEqual("85/100 (85.0%)", report.PassRateDisplay);
        }

        [TestMethod]
        public void DatasetQAReport_PassRateDisplay_ZeroTotal()
        {
            var report = new DatasetQAReport
            {
                TotalClips = 0,
                PassingClips = 0
            };

            Assert.AreEqual("0/0 (0%)", report.PassRateDisplay);
        }

        [TestMethod]
        public void DatasetQAReport_AverageQualityDisplay_FormatsCorrectly()
        {
            var report = new DatasetQAReport { AverageQuality = 4.567 };
            Assert.AreEqual("4.57", report.AverageQualityDisplay);
        }

        [TestMethod]
        public void DatasetQAReport_AverageSnrDisplay_FormatsWithDb()
        {
            var report = new DatasetQAReport { AverageSnr = 35.5 };
            Assert.AreEqual("35.5 dB", report.AverageSnrDisplay);
        }

        [TestMethod]
        public void DatasetQAReport_AverageLufsDisplay_FormatsWithLufs()
        {
            var report = new DatasetQAReport { AverageLufs = -14.0 };
            Assert.AreEqual("-14.0 LUFS", report.AverageLufsDisplay);
        }

        #endregion

        #region DatasetQAClipResult Model Tests

        [TestMethod]
        public void DatasetQAClipResult_DefaultValues()
        {
            var result = new DatasetQAClipResult();

            Assert.AreEqual(string.Empty, result.ClipId);
            Assert.AreEqual(0.0, result.Snr);
            Assert.AreEqual(0.0, result.Lufs);
            Assert.AreEqual(0.0, result.Quality);
            Assert.IsFalse(result.PassesQuality);
            Assert.IsFalse(result.PassesSnr);
            Assert.IsFalse(result.PassesLufs);
            Assert.IsFalse(result.PassesAll);
        }

        [TestMethod]
        public void DatasetQAClipResult_PropertiesSetCorrectly()
        {
            var result = new DatasetQAClipResult
            {
                ClipId = "clip123",
                Snr = 40.5,
                Lufs = -16.0,
                Quality = 4.8,
                PassesQuality = true,
                PassesSnr = true,
                PassesLufs = true,
                PassesAll = true
            };

            Assert.AreEqual("clip123", result.ClipId);
            Assert.AreEqual(40.5, result.Snr);
            Assert.AreEqual(-16.0, result.Lufs);
            Assert.AreEqual(4.8, result.Quality);
            Assert.IsTrue(result.PassesQuality);
            Assert.IsTrue(result.PassesSnr);
            Assert.IsTrue(result.PassesLufs);
            Assert.IsTrue(result.PassesAll);
        }

        [TestMethod]
        public void DatasetQAClipResult_SnrDisplay_FormatsWithDb()
        {
            var result = new DatasetQAClipResult { Snr = 35.7 };
            Assert.AreEqual("35.7 dB", result.SnrDisplay);
        }

        [TestMethod]
        public void DatasetQAClipResult_LufsDisplay_FormatsWithLufs()
        {
            var result = new DatasetQAClipResult { Lufs = -23.5 };
            Assert.AreEqual("-23.5 LUFS", result.LufsDisplay);
        }

        [TestMethod]
        public void DatasetQAClipResult_QualityDisplay_FormatsCorrectly()
        {
            var result = new DatasetQAClipResult { Quality = 3.45 };
            Assert.AreEqual("3.45", result.QualityDisplay);
        }

        [TestMethod]
        public void DatasetQAClipResult_StatusDisplay_PassWhenPassesAll()
        {
            var result = new DatasetQAClipResult { PassesAll = true };
            Assert.AreEqual("Pass", result.StatusDisplay);
        }

        [TestMethod]
        public void DatasetQAClipResult_StatusDisplay_FailWhenNotPassesAll()
        {
            var result = new DatasetQAClipResult { PassesAll = false };
            Assert.AreEqual("Fail", result.StatusDisplay);
        }

        [TestMethod]
        public void DatasetQAClipResult_IndividualPassFlags()
        {
            var result = new DatasetQAClipResult
            {
                PassesQuality = true,
                PassesSnr = false,
                PassesLufs = true,
                PassesAll = false
            };

            Assert.IsTrue(result.PassesQuality);
            Assert.IsFalse(result.PassesSnr);
            Assert.IsTrue(result.PassesLufs);
            Assert.IsFalse(result.PassesAll);
        }

        #endregion
    }
}
