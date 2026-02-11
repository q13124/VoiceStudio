using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Gateways;

namespace VoiceStudio.App.Tests.Mocks
{
  /// <summary>
  /// Mock implementation of <see cref="IVoiceGateway"/> for testing.
  /// </summary>
  public class MockVoiceGateway : IVoiceGateway
  {
    private readonly List<VoiceInfo> _voices = new();
    private readonly Dictionary<string, VoiceSynthesisResult> _synthesisResults = new();
    public List<VoiceSynthesisRequest> SynthesisRequests { get; } = new();
    public List<VoiceCloneRequest> CloneRequests { get; } = new();

    /// <summary>
    /// Adds a voice to the mock.
    /// </summary>
    public void AddVoice(VoiceInfo voice) => _voices.Add(voice);

    /// <summary>
    /// Sets up a synthesis result for a specific request text.
    /// </summary>
    public void SetupSynthesis(string text, VoiceSynthesisResult result)
    {
      _synthesisResults[text] = result;
    }

    /// <inheritdoc />
    public Task<GatewayResult<VoiceSynthesisResult>> SynthesizeAsync(VoiceSynthesisRequest request, CancellationToken cancellationToken = default)
    {
      SynthesisRequests.Add(request);

      if (_synthesisResults.TryGetValue(request.Text, out var result))
        return Task.FromResult(GatewayResult<VoiceSynthesisResult>.Ok(result));

      return Task.FromResult(GatewayResult<VoiceSynthesisResult>.Ok(new VoiceSynthesisResult
      {
        AudioPath = $"/output/synthesis_{Guid.NewGuid():N}.wav",
        AudioId = Guid.NewGuid().ToString(),
        DurationSeconds = request.Text.Length * 0.05,
        SampleRate = 22050,
        Format = "wav"
      }));
    }

    /// <inheritdoc />
    public Task<GatewayResult<bool>> SynthesizeStreamAsync(VoiceSynthesisRequest request, Stream outputStream, CancellationToken cancellationToken = default)
    {
      SynthesisRequests.Add(request);

      // Write some dummy data to the stream
      var dummyData = new byte[1024];
      outputStream.Write(dummyData, 0, dummyData.Length);

      return Task.FromResult(GatewayResult<bool>.Ok(true));
    }

    /// <inheritdoc />
    public Task<GatewayResult<VoiceCloneResult>> CloneVoiceAsync(VoiceCloneRequest request, CancellationToken cancellationToken = default)
    {
      CloneRequests.Add(request);

      return Task.FromResult(GatewayResult<VoiceCloneResult>.Ok(new VoiceCloneResult
      {
        VoiceId = Guid.NewGuid().ToString(),
        ProfileId = Guid.NewGuid().ToString(),
        Name = request.Name
      }));
    }

    /// <inheritdoc />
    public Task<GatewayResult<VoiceAnalysisResult>> AnalyzeAsync(string audioPath, CancellationToken cancellationToken = default)
    {
      return Task.FromResult(GatewayResult<VoiceAnalysisResult>.Ok(new VoiceAnalysisResult
      {
        Pitch = 150.0,
        Energy = 0.7,
        SpeechRate = 3.5,
        DetectedLanguage = "en",
        DetectedGender = "neutral"
      }));
    }

    /// <inheritdoc />
    public Task<GatewayResult<IReadOnlyList<VoiceInfo>>> GetAvailableVoicesAsync(string? engineId = null, CancellationToken cancellationToken = default)
    {
      var voices = engineId == null
          ? _voices.ToList()
          : _voices.Where(v => v.EngineId == engineId).ToList();

      return Task.FromResult(GatewayResult<IReadOnlyList<VoiceInfo>>.Ok(voices));
    }
  }

  /// <summary>
  /// Mock implementation of <see cref="IProfileGateway"/> for testing.
  /// </summary>
  public class MockProfileGateway : IProfileGateway
  {
    private readonly List<ProfileDetail> _profiles = new();
    private string? _defaultProfileId;

    /// <summary>
    /// Adds a profile to the mock.
    /// </summary>
    public void AddProfile(ProfileDetail profile)
    {
      _profiles.Add(profile);
    }

    /// <inheritdoc />
    public Task<GatewayResult<IReadOnlyList<ProfileInfo>>> GetAllAsync(CancellationToken cancellationToken = default)
    {
      var infos = _profiles.Select(p => new ProfileInfo
      {
        Id = p.Id,
        Name = p.Name,
        Description = p.Description,
        EngineId = p.EngineId,
        IsDefault = p.Id == _defaultProfileId,
        CreatedAt = p.CreatedAt,
        ModifiedAt = p.ModifiedAt
      }).ToList();

      return Task.FromResult(GatewayResult<IReadOnlyList<ProfileInfo>>.Ok(infos));
    }

