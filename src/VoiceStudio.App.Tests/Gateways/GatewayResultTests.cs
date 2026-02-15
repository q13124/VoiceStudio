using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Text.Json;
using VoiceStudio.Core.Gateways;

namespace VoiceStudio.App.Tests.Gateways;

[TestClass]
public class GatewayResultTests
{
    #region Ok Factory Method Tests

    [TestMethod]
    public void Ok_CreatesSuccessfulResult()
    {
        var result = GatewayResult<string>.Ok("test data");

        Assert.IsTrue(result.Success);
    }

    [TestMethod]
    public void Ok_SetsData()
    {
        var result = GatewayResult<string>.Ok("test data");

        Assert.AreEqual("test data", result.Data);
    }

    [TestMethod]
    public void Ok_ErrorIsNull()
    {
        var result = GatewayResult<string>.Ok("test data");

        Assert.IsNull(result.Error);
    }

    [TestMethod]
    public void Ok_GeneratesCorrelationId_WhenNotProvided()
    {
        var result = GatewayResult<string>.Ok("test data");

        Assert.IsFalse(string.IsNullOrEmpty(result.CorrelationId));
    }

    [TestMethod]
    public void Ok_UsesProvidedCorrelationId()
    {
        var result = GatewayResult<string>.Ok("test data", "custom-correlation-id");

        Assert.AreEqual("custom-correlation-id", result.CorrelationId);
    }

    [TestMethod]
    public void Ok_WithComplexType()
    {
        var data = new TestData { Id = 1, Name = "Test" };
        var result = GatewayResult<TestData>.Ok(data);

        Assert.IsTrue(result.Success);
        Assert.AreEqual(1, result.Data?.Id);
        Assert.AreEqual("Test", result.Data?.Name);
    }

    #endregion

    #region Fail Factory Method Tests (GatewayError)

    [TestMethod]
    public void Fail_WithError_CreatesFailedResult()
    {
        var error = new GatewayError("ERROR", "Something went wrong");
        var result = GatewayResult<string>.Fail(error);

        Assert.IsFalse(result.Success);
    }

    [TestMethod]
    public void Fail_WithError_SetsError()
    {
        var error = new GatewayError("ERROR", "Something went wrong");
        var result = GatewayResult<string>.Fail(error);

        Assert.IsNotNull(result.Error);
        Assert.AreEqual("ERROR", result.Error.Code);
        Assert.AreEqual("Something went wrong", result.Error.Message);
    }

    [TestMethod]
    public void Fail_WithError_DataIsDefault()
    {
        var error = new GatewayError("ERROR", "Message");
        var result = GatewayResult<string>.Fail(error);

        Assert.IsNull(result.Data);
    }

    [TestMethod]
    public void Fail_WithError_GeneratesCorrelationId()
    {
        var error = new GatewayError("ERROR", "Message");
        var result = GatewayResult<string>.Fail(error);

        Assert.IsFalse(string.IsNullOrEmpty(result.CorrelationId));
    }

    [TestMethod]
    public void Fail_WithError_UsesProvidedCorrelationId()
    {
        var error = new GatewayError("ERROR", "Message");
        var result = GatewayResult<string>.Fail(error, "custom-id");

        Assert.AreEqual("custom-id", result.CorrelationId);
    }

    #endregion

    #region Fail Factory Method Tests (Exception)

    [TestMethod]
    public void Fail_WithException_CreatesFailedResult()
    {
        var exception = new InvalidOperationException("Test exception");
        var result = GatewayResult<string>.Fail(exception);

        Assert.IsFalse(result.Success);
    }

    [TestMethod]
    public void Fail_WithException_SetsErrorMessage()
    {
        var exception = new InvalidOperationException("Test exception");
        var result = GatewayResult<string>.Fail(exception);

        Assert.IsNotNull(result.Error);
        Assert.AreEqual("Test exception", result.Error.Message);
    }

