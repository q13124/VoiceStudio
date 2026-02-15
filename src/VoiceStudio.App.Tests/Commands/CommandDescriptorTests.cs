using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Threading.Tasks;
using VoiceStudio.Core.Commands;

namespace VoiceStudio.App.Tests.Commands;

[TestClass]
public class CommandDescriptorTests
{
    #region Default Values Tests

    [TestMethod]
    public void DefaultValues_IdIsEmpty()
    {
        var cmd = new CommandDescriptor();
        Assert.AreEqual(string.Empty, cmd.Id);
    }

    [TestMethod]
    public void DefaultValues_TitleIsEmpty()
    {
        var cmd = new CommandDescriptor();
        Assert.AreEqual(string.Empty, cmd.Title);
    }

    [TestMethod]
    public void DefaultValues_KeywordsIsEmpty()
    {
        var cmd = new CommandDescriptor();
        Assert.AreEqual(0, cmd.Keywords.Length);
    }

    [TestMethod]
    public void DefaultValues_DefaultHotkeyIsNull()
    {
        var cmd = new CommandDescriptor();
        Assert.IsNull(cmd.DefaultHotkey);
    }

    [TestMethod]
    public void DefaultValues_CategoryIsGeneral()
    {
        var cmd = new CommandDescriptor();
        Assert.AreEqual("General", cmd.Category);
    }

    [TestMethod]
    public void DefaultValues_IconIsNull()
    {
        var cmd = new CommandDescriptor();
        Assert.IsNull(cmd.Icon);
    }

    [TestMethod]
    public void DefaultValues_PriorityIs100()
    {
        var cmd = new CommandDescriptor();
        Assert.AreEqual(100, cmd.Priority);
    }

    [TestMethod]
    public void DefaultValues_ExecuteAsyncIsNull()
    {
        var cmd = new CommandDescriptor();
        Assert.IsNull(cmd.ExecuteAsync);
    }

    [TestMethod]
    public void DefaultValues_ExecuteIsNull()
    {
        var cmd = new CommandDescriptor();
        Assert.IsNull(cmd.Execute);
    }

    [TestMethod]
    public void DefaultValues_CanExecuteIsNull()
    {
        var cmd = new CommandDescriptor();
        Assert.IsNull(cmd.CanExecute);
    }

    [TestMethod]
    public void DefaultValues_ShowInPaletteIsTrue()
    {
        var cmd = new CommandDescriptor();
        Assert.IsTrue(cmd.ShowInPalette);
    }

    #endregion

    #region Property Initialization Tests

    [TestMethod]
    public void InitProperties_AllPropertiesSet()
    {
        var cmd = new CommandDescriptor
        {
            Id = "test.command",
            Title = "Test Command",
            Keywords = new[] { "foo", "bar" },
            DefaultHotkey = "Ctrl+T",
            Category = "Testing",
            Icon = "\uE700",
            Priority = 50,
            ShowInPalette = false
        };

        Assert.AreEqual("test.command", cmd.Id);
        Assert.AreEqual("Test Command", cmd.Title);
        Assert.AreEqual(2, cmd.Keywords.Length);
        Assert.AreEqual("foo", cmd.Keywords[0]);
        Assert.AreEqual("bar", cmd.Keywords[1]);
        Assert.AreEqual("Ctrl+T", cmd.DefaultHotkey);
        Assert.AreEqual("Testing", cmd.Category);
        Assert.AreEqual("\uE700", cmd.Icon);
        Assert.AreEqual(50, cmd.Priority);
        Assert.IsFalse(cmd.ShowInPalette);
    }

    #endregion

    #region CheckCanExecute Tests

    [TestMethod]
    public void CheckCanExecute_NoDelegate_ReturnsTrue()
    {
        var cmd = new CommandDescriptor();
        Assert.IsTrue(cmd.CheckCanExecute());
    }

    [TestMethod]
    public void CheckCanExecute_DelegateReturnsTrue_ReturnsTrue()
    {
        var cmd = new CommandDescriptor
        {
            CanExecute = () => true
        };
        Assert.IsTrue(cmd.CheckCanExecute());
    }

    [TestMethod]
    public void CheckCanExecute_DelegateReturnsFalse_ReturnsFalse()
    {
        var cmd = new CommandDescriptor
        {
            CanExecute = () => false
        };
        Assert.IsFalse(cmd.CheckCanExecute());
    }

    [TestMethod]
    public void CheckCanExecute_DelegateIsCalled()
    {
        var callCount = 0;
        var cmd = new CommandDescriptor
        {
            CanExecute = () =>
            {
                callCount++;
                return true;
            }
        };

        cmd.CheckCanExecute();
        Assert.AreEqual(1, callCount);
    }

    #endregion

    #region InvokeAsync Tests

    [TestMethod]
    public async Task InvokeAsync_NoExecuteDelegates_DoesNotThrow()
    {
        var cmd = new CommandDescriptor();
        await cmd.InvokeAsync(); // Should not throw
    }