    /// <inheritdoc />
    public Task<GatewayResult<ProfileDetail>> GetByIdAsync(string profileId, CancellationToken cancellationToken = default)
    {
      var profile = _profiles.FirstOrDefault(p => p.Id == profileId);
      if (profile != null)
        return Task.FromResult(GatewayResult<ProfileDetail>.Ok(profile));

      return Task.FromResult(GatewayResult<ProfileDetail>.Fail(
          new GatewayError("NOT_FOUND", $"Profile {profileId} not found")));
    }

    /// <inheritdoc />
    public Task<GatewayResult<ProfileDetail>> CreateAsync(ProfileCreateRequest request, CancellationToken cancellationToken = default)
    {
      var profile = new ProfileDetail
      {
        Id = Guid.NewGuid().ToString(),
        Name = request.Name,
        Description = request.Description,
        EngineId = request.EngineId,
        Settings = request.Settings,
        CreatedAt = DateTime.UtcNow
      };
      _profiles.Add(profile);
      return Task.FromResult(GatewayResult<ProfileDetail>.Ok(profile));
    }

    /// <inheritdoc />
    public Task<GatewayResult<ProfileDetail>> UpdateAsync(string profileId, ProfileUpdateRequest request, CancellationToken cancellationToken = default)
    {
      var index = _profiles.FindIndex(p => p.Id == profileId);
      if (index >= 0)
      {
        var existing = _profiles[index];
        var updated = new ProfileDetail
        {
          Id = existing.Id,
          Name = request.Name ?? existing.Name,
          Description = request.Description ?? existing.Description,
          EngineId = existing.EngineId,
          Settings = request.Settings ?? existing.Settings,
          CreatedAt = existing.CreatedAt,
          ModifiedAt = DateTime.UtcNow
        };
        _profiles[index] = updated;
        return Task.FromResult(GatewayResult<ProfileDetail>.Ok(updated));
      }

      return Task.FromResult(GatewayResult<ProfileDetail>.Fail(
          new GatewayError("NOT_FOUND", $"Profile {profileId} not found")));
    }

    /// <inheritdoc />
    public Task<GatewayResult<bool>> DeleteAsync(string profileId, CancellationToken cancellationToken = default)
    {
      var removed = _profiles.RemoveAll(p => p.Id == profileId) > 0;
      if (profileId == _defaultProfileId)
        _defaultProfileId = null;
      return Task.FromResult(GatewayResult<bool>.Ok(removed));
    }

    /// <inheritdoc />
    public Task<GatewayResult<bool>> ExportAsync(string profileId, Stream outputStream, CancellationToken cancellationToken = default)
    {
      var profile = _profiles.FirstOrDefault(p => p.Id == profileId);
      if (profile == null)
        return Task.FromResult(GatewayResult<bool>.Fail(new GatewayError("NOT_FOUND", $"Profile {profileId} not found")));

      // Write dummy data
      var data = System.Text.Encoding.UTF8.GetBytes($"{{\"id\":\"{profile.Id}\",\"name\":\"{profile.Name}\"}}");
      outputStream.Write(data, 0, data.Length);

      return Task.FromResult(GatewayResult<bool>.Ok(true));
    }

    /// <inheritdoc />
    public Task<GatewayResult<ProfileDetail>> ImportAsync(Stream inputStream, string fileName, CancellationToken cancellationToken = default)
    {
      var profile = new ProfileDetail
      {
        Id = Guid.NewGuid().ToString(),
        Name = Path.GetFileNameWithoutExtension(fileName),
        CreatedAt = DateTime.UtcNow
      };
      _profiles.Add(profile);
      return Task.FromResult(GatewayResult<ProfileDetail>.Ok(profile));
    }

    /// <inheritdoc />
    public Task<GatewayResult<ProfileDetail?>> GetDefaultAsync(CancellationToken cancellationToken = default)
    {
      var profile = _profiles.FirstOrDefault(p => p.Id == _defaultProfileId);
      return Task.FromResult(GatewayResult<ProfileDetail?>.Ok(profile));
    }

    /// <inheritdoc />
    public Task<GatewayResult<bool>> SetDefaultAsync(string profileId, CancellationToken cancellationToken = default)
    {
      if (!_profiles.Any(p => p.Id == profileId))
        return Task.FromResult(GatewayResult<bool>.Fail(new GatewayError("NOT_FOUND", $"Profile {profileId} not found")));

      _defaultProfileId = profileId;
      return Task.FromResult(GatewayResult<bool>.Ok(true));
    }
  }

  /// <summary>
  /// Mock implementation of <see cref="IJobGateway"/> for testing.
  /// </summary>
  public class MockJobGateway : IJobGateway
  {
    private readonly Dictionary<string, JobDetail> _jobs = new();

    /// <summary>
    /// Adds a job to the mock.
    /// </summary>
    public void AddJob(JobDetail job)
    {
      _jobs[job.Id] = job;
    }

    /// <summary>
    /// Updates a job's status.
    /// </summary>
    public void UpdateJobStatus(string jobId, JobStatus status, double? progress = null)
    {
      if (_jobs.TryGetValue(jobId, out var job))
      {
        job.Status = status;
        if (progress.HasValue)
          job.Progress = progress.Value;
      }
    }

