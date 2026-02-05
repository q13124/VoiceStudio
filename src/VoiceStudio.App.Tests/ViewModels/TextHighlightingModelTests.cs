using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Collections.Generic;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Tests.ViewModels
{
    [TestClass]
    public class TextHighlightingModelTests
    {
        #region HighlightTextSegment Model Tests

        [TestMethod]
        public void HighlightTextSegment_DefaultValues()
        {
            var segment = new HighlightTextSegment();

            Assert.AreEqual(string.Empty, segment.Id);
            Assert.AreEqual(string.Empty, segment.Text);
            Assert.AreEqual(0.0, segment.StartTime);
            Assert.AreEqual(0.0, segment.EndTime);
            Assert.IsNull(segment.WordTimings);
        }

        [TestMethod]
        public void HighlightTextSegment_PropertiesSetCorrectly()
        {
            var wordTimings = new Dictionary<string, object>[]
            {
                new Dictionary<string, object> { { "word", "hello" }, { "start", 0.0 } },
                new Dictionary<string, object> { { "word", "world" }, { "start", 0.5 } }
            };

            var segment = new HighlightTextSegment
            {
                Id = "seg1",
                Text = "Hello world",
                StartTime = 0.0,
                EndTime = 1.0,
                WordTimings = wordTimings
            };

            Assert.AreEqual("seg1", segment.Id);
            Assert.AreEqual("Hello world", segment.Text);
            Assert.AreEqual(0.0, segment.StartTime);
            Assert.AreEqual(1.0, segment.EndTime);
            Assert.AreSame(wordTimings, segment.WordTimings);
        }

        #endregion

        #region HighlightTextSegmentItem Model Tests

        [TestMethod]
        public void HighlightTextSegmentItem_CreatedFromSegment()
        {
            var segment = new HighlightTextSegment
            {
                Id = "seg1",
                Text = "Test text",
                StartTime = 1.5,
                EndTime = 3.0,
                WordTimings = new Dictionary<string, object>[0]
            };

            var item = new HighlightTextSegmentItem(segment);

            Assert.AreEqual("seg1", item.Id);
            Assert.AreEqual("Test text", item.Text);
            Assert.AreEqual(1.5, item.StartTime);
            Assert.AreEqual(3.0, item.EndTime);
            Assert.IsNotNull(item.WordTimings);
        }

        [TestMethod]
        public void HighlightTextSegmentItem_DefaultHighlightType()
        {
            var segment = new HighlightTextSegment { Id = "s1" };
            var item = new HighlightTextSegmentItem(segment);

            Assert.AreEqual("word", item.HighlightType);
        }

        [TestMethod]
        public void HighlightTextSegmentItem_HighlightTypeCanBeChanged()
        {
            var segment = new HighlightTextSegment { Id = "s1" };
            var item = new HighlightTextSegmentItem(segment);

            item.HighlightType = "sentence";
            Assert.AreEqual("sentence", item.HighlightType);
        }

        [TestMethod]
        public void HighlightTextSegmentItem_TimeRangeDisplay_FormatsCorrectly()
        {
            var segment = new HighlightTextSegment
            {
                StartTime = 1.25,
                EndTime = 3.50
            };
            var item = new HighlightTextSegmentItem(segment);

            Assert.AreEqual("1.25s - 3.50s", item.TimeRangeDisplay);
        }

        [TestMethod]
        public void HighlightTextSegmentItem_TimeRangeDisplay_ZeroTimes()
        {
            var segment = new HighlightTextSegment
            {
                StartTime = 0,
                EndTime = 0
            };
            var item = new HighlightTextSegmentItem(segment);

            Assert.AreEqual("0.00s - 0.00s", item.TimeRangeDisplay);
        }

        [TestMethod]
        public void HighlightTextSegmentItem_DurationDisplay_CalculatesCorrectly()
        {
            var segment = new HighlightTextSegment
            {
                StartTime = 1.0,
                EndTime = 3.5
            };
            var item = new HighlightTextSegmentItem(segment);

            Assert.AreEqual("2.50s", item.DurationDisplay);
        }

        [TestMethod]
        public void HighlightTextSegmentItem_DurationDisplay_ZeroDuration()
        {
            var segment = new HighlightTextSegment
            {
                StartTime = 2.0,
                EndTime = 2.0
            };
            var item = new HighlightTextSegmentItem(segment);

            Assert.AreEqual("0.00s", item.DurationDisplay);
        }

        #endregion
    }
}
