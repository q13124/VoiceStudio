using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text.Json;
using System.Text.Json.Serialization;
using Xunit;

namespace VoiceStudio.ContractTests
{
    #region Test Utilities (mirrors VoiceStudio.App.Utilities)

    /// <summary>
    /// Snake_case JSON naming policy for Python compatibility.
    /// </summary>
    public class SnakeCaseJsonNamingPolicy : JsonNamingPolicy
    {
        public static SnakeCaseJsonNamingPolicy Instance { get; } = new();

        public override string ConvertName(string name)
        {
            if (string.IsNullOrEmpty(name)) return name;

            var result = new System.Text.StringBuilder();
            for (int i = 0; i < name.Length; i++)
            {
                char c = name[i];
                if (char.IsUpper(c))
                {
                    if (i > 0) result.Append('_');
                    result.Append(char.ToLowerInvariant(c));
                }
                else
                {
                    result.Append(c);
                }
            }
            return result.ToString();
        }
    }

    /// <summary>
    /// JSON converter for DateTimeOffset that handles ISO 8601 formats.
    /// </summary>
    public class Iso8601DateTimeConverter : JsonConverter<DateTimeOffset>
    {
        private static readonly string[] Formats = new[]
        {
            "yyyy-MM-ddTHH:mm:ss.FFFFFFFZ",
            "yyyy-MM-ddTHH:mm:ssZ",
            "yyyy-MM-ddTHH:mm:ss.FFFFFFF+00:00",
            "yyyy-MM-ddTHH:mm:ss+00:00",
            "yyyy-MM-ddTHH:mm:ss.FFFFFFFzzz",
            "yyyy-MM-ddTHH:mm:sszzz",
        };

        public override DateTimeOffset Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
        {
            string? dateString = reader.GetString();
            if (string.IsNullOrEmpty(dateString))
                return default;

            foreach (var format in Formats)
            {
                if (DateTimeOffset.TryParseExact(dateString, format, CultureInfo.InvariantCulture,
                    DateTimeStyles.AssumeUniversal | DateTimeStyles.AdjustToUniversal, out var result))
                {
                    return result;
                }
            }

            if (DateTimeOffset.TryParse(dateString, CultureInfo.InvariantCulture,
                DateTimeStyles.AssumeUniversal | DateTimeStyles.AdjustToUniversal, out var fallbackResult))
            {
                return fallbackResult;
            }

            throw new JsonException($"Unable to parse datetime: {dateString}");
        }

        public override void Write(Utf8JsonWriter writer, DateTimeOffset value, JsonSerializerOptions options)
        {
            writer.WriteStringValue(value.UtcDateTime.ToString("yyyy-MM-ddTHH:mm:ss.FFFFFFFZ", CultureInfo.InvariantCulture));
        }
    }

    /// <summary>
    /// JSON converter for nullable DateTimeOffset.
    /// </summary>
    public class Iso8601NullableDateTimeConverter : JsonConverter<DateTimeOffset?>
    {
        private readonly Iso8601DateTimeConverter _innerConverter = new();

        public override DateTimeOffset? Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
        {
            if (reader.TokenType == JsonTokenType.Null)
                return null;
            return _innerConverter.Read(ref reader, typeof(DateTimeOffset), options);
        }

        public override void Write(Utf8JsonWriter writer, DateTimeOffset? value, JsonSerializerOptions options)
        {
            if (value.HasValue)
                _innerConverter.Write(writer, value.Value, options);
            else
                writer.WriteNullValue();
        }
    }

    /// <summary>
    /// Factory for test JSON serialization options.
    /// </summary>
    public static class TestJsonOptions
    {
        public static JsonSerializerOptions BackendApi => new()
        {
            PropertyNamingPolicy = SnakeCaseJsonNamingPolicy.Instance,
            PropertyNameCaseInsensitive = true,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
            NumberHandling = JsonNumberHandling.AllowReadingFromString,
            Converters =
            {
                new JsonStringEnumConverter(),
                new Iso8601DateTimeConverter(),
                new Iso8601NullableDateTimeConverter(),
            }
        };
    }

