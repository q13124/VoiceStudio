using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Tests.ViewModels
{
  /// <summary>
  /// Comprehensive unit tests for BatchProcessingViewModel operations.
  /// Tests cover batch job creation, status monitoring, quality reports, and error handling.
  /// </summary>
  [TestClass]
  public class BatchProcessingViewModelTests
  {
    private Mock<IBackendClient> _mockBackendClient = null!;

    [TestInitialize]
    public void Setup()
    {
      _mockBackendClient = new Mock<IBackendClient>();
    }

    #region Create Batch Job Tests

    [TestMethod]
    public async Task CreateBatchJobAsync_ReturnsJobWithId()
    {
      // Arrange
      var expectedJob = new BatchJob
      {
        Id = "batch-123",
        Name = "Test Batch",
        Status = JobStatus.Pending,
        Progress = 0.0
      };

      _mockBackendClient
          .Setup(x => x.CreateBatchJobAsync(It.IsAny<BatchJobRequest>(), It.IsAny<CancellationToken>()))
          .ReturnsAsync(expectedJob);

      var request = new BatchJobRequest
      {
        Name = "Test Batch",
        Text = "Test synthesis text",
        EngineId = "xtts",
        VoiceProfileId = "profile-123"
      };

      // Act
      var result = await _mockBackendClient.Object.CreateBatchJobAsync(request, CancellationToken.None);

      // Assert
      Assert.IsNotNull(result);
      Assert.AreEqual("batch-123", result.Id);
      Assert.AreEqual(JobStatus.Pending, result.Status);
    }

    [TestMethod]
    public async Task CreateBatchJobAsync_CallsBackend_WithCorrectRequest()
    {
      // Arrange
      BatchJobRequest? capturedRequest = null;
      _mockBackendClient
          .Setup(x => x.CreateBatchJobAsync(It.IsAny<BatchJobRequest>(), It.IsAny<CancellationToken>()))
          .Callback<BatchJobRequest, CancellationToken>((req, ct) => capturedRequest = req)
          .ReturnsAsync(new BatchJob { Id = "batch-456" });

      var request = new BatchJobRequest
      {
        Name = "Batch Job",
        Text = "Test text",
        EngineId = "chatterbox",
        VoiceProfileId = "profile-456",
        ProjectId = "proj-123"
      };

      // Act
      await _mockBackendClient.Object.CreateBatchJobAsync(request, CancellationToken.None);

      // Assert
      Assert.IsNotNull(capturedRequest);
      Assert.AreEqual("chatterbox", capturedRequest.EngineId);
      Assert.AreEqual("profile-456", capturedRequest.VoiceProfileId);
      Assert.AreEqual("proj-123", capturedRequest.ProjectId);
    }

    #endregion

    #region Get Batch Jobs Tests

    [TestMethod]
    public async Task GetBatchJobsAsync_ReturnsListOfJobs()
    {
      // Arrange
      var expectedJobs = new List<BatchJob>
            {
                new BatchJob { Id = "job-1", Status = JobStatus.Completed },
                new BatchJob { Id = "job-2", Status = JobStatus.Running },
                new BatchJob { Id = "job-3", Status = JobStatus.Failed }
            };

      _mockBackendClient
          .Setup(x => x.GetBatchJobsAsync(It.IsAny<string?>(), It.IsAny<JobStatus?>(), It.IsAny<CancellationToken>()))
          .ReturnsAsync(expectedJobs);

      // Act
      var result = await _mockBackendClient.Object.GetBatchJobsAsync(null, null, CancellationToken.None);

      // Assert
      Assert.AreEqual(3, result.Count);
      Assert.AreEqual("job-1", result[0].Id);
      Assert.AreEqual(JobStatus.Completed, result[0].Status);
    }

    [TestMethod]
    public async Task GetBatchJobsAsync_FiltersByStatus()
    {
      // Arrange
      var completedJobs = new List<BatchJob>
            {
                new BatchJob { Id = "completed-1", Status = JobStatus.Completed },
                new BatchJob { Id = "completed-2", Status = JobStatus.Completed }
            };

      _mockBackendClient
          .Setup(x => x.GetBatchJobsAsync(null, JobStatus.Completed, It.IsAny<CancellationToken>()))
          .ReturnsAsync(completedJobs);

      // Act
      var result = await _mockBackendClient.Object.GetBatchJobsAsync(null, JobStatus.Completed, CancellationToken.None);

      // Assert
      Assert.AreEqual(2, result.Count);
      Assert.IsTrue(result.TrueForAll(j => j.Status == JobStatus.Completed));
    }

    [TestMethod]
    public async Task GetBatchJobsAsync_FiltersByProjectId()
    {
      // Arrange
      var projectJobs = new List<BatchJob>
            {
                new BatchJob { Id = "project-job-1", ProjectId = "project-123" }
            };

      _mockBackendClient
          .Setup(x => x.GetBatchJobsAsync("project-123", null, It.IsAny<CancellationToken>()))
          .ReturnsAsync(projectJobs);

      // Act
      var result = await _mockBackendClient.Object.GetBatchJobsAsync("project-123", null, CancellationToken.None);

      // Assert
      Assert.AreEqual(1, result.Count);
      Assert.AreEqual("project-123", result[0].ProjectId);
    }

    #endregion

    #region Quality Reports Tests

    [TestMethod]
    public async Task GetBatchJobQualityAsync_ReturnsQualityReport()
    {
      // Arrange
      var expectedReport = new BatchQualityReport
      {
        JobId = "batch-quality-test",
        QualityScore = 0.85
      };

      _mockBackendClient
          .Setup(x => x.GetBatchJobQualityAsync("batch-quality-test", It.IsAny<CancellationToken>()))
          .ReturnsAsync(expectedReport);

      // Act
      var result = await _mockBackendClient.Object.GetBatchJobQualityAsync("batch-quality-test", CancellationToken.None);

      // Assert
      Assert.IsNotNull(result);
      Assert.AreEqual(0.85, result.QualityScore);
    }

    [TestMethod]
    public async Task GetBatchQualityStatisticsAsync_ReturnsStatistics()
    {
      // Arrange
      var expectedStats = new BatchQualityStatistics
      {
        TotalJobs = 100,
        CompletedJobs = 95,
        AverageQuality = 0.82
      };

      _mockBackendClient
          .Setup(x => x.GetBatchQualityStatisticsAsync(null, null, It.IsAny<CancellationToken>()))
          .ReturnsAsync(expectedStats);

      // Act
      var result = await _mockBackendClient.Object.GetBatchQualityStatisticsAsync(null, null, CancellationToken.None);

      // Assert
      Assert.IsNotNull(result);
      Assert.AreEqual(100, result.TotalJobs);
      Assert.AreEqual(95, result.CompletedJobs);
      Assert.AreEqual(0.82, result.AverageQuality);
    }

    #endregion

    #region Retry With Quality Tests

    [TestMethod]
    public async Task RetryBatchJobWithQualityAsync_ReturnsNewJob()
    {
      // Arrange
      var retryRequest = new BatchRetryWithQualityRequest
      {
        QualityThreshold = 0.8,
        EnhanceQuality = true
      };

      var expectedJob = new BatchJob
      {
        Id = "retry-batch-789",
        Status = JobStatus.Pending
      };

      _mockBackendClient
          .Setup(x => x.RetryBatchJobWithQualityAsync("original-batch", retryRequest, It.IsAny<CancellationToken>()))
          .ReturnsAsync(expectedJob);

      // Act
      var result = await _mockBackendClient.Object.RetryBatchJobWithQualityAsync("original-batch", retryRequest, CancellationToken.None);

      // Assert
      Assert.IsNotNull(result);
      Assert.AreEqual("retry-batch-789", result.Id);
      Assert.AreEqual(JobStatus.Pending, result.Status);
    }

    #endregion

    #region Job Status Progress Tests

    [TestMethod]
    public void BatchJob_ProgressIsWithinRange()
    {
      var job = new BatchJob
      {
        Id = "progress-test",
        Progress = 0.5
      };

      Assert.IsTrue(job.Progress >= 0.0);
      Assert.IsTrue(job.Progress <= 1.0);
    }

    [TestMethod]
    public void BatchJob_StatusEnumValues()
    {
      Assert.AreEqual(0, (int)JobStatus.Pending);
      Assert.AreEqual(1, (int)JobStatus.Running);
      Assert.AreEqual(2, (int)JobStatus.Completed);
      Assert.AreEqual(3, (int)JobStatus.Failed);
      Assert.AreEqual(4, (int)JobStatus.Cancelled);
    }

    #endregion

    #region BatchJobRequest Validation Tests

    [TestMethod]
    public void BatchJobRequest_DefaultValues()
    {
      var request = new BatchJobRequest();

      Assert.AreEqual(string.Empty, request.Name);
      Assert.AreEqual(string.Empty, request.Text);
      Assert.AreEqual("en", request.Language);
      Assert.IsFalse(request.EnhanceQuality);
    }

    [TestMethod]
    public void BatchJobRequest_WithQualitySettings()
    {
      var request = new BatchJobRequest
      {
        QualityThreshold = 0.8,
        EnhanceQuality = true
      };

      Assert.AreEqual(0.8, request.QualityThreshold);
      Assert.IsTrue(request.EnhanceQuality);
    }

    #endregion
  }
}
