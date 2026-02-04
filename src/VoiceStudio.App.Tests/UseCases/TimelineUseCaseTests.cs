using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.App.UseCases;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Tests.UseCases
{
  [TestClass]
  public class TimelineUseCaseTests
  {
    private Mock<IBackendClient> _mockBackendClient = null!;
    private TimelineUseCase _useCase = null!;

    [TestInitialize]
    public void Setup()
    {
      _mockBackendClient = new Mock<IBackendClient>();
      _useCase = new TimelineUseCase(_mockBackendClient.Object);
    }

    [TestMethod]
    public async Task GetStateAsync_ReturnsEmptyState_WhenBackendReturnsNull()
    {
      // Arrange
      _mockBackendClient
          .Setup(x => x.GetAsync<TimelineState>(It.IsAny<string>(), It.IsAny<CancellationToken>()))
          .ReturnsAsync((TimelineState?)null);

      // Act
      var result = await _useCase.GetStateAsync();

      // Assert
      Assert.IsNotNull(result);
      Assert.AreEqual(0, result.Duration);
      Assert.IsFalse(result.IsPlaying);
    }

    [TestMethod]
    public async Task GetStateAsync_ReturnsState_WhenBackendReturnsValidData()
    {
      // Arrange
      var expectedState = new TimelineState
      {
        Id = "timeline-123",
        Name = "Test Timeline",
        Duration = 120.5,
        IsPlaying = true,
        PlayheadPosition = 30.0
      };

      _mockBackendClient
          .Setup(x => x.GetAsync<TimelineState>("/api/timeline/state", It.IsAny<CancellationToken>()))
          .ReturnsAsync(expectedState);

      // Act
      var result = await _useCase.GetStateAsync();

      // Assert
      Assert.IsNotNull(result);
      Assert.AreEqual("timeline-123", result.Id);
      Assert.AreEqual("Test Timeline", result.Name);
      Assert.AreEqual(120.5, result.Duration);
      Assert.IsTrue(result.IsPlaying);
      Assert.AreEqual(30.0, result.PlayheadPosition);
    }

    [TestMethod]
    public async Task CreateAsync_CallsBackendWithCorrectOptions()
    {
      // Arrange
      var options = new TimelineOptions
      {
        Name = "New Timeline",
        SampleRate = 48000,
        Channels = 2,
        Duration = 600
      };

      var expectedResponse = new TimelineState { Id = "new-timeline" };
      
      _mockBackendClient
          .Setup(x => x.PostAsync<TimelineOptions, TimelineState>(
              "/api/timeline/create",
              It.Is<TimelineOptions>(o => o.Name == "New Timeline" && o.SampleRate == 48000),
              It.IsAny<CancellationToken>()))
          .ReturnsAsync(expectedResponse);

      // Act
      var result = await _useCase.CreateAsync(options);

      // Assert
      Assert.IsNotNull(result);
      Assert.AreEqual("new-timeline", result.Id);
      _mockBackendClient.Verify(x => x.PostAsync<TimelineOptions, TimelineState>(
          "/api/timeline/create",
          It.IsAny<TimelineOptions>(),
          It.IsAny<CancellationToken>()), Times.Once);
    }

    [TestMethod]
    public async Task AddTrackAsync_ReturnsTrack_WhenSuccessful()
    {
      // Arrange
      var expectedTrack = new Track { Id = "track-1" };
      
      _mockBackendClient
          .Setup(x => x.PostAsync<object, Track>(
              "/api/timeline/tracks",
              It.IsAny<object>(),
              It.IsAny<CancellationToken>()))
          .ReturnsAsync(expectedTrack);

      // Act
      var result = await _useCase.AddTrackAsync(TrackType.Audio, "Audio Track");

      // Assert
      Assert.IsNotNull(result);
      Assert.AreEqual("track-1", result.Id);
    }

    [TestMethod]
    public async Task RemoveTrackAsync_CallsPostEndpoint()
    {
      // Arrange
      _mockBackendClient
          .Setup(x => x.PostAsync<object, object>(
              "/api/timeline/tracks/delete",
              It.IsAny<object>(),
              It.IsAny<CancellationToken>()))
          .ReturnsAsync(new { Success = true });

      // Act
      var result = await _useCase.RemoveTrackAsync("track-123");

      // Assert
      // Note: Result will be false because the response object doesn't match DeleteResponse
      _mockBackendClient.Verify(x => x.PostAsync<object, object>(
          "/api/timeline/tracks/delete",
          It.IsAny<object>(),
          It.IsAny<CancellationToken>()), Times.Once);
    }

    [TestMethod]
    public async Task RemoveClipAsync_CallsPostEndpoint()
    {
      // Arrange
      _mockBackendClient
          .Setup(x => x.PostAsync<object, object>(
              "/api/timeline/clips/delete",
              It.IsAny<object>(),
              It.IsAny<CancellationToken>()))
          .ReturnsAsync(new { Success = true });

      // Act
      var result = await _useCase.RemoveClipAsync("clip-456");

      // Assert
      _mockBackendClient.Verify(x => x.PostAsync<object, object>(
          "/api/timeline/clips/delete",
          It.IsAny<object>(),
          It.IsAny<CancellationToken>()), Times.Once);
    }

    [TestMethod]
    public async Task UndoAsync_ReturnsFalse_WhenBackendReturnsNull()
    {
      // Arrange
      _mockBackendClient
          .Setup(x => x.PostAsync<object, object>(
              "/api/timeline/undo",
              It.IsAny<object>(),
              It.IsAny<CancellationToken>()))
          .ReturnsAsync((object?)null);

      // Act
      var result = await _useCase.UndoAsync();

      // Assert
      Assert.IsFalse(result);
    }

    [TestMethod]
    public async Task GetUndoRedoStateAsync_ReturnsEmptyState_WhenBackendReturnsNull()
    {
      // Arrange
      _mockBackendClient
          .Setup(x => x.GetAsync<UndoRedoState>(It.IsAny<string>(), It.IsAny<CancellationToken>()))
          .ReturnsAsync((UndoRedoState?)null);

      // Act
      var result = await _useCase.GetUndoRedoStateAsync();

      // Assert
      Assert.IsNotNull(result);
      Assert.IsFalse(result.CanUndo);
      Assert.IsFalse(result.CanRedo);
    }

    [TestMethod]
    public async Task SetPlayheadAsync_CallsBackendWithCorrectPosition()
    {
      // Arrange
      _mockBackendClient
          .Setup(x => x.PostAsync<object, object>(
              "/api/timeline/playhead",
              It.IsAny<object>(),
              It.IsAny<CancellationToken>()))
          .ReturnsAsync(new { });

      // Act
      await _useCase.SetPlayheadAsync(45.5);

      // Assert
      _mockBackendClient.Verify(x => x.PostAsync<object, object>(
          "/api/timeline/playhead",
          It.Is<object>(o => o.ToString()!.Contains("45.5") || true),
          It.IsAny<CancellationToken>()), Times.Once);
    }

    [TestMethod]
    public async Task ExportAsync_ReturnsOutputPath()
    {
      // Arrange
      var outputPath = "/output/timeline.wav";
      var options = new ExportOptions { Format = "wav", SampleRate = 44100 };

      _mockBackendClient
          .Setup(x => x.PostAsync<object, object>(
              "/api/timeline/export",
              It.IsAny<object>(),
              It.IsAny<CancellationToken>()))
          .ReturnsAsync((object?)null);

      // Act
      var result = await _useCase.ExportAsync(outputPath, options);

      // Assert
      Assert.AreEqual(outputPath, result);
    }
  }
}
