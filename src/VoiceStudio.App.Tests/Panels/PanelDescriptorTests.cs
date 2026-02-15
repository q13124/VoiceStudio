using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.App.Tests.Panels;

[TestClass]
public class PanelDescriptorTests
{
    // Mock types for testing
    private class MockView { }
    private class MockViewModel { }

    #region Default Values Tests

    [TestMethod]
    public void DefaultValues_PanelIdIsEmpty()
    {
        var descriptor = new PanelDescriptor();
        Assert.AreEqual(string.Empty, descriptor.PanelId);
    }

    [TestMethod]
    public void DefaultValues_DisplayNameIsEmpty()
    {
        var descriptor = new PanelDescriptor();
        Assert.AreEqual(string.Empty, descriptor.DisplayName);
    }

    [TestMethod]
    public void DefaultValues_DefaultRegionIsLeft()
    {
        var descriptor = new PanelDescriptor();
        Assert.AreEqual(PanelRegion.Left, descriptor.DefaultRegion);
    }

    [TestMethod]
    public void DefaultValues_ViewTypeIsObject()
    {
        var descriptor = new PanelDescriptor();
        Assert.AreEqual(typeof(object), descriptor.ViewType);
    }

    [TestMethod]
    public void DefaultValues_ViewModelTypeIsNull()
    {
        var descriptor = new PanelDescriptor();
        Assert.IsNull(descriptor.ViewModelType);
    }

    [TestMethod]
    public void DefaultValues_IconIsNull()
    {
        var descriptor = new PanelDescriptor();
        Assert.IsNull(descriptor.Icon);
    }

    [TestMethod]
    public void DefaultValues_DescriptionIsNull()
    {
        var descriptor = new PanelDescriptor();
        Assert.IsNull(descriptor.Description);
    }

    #endregion

    #region Property Initialization Tests

    [TestMethod]
    public void Init_PanelId_IsSet()
    {
        var descriptor = new PanelDescriptor
        {
            PanelId = "library-panel"
        };

        Assert.AreEqual("library-panel", descriptor.PanelId);
    }

    [TestMethod]
    public void Init_DisplayName_IsSet()
    {
        var descriptor = new PanelDescriptor
        {
            DisplayName = "Library"
        };

        Assert.AreEqual("Library", descriptor.DisplayName);
    }

    [TestMethod]
    public void Init_DefaultRegion_IsSet()
    {
        var descriptor = new PanelDescriptor
        {
            DefaultRegion = PanelRegion.Center
        };

        Assert.AreEqual(PanelRegion.Center, descriptor.DefaultRegion);
    }

    [TestMethod]
    public void Init_ViewType_IsSet()
    {
        var descriptor = new PanelDescriptor
        {
            ViewType = typeof(MockView)
        };

        Assert.AreEqual(typeof(MockView), descriptor.ViewType);
    }

    [TestMethod]
    public void Init_ViewModelType_IsSet()
    {
        var descriptor = new PanelDescriptor
        {
            ViewModelType = typeof(MockViewModel)
        };

        Assert.AreEqual(typeof(MockViewModel), descriptor.ViewModelType);
    }

    [TestMethod]
    public void Init_Icon_IsSet()
    {
        var descriptor = new PanelDescriptor
        {
            Icon = "\uE8F1"
        };

        Assert.AreEqual("\uE8F1", descriptor.Icon);
    }

    [TestMethod]
    public void Init_Description_IsSet()
    {
        var descriptor = new PanelDescriptor
        {
            Description = "Manages audio library assets"
        };

        Assert.AreEqual("Manages audio library assets", descriptor.Description);
    }

    #endregion

    #region Region Alias Tests

    [TestMethod]
    public void Region_ReadsFromDefaultRegion()
    {
        var descriptor = new PanelDescriptor
        {
            DefaultRegion = PanelRegion.Right
        };

        Assert.AreEqual(PanelRegion.Right, descriptor.Region);
    }

    [TestMethod]
    public void Region_WritesToDefaultRegion()
    {
        var descriptor = new PanelDescriptor
        {
            Region = PanelRegion.Bottom
        };

        Assert.AreEqual(PanelRegion.Bottom, descriptor.DefaultRegion);
    }

