using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using VoiceStudio.Core.Gateways;
using VoiceStudio.Core.Messaging;

namespace VoiceStudio.App.Tests.Integration
{
  /// <summary>
  /// Integration tests for gateway operations.
  /// </summary>
  [TestClass]
  public class GatewayIntegrationTests : CommandTestBase
  {
    #region Voice Gateway Tests

    [TestMethod]
    public async Task SynthesizeAsync_WhenConnected_ReturnsResult()
    {
      // Arrange
      var request = new VoiceSynthesisRequest
      {
        Text = "Hello, world!",
        VoiceId = "test-voice",
        Speed = 1.0f,
        Pitch = 1.0f
      };

      // Act
      var result = await VoiceGateway.SynthesizeAsync(request);

      // Assert
      AssertSuccess(result);
      Assert.IsNotNull(result.Data?.AudioPath);
      Assert.AreEqual(1, VoiceGateway.SynthesisRequests.Count);
    }

    [TestMethod]
    public async Task GetAvailableVoices_ReturnsConfiguredVoices()
    {
      // Arrange
      VoiceGateway.AddVoice(new VoiceInfo
      {
        Id = "voice-1",
        Name = "Test Voice",
        Language = "en",
        EngineId = "xtts"
      });

      // Act
      var result = await VoiceGateway.GetAvailableVoicesAsync();

      // Assert
      AssertSuccess(result);
      Assert.AreEqual(1, result.Data?.Count);
      Assert.AreEqual("Test Voice", result.Data?[0].Name);
    }

    #endregion

    #region Job Gateway Tests

    [TestMethod]
    public async Task GetJobs_ReturnsJobsMatchingFilter()
    {
      // Arrange
      JobGateway.AddJob(new JobDetail
      {
        Id = "job-1",
        Type = "synthesis",
        Status = JobStatus.Running,
        Progress = 50
      });

      JobGateway.AddJob(new JobDetail
      {
        Id = "job-2",
        Type = "synthesis",
        Status = JobStatus.Completed,
        Progress = 100
      });

      // Act
      var result = await JobGateway.GetAllAsync(JobStatus.Running);

      // Assert
      AssertSuccess(result);
      Assert.AreEqual(1, result.Data?.Count);
      Assert.AreEqual("job-1", result.Data?[0].Id);
    }

    [TestMethod]
    public async Task CancelJob_WhenExists_Succeeds()
    {
      // Arrange
      var job = new JobDetail
      {
        Id = "job-1",
        Type = "synthesis",
        Status = JobStatus.Running,
        Progress = 50
      };
      JobGateway.AddJob(job);

      // Act
      var result = await JobGateway.CancelAsync("job-1");

      // Assert
      AssertSuccess(result);
      Assert.IsTrue(result.Data);

      // Verify status changed
      var statusResult = await JobGateway.GetByIdAsync("job-1");
      Assert.AreEqual(JobStatus.Cancelled, statusResult.Data?.Status);
    }

    #endregion

    #region Engine Gateway Tests

    [TestMethod]
    public async Task GetEngines_ReturnsConfiguredEngines()
    {
      // Arrange
      EngineGateway.AddEngine(new EngineDetail
      {
        Id = "xtts",
        Name = "XTTS",
        Version = "2.0",
        Availability = EngineAvailability.Available
      });

      EngineGateway.AddEngine(new EngineDetail
      {
        Id = "rvc",
        Name = "RVC",
        Version = "1.0",
        Availability = EngineAvailability.Available
      });

      // Act
      var result = await EngineGateway.GetAllAsync();

      // Assert
      AssertSuccess(result);
      Assert.AreEqual(2, result.Data?.Count);
    }

    [TestMethod]
    public async Task GetSchema_WhenConfigured_ReturnsSchema()
    {
      // Arrange
      var schema = new EngineParameterSchema
      {
        EngineId = "xtts",
        Parameters = new List<ParameterDefinition>
        {
          new ParameterDefinition
          {
            Name = "temperature",
            DisplayName = "Temperature",
            Type = ParameterType.Number
          }
        }
      };

      EngineGateway.AddEngine(new EngineDetail { Id = "xtts", Name = "XTTS" }, schema);

      // Act
      var result = await EngineGateway.GetSchemaAsync("xtts");

      // Assert
      AssertSuccess(result);
      Assert.AreEqual(1, result.Data?.Parameters.Count);
      Assert.AreEqual("temperature", result.Data?.Parameters[0].Name);
    }