    /// <inheritdoc />
    public Task<GatewayResult<IReadOnlyList<JobInfo>>> GetAllAsync(JobStatus? status = null, int? limit = null, CancellationToken cancellationToken = default)
    {
      var jobs = _jobs.Values.AsEnumerable();

      if (status.HasValue)
        jobs = jobs.Where(j => j.Status == status.Value);
      if (limit.HasValue)
        jobs = jobs.Take(limit.Value);

      var infos = jobs.Select(j => new JobInfo
      {
        Id = j.Id,
        Type = j.Type,
        Description = j.Description,
        Status = j.Status,
        Progress = j.Progress,
        CreatedAt = j.CreatedAt,
        StartedAt = j.StartedAt,
        CompletedAt = j.CompletedAt
      }).ToList();

      return Task.FromResult(GatewayResult<IReadOnlyList<JobInfo>>.Ok(infos));
    }

    /// <inheritdoc />
    public Task<GatewayResult<JobDetail>> GetByIdAsync(string jobId, CancellationToken cancellationToken = default)
    {
      if (_jobs.TryGetValue(jobId, out var job))
        return Task.FromResult(GatewayResult<JobDetail>.Ok(job));

      return Task.FromResult(GatewayResult<JobDetail>.Fail(
          new GatewayError("NOT_FOUND", $"Job {jobId} not found")));
    }

    /// <inheritdoc />
    public Task<GatewayResult<bool>> CancelAsync(string jobId, CancellationToken cancellationToken = default)
    {
      if (_jobs.TryGetValue(jobId, out var job))
      {
        job.Status = JobStatus.Cancelled;
        return Task.FromResult(GatewayResult<bool>.Ok(true));
      }

      return Task.FromResult(GatewayResult<bool>.Fail(
          new GatewayError("NOT_FOUND", $"Job {jobId} not found")));
    }

    /// <inheritdoc />
    public Task<GatewayResult<JobDetail>> RetryAsync(string jobId, CancellationToken cancellationToken = default)
    {
      if (_jobs.TryGetValue(jobId, out var job))
      {
        var newJob = new JobDetail
        {
          Id = Guid.NewGuid().ToString(),
          Type = job.Type,
          Description = job.Description,
          Status = JobStatus.Pending,
          Progress = 0,
          CreatedAt = DateTime.UtcNow,
          Input = job.Input
        };
        _jobs[newJob.Id] = newJob;
        return Task.FromResult(GatewayResult<JobDetail>.Ok(newJob));
      }

      return Task.FromResult(GatewayResult<JobDetail>.Fail(
          new GatewayError("NOT_FOUND", $"Job {jobId} not found")));
    }

    /// <inheritdoc />
    public Task<GatewayResult<JobQueueStatus>> GetQueueStatusAsync(CancellationToken cancellationToken = default)
    {
      var status = new JobQueueStatus
      {
        PendingCount = _jobs.Values.Count(j => j.Status == JobStatus.Pending),
        RunningCount = _jobs.Values.Count(j => j.Status == JobStatus.Running),
        CompletedCount = _jobs.Values.Count(j => j.Status == JobStatus.Completed),
        FailedCount = _jobs.Values.Count(j => j.Status == JobStatus.Failed),
        CurrentJob = _jobs.Values
            .Where(j => j.Status == JobStatus.Running)
            .Select(j => new JobInfo { Id = j.Id, Type = j.Type, Status = j.Status, Progress = j.Progress })
            .FirstOrDefault()
      };

      return Task.FromResult(GatewayResult<JobQueueStatus>.Ok(status));
    }

    /// <inheritdoc />
    public Task<GatewayResult<int>> ClearHistoryAsync(TimeSpan? olderThan = null, CancellationToken cancellationToken = default)
    {
      var cutoff = olderThan.HasValue ? DateTime.UtcNow - olderThan.Value : DateTime.MinValue;
      var toRemove = _jobs.Values
          .Where(j => j.Status == JobStatus.Completed || j.Status == JobStatus.Failed || j.Status == JobStatus.Cancelled)
          .Where(j => j.CompletedAt < cutoff)
          .Select(j => j.Id)
          .ToList();

      foreach (var id in toRemove)
        _jobs.Remove(id);

      return Task.FromResult(GatewayResult<int>.Ok(toRemove.Count));
    }
  }

  /// <summary>
  /// Mock implementation of <see cref="IEngineGateway"/> for testing.
  /// </summary>
  public class MockEngineGateway : IEngineGateway
  {
    private readonly List<EngineDetail> _engines = new();
    private readonly Dictionary<string, EngineParameterSchema> _schemas = new();
    private readonly Dictionary<string, EngineStatus> _statuses = new();
    private string? _activeEngineId;