    [TestMethod]
    public void Fail_WithException_UsesProvidedCorrelationId()
    {
        var exception = new InvalidOperationException("Test");
        var result = GatewayResult<string>.Fail(exception, "exception-correlation");

        Assert.AreEqual("exception-correlation", result.CorrelationId);
    }

    #endregion

    #region Map Tests

    [TestMethod]
    public void Map_SuccessfulResult_TransformsData()
    {
        var result = GatewayResult<int>.Ok(42);

        var mapped = result.Map(x => x.ToString());

        Assert.IsTrue(mapped.Success);
        Assert.AreEqual("42", mapped.Data);
    }

    [TestMethod]
    public void Map_SuccessfulResult_PreservesCorrelationId()
    {
        var result = GatewayResult<int>.Ok(42, "map-test-id");

        var mapped = result.Map(x => x * 2);

        Assert.AreEqual("map-test-id", mapped.CorrelationId);
    }

    [TestMethod]
    public void Map_FailedResult_PropagatesError()
    {
        var error = new GatewayError("FAILED", "Original error");
        var result = GatewayResult<int>.Fail(error);

        var mapped = result.Map(x => x.ToString());

        Assert.IsFalse(mapped.Success);
        Assert.IsNotNull(mapped.Error);
        Assert.AreEqual("FAILED", mapped.Error.Code);
    }

    [TestMethod]
    public void Map_FailedResult_PreservesCorrelationId()
    {
        var error = new GatewayError("FAILED", "Error");
        var result = GatewayResult<int>.Fail(error, "error-correlation");

        var mapped = result.Map(x => x.ToString());

        Assert.AreEqual("error-correlation", mapped.CorrelationId);
    }

    [TestMethod]
    public void Map_ComplexTransformation()
    {
        var data = new TestData { Id = 1, Name = "Test" };
        var result = GatewayResult<TestData>.Ok(data);

        var mapped = result.Map(d => new { Combined = $"{d.Id}:{d.Name}" });

        Assert.IsTrue(mapped.Success);
        Assert.AreEqual("1:Test", mapped.Data?.Combined);
    }

    #endregion

    // Test helper class
    private class TestData
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
    }
}

[TestClass]
public class GatewayErrorTests
{
    #region Constructor Tests

    [TestMethod]
    public void Constructor_SetsCode()
    {
        var error = new GatewayError("TEST_ERROR", "Message");
        Assert.AreEqual("TEST_ERROR", error.Code);
    }

    [TestMethod]
    public void Constructor_SetsMessage()
    {
        var error = new GatewayError("CODE", "Test message");
        Assert.AreEqual("Test message", error.Message);
    }

    [TestMethod]
    public void Constructor_DefaultStatusCode_IsNull()
    {
        var error = new GatewayError("CODE", "Message");
        Assert.IsNull(error.StatusCode);
    }

    [TestMethod]
    public void Constructor_SetsStatusCode()
    {
        var error = new GatewayError("CODE", "Message", statusCode: 404);
        Assert.AreEqual(404, error.StatusCode);
    }

    [TestMethod]
    public void Constructor_DefaultIsRetryable_IsFalse()
    {
        var error = new GatewayError("CODE", "Message");
        Assert.IsFalse(error.IsRetryable);
    }

    [TestMethod]
    public void Constructor_SetsIsRetryable()
    {
        var error = new GatewayError("CODE", "Message", isRetryable: true);
        Assert.IsTrue(error.IsRetryable);
    }

    [TestMethod]
    public void Constructor_SetsRecoverySuggestion()
    {
        var error = new GatewayError("CODE", "Message", recoverySuggestion: "Try again");
        Assert.AreEqual("Try again", error.RecoverySuggestion);
    }

    [TestMethod]
    public void Constructor_SetsOptionalFields()
    {
        var error = new GatewayError(
            "CODE", 
            "Message",
            requestId: "req-123",
            timestamp: "2025-01-15T12:00:00Z",
            path: "/api/test");

        Assert.AreEqual("req-123", error.RequestId);
        Assert.AreEqual("2025-01-15T12:00:00Z", error.Timestamp);
        Assert.AreEqual("/api/test", error.Path);
    }