    [TestMethod]
    public async Task GetSchema_WhenNotConfigured_ReturnsFail()
    {
      // Act
      var result = await EngineGateway.GetSchemaAsync("unknown-engine");

      // Assert
      AssertFailure(result, "NOT_FOUND");
    }

    #endregion

    #region Project Gateway Tests

    [TestMethod]
    public async Task CreateProject_ReturnsNewProject()
    {
      // Arrange
      var request = new ProjectCreateRequest
      {
        Name = "My Project",
        Description = "Test project"
      };

      // Act
      var result = await ProjectGateway.CreateAsync(request);

      // Assert
      AssertSuccess(result);
      Assert.AreEqual("My Project", result.Data?.Name);
      Assert.AreEqual("Test project", result.Data?.Description);
    }

    [TestMethod]
    public async Task GetProject_WhenExists_ReturnsProject()
    {
      // Arrange
      var project = new ProjectDetail
      {
        Id = "test-id",
        Name = "Existing Project",
        Description = "Test description",
        CreatedAt = DateTime.UtcNow
      };
      ProjectGateway.AddProject(project);

      // Act
      var result = await ProjectGateway.GetByIdAsync("test-id");

      // Assert
      AssertSuccess(result);
      Assert.AreEqual("Existing Project", result.Data?.Name);
    }

    [TestMethod]
    public async Task GetProject_WhenNotExists_ReturnsFail()
    {
      // Act
      var result = await ProjectGateway.GetByIdAsync("non-existent-id");

      // Assert
      AssertFailure(result, "NOT_FOUND");
    }

    #endregion

    #region Transport Tests

    [TestMethod]
    public async Task Transport_WhenDisconnected_ReturnsNetworkError()
    {
      // Arrange
      Transport.IsConnected = false;

      // Act
      var result = await Transport.GetAsync<object>("/api/test");

      // Assert
      AssertFailure(result, "NETWORK_ERROR");
      Assert.IsTrue(result.Error?.IsRetryable ?? false);
    }

    [TestMethod]
    public async Task Transport_WhenSimulatedError_ReturnsError()
    {
      // Arrange
      Transport.SimulatedError = new GatewayError("SERVER_ERROR", "Internal server error");

      // Act
      var result = await Transport.GetAsync<object>("/api/test");

      // Assert
      AssertFailure(result, "SERVER_ERROR");
    }

    [TestMethod]
    public async Task Transport_RecordsRequests()
    {
      // Arrange
      Transport.SetupGet("/api/test", new { value = 42 });

      // Act
      await Transport.GetAsync<object>("/api/test");
      await Transport.GetAsync<object>("/api/other");

      // Assert
      Assert.AreEqual(2, Transport.Requests.Count);
      Assert.AreEqual(("GET", "/api/test", null), Transport.Requests[0]);
      Assert.AreEqual(("GET", "/api/other", null), Transport.Requests[1]);
    }

    #endregion

    #region Messaging Tests

    [TestMethod]
    public void Messenger_SendAndReceive_Works()
    {
      // Arrange
      ShowToastMessage? received = null;
      Messenger.Register<ShowToastMessage>(this, msg => received = msg);

      // Act
      Messenger.Send(new ShowToastMessage("Test", "Message"));

      // Assert
      Assert.IsNotNull(received);
      Assert.AreEqual("Test", received.Title);
      Assert.AreEqual("Message", received.Message);
    }

    [TestMethod]
    public void Messenger_TracksAllSentMessages()
    {
      // Act
      Messenger.Send(new ShowToastMessage("Toast 1", "Message 1"));
      Messenger.Send(new ShowToastMessage("Toast 2", "Message 2"));
      Messenger.Send(new ProjectOpenedMessage("path", "name"));

      // Assert
      Assert.AreEqual(3, Messenger.SentMessages.Count);
      AssertMessageSent<ShowToastMessage>();
      AssertMessageSent<ProjectOpenedMessage>();
      AssertMessageSent<ShowToastMessage>(t => t.Title == "Toast 1");
    }

    [TestMethod]
    public void Messenger_Unregister_StopsReceiving()
    {
      // Arrange
      int count = 0;
      Messenger.Register<ShowToastMessage>(this, _ => count++);

      Messenger.Send(new ShowToastMessage("1", "1"));
      Assert.AreEqual(1, count);

      // Act
      Messenger.Unregister<ShowToastMessage>(this);
      Messenger.Send(new ShowToastMessage("2", "2"));

      // Assert
      Assert.AreEqual(1, count);
    }

    #endregion
  }
}
