using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using VoiceStudio.Core.Events;

namespace VoiceStudio.App.Tests.Events;

[TestClass]
public class EventEnvelopeTests
{
    // Test payload class
    private record TestPayload(string Message, int Value);
    private record AnotherPayload(string Data);

    #region Constructor Tests

    [TestMethod]
    public void Constructor_CreatesUniqueEventId()
    {
        var payload = new TestPayload("Test", 1);
        var envelope = new EventEnvelope<TestPayload>(payload, "panel1");

        Assert.AreNotEqual(Guid.Empty, envelope.EventId);
    }

    [TestMethod]
    public void Constructor_SetsTimestamp()
    {
        var before = DateTimeOffset.UtcNow;
        var payload = new TestPayload("Test", 1);
        var envelope = new EventEnvelope<TestPayload>(payload, "panel1");
        var after = DateTimeOffset.UtcNow;

        Assert.IsTrue(envelope.Timestamp >= before);
        Assert.IsTrue(envelope.Timestamp <= after);
    }

    [TestMethod]
    public void Constructor_SetsSourcePanelId()
    {
        var payload = new TestPayload("Test", 1);
        var envelope = new EventEnvelope<TestPayload>(payload, "panel1");

        Assert.AreEqual("panel1", envelope.SourcePanelId);
    }

    [TestMethod]
    public void Constructor_NullSourcePanelId_SetsEmptyString()
    {
        var payload = new TestPayload("Test", 1);
        var envelope = new EventEnvelope<TestPayload>(payload, null!);

        Assert.AreEqual(string.Empty, envelope.SourcePanelId);
    }

    [TestMethod]
    public void Constructor_SetsPayload()
    {
        var payload = new TestPayload("Test", 42);
        var envelope = new EventEnvelope<TestPayload>(payload, "panel1");

        Assert.AreEqual(payload, envelope.Payload);
        Assert.AreEqual("Test", envelope.Payload.Message);
        Assert.AreEqual(42, envelope.Payload.Value);
    }

    [TestMethod]
    public void Constructor_DefaultIntent_IsNavigation()
    {
        var payload = new TestPayload("Test", 1);
        var envelope = new EventEnvelope<TestPayload>(payload, "panel1");

        Assert.AreEqual(InteractionIntent.Navigation, envelope.Intent);
    }

    [TestMethod]
    public void Constructor_CustomIntent_IsSet()
    {
        var payload = new TestPayload("Test", 1);
        var envelope = new EventEnvelope<TestPayload>(payload, "panel1", InteractionIntent.Edit);

        Assert.AreEqual(InteractionIntent.Edit, envelope.Intent);
    }

    [TestMethod]
    public void Constructor_DefaultIsUserInitiated_IsTrue()
    {
        var payload = new TestPayload("Test", 1);
        var envelope = new EventEnvelope<TestPayload>(payload, "panel1");

        Assert.IsTrue(envelope.IsUserInitiated);
    }

    [TestMethod]
    public void Constructor_CustomIsUserInitiated_IsSet()
    {
        var payload = new TestPayload("Test", 1);
        var envelope = new EventEnvelope<TestPayload>(payload, "panel1", isUserInitiated: false);

        Assert.IsFalse(envelope.IsUserInitiated);
    }

    [TestMethod]
    public void Constructor_NoCorrelationId_CreatesNewGuid()
    {
        var payload = new TestPayload("Test", 1);
        var envelope = new EventEnvelope<TestPayload>(payload, "panel1");

        Assert.AreNotEqual(Guid.Empty, envelope.CorrelationId);
    }

    [TestMethod]
    public void Constructor_CustomCorrelationId_IsSet()
    {
        var correlationId = Guid.NewGuid();
        var payload = new TestPayload("Test", 1);
        var envelope = new EventEnvelope<TestPayload>(payload, "panel1", correlationId: correlationId);

        Assert.AreEqual(correlationId, envelope.CorrelationId);
    }

