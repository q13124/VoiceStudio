using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Collections.Generic;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Tests.ViewModels
{
    [TestClass]
    public class AutomationModelTests
    {
        #region AutomationPoint Model Tests

        [TestMethod]
        public void AutomationPoint_DefaultValues()
        {
            var point = new AutomationPoint();

            Assert.AreEqual(0.0, point.Time);
            Assert.AreEqual(0.0, point.Value);
            Assert.IsNull(point.BezierHandleInX);
            Assert.IsNull(point.BezierHandleInY);
            Assert.IsNull(point.BezierHandleOutX);
            Assert.IsNull(point.BezierHandleOutY);
        }

        [TestMethod]
        public void AutomationPoint_PropertiesSetCorrectly()
        {
            var point = new AutomationPoint
            {
                Time = 2.5,
                Value = 0.75,
                BezierHandleInX = -0.1,
                BezierHandleInY = -0.1,
                BezierHandleOutX = 0.1,
                BezierHandleOutY = 0.1
            };

            Assert.AreEqual(2.5, point.Time);
            Assert.AreEqual(0.75, point.Value);
            Assert.AreEqual(-0.1, point.BezierHandleInX);
            Assert.AreEqual(-0.1, point.BezierHandleInY);
            Assert.AreEqual(0.1, point.BezierHandleOutX);
            Assert.AreEqual(0.1, point.BezierHandleOutY);
        }

        [TestMethod]
        public void AutomationPoint_BezierHandlesOptional()
        {
            var point = new AutomationPoint
            {
                Time = 1.0,
                Value = 0.5
            };

            Assert.IsNull(point.BezierHandleInX);
            Assert.IsNull(point.BezierHandleOutX);
        }

        #endregion

        #region ParameterInfo Model Tests

        [TestMethod]
        public void ParameterInfo_DefaultValues()
        {
            var param = new ParameterInfo();

            Assert.AreEqual(string.Empty, param.Id);
            Assert.AreEqual(string.Empty, param.Name);
            Assert.AreEqual(0.0, param.Min);
            Assert.AreEqual(0.0, param.Max);
        }

        [TestMethod]
        public void ParameterInfo_PropertiesSetCorrectly()
        {
            var param = new ParameterInfo
            {
                Id = "volume",
                Name = "Volume",
                Min = 0.0,
                Max = 1.0
            };

            Assert.AreEqual("volume", param.Id);
            Assert.AreEqual("Volume", param.Name);
            Assert.AreEqual(0.0, param.Min);
            Assert.AreEqual(1.0, param.Max);
        }

        #endregion

        #region AutomationCurve Model Tests

        [TestMethod]
        public void AutomationCurve_DefaultValues()
        {
            var curve = new AutomationCurve();

            Assert.AreEqual(string.Empty, curve.Id);
            Assert.AreEqual(string.Empty, curve.Name);
            Assert.AreEqual(string.Empty, curve.ParameterId);
            Assert.AreEqual(string.Empty, curve.TrackId);
            Assert.IsNotNull(curve.Points);
            Assert.AreEqual(0, curve.Points.Count);
            Assert.AreEqual("linear", curve.Interpolation);
            Assert.AreEqual(string.Empty, curve.Created);
            Assert.AreEqual(string.Empty, curve.Modified);
        }

        [TestMethod]
        public void AutomationCurve_PropertiesSetCorrectly()
        {
            var points = new List<AutomationPoint>
            {
                new AutomationPoint { Time = 0, Value = 0 },
                new AutomationPoint { Time = 1, Value = 1 }
            };

            var curve = new AutomationCurve
            {
                Id = "curve1",
                Name = "Volume Curve",
                ParameterId = "volume",
                TrackId = "track1",
                Points = points,
                Interpolation = "bezier",
                Created = "2026-01-01",
                Modified = "2026-01-02"
            };

            Assert.AreEqual("curve1", curve.Id);
            Assert.AreEqual("Volume Curve", curve.Name);
            Assert.AreEqual("volume", curve.ParameterId);
            Assert.AreEqual("track1", curve.TrackId);
            Assert.AreSame(points, curve.Points);
            Assert.AreEqual("bezier", curve.Interpolation);
            Assert.AreEqual("2026-01-01", curve.Created);
            Assert.AreEqual("2026-01-02", curve.Modified);
        }

        #endregion

        #region AutomationCurveItem Model Tests

        [TestMethod]
        public void AutomationCurveItem_CreatedFromCurve()
        {
            var curve = new AutomationCurve
            {
                Id = "c1",
                Name = "Pan Curve",
                ParameterId = "pan",
                TrackId = "t1",
                Points = new List<AutomationPoint>
                {
                    new AutomationPoint { Time = 0, Value = 0.5 }
                },
                Interpolation = "linear"
            };

            var item = new AutomationCurveItem(curve);

            Assert.AreEqual("c1", item.Id);
            Assert.AreEqual("Pan Curve", item.Name);
            Assert.AreEqual("pan", item.ParameterId);
            Assert.AreEqual("t1", item.TrackId);
            Assert.AreEqual(1, item.Points.Count);
            Assert.AreEqual("linear", item.Interpolation);
        }

        [TestMethod]
        public void AutomationCurveItem_PointCount_ReturnsCorrectCount()
        {
            var curve = new AutomationCurve
            {
                Points = new List<AutomationPoint>
                {
                    new AutomationPoint(),
                    new AutomationPoint(),
                    new AutomationPoint()
                }
            };
            var item = new AutomationCurveItem(curve);

            Assert.AreEqual(3, item.PointCount);
        }

        [TestMethod]
        public void AutomationCurveItem_PointCount_ZeroWhenEmpty()
        {
            var curve = new AutomationCurve { Points = new List<AutomationPoint>() };
            var item = new AutomationCurveItem(curve);

            Assert.AreEqual(0, item.PointCount);
        }

        [TestMethod]
        public void AutomationCurveItem_UpdateFrom_UpdatesProperties()
        {
            var original = new AutomationCurve
            {
                Id = "c1",
                Name = "Original",
                Points = new List<AutomationPoint> { new AutomationPoint() },
                Interpolation = "linear"
            };
            var item = new AutomationCurveItem(original);

            var updated = new AutomationCurve
            {
                Name = "Updated",
                Points = new List<AutomationPoint>
                {
                    new AutomationPoint(),
                    new AutomationPoint(),
                    new AutomationPoint()
                },
                Interpolation = "bezier"
            };
            item.UpdateFrom(updated);

            Assert.AreEqual("Updated", item.Name);
            Assert.AreEqual(3, item.Points.Count);
            Assert.AreEqual(3, item.PointCount);
            Assert.AreEqual("bezier", item.Interpolation);
            // Id should not change
            Assert.AreEqual("c1", item.Id);
        }

        [TestMethod]
        public void AutomationCurveItem_NullPointsHandled()
        {
            var curve = new AutomationCurve
            {
                Id = "c1",
                Points = null!
            };

            var item = new AutomationCurveItem(curve);

            Assert.IsNotNull(item.Points);
            Assert.AreEqual(0, item.PointCount);
        }

        #endregion
    }
}
