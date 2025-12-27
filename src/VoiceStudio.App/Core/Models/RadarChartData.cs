using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Represents radar chart data for multi-dimensional quality metrics visualization.
    /// Used to display voice quality characteristics in a radial/spider chart format.
    /// </summary>
    public class RadarChartData
    {
        /// <summary>
        /// List of axes (dimensions) for the radar chart.
        /// Each axis represents a quality metric (e.g., MOS, Similarity, Naturalness).
        /// </summary>
        public List<RadarAxis> Axes { get; set; } = new List<RadarAxis>();

        /// <summary>
        /// Data points for each axis.
        /// Values should be normalized to 0.0-1.0 range.
        /// </summary>
        public List<RadarDataPoint> Points { get; set; } = new List<RadarDataPoint>();

        /// <summary>
        /// Label for this radar chart dataset.
        /// </summary>
        public string Label { get; set; } = string.Empty;

        /// <summary>
        /// Color for rendering the radar chart polygon (as a hex or named color string).
        /// This is kept UI-agnostic so Core does not take a dependency on WinUI color types.
        /// </summary>
        public string Color { get; set; } = "#00FFFF";
    }

    /// <summary>
    /// Represents a single axis in a radar chart.
    /// </summary>
    public class RadarAxis
    {
        /// <summary>
        /// Name of the axis (e.g., "MOS", "Similarity", "Naturalness").
        /// </summary>
        public string Name { get; set; } = string.Empty;

        /// <summary>
        /// Maximum value for this axis (for normalization).
        /// </summary>
        public double MaxValue { get; set; } = 1.0;

        /// <summary>
        /// Minimum value for this axis (for normalization).
        /// </summary>
        public double MinValue { get; set; } = 0.0;
    }

    /// <summary>
    /// Represents a single data point on a radar chart axis.
    /// </summary>
    public class RadarDataPoint
    {
        /// <summary>
        /// Name of the axis this point belongs to.
        /// </summary>
        public string AxisName { get; set; } = string.Empty;

        /// <summary>
        /// Normalized value (0.0 to 1.0) for this axis.
        /// </summary>
        public double Value { get; set; } = 0.0;
    }
}

