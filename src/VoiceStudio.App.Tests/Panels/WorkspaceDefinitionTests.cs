using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Collections.Generic;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.App.Tests.Panels;

[TestClass]
public class PanelPlacementTests
{
    #region Required Properties Tests

    [TestMethod]
    public void PanelPlacement_RequiredProperties_AreSet()
    {
        var placement = new PanelPlacement
        {
            PanelId = "library",
            Region = PanelRegion.Left
        };

        Assert.AreEqual("library", placement.PanelId);
        Assert.AreEqual(PanelRegion.Left, placement.Region);
    }

    #endregion

    #region Default Values Tests

    [TestMethod]
    public void PanelPlacement_Order_DefaultsToZero()
    {
        var placement = new PanelPlacement
        {
            PanelId = "panel",
            Region = PanelRegion.Center
        };

        Assert.AreEqual(0, placement.Order);
    }

    [TestMethod]
    public void PanelPlacement_IsCollapsed_DefaultsToFalse()
    {
        var placement = new PanelPlacement
        {
            PanelId = "panel",
            Region = PanelRegion.Center
        };

        Assert.IsFalse(placement.IsCollapsed);
    }

    [TestMethod]
    public void PanelPlacement_IsVisible_DefaultsToTrue()
    {
        var placement = new PanelPlacement
        {
            PanelId = "panel",
            Region = PanelRegion.Center
        };

        Assert.IsTrue(placement.IsVisible);
    }

    [TestMethod]
    public void PanelPlacement_RelativeWidth_DefaultsToNull()
    {
        var placement = new PanelPlacement
        {
            PanelId = "panel",
            Region = PanelRegion.Center
        };

        Assert.IsNull(placement.RelativeWidth);
    }

    [TestMethod]
    public void PanelPlacement_RelativeHeight_DefaultsToNull()
    {
        var placement = new PanelPlacement
        {
            PanelId = "panel",
            Region = PanelRegion.Center
        };

        Assert.IsNull(placement.RelativeHeight);
    }

    [TestMethod]
    public void PanelPlacement_PanelState_DefaultsToNull()
    {
        var placement = new PanelPlacement
        {
            PanelId = "panel",
            Region = PanelRegion.Center
        };

        Assert.IsNull(placement.PanelState);
    }

    #endregion

    #region Optional Properties Tests

    [TestMethod]
    public void PanelPlacement_Order_CanBeSet()
    {
        var placement = new PanelPlacement
        {
            PanelId = "panel",
            Region = PanelRegion.Left,
            Order = 3
        };

        Assert.AreEqual(3, placement.Order);
    }

    [TestMethod]
    public void PanelPlacement_IsCollapsed_CanBeTrue()
    {
        var placement = new PanelPlacement
        {
            PanelId = "panel",
            Region = PanelRegion.Right,
            IsCollapsed = true
        };

        Assert.IsTrue(placement.IsCollapsed);
    }

    [TestMethod]
    public void PanelPlacement_IsVisible_CanBeFalse()
    {
        var placement = new PanelPlacement
        {
            PanelId = "panel",
            Region = PanelRegion.Bottom,
            IsVisible = false
        };

        Assert.IsFalse(placement.IsVisible);
    }

    [TestMethod]
    public void PanelPlacement_RelativeDimensions_CanBeSet()
    {
        var placement = new PanelPlacement
        {
            PanelId = "panel",
            Region = PanelRegion.Left,
            RelativeWidth = 0.25,
            RelativeHeight = 0.5
        };

        Assert.AreEqual(0.25, placement.RelativeWidth);
        Assert.AreEqual(0.5, placement.RelativeHeight);
    }

    [TestMethod]
    public void PanelPlacement_PanelState_CanBeSet()
    {
        var placement = new PanelPlacement
        {
            PanelId = "panel",
            Region = PanelRegion.Center,
            PanelState = new Dictionary<string, object>
            {
                ["scrollPosition"] = 150.0,
                ["selectedItem"] = "item-1"
            }
        };

        Assert.IsNotNull(placement.PanelState);
        Assert.AreEqual(150.0, placement.PanelState["scrollPosition"]);
        Assert.AreEqual("item-1", placement.PanelState["selectedItem"]);
    }

    #endregion
}

[TestClass]
public class WorkspaceDefinitionTests
{
    #region Required Properties Tests

    [TestMethod]
    public void WorkspaceDefinition_RequiredProperties_AreSet()
    {
        var workspace = new WorkspaceDefinition
        {
            Id = "ws-1",
            Name = "Default",
            Panels = new List<PanelPlacement>()
        };

        Assert.AreEqual("ws-1", workspace.Id);
        Assert.AreEqual("Default", workspace.Name);
        Assert.AreEqual(0, workspace.Panels.Count);
    }

