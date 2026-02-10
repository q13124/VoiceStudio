// Phase 5.5: Chart Control Implementations
// Task 5.5.3: Pitch Contour visualization control

using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Shapes;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Pitch contour (F0) visualization control.
    /// Displays pitch over time with optional reference grid and note indicators.
    /// </summary>
    public sealed partial class PitchContourControl : UserControl
    {
        private Path? _contourPath;
        private Path? _referencePath;
        private const double DefaultMinFrequency = 50;  // Hz
        private const double DefaultMaxFrequency = 500; // Hz

        public static readonly DependencyProperty PitchDataProperty =
            DependencyProperty.Register(
                nameof(PitchData),
                typeof(object),
                typeof(PitchContourControl),
                new PropertyMetadata(null, OnDataChanged));

        public static readonly DependencyProperty ReferencePitchDataProperty =
            DependencyProperty.Register(
                nameof(ReferencePitchData),
                typeof(object),
                typeof(PitchContourControl),
                new PropertyMetadata(null, OnDataChanged));

        public static readonly DependencyProperty MinFrequencyProperty =
            DependencyProperty.Register(
                nameof(MinFrequency),
                typeof(double),
                typeof(PitchContourControl),
                new PropertyMetadata(DefaultMinFrequency, OnRangeChanged));

        public static readonly DependencyProperty MaxFrequencyProperty =
            DependencyProperty.Register(
                nameof(MaxFrequency),
                typeof(double),
                typeof(PitchContourControl),
                new PropertyMetadata(DefaultMaxFrequency, OnRangeChanged));

        public static readonly DependencyProperty ContourColorProperty =
            DependencyProperty.Register(
                nameof(ContourColor),
                typeof(Brush),
                typeof(PitchContourControl),
                new PropertyMetadata(null, OnVisualChanged));

        public static readonly DependencyProperty ReferenceColorProperty =
            DependencyProperty.Register(
                nameof(ReferenceColor),
                typeof(Brush),
                typeof(PitchContourControl),
                new PropertyMetadata(null, OnVisualChanged));

        public static readonly DependencyProperty ShowGridProperty =
            DependencyProperty.Register(
                nameof(ShowGrid),
                typeof(bool),
                typeof(PitchContourControl),
                new PropertyMetadata(true, OnVisualChanged));

        public static readonly DependencyProperty ShowNoteLinesProperty =
            DependencyProperty.Register(
                nameof(ShowNoteLines),
                typeof(bool),
                typeof(PitchContourControl),
                new PropertyMetadata(false, OnVisualChanged));

        public static readonly DependencyProperty UseLogScaleProperty =
            DependencyProperty.Register(
                nameof(UseLogScale),
                typeof(bool),
                typeof(PitchContourControl),
                new PropertyMetadata(true, OnRangeChanged));

        public static readonly DependencyProperty StrokeThicknessProperty =
            DependencyProperty.Register(
                nameof(StrokeThickness),
                typeof(double),
                typeof(PitchContourControl),
                new PropertyMetadata(2.0, OnVisualChanged));

        public PitchContourControl()
        {
            InitializeComponent();
            SizeChanged += OnSizeChanged;
            Loaded += OnLoaded;
        }

        /// <summary>
        /// Pitch data points (frequency in Hz over time).
        /// </summary>
        public object? PitchData
        {
            get => GetValue(PitchDataProperty);
            set => SetValue(PitchDataProperty, value);
        }

        /// <summary>
        /// Reference pitch data for comparison (optional).
        /// </summary>
        public object? ReferencePitchData
        {
            get => GetValue(ReferencePitchDataProperty);
            set => SetValue(ReferencePitchDataProperty, value);
        }

        /// <summary>
        /// Minimum frequency for the Y-axis scale.
        /// </summary>
        public double MinFrequency
        {
            get => (double)GetValue(MinFrequencyProperty);
            set => SetValue(MinFrequencyProperty, value);
        }

        /// <summary>
        /// Maximum frequency for the Y-axis scale.
        /// </summary>
        public double MaxFrequency
        {
            get => (double)GetValue(MaxFrequencyProperty);
            set => SetValue(MaxFrequencyProperty, value);
        }

        public Brush? ContourColor
        {
            get => (Brush?)GetValue(ContourColorProperty);
            set => SetValue(ContourColorProperty, value);
        }

        public Brush? ReferenceColor
        {
            get => (Brush?)GetValue(ReferenceColorProperty);
            set => SetValue(ReferenceColorProperty, value);
        }

        public bool ShowGrid
        {
            get => (bool)GetValue(ShowGridProperty);
            set => SetValue(ShowGridProperty, value);
        }

        public bool ShowNoteLines
        {
            get => (bool)GetValue(ShowNoteLinesProperty);
            set => SetValue(ShowNoteLinesProperty, value);
        }

        public bool UseLogScale
        {
            get => (bool)GetValue(UseLogScaleProperty);
            set => SetValue(UseLogScaleProperty, value);
        }

        public double StrokeThickness
        {
            get => (double)GetValue(StrokeThicknessProperty);
            set => SetValue(StrokeThicknessProperty, value);
        }

        private static void OnDataChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is PitchContourControl control)
            {
                control.UpdateContour();
            }
        }

        private static void OnRangeChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is PitchContourControl control)
            {
                control.UpdateContour();
            }
        }

        private static void OnVisualChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is PitchContourControl control)
            {
                control.UpdateVisuals();
            }
        }

        private void OnLoaded(object sender, RoutedEventArgs e)
        {
            InitializeControls();
        }

        private void OnSizeChanged(object sender, SizeChangedEventArgs e)
        {
            UpdateContour();
        }

        private void InitializeControls()
        {
            if (Content is not Grid grid)
                return;

            // Create reference path (behind main contour)
            _referencePath = new Path
            {
                StrokeThickness = StrokeThickness,
                StrokeLineJoin = PenLineJoin.Round,
                StrokeDashArray = new DoubleCollection { 4, 2 },
                Stroke = ReferenceColor ?? new SolidColorBrush(Windows.UI.Color.FromArgb(128, 128, 128, 128)),
                HorizontalAlignment = HorizontalAlignment.Stretch,
                VerticalAlignment = VerticalAlignment.Stretch
            };

            // Create main contour path
            _contourPath = new Path
            {
                StrokeThickness = StrokeThickness,
                StrokeLineJoin = PenLineJoin.Round,
                Stroke = ContourColor ?? new SolidColorBrush(Windows.UI.Color.FromArgb(255, 0, 200, 255)),
                HorizontalAlignment = HorizontalAlignment.Stretch,
                VerticalAlignment = VerticalAlignment.Stretch
            };

            grid.Children.Add(_referencePath);
            grid.Children.Add(_contourPath);

            UpdateContour();
        }

        private void UpdateContour()
        {
            UpdatePath(_contourPath, PitchData);
            UpdatePath(_referencePath, ReferencePitchData);
        }

        private void UpdatePath(Path? path, object? data)
        {
            if (path == null)
                return;

            var pitchPoints = GetPitchList(data);
            if (pitchPoints == null || pitchPoints.Count == 0)
            {
                path.Data = null;
                return;
            }

            var width = ActualWidth;
            var height = ActualHeight;

            if (width <= 0 || height <= 0)
                return;

            var pathGeometry = new PathGeometry();
            var pathFigure = new PathFigure();
            var isFirstPoint = true;

            var pointSpacing = width / Math.Max(1, pitchPoints.Count - 1);

            for (int i = 0; i < pitchPoints.Count; i++)
            {
                var frequency = pitchPoints[i];

                // Skip unvoiced segments (frequency = 0 or negative)
                if (frequency <= 0)
                {
                    // End current figure and start a new one for the next voiced segment
                    if (!isFirstPoint && pathFigure.Segments.Count > 0)
                    {
                        pathGeometry.Figures.Add(pathFigure);
                        pathFigure = new PathFigure();
                        isFirstPoint = true;
                    }
                    continue;
                }

                var x = i * pointSpacing;
                var y = FrequencyToY(frequency, height);

                if (isFirstPoint)
                {
                    pathFigure.StartPoint = new Windows.Foundation.Point(x, y);
                    isFirstPoint = false;
                }
                else
                {
                    pathFigure.Segments.Add(new LineSegment { Point = new Windows.Foundation.Point(x, y) });
                }
            }

            if (pathFigure.Segments.Count > 0 || !isFirstPoint)
            {
                pathGeometry.Figures.Add(pathFigure);
            }

            path.Data = pathGeometry;
        }

        private double FrequencyToY(double frequency, double height)
        {
            double normalized;

            if (UseLogScale)
            {
                // Logarithmic scale (more natural for pitch perception)
                var logMin = Math.Log(MinFrequency);
                var logMax = Math.Log(MaxFrequency);
                var logFreq = Math.Log(Math.Clamp(frequency, MinFrequency, MaxFrequency));
                normalized = (logFreq - logMin) / (logMax - logMin);
            }
            else
            {
                // Linear scale
                normalized = (frequency - MinFrequency) / (MaxFrequency - MinFrequency);
                normalized = Math.Clamp(normalized, 0, 1);
            }

            // Invert Y (higher frequency = higher on screen)
            return height * (1 - normalized);
        }

        private List<double>? GetPitchList(object? data)
        {
            if (data == null)
                return null;

            if (data is IList<double> doubleList)
                return doubleList.ToList();

            if (data is double[] doubleArray)
                return doubleArray.ToList();

            if (data is IList<float> floatList)
                return floatList.Select(f => (double)f).ToList();

            if (data is float[] floatArray)
                return floatArray.Select(f => (double)f).ToList();

            if (data is IEnumerable<double> doubleEnumerable)
                return doubleEnumerable.ToList();

            return null;
        }

        private void UpdateVisuals()
        {
            if (_contourPath != null)
            {
                _contourPath.Stroke = ContourColor ?? new SolidColorBrush(Windows.UI.Color.FromArgb(255, 0, 200, 255));
                _contourPath.StrokeThickness = StrokeThickness;
            }

            if (_referencePath != null)
            {
                _referencePath.Stroke = ReferenceColor ?? new SolidColorBrush(Windows.UI.Color.FromArgb(128, 128, 128, 128));
                _referencePath.StrokeThickness = StrokeThickness;
            }
        }

        /// <summary>
        /// Convert a frequency (Hz) to its musical note name.
        /// </summary>
        public static string FrequencyToNoteName(double frequency)
        {
            if (frequency <= 0)
                return "-";

            var noteNames = new[] { "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B" };

            // Calculate semitones from A4 (440 Hz)
            var semitones = 12 * Math.Log2(frequency / 440.0);
            var noteIndex = (int)Math.Round(semitones) + 9; // A is 9 semitones above C

            // Handle negative modulo
            var noteNameIndex = ((noteIndex % 12) + 12) % 12;
            var octave = 4 + (noteIndex + 3) / 12;

            if (noteIndex < 0)
                octave--;

            return $"{noteNames[noteNameIndex]}{octave}";
        }

        /// <summary>
        /// Get the frequency (Hz) for a given musical note.
        /// </summary>
        public static double NoteToFrequency(string noteName)
        {
            var noteMap = new Dictionary<string, int>
            {
                { "C", 0 }, { "C#", 1 }, { "Db", 1 },
                { "D", 2 }, { "D#", 3 }, { "Eb", 3 },
                { "E", 4 }, { "Fb", 4 }, { "E#", 5 },
                { "F", 5 }, { "F#", 6 }, { "Gb", 6 },
                { "G", 7 }, { "G#", 8 }, { "Ab", 8 },
                { "A", 9 }, { "A#", 10 }, { "Bb", 10 },
                { "B", 11 }, { "Cb", 11 }, { "B#", 0 }
            };

            if (string.IsNullOrWhiteSpace(noteName) || noteName.Length < 2)
                return 0;

            var notePartLength = char.IsDigit(noteName[1]) ? 1 : 2;
            var notePart = noteName.Substring(0, notePartLength);
            var octavePart = noteName.Substring(notePartLength);

            if (!noteMap.TryGetValue(notePart, out var noteIndex) || !int.TryParse(octavePart, out var octave))
                return 0;

            // Calculate semitones from A4
            var semitonesFromA4 = (noteIndex - 9) + (octave - 4) * 12;

            return 440.0 * Math.Pow(2, semitonesFromA4 / 12.0);
        }

        /// <summary>
        /// Clear all pitch data.
        /// </summary>
        public void Clear()
        {
            PitchData = null;
            ReferencePitchData = null;
        }
    }
}