    [TestMethod]
    public void Constructor_DefaultSequence_IsZero()
    {
        var payload = new TestPayload("Test", 1);
        var envelope = new EventEnvelope<TestPayload>(payload, "panel1");

        Assert.AreEqual(0, envelope.Sequence);
    }

    [TestMethod]
    public void Sequence_CanBeSetInternally()
    {
        var payload = new TestPayload("Test", 1);
        var envelope = new EventEnvelope<TestPayload>(payload, "panel1");
        
        envelope.Sequence = 42;

        Assert.AreEqual(42, envelope.Sequence);
    }

    #endregion

    #region Continue Tests

    [TestMethod]
    public void Continue_PreservesCorrelationId()
    {
        var payload1 = new TestPayload("First", 1);
        var envelope1 = new EventEnvelope<TestPayload>(payload1, "panel1");

        var payload2 = new AnotherPayload("Second");
        var envelope2 = envelope1.Continue(payload2, "panel2");

        Assert.AreEqual(envelope1.CorrelationId, envelope2.CorrelationId);
    }

    [TestMethod]
    public void Continue_CreatesNewEventId()
    {
        var payload1 = new TestPayload("First", 1);
        var envelope1 = new EventEnvelope<TestPayload>(payload1, "panel1");

        var payload2 = new AnotherPayload("Second");
        var envelope2 = envelope1.Continue(payload2, "panel2");

        Assert.AreNotEqual(envelope1.EventId, envelope2.EventId);
    }

    [TestMethod]
    public void Continue_SetsNewPayload()
    {
        var payload1 = new TestPayload("First", 1);
        var envelope1 = new EventEnvelope<TestPayload>(payload1, "panel1");

        var payload2 = new AnotherPayload("Second");
        var envelope2 = envelope1.Continue(payload2, "panel2");

        Assert.AreEqual(payload2, envelope2.Payload);
        Assert.AreEqual("Second", envelope2.Payload.Data);
    }

    [TestMethod]
    public void Continue_SetsNewSourcePanelId()
    {
        var payload1 = new TestPayload("First", 1);
        var envelope1 = new EventEnvelope<TestPayload>(payload1, "panel1");

        var payload2 = new AnotherPayload("Second");
        var envelope2 = envelope1.Continue(payload2, "panel2");

        Assert.AreEqual("panel2", envelope2.SourcePanelId);
    }

    [TestMethod]
    public void Continue_InheritsIntent_ByDefault()
    {
        var payload1 = new TestPayload("First", 1);
        var envelope1 = new EventEnvelope<TestPayload>(payload1, "panel1", InteractionIntent.Edit);

        var payload2 = new AnotherPayload("Second");
        var envelope2 = envelope1.Continue(payload2, "panel2");

        Assert.AreEqual(InteractionIntent.Edit, envelope2.Intent);
    }

    [TestMethod]
    public void Continue_OverridesIntent_WhenProvided()
    {
        var payload1 = new TestPayload("First", 1);
        var envelope1 = new EventEnvelope<TestPayload>(payload1, "panel1", InteractionIntent.Navigation);

        var payload2 = new AnotherPayload("Second");
        var envelope2 = envelope1.Continue(payload2, "panel2", InteractionIntent.Preview);

        Assert.AreEqual(InteractionIntent.Preview, envelope2.Intent);
    }

    [TestMethod]
    public void Continue_InheritsIsUserInitiated_ByDefault()
    {
        var payload1 = new TestPayload("First", 1);
        var envelope1 = new EventEnvelope<TestPayload>(payload1, "panel1", isUserInitiated: false);

        var payload2 = new AnotherPayload("Second");
        var envelope2 = envelope1.Continue(payload2, "panel2");

        Assert.IsFalse(envelope2.IsUserInitiated);
    }

