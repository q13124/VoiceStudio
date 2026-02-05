// ============================================================================
// DesignTimeData.cs - Design-time sample data providers for XAML designer
// 
// AI GUIDELINES:
// - This file provides sample data for XAML design-time preview
// - All collections should have 2-5 sample items for realistic preview
// - Sample data should match real model structures exactly
// - DO NOT modify without updating corresponding ViewModels
// ============================================================================

using System.Collections.ObjectModel;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.DesignTime;

/// <summary>
/// Provides design-time sample data for XAML previews.
/// Use with d:DataContext="{d:DesignInstance Type=local:DesignTimeData, IsDesignTimeCreatable=True}"
/// </summary>
public class DesignTimeData
{
    // ============================================
    // Voice Profile Sample Data
    // ============================================
    
    public static ObservableCollection<VoiceProfile> SampleProfiles { get; } = new()
    {
        new VoiceProfile
        {
            Id = "profile-001",
            Name = "Professional Narrator",
            Language = "en-US",
            Emotion = "neutral",
            QualityScore = 4.5
        },
        new VoiceProfile
        {
            Id = "profile-002",
            Name = "Casual Conversational",
            Language = "en-US",
            Emotion = "happy",
            QualityScore = 4.2
        },
        new VoiceProfile
        {
            Id = "profile-003",
            Name = "News Anchor",
            Language = "en-GB",
            Emotion = "neutral",
            QualityScore = 4.8
        }
    };

    // ============================================
    // Timeline/Track Sample Data
    // ============================================
    
    public static ObservableCollection<AudioTrack> SampleTracks { get; } = new()
    {
        new AudioTrack
        {
            Id = "track-001",
            Name = "Main Narration",
            IsMuted = false,
            IsSolo = false,
            TrackNumber = 1
        },
        new AudioTrack
        {
            Id = "track-002",
            Name = "Background Music",
            IsMuted = false,
            IsSolo = false,
            TrackNumber = 2
        },
        new AudioTrack
        {
            Id = "track-003",
            Name = "Sound Effects",
            IsMuted = true,
            IsSolo = false,
            TrackNumber = 3
        }
    };

    // ============================================
    // Effect Chain Sample Data
    // ============================================
    
    public static ObservableCollection<string> SampleEffects { get; } = new()
    {
        "Noise Reduction",
        "Compressor",
        "EQ - Vocal Presence",
        "Reverb - Small Room",
        "Limiter"
    };

    // ============================================
    // Quality Metrics Sample Data
    // ============================================
    
    public static double SampleMosScore => 4.2;
    public static double SampleSnrDb => 35.5;
    public static double SampleSimilarityScore => 0.92;
    public static string SampleDuration => "00:03:45";
    public static int SampleSampleRate => 48000;

    // ============================================
    // Status/State Sample Data
    // ============================================
    
    public static bool IsProcessing => true;
    public static bool IsConnected => true;
    public static string StatusMessage => "Ready";
    public static double Progress => 0.65;
}