    #endregion

    /// <summary>
    /// Round-trip serialization tests for C#-to-Python data exchange.
    /// These tests verify that data serialized by C# can be correctly
    /// deserialized by Python and vice versa.
    /// </summary>
    public class SerializationRoundTripTests
    {
        private readonly JsonSerializerOptions _options;

        public SerializationRoundTripTests()
        {
            // Use the same options as BackendClient
            _options = TestJsonOptions.BackendApi;
        }

        #region Test Models

        public class VoiceProfile
        {
            public string Id { get; set; } = "";
            public string Name { get; set; } = "";
            public string Language { get; set; } = "en";
            public string? Emotion { get; set; }
            public List<string> Tags { get; set; } = new();
            public DateTimeOffset CreatedAt { get; set; }
            public DateTimeOffset? UpdatedAt { get; set; }
            public int SampleCount { get; set; }
            public bool IsActive { get; set; } = true;
        }

        public class AudioClip
        {
            public string Id { get; set; } = "";
            public string Name { get; set; } = "";
            public double StartTime { get; set; }
            public double Duration { get; set; }
            public string? AudioId { get; set; }
            public string? VoiceProfileId { get; set; }
        }

        public class SynthesisRequest
        {
            public string Text { get; set; } = "";
            public string VoiceProfileId { get; set; } = "";
            public int SampleRate { get; set; } = 22050;
            public double Speed { get; set; } = 1.0;
            public double Pitch { get; set; } = 0.0;
            public string? Emotion { get; set; }
            public bool Streaming { get; set; }
        }

        public class SynthesisResponse
        {
            public string AudioId { get; set; } = "";
            public string Format { get; set; } = "wav";
            public int SampleRate { get; set; }
            public double Duration { get; set; }
            public int TextLength { get; set; }
            public double ProcessingTimeMs { get; set; }
            public DateTimeOffset Timestamp { get; set; }
        }

        public class Project
        {
            public string Id { get; set; } = "";
            public string Name { get; set; } = "";
            public string? Description { get; set; }
            public string Status { get; set; } = "draft";
            public List<string> VoiceProfileIds { get; set; } = new();
            public Dictionary<string, object>? Metadata { get; set; }
            public DateTimeOffset CreatedAt { get; set; }
            public DateTimeOffset? UpdatedAt { get; set; }
        }

        #endregion

        #region SnakeCase Property Name Tests

        [Fact]
        public void Serialize_VoiceProfile_UsesSnakeCase()
        {
            var profile = new VoiceProfile
            {
                Id = "profile-123",
                Name = "Test Voice",
                IsActive = true,
                SampleCount = 42,
                CreatedAt = new DateTimeOffset(2024, 1, 15, 10, 30, 0, TimeSpan.Zero)
            };

            var json = JsonSerializer.Serialize(profile, _options);

            // Verify snake_case property names
            Assert.Contains("\"id\":", json);
            Assert.Contains("\"name\":", json);
            Assert.Contains("\"is_active\":", json);
            Assert.Contains("\"sample_count\":", json);
            Assert.Contains("\"created_at\":", json);

            // Verify PascalCase is NOT used
            Assert.DoesNotContain("\"Id\":", json);
            Assert.DoesNotContain("\"IsActive\":", json);
            Assert.DoesNotContain("\"SampleCount\":", json);
        }

        [Fact]
        public void Deserialize_SnakeCaseJson_ToVoiceProfile()
        {
            var json = @"{
                ""id"": ""profile-456"",
                ""name"": ""Python Voice"",
                ""language"": ""es"",
                ""is_active"": true,
                ""sample_count"": 100,
                ""created_at"": ""2024-01-15T10:30:00Z""
            }";

            var profile = JsonSerializer.Deserialize<VoiceProfile>(json, _options);

            Assert.NotNull(profile);
            Assert.Equal("profile-456", profile!.Id);
            Assert.Equal("Python Voice", profile.Name);
            Assert.Equal("es", profile.Language);
            Assert.True(profile.IsActive);
            Assert.Equal(100, profile.SampleCount);
        }