    /// <summary>
    /// Adds an engine to the mock.
    /// </summary>
    public void AddEngine(EngineDetail engine, EngineParameterSchema? schema = null)
    {
      _engines.Add(engine);
      if (schema != null)
        _schemas[engine.Id] = schema;
      _statuses[engine.Id] = new EngineStatus
      {
        EngineId = engine.Id,
        Availability = engine.Availability,
        IsInitialized = false,
        IsProcessing = false
      };
    }

    /// <inheritdoc />
    public Task<GatewayResult<IReadOnlyList<EngineInfo>>> GetAllAsync(CancellationToken cancellationToken = default)
    {
      var infos = _engines.Select(e => new EngineInfo
      {
        Id = e.Id,
        Name = e.Name,
        Description = e.Description,
        Version = e.Version,
        Availability = e.Availability,
        IsActive = e.Id == _activeEngineId,
        Capabilities = e.Capabilities
      }).ToList();

      return Task.FromResult(GatewayResult<IReadOnlyList<EngineInfo>>.Ok(infos));
    }

    /// <inheritdoc />
    public Task<GatewayResult<EngineDetail>> GetByIdAsync(string engineId, CancellationToken cancellationToken = default)
    {
      var engine = _engines.FirstOrDefault(e => e.Id == engineId);
      if (engine != null)
        return Task.FromResult(GatewayResult<EngineDetail>.Ok(engine));

      return Task.FromResult(GatewayResult<EngineDetail>.Fail(
          new GatewayError("NOT_FOUND", $"Engine {engineId} not found")));
    }

    /// <inheritdoc />
    public Task<GatewayResult<EngineParameterSchema>> GetSchemaAsync(string engineId, CancellationToken cancellationToken = default)
    {
      if (_schemas.TryGetValue(engineId, out var schema))
        return Task.FromResult(GatewayResult<EngineParameterSchema>.Ok(schema));

      return Task.FromResult(GatewayResult<EngineParameterSchema>.Fail(
          new GatewayError("NOT_FOUND", $"Schema for engine {engineId} not found")));
    }

    /// <inheritdoc />
    public Task<GatewayResult<EngineStatus>> GetStatusAsync(string engineId, CancellationToken cancellationToken = default)
    {
      if (_statuses.TryGetValue(engineId, out var status))
        return Task.FromResult(GatewayResult<EngineStatus>.Ok(status));

      return Task.FromResult(GatewayResult<EngineStatus>.Fail(
          new GatewayError("NOT_FOUND", $"Engine {engineId} not found")));
    }

    /// <inheritdoc />
    public Task<GatewayResult<bool>> SetActiveAsync(string engineId, CancellationToken cancellationToken = default)
    {
      if (!_engines.Any(e => e.Id == engineId))
        return Task.FromResult(GatewayResult<bool>.Fail(new GatewayError("NOT_FOUND", $"Engine {engineId} not found")));

      _activeEngineId = engineId;
      return Task.FromResult(GatewayResult<bool>.Ok(true));
    }

    /// <inheritdoc />
    public Task<GatewayResult<EngineInfo?>> GetActiveAsync(CancellationToken cancellationToken = default)
    {
      if (_activeEngineId == null)
        return Task.FromResult(GatewayResult<EngineInfo?>.Ok(null));

      var engine = _engines.FirstOrDefault(e => e.Id == _activeEngineId);
      if (engine == null)
        return Task.FromResult(GatewayResult<EngineInfo?>.Ok(null));

      return Task.FromResult(GatewayResult<EngineInfo?>.Ok(new EngineInfo
      {
        Id = engine.Id,
        Name = engine.Name,
        Description = engine.Description,
        Version = engine.Version,
        Availability = engine.Availability,
        IsActive = true,
        Capabilities = engine.Capabilities
      }));
    }

    /// <inheritdoc />
    public Task<GatewayResult<bool>> InitializeAsync(string engineId, CancellationToken cancellationToken = default)
    {
      if (_statuses.TryGetValue(engineId, out var status))
      {
        _statuses[engineId] = new EngineStatus
        {
          EngineId = engineId,
          Availability = EngineAvailability.Available,
          IsInitialized = true,
          IsProcessing = false
        };
        return Task.FromResult(GatewayResult<bool>.Ok(true));
      }

      return Task.FromResult(GatewayResult<bool>.Fail(
          new GatewayError("NOT_FOUND", $"Engine {engineId} not found")));
    }
  }

  /// <summary>
  /// Mock implementation of <see cref="IAudioGateway"/> for testing.
  /// </summary>
  public class MockAudioGateway : IAudioGateway
  {
    private readonly Dictionary<string, AudioFileInfo> _files = new();
    private readonly Dictionary<string, byte[]> _fileData = new();
    public List<(string FileName, byte[] Data)> UploadedFiles { get; } = new();

    /// <summary>
    /// Adds an audio file to the mock.
    /// </summary>
    public void AddFile(AudioFileInfo file, byte[]? data = null)
    {
      _files[file.Id] = file;
      if (data != null)
        _fileData[file.Id] = data;
    }