    [TestMethod]
    public void Region_AndDefaultRegion_AreSynchronized()
    {
        var descriptor = new PanelDescriptor
        {
            DefaultRegion = PanelRegion.Floating
        };

        Assert.AreEqual(descriptor.DefaultRegion, descriptor.Region);
    }

    #endregion

    #region Full Initialization Tests

    [TestMethod]
    public void FullInitialization_AllPropertiesSet()
    {
        var descriptor = new PanelDescriptor
        {
            PanelId = "timeline-panel",
            DisplayName = "Timeline",
            DefaultRegion = PanelRegion.Bottom,
            ViewType = typeof(MockView),
            ViewModelType = typeof(MockViewModel),
            Icon = "\uE768",
            Description = "Audio timeline editor"
        };

        Assert.AreEqual("timeline-panel", descriptor.PanelId);
        Assert.AreEqual("Timeline", descriptor.DisplayName);
        Assert.AreEqual(PanelRegion.Bottom, descriptor.DefaultRegion);
        Assert.AreEqual(PanelRegion.Bottom, descriptor.Region);
        Assert.AreEqual(typeof(MockView), descriptor.ViewType);
        Assert.AreEqual(typeof(MockViewModel), descriptor.ViewModelType);
        Assert.AreEqual("\uE768", descriptor.Icon);
        Assert.AreEqual("Audio timeline editor", descriptor.Description);
    }

    #endregion

    #region Typical Usage Scenarios

    [TestMethod]
    public void TypicalUsage_LibraryPanel()
    {
        var descriptor = new PanelDescriptor
        {
            PanelId = "library",
            DisplayName = "Library",
            DefaultRegion = PanelRegion.Left,
            Icon = "\uE8F1",
            Description = "Browse and manage audio assets"
        };

        Assert.AreEqual("library", descriptor.PanelId);
        Assert.AreEqual(PanelRegion.Left, descriptor.DefaultRegion);
    }

    [TestMethod]
    public void TypicalUsage_FloatingPanel()
    {
        var descriptor = new PanelDescriptor
        {
            PanelId = "settings",
            DisplayName = "Settings",
            Region = PanelRegion.Floating,
            Description = "Application settings"
        };

        Assert.AreEqual(PanelRegion.Floating, descriptor.DefaultRegion);
    }

    #endregion
}

[TestClass]
public class PanelRegionTests
{
    [TestMethod]
    public void PanelRegion_HasExpectedValues()
    {
        Assert.AreEqual(0, (int)PanelRegion.Left);
        Assert.AreEqual(1, (int)PanelRegion.Center);
        Assert.AreEqual(2, (int)PanelRegion.Right);
        Assert.AreEqual(3, (int)PanelRegion.Bottom);
        Assert.AreEqual(4, (int)PanelRegion.Floating);
    }

    [TestMethod]
    public void PanelRegion_AllValuesAreDefined()
    {
        var values = Enum.GetValues<PanelRegion>();
        Assert.AreEqual(5, values.Length);
    }

    [TestMethod]
    public void PanelRegion_CanBeUsedInSwitch()
    {
        var region = PanelRegion.Center;
        string result = region switch
        {
            PanelRegion.Left => "left",
            PanelRegion.Center => "center",
            PanelRegion.Right => "right",
            PanelRegion.Bottom => "bottom",
            PanelRegion.Floating => "floating",
            _ => "unknown"
        };

        Assert.AreEqual("center", result);
    }

    [TestMethod]
    public void PanelRegion_ToString_ReturnsName()
    {
        Assert.AreEqual("Left", PanelRegion.Left.ToString());
        Assert.AreEqual("Center", PanelRegion.Center.ToString());
        Assert.AreEqual("Right", PanelRegion.Right.ToString());
        Assert.AreEqual("Bottom", PanelRegion.Bottom.ToString());
        Assert.AreEqual("Floating", PanelRegion.Floating.ToString());
    }

    [TestMethod]
    public void PanelRegion_ParseFromString()
    {
        Assert.AreEqual(PanelRegion.Left, Enum.Parse<PanelRegion>("Left"));
        Assert.AreEqual(PanelRegion.Center, Enum.Parse<PanelRegion>("Center"));
        Assert.AreEqual(PanelRegion.Floating, Enum.Parse<PanelRegion>("Floating"));
    }
}
