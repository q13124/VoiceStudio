using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Collections.Generic;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Tests.Services
{
    /// <summary>
    /// Unit tests for GracefulDegradationService.
    /// Tests feature degradation, enable/disable, and event handling.
    /// </summary>
    [TestClass]
    public class GracefulDegradationServiceTests
    {
        private GracefulDegradationService _sut = null!;

        [TestInitialize]
        public void Setup()
        {
            _sut = new GracefulDegradationService();
        }

        #region Initial State Tests

        [TestMethod]
        public void Constructor_InitialState_NotDegraded()
        {
            // Assert
            Assert.IsFalse(_sut.IsDegradedMode);
        }

        [TestMethod]
        public void Constructor_InitialState_NoDisabledFeatures()
        {
            // Assert
            Assert.AreEqual(0, _sut.DisabledFeatures.Count);
        }

        [TestMethod]
        public void Constructor_InitialState_NoDegradationReason()
        {
            // Assert
            Assert.IsNull(_sut.DegradationReason);
        }

        #endregion

        #region EnterDegradedMode Tests

        [TestMethod]
        public void EnterDegradedMode_SetsDegradedMode_True()
        {
            // Act
            _sut.EnterDegradedMode("Test reason");

            // Assert
            Assert.IsTrue(_sut.IsDegradedMode);
        }

        [TestMethod]
        public void EnterDegradedMode_SetsDegradationReason()
        {
            // Act
            _sut.EnterDegradedMode("Backend connection lost");

            // Assert
            Assert.AreEqual("Backend connection lost", _sut.DegradationReason);
        }

        [TestMethod]
        public void EnterDegradedMode_DisablesSpecifiedFeatures()
        {
            // Act
            _sut.EnterDegradedMode("Test", "Feature1", "Feature2", "Feature3");

            // Assert
            Assert.IsTrue(_sut.DisabledFeatures.Contains("Feature1"));
            Assert.IsTrue(_sut.DisabledFeatures.Contains("Feature2"));
            Assert.IsTrue(_sut.DisabledFeatures.Contains("Feature3"));
            Assert.AreEqual(3, _sut.DisabledFeatures.Count);
        }

        [TestMethod]
        public void EnterDegradedMode_RaisesDegradedModeChangedEvent()
        {
            // Arrange
            bool eventRaised = false;
            bool eventValue = false;
            _sut.DegradedModeChanged += (sender, isDegraded) =>
            {
                eventRaised = true;
                eventValue = isDegraded;
            };

            // Act
            _sut.EnterDegradedMode("Test");

            // Assert
            Assert.IsTrue(eventRaised);
            Assert.IsTrue(eventValue);
        }

        [TestMethod]
        public void EnterDegradedMode_RaisesFeatureDisabledEvents()
        {
            // Arrange
            var disabledFeatures = new List<string>();
            _sut.FeatureDisabled += (sender, feature) => disabledFeatures.Add(feature);

            // Act
            _sut.EnterDegradedMode("Test", "FeatureA", "FeatureB");

            // Assert
            Assert.AreEqual(2, disabledFeatures.Count);
            Assert.IsTrue(disabledFeatures.Contains("FeatureA"));
            Assert.IsTrue(disabledFeatures.Contains("FeatureB"));
        }

        [TestMethod]
        public void EnterDegradedMode_WithNoFeatures_StillEntersDegradedMode()
        {
            // Act
            _sut.EnterDegradedMode("Minimal degradation");

            // Assert
            Assert.IsTrue(_sut.IsDegradedMode);
            Assert.AreEqual(0, _sut.DisabledFeatures.Count);
        }

        #endregion

        #region ExitDegradedMode Tests

        [TestMethod]
        public void ExitDegradedMode_SetsDegradedMode_False()
        {
            // Arrange
            _sut.EnterDegradedMode("Test");

            // Act
            _sut.ExitDegradedMode();

            // Assert
            Assert.IsFalse(_sut.IsDegradedMode);
        }

        [TestMethod]
        public void ExitDegradedMode_ClearsDegradationReason()
        {
            // Arrange
            _sut.EnterDegradedMode("Some reason");

            // Act
            _sut.ExitDegradedMode();

            // Assert
            Assert.IsNull(_sut.DegradationReason);
        }

        [TestMethod]
        public void ExitDegradedMode_ReEnablesAllFeatures()
        {
            // Arrange
            _sut.EnterDegradedMode("Test", "Feature1", "Feature2");
            Assert.AreEqual(2, _sut.DisabledFeatures.Count);

            // Act
            _sut.ExitDegradedMode();

            // Assert
            Assert.AreEqual(0, _sut.DisabledFeatures.Count);
        }

        [TestMethod]
        public void ExitDegradedMode_RaisesDegradedModeChangedEvent()
        {
            // Arrange
            _sut.EnterDegradedMode("Test");
            bool eventRaised = false;
            bool eventValue = true;
            _sut.DegradedModeChanged += (sender, isDegraded) =>
            {
                eventRaised = true;
                eventValue = isDegraded;
            };

            // Act
            _sut.ExitDegradedMode();

            // Assert
            Assert.IsTrue(eventRaised);
            Assert.IsFalse(eventValue);
        }

        [TestMethod]
        public void ExitDegradedMode_RaisesFeatureEnabledEvents()
        {
            // Arrange
            _sut.EnterDegradedMode("Test", "FeatureA", "FeatureB");
            var enabledFeatures = new List<string>();
            _sut.FeatureEnabled += (sender, feature) => enabledFeatures.Add(feature);

            // Act
            _sut.ExitDegradedMode();

            // Assert
            Assert.AreEqual(2, enabledFeatures.Count);
            Assert.IsTrue(enabledFeatures.Contains("FeatureA"));
            Assert.IsTrue(enabledFeatures.Contains("FeatureB"));
        }

        [TestMethod]
        public void ExitDegradedMode_WhenNotDegraded_DoesNotRaiseDegradedModeChangedEvent()
        {
            // Arrange
            bool eventRaised = false;
            _sut.DegradedModeChanged += (sender, isDegraded) => eventRaised = true;

            // Act
            _sut.ExitDegradedMode();

            // Assert
            Assert.IsFalse(eventRaised);
        }

        #endregion

        #region DisableFeature Tests

        [TestMethod]
        public void DisableFeature_AddsFeatureToDisabledSet()
        {
            // Act
            _sut.DisableFeature("SomeFeature");

            // Assert
            Assert.IsTrue(_sut.DisabledFeatures.Contains("SomeFeature"));
        }

        [TestMethod]
        public void DisableFeature_RaisesFeatureDisabledEvent()
        {
            // Arrange
            string? disabledFeature = null;
            _sut.FeatureDisabled += (sender, feature) => disabledFeature = feature;

            // Act
            _sut.DisableFeature("TestFeature");

            // Assert
            Assert.AreEqual("TestFeature", disabledFeature);
        }

        [TestMethod]
        public void DisableFeature_WhenAlreadyDisabled_DoesNotRaiseEvent()
        {
            // Arrange
            _sut.DisableFeature("TestFeature");
            int eventCount = 0;
            _sut.FeatureDisabled += (sender, feature) => eventCount++;

            // Act
            _sut.DisableFeature("TestFeature");

            // Assert
            Assert.AreEqual(0, eventCount); // No new event for already disabled feature
        }

        #endregion

        #region EnableFeature Tests

        [TestMethod]
        public void EnableFeature_RemovesFeatureFromDisabledSet()
        {
            // Arrange
            _sut.DisableFeature("SomeFeature");
            Assert.IsTrue(_sut.DisabledFeatures.Contains("SomeFeature"));

            // Act
            _sut.EnableFeature("SomeFeature");

            // Assert
            Assert.IsFalse(_sut.DisabledFeatures.Contains("SomeFeature"));
        }

        [TestMethod]
        public void EnableFeature_RaisesFeatureEnabledEvent()
        {
            // Arrange
            _sut.DisableFeature("TestFeature");
            string? enabledFeature = null;
            _sut.FeatureEnabled += (sender, feature) => enabledFeature = feature;

            // Act
            _sut.EnableFeature("TestFeature");

            // Assert
            Assert.AreEqual("TestFeature", enabledFeature);
        }

        [TestMethod]
        public void EnableFeature_WhenNotDisabled_DoesNotRaiseEvent()
        {
            // Arrange
            int eventCount = 0;
            _sut.FeatureEnabled += (sender, feature) => eventCount++;

            // Act
            _sut.EnableFeature("NeverDisabledFeature");

            // Assert
            Assert.AreEqual(0, eventCount);
        }

        #endregion

        #region IsFeatureEnabled Tests

        [TestMethod]
        public void IsFeatureEnabled_WhenNotDisabled_ReturnsTrue()
        {
            // Assert
            Assert.IsTrue(_sut.IsFeatureEnabled("AnyFeature"));
        }

        [TestMethod]
        public void IsFeatureEnabled_WhenDisabled_ReturnsFalse()
        {
            // Arrange
            _sut.DisableFeature("DisabledFeature");

            // Assert
            Assert.IsFalse(_sut.IsFeatureEnabled("DisabledFeature"));
        }

        [TestMethod]
        public void IsFeatureEnabled_AfterReEnable_ReturnsTrue()
        {
            // Arrange
            _sut.DisableFeature("Feature");
            _sut.EnableFeature("Feature");

            // Assert
            Assert.IsTrue(_sut.IsFeatureEnabled("Feature"));
        }

        [TestMethod]
        public void IsFeatureEnabled_AfterExitDegradedMode_ReturnsTrue()
        {
            // Arrange
            _sut.EnterDegradedMode("Test", "FeatureX");
            Assert.IsFalse(_sut.IsFeatureEnabled("FeatureX"));

            // Act
            _sut.ExitDegradedMode();

            // Assert
            Assert.IsTrue(_sut.IsFeatureEnabled("FeatureX"));
        }

        #endregion

        #region Edge Cases

        [TestMethod]
        public void EnterDegradedMode_MultipleTimes_UpdatesReason()
        {
            // Arrange
            _sut.EnterDegradedMode("First reason", "FeatureA");

            // Act
            _sut.EnterDegradedMode("Second reason", "FeatureB");

            // Assert
            Assert.AreEqual("Second reason", _sut.DegradationReason);
            Assert.IsTrue(_sut.DisabledFeatures.Contains("FeatureA"));
            Assert.IsTrue(_sut.DisabledFeatures.Contains("FeatureB"));
        }

        [TestMethod]
        public void DisabledFeatures_IsCasePreserving()
        {
            // Act
            _sut.DisableFeature("FeatureA");
            _sut.DisableFeature("featurea"); // Different case

            // Assert - Both should be added as separate entries
            Assert.IsTrue(_sut.DisabledFeatures.Contains("FeatureA"));
            Assert.IsTrue(_sut.DisabledFeatures.Contains("featurea"));
        }

        [TestMethod]
        public void DisableFeature_EmptyString_IsAllowed()
        {
            // Act
            _sut.DisableFeature("");

            // Assert
            Assert.IsTrue(_sut.DisabledFeatures.Contains(""));
        }

        #endregion
    }
}