    /// <inheritdoc />
    public Task<GatewayResult<AudioFileInfo>> UploadAsync(
        Stream fileStream,
        string fileName,
        Action<long, long>? progress = null,
        CancellationToken cancellationToken = default)
    {
      using var ms = new MemoryStream();
      fileStream.CopyTo(ms);
      var data = ms.ToArray();
      UploadedFiles.Add((fileName, data));

      var file = new AudioFileInfo
      {
        Id = Guid.NewGuid().ToString(),
        FileName = fileName,
        Format = System.IO.Path.GetExtension(fileName).TrimStart('.'),
        SizeBytes = data.Length,
        DurationSeconds = 5.0,
        SampleRate = 44100,
        Channels = 2,
        BitDepth = 16,
        CreatedAt = DateTime.UtcNow,
        Path = $"/audio/{fileName}"
      };
      _files[file.Id] = file;
      _fileData[file.Id] = data;

      progress?.Invoke(data.Length, data.Length);
      return Task.FromResult(GatewayResult<AudioFileInfo>.Ok(file));
    }

    /// <inheritdoc />
    public Task<GatewayResult<bool>> DownloadAsync(
        string audioId,
        Stream outputStream,
        Action<long, long>? progress = null,
        CancellationToken cancellationToken = default)
    {
      if (_fileData.TryGetValue(audioId, out var data))
      {
        outputStream.Write(data, 0, data.Length);
        progress?.Invoke(data.Length, data.Length);
        return Task.FromResult(GatewayResult<bool>.Ok(true));
      }

      if (_files.ContainsKey(audioId))
      {
        // File exists but no data - write dummy data
        var dummyData = new byte[1024];
        outputStream.Write(dummyData, 0, dummyData.Length);
        progress?.Invoke(dummyData.Length, dummyData.Length);
        return Task.FromResult(GatewayResult<bool>.Ok(true));
      }

      return Task.FromResult(GatewayResult<bool>.Fail(
          new GatewayError("NOT_FOUND", $"Audio {audioId} not found")));
    }

    /// <inheritdoc />
    public Task<GatewayResult<AudioFileInfo>> GetInfoAsync(
        string audioId,
        CancellationToken cancellationToken = default)
    {
      if (_files.TryGetValue(audioId, out var file))
        return Task.FromResult(GatewayResult<AudioFileInfo>.Ok(file));

      return Task.FromResult(GatewayResult<AudioFileInfo>.Fail(
          new GatewayError("NOT_FOUND", $"Audio {audioId} not found")));
    }

    /// <inheritdoc />
    public Task<GatewayResult<WaveformData>> GetWaveformAsync(
        string audioId,
        int samplesPerSecond = 100,
        CancellationToken cancellationToken = default)
    {
      if (!_files.TryGetValue(audioId, out var file))
        return Task.FromResult(GatewayResult<WaveformData>.Fail(
            new GatewayError("NOT_FOUND", $"Audio {audioId} not found")));

      var sampleCount = (int)(file.DurationSeconds * samplesPerSecond);
      var samples = new float[sampleCount];
      var random = new Random(audioId.GetHashCode());
      for (var i = 0; i < sampleCount; i++)
        samples[i] = (float)(random.NextDouble() * 2 - 1);

      return Task.FromResult(GatewayResult<WaveformData>.Ok(new WaveformData
      {
        AudioId = audioId,
        SamplesPerSecond = samplesPerSecond,
        DurationSeconds = file.DurationSeconds,
        Samples = samples,
        Min = -1.0f,
        Max = 1.0f
      }));
    }

    /// <inheritdoc />
    public Task<GatewayResult<bool>> DeleteAsync(
        string audioId,
        CancellationToken cancellationToken = default)
    {
      var removed = _files.Remove(audioId);
      _fileData.Remove(audioId);
      return Task.FromResult(GatewayResult<bool>.Ok(removed));
    }

    /// <inheritdoc />
    public Task<GatewayResult<AudioFileInfo>> ConvertAsync(
        string audioId,
        string targetFormat,
        CancellationToken cancellationToken = default)
    {
      if (!_files.TryGetValue(audioId, out var sourceFile))
        return Task.FromResult(GatewayResult<AudioFileInfo>.Fail(
            new GatewayError("NOT_FOUND", $"Audio {audioId} not found")));

      var convertedFile = new AudioFileInfo
      {
        Id = Guid.NewGuid().ToString(),
        FileName = System.IO.Path.ChangeExtension(sourceFile.FileName, targetFormat),
        Format = targetFormat,
        SizeBytes = sourceFile.SizeBytes,
        DurationSeconds = sourceFile.DurationSeconds,
        SampleRate = sourceFile.SampleRate,
        Channels = sourceFile.Channels,
        BitDepth = sourceFile.BitDepth,
        CreatedAt = DateTime.UtcNow,
        Path = $"/audio/converted_{Guid.NewGuid():N}.{targetFormat}"
      };

      _files[convertedFile.Id] = convertedFile;
      return Task.FromResult(GatewayResult<AudioFileInfo>.Ok(convertedFile));
    }