    [TestMethod]
    public void Continue_OverridesIsUserInitiated_WhenProvided()
    {
        var payload1 = new TestPayload("First", 1);
        var envelope1 = new EventEnvelope<TestPayload>(payload1, "panel1", isUserInitiated: true);

        var payload2 = new AnotherPayload("Second");
        var envelope2 = envelope1.Continue(payload2, "panel2", isUserInitiated: false);

        Assert.IsFalse(envelope2.IsUserInitiated);
    }

    #endregion

    #region Factory Method Tests

    [TestMethod]
    public void ForNavigation_CreatesNavigationIntent()
    {
        var payload = new TestPayload("Test", 1);
        var envelope = EventEnvelope.ForNavigation(payload, "panel1");

        Assert.AreEqual(InteractionIntent.Navigation, envelope.Intent);
        Assert.IsTrue(envelope.IsUserInitiated);
    }

    [TestMethod]
    public void ForPreview_CreatesPreviewIntent()
    {
        var payload = new TestPayload("Test", 1);
        var envelope = EventEnvelope.ForPreview(payload, "panel1");

        Assert.AreEqual(InteractionIntent.Preview, envelope.Intent);
        Assert.IsTrue(envelope.IsUserInitiated);
    }

    [TestMethod]
    public void ForEdit_CreatesEditIntent()
    {
        var payload = new TestPayload("Test", 1);
        var envelope = EventEnvelope.ForEdit(payload, "panel1");

        Assert.AreEqual(InteractionIntent.Edit, envelope.Intent);
        Assert.IsTrue(envelope.IsUserInitiated);
    }

    [TestMethod]
    public void ForImmediateUse_CreatesImmediateUseIntent()
    {
        var payload = new TestPayload("Test", 1);
        var envelope = EventEnvelope.ForImmediateUse(payload, "panel1");

        Assert.AreEqual(InteractionIntent.ImmediateUse, envelope.Intent);
        Assert.IsTrue(envelope.IsUserInitiated);
    }

    [TestMethod]
    public void ForSystemRestore_CreatesSystemRestoreIntent()
    {
        var payload = new TestPayload("Test", 1);
        var envelope = EventEnvelope.ForSystemRestore(payload, "panel1");

        Assert.AreEqual(InteractionIntent.SystemRestore, envelope.Intent);
        Assert.IsFalse(envelope.IsUserInitiated);
    }

    [TestMethod]
    public void ForBackgroundProcess_CreatesBackgroundProcessIntent()
    {
        var payload = new TestPayload("Test", 1);
        var envelope = EventEnvelope.ForBackgroundProcess(payload, "panel1");

        Assert.AreEqual(InteractionIntent.BackgroundProcess, envelope.Intent);
        Assert.IsFalse(envelope.IsUserInitiated);
    }

    #endregion

    #region Unique ID Tests

    [TestMethod]
    public void MultipleEnvelopes_HaveUniqueEventIds()
    {
        var payload = new TestPayload("Test", 1);
        var envelope1 = new EventEnvelope<TestPayload>(payload, "panel1");
        var envelope2 = new EventEnvelope<TestPayload>(payload, "panel1");
        var envelope3 = new EventEnvelope<TestPayload>(payload, "panel1");

        Assert.AreNotEqual(envelope1.EventId, envelope2.EventId);
        Assert.AreNotEqual(envelope2.EventId, envelope3.EventId);
        Assert.AreNotEqual(envelope1.EventId, envelope3.EventId);
    }

    [TestMethod]
    public void MultipleEnvelopes_HaveUniqueCorrelationIds_ByDefault()
    {
        var payload = new TestPayload("Test", 1);
        var envelope1 = new EventEnvelope<TestPayload>(payload, "panel1");
        var envelope2 = new EventEnvelope<TestPayload>(payload, "panel1");

        Assert.AreNotEqual(envelope1.CorrelationId, envelope2.CorrelationId);
    }

    #endregion
}
