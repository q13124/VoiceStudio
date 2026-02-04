using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Represents a macro graph with nodes and connections.
  /// Macros can automate voice cloning workflows and effects processing.
  /// </summary>
  public class Macro
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string ProjectId { get; set; } = string.Empty;
    public List<MacroNode> Nodes { get; set; } = new();
    public List<MacroConnection> Connections { get; set; } = new();
    public bool IsEnabled { get; set; } = true;
    public System.DateTime Created { get; set; }
    public System.DateTime Modified { get; set; }
  }

  /// <summary>
  /// Represents a node in a macro graph.
  /// </summary>
  public class MacroNode
  {
    public string Id { get; set; } = string.Empty;
    public string Type { get; set; } = string.Empty; // "source", "processor", "control", "conditional", "output"
    public string Name { get; set; } = string.Empty;
    public double X { get; set; } // Canvas position
    public double Y { get; set; } // Canvas position
    public Dictionary<string, object> Properties { get; set; } = new();
    public List<MacroPort> InputPorts { get; set; } = new();
    public List<MacroPort> OutputPorts { get; set; } = new();
  }

  /// <summary>
  /// Represents a connection between two nodes in a macro graph.
  /// </summary>
  public class MacroConnection
  {
    public string Id { get; set; } = string.Empty;
    public string SourceNodeId { get; set; } = string.Empty;
    public string SourcePortId { get; set; } = string.Empty;
    public string TargetNodeId { get; set; } = string.Empty;
    public string TargetPortId { get; set; } = string.Empty;
  }

  /// <summary>
  /// Represents a port on a macro node (input or output).
  /// </summary>
  public class MacroPort
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Type { get; set; } = string.Empty; // "audio", "control", "data"
    public bool IsRequired { get; set; }
  }

  /// <summary>
  /// Represents an automation curve for a parameter over time.
  /// </summary>
  public class AutomationCurve
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string ParameterId { get; set; } = string.Empty; // e.g., "volume", "pitch", "speed"
    public string TrackId { get; set; } = string.Empty;
    public List<AutomationPoint> Points { get; set; } = new();
    public string Interpolation { get; set; } = "linear"; // "linear", "bezier", "step"
  }

  /// <summary>
  /// Represents a single point on an automation curve.
  /// </summary>
  public class AutomationPoint
  {
    public double Time { get; set; } // Time in seconds
    public double Value { get; set; } // Parameter value (normalized 0.0-1.0 or specific range)
    public double? BezierHandleInX { get; set; } // For bezier interpolation
    public double? BezierHandleInY { get; set; }
    public double? BezierHandleOutX { get; set; }
    public double? BezierHandleOutY { get; set; }
  }

  /// <summary>
  /// Represents the execution status of a macro.
  /// </summary>
  public class MacroExecutionStatus
  {
    public string MacroId { get; set; } = string.Empty;
    public string Status { get; set; } = "idle"; // "idle", "running", "completed", "failed"
    public int CurrentNodeIndex { get; set; }
    public int TotalNodes { get; set; }
    public string? CurrentNodeName { get; set; }
    public double Progress { get; set; }  // 0.0 to 1.0
    public string? ErrorMessage { get; set; }
    public System.DateTime? StartedAt { get; set; }
    public System.DateTime? CompletedAt { get; set; }
  }
}