    #endregion

    #region Default Values Tests

    [TestMethod]
    public void WorkspaceDefinition_Description_DefaultsToNull()
    {
        var workspace = new WorkspaceDefinition
        {
            Id = "ws",
            Name = "Test",
            Panels = new List<PanelPlacement>()
        };

        Assert.IsNull(workspace.Description);
    }

    [TestMethod]
    public void WorkspaceDefinition_IconGlyph_DefaultsToNull()
    {
        var workspace = new WorkspaceDefinition
        {
            Id = "ws",
            Name = "Test",
            Panels = new List<PanelPlacement>()
        };

        Assert.IsNull(workspace.IconGlyph);
    }

    [TestMethod]
    public void WorkspaceDefinition_IsPreset_DefaultsToFalse()
    {
        var workspace = new WorkspaceDefinition
        {
            Id = "ws",
            Name = "Test",
            Panels = new List<PanelPlacement>()
        };

        Assert.IsFalse(workspace.IsPreset);
    }

    [TestMethod]
    public void WorkspaceDefinition_IsActive_DefaultsToFalse()
    {
        var workspace = new WorkspaceDefinition
        {
            Id = "ws",
            Name = "Test",
            Panels = new List<PanelPlacement>()
        };

        Assert.IsFalse(workspace.IsActive);
    }

    [TestMethod]
    public void WorkspaceDefinition_CreatedAt_IsSetAutomatically()
    {
        var before = DateTimeOffset.UtcNow;
        var workspace = new WorkspaceDefinition
        {
            Id = "ws",
            Name = "Test",
            Panels = new List<PanelPlacement>()
        };
        var after = DateTimeOffset.UtcNow;

        Assert.IsTrue(workspace.CreatedAt >= before);
        Assert.IsTrue(workspace.CreatedAt <= after);
    }

    [TestMethod]
    public void WorkspaceDefinition_ModifiedAt_IsSetAutomatically()
    {
        var before = DateTimeOffset.UtcNow;
        var workspace = new WorkspaceDefinition
        {
            Id = "ws",
            Name = "Test",
            Panels = new List<PanelPlacement>()
        };
        var after = DateTimeOffset.UtcNow;

        Assert.IsTrue(workspace.ModifiedAt >= before);
        Assert.IsTrue(workspace.ModifiedAt <= after);
    }

    [TestMethod]
    public void WorkspaceDefinition_KeyboardShortcut_DefaultsToNull()
    {
        var workspace = new WorkspaceDefinition
        {
            Id = "ws",
            Name = "Test",
            Panels = new List<PanelPlacement>()
        };

        Assert.IsNull(workspace.KeyboardShortcut);
    }

    #endregion

    #region WithModified Tests

    [TestMethod]
    public void WithModified_UpdatesModifiedTimestamp()
    {
        var workspace = new WorkspaceDefinition
        {
            Id = "ws",
            Name = "Test",
            Panels = new List<PanelPlacement>()
        };

        var originalModified = workspace.ModifiedAt;

        // Small delay to ensure different timestamp
        System.Threading.Thread.Sleep(10);

        var updated = workspace.WithModified();

        Assert.IsTrue(updated.ModifiedAt > originalModified);
    }

    [TestMethod]
    public void WithModified_PreservesOtherProperties()
    {
        var panels = new List<PanelPlacement>
        {
            new PanelPlacement { PanelId = "library", Region = PanelRegion.Left }
        };

        var workspace = new WorkspaceDefinition
        {
            Id = "ws-1",
            Name = "My Workspace",
            Description = "Test workspace",
            IconGlyph = "\uE768",
            IsPreset = true,
            IsActive = true,
            Panels = panels,
            KeyboardShortcut = "Ctrl+1"
        };

        var updated = workspace.WithModified();

        Assert.AreEqual(workspace.Id, updated.Id);
        Assert.AreEqual(workspace.Name, updated.Name);
        Assert.AreEqual(workspace.Description, updated.Description);
        Assert.AreEqual(workspace.IconGlyph, updated.IconGlyph);
        Assert.AreEqual(workspace.IsPreset, updated.IsPreset);
        Assert.AreEqual(workspace.IsActive, updated.IsActive);
        Assert.AreEqual(workspace.Panels, updated.Panels);
        Assert.AreEqual(workspace.CreatedAt, updated.CreatedAt);
        Assert.AreEqual(workspace.KeyboardShortcut, updated.KeyboardShortcut);
    }

    #endregion

    #region Full Initialization Tests

