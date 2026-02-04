using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Represents a mixer channel with volume, pan, and routing controls.
  /// </summary>
  public class MixerChannel
  {
    public string Id { get; set; } = string.Empty;
    public int ChannelNumber { get; set; }
    public string Name { get; set; } = string.Empty;
    public double PeakLevel { get; set; }
    public double RmsLevel { get; set; }
    public double Volume { get; set; } = 1.0; // 0.0 to 2.0 (0 = -∞ dB, 1.0 = 0 dB, 2.0 = +6 dB)
    public double Pan { get; set; }  // -1.0 (left) to 1.0 (right), 0.0 = center
    public bool IsMuted { get; set; }
    public bool IsSoloed { get; set; }
    public string MainDestination { get; set; } = "Master"; // "Master" or "SubGroup"
    public string? SubGroupId { get; set; }
    public Dictionary<string, double> SendLevels { get; set; } = new(); // send ID -> level 0.0-1.0
    public Dictionary<string, bool> SendEnabled { get; set; } = new(); // send ID -> enabled
  }

  /// <summary>
  /// Represents a mixer send bus (e.g., reverb send, delay send).
  /// Channels can send audio to these busses at varying levels.
  /// </summary>
  public class MixerSend
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty; // e.g., "Reverb Send", "Delay Send"
    public int BusNumber { get; set; } // 1-8 typically
    public double Volume { get; set; } = 1.0; // Send bus master volume
    public bool IsEnabled { get; set; } = true;
  }

  /// <summary>
  /// Represents a mixer return bus (receives audio from sends and returns it to master).
  /// Usually has effects applied (reverb, delay, etc.).
  /// </summary>
  public class MixerReturn
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty; // e.g., "Reverb Return", "Delay Return"
    public int BusNumber { get; set; } // Should match corresponding Send
    public double Volume { get; set; } = 1.0; // Return bus volume
    public double Pan { get; set; }  // Return bus pan (-1.0 to 1.0)
    public bool IsEnabled { get; set; } = true;
    public string? EffectChainId { get; set; } // Optional effect chain applied to return
  }

  /// <summary>
  /// Represents a mixer sub-group bus.
  /// Multiple channels can be routed to a sub-group, which is then routed to master.
  /// </summary>
  public class MixerSubGroup
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty; // e.g., "Drums", "Vocals", "Instruments"
    public int BusNumber { get; set; } // 1-8 typically
    public double Volume { get; set; } = 1.0; // Sub-group master volume
    public double Pan { get; set; }  // Sub-group pan (-1.0 to 1.0)
    public bool IsMuted { get; set; }
    public bool IsSoloed { get; set; }
    public string? EffectChainId { get; set; } // Optional effect chain applied to sub-group
    public List<string> ChannelIds { get; set; } = new(); // Channels routed to this sub-group
  }

  /// <summary>
  /// Represents the master bus (final output).
  /// </summary>
  public class MixerMaster
  {
    public string Id { get; set; } = string.Empty;
    public double Volume { get; set; } = 1.0; // Master volume (0.0 to 2.0)
    public double Pan { get; set; }  // Master pan (-1.0 to 1.0)
    public bool IsMuted { get; set; }
    public double PeakLevel { get; set; }
    public double RmsLevel { get; set; }
    public string? EffectChainId { get; set; } // Optional effect chain on master
  }

  /// <summary>
  /// Routing information for a mixer channel.
  /// </summary>
  public class ChannelRouting
  {
    public string ChannelId { get; set; } = string.Empty;

    // Main routing
    public RoutingDestination MainDestination { get; set; } = RoutingDestination.Master;
    public string? SubGroupId { get; set; } // If MainDestination is SubGroup

    // Send levels (channel ID -> send level 0.0-1.0)
    public Dictionary<string, double> SendLevels { get; set; } = new();

    // Send on/off (channel ID -> enabled)
    public Dictionary<string, bool> SendEnabled { get; set; } = new();
  }

  /// <summary>
  /// Routing destination for a channel.
  /// </summary>
  public enum RoutingDestination
  {
    Master = 0,      // Route directly to master bus
    SubGroup = 1     // Route to a sub-group bus
  }

  /// <summary>
  /// Complete mixer configuration and state.
  /// </summary>
  public class MixerState
  {
    public string Id { get; set; } = string.Empty;
    public string ProjectId { get; set; } = string.Empty;

    // Channels
    public List<MixerChannel> Channels { get; set; } = new();

    // Routing
    public List<ChannelRouting> ChannelRouting { get; set; } = new();

    // Sends
    public List<MixerSend> Sends { get; set; } = new();

    // Returns
    public List<MixerReturn> Returns { get; set; } = new();

    // Sub-groups
    public List<MixerSubGroup> SubGroups { get; set; } = new();

    // Master
    public MixerMaster Master { get; set; } = new();

    // Timestamps
    public DateTime Created { get; set; } = DateTime.UtcNow;
    public DateTime Modified { get; set; } = DateTime.UtcNow;
  }

  /// <summary>
  /// Mixer preset - saved mixer configuration.
  /// </summary>
  public class MixerPreset
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string ProjectId { get; set; } = string.Empty;
    public MixerState State { get; set; } = new();
    public DateTime Created { get; set; } = DateTime.UtcNow;
    public DateTime Modified { get; set; } = DateTime.UtcNow;
  }
}