    [TestMethod]
    public async Task InvokeAsync_WithExecuteAsync_CallsDelegate()
    {
        var executed = false;
        var cmd = new CommandDescriptor
        {
            ExecuteAsync = () =>
            {
                executed = true;
                return Task.CompletedTask;
            }
        };

        await cmd.InvokeAsync();
        Assert.IsTrue(executed);
    }

    [TestMethod]
    public async Task InvokeAsync_WithExecute_CallsDelegate()
    {
        var executed = false;
        var cmd = new CommandDescriptor
        {
            Execute = () => executed = true
        };

        await cmd.InvokeAsync();
        Assert.IsTrue(executed);
    }

    [TestMethod]
    public async Task InvokeAsync_BothDelegates_PrefersExecuteAsync()
    {
        var asyncExecuted = false;
        var syncExecuted = false;
        var cmd = new CommandDescriptor
        {
            ExecuteAsync = () =>
            {
                asyncExecuted = true;
                return Task.CompletedTask;
            },
            Execute = () => syncExecuted = true
        };

        await cmd.InvokeAsync();
        Assert.IsTrue(asyncExecuted);
        Assert.IsFalse(syncExecuted);
    }

    [TestMethod]
    public async Task InvokeAsync_CanExecuteReturnsTrue_Executes()
    {
        var executed = false;
        var cmd = new CommandDescriptor
        {
            CanExecute = () => true,
            Execute = () => executed = true
        };

        await cmd.InvokeAsync();
        Assert.IsTrue(executed);
    }

    [TestMethod]
    public async Task InvokeAsync_CanExecuteReturnsFalse_DoesNotExecute()
    {
        var executed = false;
        var cmd = new CommandDescriptor
        {
            CanExecute = () => false,
            Execute = () => executed = true
        };

        await cmd.InvokeAsync();
        Assert.IsFalse(executed);
    }

    [TestMethod]
    public async Task InvokeAsync_CanExecuteReturnsFalse_DoesNotCallExecuteAsync()
    {
        var executed = false;
        var cmd = new CommandDescriptor
        {
            CanExecute = () => false,
            ExecuteAsync = () =>
            {
                executed = true;
                return Task.CompletedTask;
            }
        };

        await cmd.InvokeAsync();
        Assert.IsFalse(executed);
    }

    [TestMethod]
    public async Task InvokeAsync_CanExecuteIsNull_StillExecutes()
    {
        var executed = false;
        var cmd = new CommandDescriptor
        {
            Execute = () => executed = true
        };

        await cmd.InvokeAsync();
        Assert.IsTrue(executed);
    }

    [TestMethod]
    public async Task InvokeAsync_ExecuteAsyncAwaitable_CompletesAsync()
    {
        var completed = false;
        var cmd = new CommandDescriptor
        {
            ExecuteAsync = async () =>
            {
                await Task.Delay(10);
                completed = true;
            }
        };

        await cmd.InvokeAsync();
        Assert.IsTrue(completed);
    }

    #endregion

    #region Typical Usage Scenarios

    [TestMethod]
    public async Task TypicalUsage_VoiceSynthesizeCommand()
    {
        var synthesized = false;
        var cmd = new CommandDescriptor
        {
            Id = "voice.synthesize",
            Title = "Synthesize Voice",
            Keywords = new[] { "generate", "tts", "speak" },
            DefaultHotkey = "Ctrl+Shift+S",
            Category = "Voice",
            Icon = "\uE768",
            Priority = 10,
            ShowInPalette = true,
            ExecuteAsync = () =>
            {
                synthesized = true;
                return Task.CompletedTask;
            }
        };

        Assert.IsTrue(cmd.CheckCanExecute());
        await cmd.InvokeAsync();
        Assert.IsTrue(synthesized);
    }

    [TestMethod]
    public void TypicalUsage_DisabledCommand()
    {
        var isProfileLoaded = false;
        var cmd = new CommandDescriptor
        {
            Id = "profile.export",
            Title = "Export Profile",
            Category = "Profile",
            CanExecute = () => isProfileLoaded,
            Execute = () => { /* export logic */ }
        };

        Assert.IsFalse(cmd.CheckCanExecute());

        isProfileLoaded = true;
        Assert.IsTrue(cmd.CheckCanExecute());
    }

    [TestMethod]
    public void TypicalUsage_HiddenKeyboardShortcut()
    {
        var cmd = new CommandDescriptor
        {
            Id = "editor.quicksave",
            Title = "Quick Save",
            DefaultHotkey = "Ctrl+S",
            ShowInPalette = false, // Only accessible via hotkey
            Execute = () => { }
        };

        Assert.IsFalse(cmd.ShowInPalette);
        Assert.AreEqual("Ctrl+S", cmd.DefaultHotkey);
    }

    #endregion
}