    /// <inheritdoc />
    public Task<GatewayResult<Stream>> StreamAsync(
        string audioId,
        CancellationToken cancellationToken = default)
    {
      if (_fileData.TryGetValue(audioId, out var data))
      {
        Stream stream = new MemoryStream(data);
        return Task.FromResult(GatewayResult<Stream>.Ok(stream));
      }

      if (_files.ContainsKey(audioId))
      {
        Stream stream = new MemoryStream(new byte[1024]);
        return Task.FromResult(GatewayResult<Stream>.Ok(stream));
      }

      return Task.FromResult(GatewayResult<Stream>.Fail(
          new GatewayError("NOT_FOUND", $"Audio {audioId} not found")));
    }
  }

  /// <summary>
  /// Mock implementation of <see cref="IProjectGateway"/> for testing.
  /// </summary>
  public class MockProjectGateway : IProjectGateway
  {
    private readonly Dictionary<string, ProjectDetail> _projects = new();
    private readonly List<string> _recentProjectIds = new();

    /// <summary>
    /// Adds a project to the mock.
    /// </summary>
    public void AddProject(ProjectDetail project)
    {
      _projects[project.Id] = project;
    }

    /// <inheritdoc />
    public Task<GatewayResult<IReadOnlyList<ProjectInfo>>> GetAllAsync(
        CancellationToken cancellationToken = default)
    {
      var infos = _projects.Values.Select(p => new ProjectInfo
      {
        Id = p.Id,
        Name = p.Name,
        Description = p.Description,
        CreatedAt = p.CreatedAt,
        ModifiedAt = p.ModifiedAt,
        IsDirty = p.IsDirty
      }).ToList();

      return Task.FromResult(GatewayResult<IReadOnlyList<ProjectInfo>>.Ok(infos));
    }

    /// <inheritdoc />
    public Task<GatewayResult<ProjectDetail>> GetByIdAsync(
        string projectId,
        CancellationToken cancellationToken = default)
    {
      if (_projects.TryGetValue(projectId, out var project))
      {
        if (!_recentProjectIds.Contains(projectId))
          _recentProjectIds.Insert(0, projectId);
        return Task.FromResult(GatewayResult<ProjectDetail>.Ok(project));
      }

      return Task.FromResult(GatewayResult<ProjectDetail>.Fail(
          new GatewayError("NOT_FOUND", $"Project {projectId} not found")));
    }

    /// <inheritdoc />
    public Task<GatewayResult<ProjectDetail>> CreateAsync(
        ProjectCreateRequest request,
        CancellationToken cancellationToken = default)
    {
      var project = new ProjectDetail
      {
        Id = Guid.NewGuid().ToString(),
        Name = request.Name,
        Description = request.Description,
        CreatedAt = DateTime.UtcNow,
        ModifiedAt = DateTime.UtcNow,
        Settings = request.Settings
      };
      _projects[project.Id] = project;
      _recentProjectIds.Insert(0, project.Id);
      return Task.FromResult(GatewayResult<ProjectDetail>.Ok(project));
    }

    /// <inheritdoc />
    public Task<GatewayResult<ProjectDetail>> UpdateAsync(
        string projectId,
        ProjectUpdateRequest request,
        CancellationToken cancellationToken = default)
    {
      if (!_projects.TryGetValue(projectId, out var project))
        return Task.FromResult(GatewayResult<ProjectDetail>.Fail(
            new GatewayError("NOT_FOUND", $"Project {projectId} not found")));

      if (request.Name != null)
        project.Name = request.Name;
      if (request.Description != null)
        project.Description = request.Description;
      if (request.Settings != null)
        project.Settings = request.Settings;

      project.ModifiedAt = DateTime.UtcNow;
      project.IsDirty = true;

      return Task.FromResult(GatewayResult<ProjectDetail>.Ok(project));
    }

    /// <inheritdoc />
    public Task<GatewayResult<bool>> DeleteAsync(
        string projectId,
        CancellationToken cancellationToken = default)
    {
      var removed = _projects.Remove(projectId);
      _recentProjectIds.Remove(projectId);
      return Task.FromResult(GatewayResult<bool>.Ok(removed));
    }

    /// <inheritdoc />
    public Task<GatewayResult<bool>> SaveAsync(
        string projectId,
        CancellationToken cancellationToken = default)
    {
      if (_projects.TryGetValue(projectId, out var project))
      {
        project.ModifiedAt = DateTime.UtcNow;
        project.IsDirty = false;
        return Task.FromResult(GatewayResult<bool>.Ok(true));
      }

      return Task.FromResult(GatewayResult<bool>.Fail(
          new GatewayError("NOT_FOUND", $"Project {projectId} not found")));
    }