    [TestMethod]
    public void WorkspaceDefinition_FullInitialization()
    {
        var panels = new List<PanelPlacement>
        {
            new PanelPlacement { PanelId = "library", Region = PanelRegion.Left, Order = 0 },
            new PanelPlacement { PanelId = "profiles", Region = PanelRegion.Left, Order = 1 },
            new PanelPlacement { PanelId = "synthesis", Region = PanelRegion.Center },
            new PanelPlacement { PanelId = "timeline", Region = PanelRegion.Bottom }
        };

        var workspace = new WorkspaceDefinition
        {
            Id = "production",
            Name = "Production Layout",
            Description = "Layout optimized for voice production",
            IconGlyph = "\uE768",
            IsPreset = true,
            IsActive = true,
            Panels = panels,
            KeyboardShortcut = "Ctrl+1"
        };

        Assert.AreEqual(4, workspace.Panels.Count);
        Assert.AreEqual("library", workspace.Panels[0].PanelId);
        Assert.AreEqual(PanelRegion.Bottom, workspace.Panels[3].Region);
    }

    #endregion
}

[TestClass]
public class WorkspaceConfigurationTests
{
    #region Default Values Tests

    [TestMethod]
    public void WorkspaceConfiguration_ActiveWorkspaceId_DefaultsToNull()
    {
        var config = new WorkspaceConfiguration();
        Assert.IsNull(config.ActiveWorkspaceId);
    }

    [TestMethod]
    public void WorkspaceConfiguration_Workspaces_DefaultsToEmptyList()
    {
        var config = new WorkspaceConfiguration();
        Assert.IsNotNull(config.Workspaces);
        Assert.AreEqual(0, config.Workspaces.Count);
    }

    [TestMethod]
    public void WorkspaceConfiguration_Version_DefaultsToOne()
    {
        var config = new WorkspaceConfiguration();
        Assert.AreEqual(1, config.Version);
    }

    [TestMethod]
    public void WorkspaceConfiguration_LastSaved_IsSetAutomatically()
    {
        var before = DateTimeOffset.UtcNow;
        var config = new WorkspaceConfiguration();
        var after = DateTimeOffset.UtcNow;

        Assert.IsTrue(config.LastSaved >= before);
        Assert.IsTrue(config.LastSaved <= after);
    }

    #endregion

    #region Property Modification Tests

    [TestMethod]
    public void WorkspaceConfiguration_ActiveWorkspaceId_CanBeSet()
    {
        var config = new WorkspaceConfiguration
        {
            ActiveWorkspaceId = "ws-production"
        };

        Assert.AreEqual("ws-production", config.ActiveWorkspaceId);
    }

    [TestMethod]
    public void WorkspaceConfiguration_Workspaces_CanBeModified()
    {
        var config = new WorkspaceConfiguration();
        var workspace = new WorkspaceDefinition
        {
            Id = "ws-1",
            Name = "Test",
            Panels = new List<PanelPlacement>()
        };

        config.Workspaces.Add(workspace);

        Assert.AreEqual(1, config.Workspaces.Count);
        Assert.AreEqual("ws-1", config.Workspaces[0].Id);
    }

    [TestMethod]
    public void WorkspaceConfiguration_Version_CanBeSet()
    {
        var config = new WorkspaceConfiguration
        {
            Version = 2
        };

        Assert.AreEqual(2, config.Version);
    }

    [TestMethod]
    public void WorkspaceConfiguration_LastSaved_CanBeSet()
    {
        var specificTime = new DateTimeOffset(2025, 6, 15, 12, 0, 0, TimeSpan.Zero);
        var config = new WorkspaceConfiguration
        {
            LastSaved = specificTime
        };

        Assert.AreEqual(specificTime, config.LastSaved);
    }

    #endregion

    #region Typical Usage Tests

    [TestMethod]
    public void TypicalUsage_MultipleWorkspaces()
    {
        var config = new WorkspaceConfiguration
        {
            ActiveWorkspaceId = "production",
            Version = 1
        };

        config.Workspaces.Add(new WorkspaceDefinition
        {
            Id = "production",
            Name = "Production",
            IsPreset = true,
            Panels = new List<PanelPlacement>
            {
                new PanelPlacement { PanelId = "library", Region = PanelRegion.Left }
            }
        });

        config.Workspaces.Add(new WorkspaceDefinition
        {
            Id = "editing",
            Name = "Editing",
            IsPreset = true,
            Panels = new List<PanelPlacement>
            {
                new PanelPlacement { PanelId = "timeline", Region = PanelRegion.Center }
            }
        });

        Assert.AreEqual(2, config.Workspaces.Count);
        Assert.AreEqual("production", config.ActiveWorkspaceId);
    }

    #endregion
}