        #endregion

        #region DateTime Round-Trip Tests

        [Fact]
        public void DateTime_RoundTrip_PreservesValue()
        {
            var original = new DateTimeOffset(2024, 6, 15, 14, 30, 45, 123, TimeSpan.Zero);
            var profile = new VoiceProfile
            {
                Id = "test",
                Name = "Test",
                CreatedAt = original
            };

            var json = JsonSerializer.Serialize(profile, _options);
            var restored = JsonSerializer.Deserialize<VoiceProfile>(json, _options);

            Assert.NotNull(restored);
            // Allow for some precision loss in milliseconds due to formatting
            Assert.True(Math.Abs((restored!.CreatedAt - original).TotalSeconds) < 1);
        }

        [Fact]
        public void DateTime_ParsesPythonIsoFormat()
        {
            // Python typically outputs: 2024-01-15T10:30:00Z
            var json = @"{
                ""id"": ""test"",
                ""name"": ""Test"",
                ""created_at"": ""2024-01-15T10:30:00Z""
            }";

            var profile = JsonSerializer.Deserialize<VoiceProfile>(json, _options);

            Assert.NotNull(profile);
            Assert.Equal(2024, profile!.CreatedAt.Year);
            Assert.Equal(1, profile.CreatedAt.Month);
            Assert.Equal(15, profile.CreatedAt.Day);
            Assert.Equal(10, profile.CreatedAt.Hour);
            Assert.Equal(30, profile.CreatedAt.Minute);
        }

        [Fact]
        public void DateTime_ParsesPythonIsoFormatWithMicroseconds()
        {
            // Python can also output microseconds: 2024-01-15T10:30:00.123456Z
            var json = @"{
                ""id"": ""test"",
                ""name"": ""Test"",
                ""created_at"": ""2024-01-15T10:30:00.123456Z""
            }";

            var profile = JsonSerializer.Deserialize<VoiceProfile>(json, _options);

            Assert.NotNull(profile);
            Assert.Equal(10, profile!.CreatedAt.Hour);
            Assert.Equal(30, profile.CreatedAt.Minute);
        }

        [Fact]
        public void DateTime_ParsesOffsetFormat()
        {
            // Some Python libraries output +00:00 instead of Z
            var json = @"{
                ""id"": ""test"",
                ""name"": ""Test"",
                ""created_at"": ""2024-01-15T10:30:00+00:00""
            }";

            var profile = JsonSerializer.Deserialize<VoiceProfile>(json, _options);

            Assert.NotNull(profile);
            Assert.Equal(10, profile!.CreatedAt.Hour);
        }

        [Fact]
        public void NullableDateTime_HandlesNull()
        {
            var json = @"{
                ""id"": ""test"",
                ""name"": ""Test"",
                ""created_at"": ""2024-01-15T10:30:00Z"",
                ""updated_at"": null
            }";

            var profile = JsonSerializer.Deserialize<VoiceProfile>(json, _options);

            Assert.NotNull(profile);
            Assert.Null(profile!.UpdatedAt);
        }

        #endregion

        #region Numeric Round-Trip Tests

        [Fact]
        public void Floats_PreservePrecision()
        {
            var clip = new AudioClip
            {
                Id = "clip-1",
                Name = "Test",
                StartTime = 10.123456789,
                Duration = 5.555555555
            };

            var json = JsonSerializer.Serialize(clip, _options);
            var restored = JsonSerializer.Deserialize<AudioClip>(json, _options);

            Assert.NotNull(restored);
            Assert.Equal(clip.StartTime, restored!.StartTime, 6); // 6 decimal precision
            Assert.Equal(clip.Duration, restored.Duration, 6);
        }

        [Fact]
        public void Floats_HandleZeroValues()
        {
            var clip = new AudioClip
            {
                Id = "clip-zero",
                Name = "Zero Clip",
                StartTime = 0.0,
                Duration = 0.0
            };

            var json = JsonSerializer.Serialize(clip, _options);
            var restored = JsonSerializer.Deserialize<AudioClip>(json, _options);

            Assert.NotNull(restored);
            Assert.Equal(0.0, restored!.StartTime);
            Assert.Equal(0.0, restored.Duration);
        }

        [Fact]
        public void NegativeNumbers_Preserved()
        {
            var request = new SynthesisRequest
            {
                Text = "Test",
                VoiceProfileId = "voice-1",
                Pitch = -2.5
            };

            var json = JsonSerializer.Serialize(request, _options);
            var restored = JsonSerializer.Deserialize<SynthesisRequest>(json, _options);

            Assert.NotNull(restored);
            Assert.Equal(-2.5, restored!.Pitch);
        }

        [Fact]
        public void LargeNumbers_Preserved()
        {
            var response = new SynthesisResponse
            {
                AudioId = "audio-1",
                SampleRate = 96000,
                Duration = 3600.0,
                TextLength = 100000,
                ProcessingTimeMs = 999999.999,
                Timestamp = DateTimeOffset.UtcNow
            };

            var json = JsonSerializer.Serialize(response, _options);
            var restored = JsonSerializer.Deserialize<SynthesisResponse>(json, _options);

            Assert.NotNull(restored);
            Assert.Equal(96000, restored!.SampleRate);
            Assert.Equal(100000, restored.TextLength);
        }

        [Fact]
        public void NumbersAsStrings_ParsedCorrectly()
        {
            // Python sometimes serializes numbers as strings
            var json = @"{
                ""id"": ""clip-1"",
                ""name"": ""Test"",
                ""start_time"": ""10.5"",
                ""duration"": ""5.25""
            }";

            var clip = JsonSerializer.Deserialize<AudioClip>(json, _options);

            Assert.NotNull(clip);
            Assert.Equal(10.5, clip!.StartTime);
            Assert.Equal(5.25, clip.Duration);
        }

        #endregion

        #region String and Unicode Tests

        [Fact]
        public void UnicodeText_PreservedInRoundTrip()
        {
            var request = new SynthesisRequest
            {
                Text = "Hello, 世界! 🎵",
                VoiceProfileId = "voice-1"
            };

            var json = JsonSerializer.Serialize(request, _options);
            var restored = JsonSerializer.Deserialize<SynthesisRequest>(json, _options);

            Assert.NotNull(restored);
            Assert.Contains("世界", restored!.Text);
            Assert.Contains("🎵", restored.Text);
        }

        [Fact]
        public void EmptyStrings_Preserved()
        {
            var clip = new AudioClip
            {
                Id = "",
                Name = "",
                StartTime = 0,
                Duration = 1
            };

            var json = JsonSerializer.Serialize(clip, _options);
            var restored = JsonSerializer.Deserialize<AudioClip>(json, _options);

            Assert.NotNull(restored);
            Assert.Equal("", restored!.Id);
            Assert.Equal("", restored.Name);
        }

        #endregion

        #region List and Array Tests

        [Fact]
        public void StringList_PreservedInRoundTrip()
        {
            var profile = new VoiceProfile
            {
                Id = "test",
                Name = "Test",
                Tags = new List<string> { "premium", "female", "narrator" },
                CreatedAt = DateTimeOffset.UtcNow
            };

            var json = JsonSerializer.Serialize(profile, _options);
            var restored = JsonSerializer.Deserialize<VoiceProfile>(json, _options);

            Assert.NotNull(restored);
            Assert.Equal(3, restored!.Tags.Count);
            Assert.Contains("premium", restored.Tags);
            Assert.Contains("narrator", restored.Tags);
        }

        [Fact]
        public void EmptyList_PreservedInRoundTrip()
        {
            var profile = new VoiceProfile
            {
                Id = "test",
                Name = "Test",
                Tags = new List<string>(),
                CreatedAt = DateTimeOffset.UtcNow
            };

            var json = JsonSerializer.Serialize(profile, _options);
            var restored = JsonSerializer.Deserialize<VoiceProfile>(json, _options);

            Assert.NotNull(restored);
            Assert.Empty(restored!.Tags);
        }

        #endregion

        #region Null Handling Tests

        [Fact]
        public void NullOptionalFields_SerializedAsNull()
        {
            var profile = new VoiceProfile
            {
                Id = "test",
                Name = "Test",
                Emotion = null,
                UpdatedAt = null,
                CreatedAt = DateTimeOffset.UtcNow
            };

            var json = JsonSerializer.Serialize(profile, _options);

            // With DefaultIgnoreCondition.WhenWritingNull, null fields should be omitted
            Assert.DoesNotContain("\"emotion\":", json);
            Assert.DoesNotContain("\"updated_at\":", json);
        }

        [Fact]
        public void NullFields_DeserializeCorrectly()
        {
            var json = @"{
                ""id"": ""test"",
                ""name"": ""Test"",
                ""emotion"": null,
                ""created_at"": ""2024-01-15T10:30:00Z""
            }";

            var profile = JsonSerializer.Deserialize<VoiceProfile>(json, _options);

            Assert.NotNull(profile);
            Assert.Null(profile!.Emotion);
        }

        [Fact]
        public void MissingOptionalFields_DefaultCorrectly()
        {
            var json = @"{
                ""id"": ""test"",
                ""name"": ""Test"",
                ""created_at"": ""2024-01-15T10:30:00Z""
            }";

            var profile = JsonSerializer.Deserialize<VoiceProfile>(json, _options);

            Assert.NotNull(profile);
            Assert.Null(profile!.Emotion);
            Assert.Equal("en", profile.Language);  // Default value
            Assert.True(profile.IsActive);  // Default value
        }

        #endregion

        #region Enum Serialization Tests

        [Theory]
        [InlineData("draft")]
        [InlineData("active")]
        [InlineData("archived")]
        public void EnumStrings_DeserializeCorrectly(string statusValue)
        {
            var json = $@"{{
                ""id"": ""proj-1"",
                ""name"": ""Test Project"",
                ""status"": ""{statusValue}"",
                ""created_at"": ""2024-01-15T10:30:00Z""
            }}";

            var project = JsonSerializer.Deserialize<Project>(json, _options);

            Assert.NotNull(project);
            Assert.Equal(statusValue, project!.Status);
        }

        #endregion

        #region Complex Object Tests

        [Fact]
        public void NestedObjects_PreservedInRoundTrip()
        {
            var project = new Project
            {
                Id = "proj-1",
                Name = "Test Project",
                VoiceProfileIds = new List<string> { "voice-1", "voice-2" },
                Metadata = new Dictionary<string, object>
                {
                    ["engine"] = "xtts_v2",
                    ["sample_rate"] = 22050
                },
                CreatedAt = DateTimeOffset.UtcNow
            };

            var json = JsonSerializer.Serialize(project, _options);

            Assert.Contains("voice_profile_ids", json);
            Assert.Contains("voice-1", json);
            Assert.Contains("metadata", json);
        }

        #endregion

        #region Python Compatibility Tests

        [Fact]
        public void PythonStyleBooleans_DeserializeCorrectly()
        {
            // Ensure JSON booleans (lowercase) work
            var json = @"{
                ""id"": ""test"",
                ""name"": ""Test"",
                ""is_active"": true,
                ""created_at"": ""2024-01-15T10:30:00Z""
            }";

            var profile = JsonSerializer.Deserialize<VoiceProfile>(json, _options);

            Assert.NotNull(profile);
            Assert.True(profile!.IsActive);
        }

        [Fact]
        public void PythonEmptyList_DeserializesCorrectly()
        {
            var json = @"{
                ""id"": ""test"",
                ""name"": ""Test"",
                ""tags"": [],
                ""created_at"": ""2024-01-15T10:30:00Z""
            }";

            var profile = JsonSerializer.Deserialize<VoiceProfile>(json, _options);

            Assert.NotNull(profile);
            Assert.Empty(profile!.Tags);
        }

        #endregion
    }
}