    /// <inheritdoc />
    public Task<GatewayResult<bool>> ExportAsync(
        string projectId,
        Stream outputStream,
        string format = "vsproj",
        CancellationToken cancellationToken = default)
    {
      if (!_projects.ContainsKey(projectId))
        return Task.FromResult(GatewayResult<bool>.Fail(
            new GatewayError("NOT_FOUND", $"Project {projectId} not found")));

      // Write dummy export data
      var exportData = System.Text.Encoding.UTF8.GetBytes($"{{\"id\":\"{projectId}\",\"format\":\"{format}\"}}");
      outputStream.Write(exportData, 0, exportData.Length);
      return Task.FromResult(GatewayResult<bool>.Ok(true));
    }

    /// <inheritdoc />
    public Task<GatewayResult<ProjectDetail>> ImportAsync(
        Stream inputStream,
        string fileName,
        CancellationToken cancellationToken = default)
    {
      var project = new ProjectDetail
      {
        Id = Guid.NewGuid().ToString(),
        Name = System.IO.Path.GetFileNameWithoutExtension(fileName),
        Description = $"Imported from {fileName}",
        CreatedAt = DateTime.UtcNow,
        ModifiedAt = DateTime.UtcNow
      };

      _projects[project.Id] = project;
      _recentProjectIds.Insert(0, project.Id);
      return Task.FromResult(GatewayResult<ProjectDetail>.Ok(project));
    }

    /// <inheritdoc />
    public Task<GatewayResult<IReadOnlyList<ProjectInfo>>> GetRecentAsync(
        int limit = 10,
        CancellationToken cancellationToken = default)
    {
      var recent = _recentProjectIds
          .Take(limit)
          .Where(id => _projects.ContainsKey(id))
          .Select(id =>
          {
            var p = _projects[id];
            return new ProjectInfo
            {
              Id = p.Id,
              Name = p.Name,
              Description = p.Description,
              CreatedAt = p.CreatedAt,
              ModifiedAt = p.ModifiedAt,
              IsDirty = p.IsDirty
            };
          })
          .ToList();

      return Task.FromResult(GatewayResult<IReadOnlyList<ProjectInfo>>.Ok(recent));
    }
  }

  /// <summary>
  /// Mock implementation of <see cref="ITimelineGateway"/> for testing.
  /// </summary>
  public class MockTimelineGateway : ITimelineGateway
  {
    private readonly Dictionary<string, TimelineDetail> _timelines = new();

    /// <summary>
    /// Adds a timeline to the mock.
    /// </summary>
    public void AddTimeline(string projectId, TimelineDetail timeline)
    {
      _timelines[projectId] = timeline;
    }

    /// <inheritdoc />
    public Task<GatewayResult<TimelineDetail>> GetAsync(
        string projectId,
        CancellationToken cancellationToken = default)
    {
      if (_timelines.TryGetValue(projectId, out var timeline))
        return Task.FromResult(GatewayResult<TimelineDetail>.Ok(timeline));

      return Task.FromResult(GatewayResult<TimelineDetail>.Ok(new TimelineDetail
      {
        ProjectId = projectId,
        DurationSeconds = 0,
        FrameRate = 30.0,
        Tracks = new List<TrackInfo>(),
        Markers = new List<MarkerInfo>()
      }));
    }

    /// <inheritdoc />
    public Task<GatewayResult<TrackInfo>> AddTrackAsync(
        string projectId,
        TrackCreateRequest request,
        CancellationToken cancellationToken = default)
    {
      if (!_timelines.TryGetValue(projectId, out var timeline))
      {
        timeline = new TimelineDetail
        {
          ProjectId = projectId,
          DurationSeconds = 0,
          FrameRate = 30.0,
          Tracks = new List<TrackInfo>(),
          Markers = new List<MarkerInfo>()
        };
        _timelines[projectId] = timeline;
      }

      var track = new TrackInfo
      {
        Id = Guid.NewGuid().ToString(),
        Name = request.Name,
        Type = request.Type,
        Order = request.Order ?? ((List<TrackInfo>)timeline.Tracks).Count,
        IsMuted = false,
        IsLocked = false,
        Volume = 1.0f,
        Clips = new List<ClipInfo>()
      };

      ((List<TrackInfo>)timeline.Tracks).Add(track);
      return Task.FromResult(GatewayResult<TrackInfo>.Ok(track));
    }

    /// <inheritdoc />
    public Task<GatewayResult<bool>> RemoveTrackAsync(
        string projectId,
        string trackId,
        CancellationToken cancellationToken = default)
    {
      if (_timelines.TryGetValue(projectId, out var timeline))
      {
        var tracks = (List<TrackInfo>)timeline.Tracks;
        var removed = tracks.RemoveAll(t => t.Id == trackId) > 0;
        return Task.FromResult(GatewayResult<bool>.Ok(removed));
      }

      return Task.FromResult(GatewayResult<bool>.Ok(false));
    }