    #endregion

    #region Factory Method Tests

    [TestMethod]
    public void Validation_CreatesValidationError()
    {
        var error = GatewayError.Validation("Invalid input");

        Assert.AreEqual("VALIDATION_ERROR", error.Code);
        Assert.AreEqual("Invalid input", error.Message);
        Assert.AreEqual(400, error.StatusCode);
        Assert.IsFalse(error.IsRetryable);
    }

    [TestMethod]
    public void NotFound_CreatesNotFoundError()
    {
        var error = GatewayError.NotFound("Resource not found");

        Assert.AreEqual("NOT_FOUND", error.Code);
        Assert.AreEqual("Resource not found", error.Message);
        Assert.AreEqual(404, error.StatusCode);
        Assert.IsFalse(error.IsRetryable);
    }

    [TestMethod]
    public void ServerError_CreatesServerError()
    {
        var error = GatewayError.ServerError("Internal error");

        Assert.AreEqual("SERVER_ERROR", error.Code);
        Assert.AreEqual("Internal error", error.Message);
        Assert.AreEqual(500, error.StatusCode);
        Assert.IsTrue(error.IsRetryable); // Default
    }

    [TestMethod]
    public void ServerError_CanSetIsRetryableFalse()
    {
        var error = GatewayError.ServerError("Fatal error", isRetryable: false);

        Assert.IsFalse(error.IsRetryable);
    }

    [TestMethod]
    public void Unavailable_CreatesUnavailableError()
    {
        var error = GatewayError.Unavailable();

        Assert.AreEqual("UNAVAILABLE", error.Code);
        Assert.AreEqual("Service is temporarily unavailable", error.Message);
        Assert.AreEqual(503, error.StatusCode);
        Assert.IsTrue(error.IsRetryable);
        Assert.AreEqual("Please try again in a moment.", error.RecoverySuggestion);
    }

    [TestMethod]
    public void Unavailable_CustomMessage()
    {
        var error = GatewayError.Unavailable("Backend offline");

        Assert.AreEqual("Backend offline", error.Message);
    }

    #endregion

    #region FromException Tests

    [TestMethod]
    public void FromException_StandardException_ExtractsMessage()
    {
        var exception = new InvalidOperationException("Test error");
        var error = GatewayError.FromException(exception);

        Assert.AreEqual("Test error", error.Message);
    }

    [TestMethod]
    public void FromException_StandardException_SetsUnknownCode()
    {
        var exception = new InvalidOperationException("Test");
        var error = GatewayError.FromException(exception);

        Assert.AreEqual("UNKNOWN_ERROR", error.Code);
    }

    [TestMethod]
    public void FromException_StandardException_IsNotRetryable()
    {
        var exception = new InvalidOperationException("Test");
        var error = GatewayError.FromException(exception);

        Assert.IsFalse(error.IsRetryable);
    }

    [TestMethod]
    public void FromException_NullReferenceException()
    {
        var exception = new NullReferenceException("Null ref");
        var error = GatewayError.FromException(exception);

        Assert.AreEqual("Null ref", error.Message);
        Assert.AreEqual("UNKNOWN_ERROR", error.Code);
    }

    [TestMethod]
    public void FromException_ArgumentException()
    {
        var exception = new ArgumentException("Invalid argument");
        var error = GatewayError.FromException(exception);

        Assert.AreEqual("Invalid argument", error.Message);
    }

    #endregion

    #region Validation with Details Tests

    [TestMethod]
    public void Validation_WithDetails_IncludesDetails()
    {
        var detailsJson = JsonDocument.Parse("{\"field\": \"email\", \"reason\": \"invalid format\"}");
        var error = GatewayError.Validation("Validation failed", detailsJson.RootElement);

        Assert.IsNotNull(error.Details);
    }

    #endregion
}
