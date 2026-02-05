using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Tests.Services
{
    /// <summary>
    /// Unit tests for ErrorCoordinator service.
    /// Tests centralized error handling, logging, and dialog coordination.
    /// </summary>
    [TestClass]
    public class ErrorCoordinatorTests
    {
        private Mock<IErrorLoggingService> _mockLoggingService = null!;
        private Mock<IErrorDialogService> _mockDialogService = null!;
        private ErrorCoordinator _sut = null!;

        [TestInitialize]
        public void Setup()
        {
            _mockLoggingService = new Mock<IErrorLoggingService>();
            _mockDialogService = new Mock<IErrorDialogService>();
            _sut = new ErrorCoordinator(_mockLoggingService.Object, _mockDialogService.Object);
        }

        #region Initial State Tests

        [TestMethod]
        public void Constructor_WithNullServices_DoesNotThrow()
        {
            // Act - should not throw
            var coordinator = new ErrorCoordinator(null, null);

            // Assert
            Assert.IsNotNull(coordinator);
            Assert.IsFalse(coordinator.HasError);
            Assert.IsNull(coordinator.CurrentError);
        }

        [TestMethod]
        public void InitialState_HasNoError()
        {
            // Assert
            Assert.IsFalse(_sut.HasError);
        }

        [TestMethod]
        public void InitialState_CurrentError_IsNull()
        {
            // Assert
            Assert.IsNull(_sut.CurrentError);
        }

        #endregion

        #region HandleErrorAsync Tests

        [TestMethod]
        public async Task HandleErrorAsync_WithNullException_DoesNothing()
        {
            // Arrange
            Exception? nullException = null;

            // Act
            await _sut.HandleErrorAsync(nullException!, "context");

            // Assert
            Assert.IsFalse(_sut.HasError);
            _mockLoggingService.Verify(x => x.LogError(It.IsAny<Exception>(), It.IsAny<string>(), It.IsAny<Dictionary<string, object>?>()), Times.Never);
        }

        [TestMethod]
        public async Task HandleErrorAsync_SetsHasError_ToTrue()
        {
            // Arrange
            var exception = new InvalidOperationException("Test error");

            // Act
            await _sut.HandleErrorAsync(exception, "TestContext");

            // Assert
            Assert.IsTrue(_sut.HasError);
        }

        [TestMethod]
        public async Task HandleErrorAsync_SetsCurrentError()
        {
            // Arrange
            var exception = new InvalidOperationException("Test error message");

            // Act
            await _sut.HandleErrorAsync(exception, "TestContext");

            // Assert
            Assert.IsNotNull(_sut.CurrentError);
        }

        [TestMethod]
        public async Task HandleErrorAsync_LogsErrorViaLoggingService()
        {
            // Arrange
            var exception = new InvalidOperationException("Test error");

            // Act
            await _sut.HandleErrorAsync(exception, "TestContext");

            // Assert
            _mockLoggingService.Verify(x => x.LogError(exception, "TestContext", It.IsAny<Dictionary<string, object>?>()), Times.Once);
        }

        [TestMethod]
        public async Task HandleErrorAsync_WithShowDialog_CallsDialogService()
        {
            // Arrange
            var exception = new InvalidOperationException("Test error");
            _mockDialogService.Setup(x => x.ShowErrorAsync(It.IsAny<Exception>(), It.IsAny<string?>(), It.IsAny<string?>()))
                .Returns(Task.CompletedTask);

            // Act
            await _sut.HandleErrorAsync(exception, "TestContext", showDialog: true);

            // Assert
            _mockDialogService.Verify(x => x.ShowErrorAsync(exception, "TestContext", It.IsAny<string?>()), Times.Once);
        }

        [TestMethod]
        public async Task HandleErrorAsync_WithoutShowDialog_DoesNotCallDialogService()
        {
            // Arrange
            var exception = new InvalidOperationException("Test error");

            // Act
            await _sut.HandleErrorAsync(exception, "TestContext", showDialog: false);

            // Assert
            _mockDialogService.Verify(x => x.ShowErrorAsync(It.IsAny<Exception>(), It.IsAny<string?>(), It.IsAny<string?>()), Times.Never);
        }

        [TestMethod]
        public async Task HandleErrorAsync_RaisesErrorOccurredEvent()
        {
            // Arrange
            var exception = new InvalidOperationException("Test error");
            ErrorInfo? raisedInfo = null;
            _sut.ErrorOccurred += info => raisedInfo = info;

            // Act
            await _sut.HandleErrorAsync(exception, "TestContext", ErrorSeverity.Warning);

            // Assert
            Assert.IsNotNull(raisedInfo);
            Assert.AreEqual(exception, raisedInfo.Exception);
            Assert.AreEqual("TestContext", raisedInfo.Context);
            Assert.AreEqual(ErrorSeverity.Warning, raisedInfo.Severity);
        }

        [TestMethod]
        public async Task HandleErrorAsync_DefaultSeverity_IsError()
        {
            // Arrange
            var exception = new InvalidOperationException("Test error");
            ErrorInfo? raisedInfo = null;
            _sut.ErrorOccurred += info => raisedInfo = info;

            // Act
            await _sut.HandleErrorAsync(exception, "TestContext");

            // Assert
            Assert.IsNotNull(raisedInfo);
            Assert.AreEqual(ErrorSeverity.Error, raisedInfo.Severity);
        }

        [TestMethod]
        public async Task HandleErrorAsync_WhenLoggingServiceThrows_ContinuesWithoutThrowing()
        {
            // Arrange
            var exception = new InvalidOperationException("Test error");
            _mockLoggingService.Setup(x => x.LogError(It.IsAny<Exception>(), It.IsAny<string>(), It.IsAny<Dictionary<string, object>?>()))
                .Throws(new Exception("Logging failed"));

            // Act - should not throw
            await _sut.HandleErrorAsync(exception, "TestContext");

            // Assert
            Assert.IsTrue(_sut.HasError); // Error state should still be set
        }

        [TestMethod]
        public async Task HandleErrorAsync_WhenDialogServiceThrows_ContinuesWithoutThrowing()
        {
            // Arrange
            var exception = new InvalidOperationException("Test error");
            _mockDialogService.Setup(x => x.ShowErrorAsync(It.IsAny<Exception>(), It.IsAny<string?>(), It.IsAny<string?>()))
                .Throws(new Exception("Dialog failed"));

            // Act - should not throw
            await _sut.HandleErrorAsync(exception, "TestContext", showDialog: true);

            // Assert
            Assert.IsTrue(_sut.HasError);
        }

        #endregion

        #region ClearError Tests

        [TestMethod]
        public async Task ClearError_SetsHasError_ToFalse()
        {
            // Arrange
            var exception = new InvalidOperationException("Test error");
            await _sut.HandleErrorAsync(exception, "TestContext");
            Assert.IsTrue(_sut.HasError);

            // Act
            _sut.ClearError();

            // Assert
            Assert.IsFalse(_sut.HasError);
        }

        [TestMethod]
        public async Task ClearError_SetsCurrentError_ToNull()
        {
            // Arrange
            var exception = new InvalidOperationException("Test error");
            await _sut.HandleErrorAsync(exception, "TestContext");
            Assert.IsNotNull(_sut.CurrentError);

            // Act
            _sut.ClearError();

            // Assert
            Assert.IsNull(_sut.CurrentError);
        }

        [TestMethod]
        public async Task ClearError_RaisesErrorClearedEvent()
        {
            // Arrange
            var exception = new InvalidOperationException("Test error");
            await _sut.HandleErrorAsync(exception, "TestContext");
            bool eventRaised = false;
            _sut.ErrorCleared += () => eventRaised = true;

            // Act
            _sut.ClearError();

            // Assert
            Assert.IsTrue(eventRaised);
        }

        [TestMethod]
        public void ClearError_WhenNoError_StillRaisesEvent()
        {
            // Arrange
            bool eventRaised = false;
            _sut.ErrorCleared += () => eventRaised = true;

            // Act
            _sut.ClearError();

            // Assert
            Assert.IsTrue(eventRaised);
        }

        #endregion

        #region Thread Safety Tests

        [TestMethod]
        public async Task MultipleHandleErrorAsync_ThreadSafe()
        {
            // Arrange
            var tasks = new Task[10];
            for (int i = 0; i < 10; i++)
            {
                var exception = new InvalidOperationException($"Error {i}");
                tasks[i] = _sut.HandleErrorAsync(exception, $"Context{i}");
            }

            // Act
            await Task.WhenAll(tasks);

            // Assert - Should not throw and should have error state
            Assert.IsTrue(_sut.HasError);
            Assert.IsNotNull(_sut.CurrentError);
        }

        #endregion

        #region Error Severity Tests

        [TestMethod]
        public async Task HandleErrorAsync_CriticalSeverity_IsPreserved()
        {
            // Arrange
            var exception = new InvalidOperationException("Critical error");
            ErrorInfo? raisedInfo = null;
            _sut.ErrorOccurred += info => raisedInfo = info;

            // Act
            await _sut.HandleErrorAsync(exception, "CriticalContext", ErrorSeverity.Critical);

            // Assert
            Assert.IsNotNull(raisedInfo);
            Assert.AreEqual(ErrorSeverity.Critical, raisedInfo.Severity);
        }

        [TestMethod]
        public async Task HandleErrorAsync_WarningSeverity_IsPreserved()
        {
            // Arrange
            var exception = new InvalidOperationException("Warning");
            ErrorInfo? raisedInfo = null;
            _sut.ErrorOccurred += info => raisedInfo = info;

            // Act
            await _sut.HandleErrorAsync(exception, "WarningContext", ErrorSeverity.Warning);

            // Assert
            Assert.IsNotNull(raisedInfo);
            Assert.AreEqual(ErrorSeverity.Warning, raisedInfo.Severity);
        }

        #endregion
    }
}