    /// <inheritdoc />
    public Task<GatewayResult<ClipInfo>> AddClipAsync(
        string projectId,
        string trackId,
        ClipCreateRequest request,
        CancellationToken cancellationToken = default)
    {
      if (!_timelines.TryGetValue(projectId, out var timeline))
        return Task.FromResult(GatewayResult<ClipInfo>.Fail(
            new GatewayError("NOT_FOUND", "Timeline not found")));

      var track = timeline.Tracks.FirstOrDefault(t => t.Id == trackId);
      if (track == null)
        return Task.FromResult(GatewayResult<ClipInfo>.Fail(
            new GatewayError("NOT_FOUND", "Track not found")));

      var clip = new ClipInfo
      {
        Id = Guid.NewGuid().ToString(),
        AudioId = request.AudioId,
        StartTime = request.StartTime,
        Duration = request.Duration ?? 5.0,
        TrimStart = 0,
        TrimEnd = 0,
        Volume = 1.0f,
        FadeIn = 0,
        FadeOut = 0,
        Label = request.Label
      };

      ((List<ClipInfo>)track.Clips).Add(clip);
      return Task.FromResult(GatewayResult<ClipInfo>.Ok(clip));
    }

    /// <inheritdoc />
    public Task<GatewayResult<ClipInfo>> UpdateClipAsync(
        string projectId,
        string trackId,
        string clipId,
        ClipUpdateRequest request,
        CancellationToken cancellationToken = default)
    {
      if (!_timelines.TryGetValue(projectId, out var timeline))
        return Task.FromResult(GatewayResult<ClipInfo>.Fail(
            new GatewayError("NOT_FOUND", "Timeline not found")));

      var track = timeline.Tracks.FirstOrDefault(t => t.Id == trackId);
      var clip = track?.Clips.FirstOrDefault(c => c.Id == clipId);

      if (clip == null)
        return Task.FromResult(GatewayResult<ClipInfo>.Fail(
            new GatewayError("NOT_FOUND", $"Clip {clipId} not found")));

      // Create a new clip with updated values (since ClipInfo properties have init setters)
      var updatedClip = new ClipInfo
      {
        Id = clip.Id,
        AudioId = clip.AudioId,
        StartTime = request.StartTime ?? clip.StartTime,
        Duration = request.Duration ?? clip.Duration,
        TrimStart = request.TrimStart ?? clip.TrimStart,
        TrimEnd = request.TrimEnd ?? clip.TrimEnd,
        Volume = request.Volume ?? clip.Volume,
        FadeIn = request.FadeIn ?? clip.FadeIn,
        FadeOut = request.FadeOut ?? clip.FadeOut,
        Label = request.Label ?? clip.Label
      };

      var clips = (List<ClipInfo>)track!.Clips;
      var index = clips.FindIndex(c => c.Id == clipId);
      if (index >= 0)
        clips[index] = updatedClip;

      return Task.FromResult(GatewayResult<ClipInfo>.Ok(updatedClip));
    }

    /// <inheritdoc />
    public Task<GatewayResult<bool>> RemoveClipAsync(
        string projectId,
        string trackId,
        string clipId,
        CancellationToken cancellationToken = default)
    {
      if (_timelines.TryGetValue(projectId, out var timeline))
      {
        var track = timeline.Tracks.FirstOrDefault(t => t.Id == trackId);
        if (track != null)
        {
          var clips = (List<ClipInfo>)track.Clips;
          var removed = clips.RemoveAll(c => c.Id == clipId) > 0;
          return Task.FromResult(GatewayResult<bool>.Ok(removed));
        }
      }

      return Task.FromResult(GatewayResult<bool>.Ok(false));
    }

    /// <inheritdoc />
    public Task<GatewayResult<MarkerInfo>> AddMarkerAsync(
        string projectId,
        MarkerCreateRequest request,
        CancellationToken cancellationToken = default)
    {
      if (!_timelines.TryGetValue(projectId, out var timeline))
      {
        timeline = new TimelineDetail
        {
          ProjectId = projectId,
          DurationSeconds = 0,
          FrameRate = 30.0,
          Tracks = new List<TrackInfo>(),
          Markers = new List<MarkerInfo>()
        };
        _timelines[projectId] = timeline;
      }

      var marker = new MarkerInfo
      {
        Id = Guid.NewGuid().ToString(),
        Label = request.Label,
        Time = request.Time,
        Color = request.Color,
        Description = request.Description
      };

      ((List<MarkerInfo>)timeline.Markers).Add(marker);
      return Task.FromResult(GatewayResult<MarkerInfo>.Ok(marker));
    }

    /// <inheritdoc />
    public Task<GatewayResult<bool>> RemoveMarkerAsync(
        string projectId,
        string markerId,
        CancellationToken cancellationToken = default)
    {
      if (_timelines.TryGetValue(projectId, out var timeline))
      {
        var markers = (List<MarkerInfo>)timeline.Markers;
        var removed = markers.RemoveAll(m => m.Id == markerId) > 0;
        return Task.FromResult(GatewayResult<bool>.Ok(removed));
      }

      return Task.FromResult(GatewayResult<bool>.Ok(false));
    }
  }
}
