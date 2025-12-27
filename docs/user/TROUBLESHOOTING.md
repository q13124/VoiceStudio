# VoiceStudio Quantum+ Troubleshooting Guide

Comprehensive solutions to common issues and problems.

**Last Updated:** 2025-01-28  
**Version:** 1.0

## Table of Contents

1. [Common Issues](#common-issues)
2. [Engine Loading Problems](#engine-loading-problems)
3. [Audio Playback Issues](#audio-playback-issues)
4. [Performance Problems](#performance-problems)
5. [Memory and VRAM Issues](#memory-and-vram-issues)
6. [Quality Features Issues](#quality-features-issues)
7. [UI Features Issues](#ui-features-issues)
8. [Error Messages](#error-messages)
9. [How to Report Bugs](#how-to-report-bugs)
10. [Log File Locations](#log-file-locations)

---

## Common Issues

### Application Won't Start

**Symptoms:**
- VoiceStudio doesn't launch
- Crashes immediately on startup
- Error dialog appears

**Solutions:**

1. **Check System Requirements:**
   - Verify Windows 10 (1903+) or Windows 11
   - Check .NET 8 Runtime installed
   - Verify sufficient disk space

2. **Run as Administrator:**
   - Right-click VoiceStudio shortcut
   - Select "Run as administrator"
   - Try launching again

3. **Check Antivirus:**
   - Temporarily disable antivirus
   - Add VoiceStudio to exceptions
   - Re-enable antivirus

4. **Check Logs:**
   - Location: `%LocalAppData%\VoiceStudio\logs\`
   - Review latest log file
   - Look for error messages

5. **Reinstall:**
   - Uninstall VoiceStudio
   - Delete installation directory
   - Restart computer
   - Reinstall from fresh download

### Backend Connection Failed

**Symptoms:**
- "Backend not connected" message
- Cannot synthesize audio
- API calls fail

**Solutions:**

1. **Check Backend Status:**
   - Open Diagnostics panel
   - Check "Backend Status"
   - Should show "Connected"

2. **Restart Backend:**
   - Close VoiceStudio completely
   - Restart VoiceStudio
   - Backend starts automatically

3. **Check Port Availability:**
   - Default port: 8000
   - Ensure port not in use
   - Check firewall settings

4. **Check Python:**
   - Verify Python 3.10+ installed
   - Check Python in PATH
   - Test: `python --version`

5. **Check Dependencies:**
   - Backend requires Python packages
   - Install manually: `pip install -r backend/requirements.txt`
   - Check for errors

6. **Check Logs:**
   - Backend logs: `backend/logs/` or `%LocalAppData%\VoiceStudio\logs\`
   - Review for Python errors
   - Check for missing dependencies

7. **Manual Backend Start:**
   - Open terminal in `backend/` directory
   - Run: `python -m uvicorn api.main:app --host 127.0.0.1 --port 8000`
   - Check for errors

### Voice Synthesis Fails

**Symptoms:**
- Synthesis button does nothing
- Error message appears
- No audio generated

**Solutions:**

1. **Check Engine Availability:**
   - Open Diagnostics panel
   - Check "Available Engines"
   - At least one engine should be listed

2. **Check Voice Profile:**
   - Verify profile has reference audio
   - Check reference audio is valid WAV file
   - Re-upload reference audio if needed

3. **Check Text Input:**
   - Ensure text is not empty
   - Check for special characters
   - Try simple text first

4. **Check Engine Selection:**
   - Verify engine is selected
   - Try different engine
   - Check engine-specific requirements

5. **Check Quality Settings:**
   - Try "Fast" quality mode first
   - "Ultra" mode may be too slow
   - Adjust quality settings

6. **Check Backend Logs:**
   - Review backend logs for errors
   - Look for engine-specific errors
   - Check for missing models

7. **Restart Application:**
   - Close VoiceStudio
   - Restart application
   - Try synthesis again

### Projects Won't Save

**Symptoms:**
- Save button doesn't work
- "Save failed" error
- Project not saved

**Solutions:**

1. **Check File Permissions:**
   - Verify write permissions to project location
   - Try saving to different location
   - Check disk space

2. **Check File Path:**
   - Ensure path is valid
   - Avoid special characters in path
   - Use shorter path if needed

3. **Check Project File:**
   - Verify `.voiceproj` file not locked
   - Close file if open elsewhere
   - Check file permissions

4. **Save As:**
   - Use "Save As" instead of "Save"
   - Choose new location
   - Verify save succeeds

5. **Check Logs:**
   - Review application logs
   - Look for file I/O errors
   - Check for permission errors

---

## Engine Loading Problems

### Engines Not Discovered

**Symptoms:**
- No engines available
- "No engines found" message
- Cannot synthesize

**Solutions:**

1. **Check Engine Directory:**
   - Location: `engines/audio/` (in installation directory)
   - Verify engine folders exist
   - Check for `engine.manifest.json` files

2. **Verify Manifests:**
   - Check JSON syntax is valid
   - Verify required fields present
   - Compare with working engines

3. **Check File Permissions:**
   - Ensure read permissions
   - Check file not locked
   - Verify directory accessible

4. **Restart Application:**
   - Close VoiceStudio
   - Restart application
   - Engines reload on startup

5. **Manual Engine Registration:**
   - Check backend logs for errors
   - Verify engine dependencies installed
   - Check engine-specific requirements

### Engine Fails to Load

**Symptoms:**
- Engine appears in list but fails
- Error when selecting engine
- "Engine unavailable" message

**Solutions:**

1. **Check Engine Dependencies:**
   - Engine may need additional packages
   - Check backend logs for missing dependencies
   - Install manually: `pip install [package]`

2. **Check Engine Models:**
   - Some engines require model files
   - Verify models downloaded
   - Check model paths in manifest

3. **Check GPU Availability:**
   - Some engines require GPU
   - Verify GPU available
   - Check GPU drivers updated

4. **Check Engine Logs:**
   - Review engine-specific logs
   - Look for initialization errors
   - Check for resource errors

5. **Try Different Engine:**
   - Test with other engines
   - Isolate engine-specific issue
   - Report engine-specific bug

### Engine Performance Issues

**Symptoms:**
- Synthesis very slow
- High CPU/GPU usage
- Out of memory errors

**Solutions:**

1. **Reduce Quality Settings:**
   - Use "Fast" instead of "Ultra"
   - Disable quality enhancement
   - Reduce batch size

2. **Check System Resources:**
   - Close other applications
   - Check available RAM
   - Monitor GPU memory

3. **GPU Acceleration:**
   - Enable GPU if available
   - Update GPU drivers
   - Check GPU compatibility

4. **Engine-Specific:**
   - Tortoise: Very slow, use for final only
   - XTTS: Faster, good quality
   - Chatterbox: Balanced speed/quality

5. **Reduce Text Length:**
   - Shorter text = faster synthesis
   - Split long text into chunks
   - Use batch processing for multiple

---

## Audio Playback Issues

### No Audio Playback

**Symptoms:**
- No sound when playing
- Playback appears to work but no audio
- Audio levels show but no sound

**Solutions:**

1. **Check Audio Device:**
   - Verify output device selected
   - Check device not muted
   - Test device with other applications

2. **Check Volume:**
   - Check system volume
   - Check application volume
   - Check track/mixer volume

3. **Check Audio Settings:**
   - Open Settings > Audio
   - Verify output device
   - Check sample rate compatibility

4. **Check Audio File:**
   - Verify audio file exists
   - Check file format supported
   - Test file in other player

5. **Restart Audio System:**
   - Close VoiceStudio
   - Restart audio service (if possible)
   - Restart VoiceStudio

### Audio Clicks/Pops

**Symptoms:**
- Audio has clicks or pops
- Distortion during playback
- Audio artifacts

**Solutions:**

1. **Increase Buffer Size:**
   - Open Settings > Audio
   - Increase buffer size
   - Restart application

2. **Check Sample Rate:**
   - Verify sample rate matches
   - Use 44.1 kHz or 48 kHz
   - Avoid mismatched rates

3. **Check CPU Usage:**
   - Close other applications
   - Reduce real-time effects
   - Freeze tracks if needed

4. **Check Audio Drivers:**
   - Update audio drivers
   - Use ASIO drivers if available
   - Check driver compatibility

5. **Apply Denoise Effect:**
   - Use Denoise effect
   - Reduce artifact strength
   - Process audio

### Audio Out of Sync

**Symptoms:**
- Audio and video out of sync
- Timeline playback mismatch
- Playhead and audio don't match

**Solutions:**

1. **Check Sample Rate:**
   - Verify all audio same sample rate
   - Resample if needed
   - Use consistent sample rate

2. **Check Latency:**
   - Reduce buffer size
   - Use low-latency drivers
   - Check audio device latency

3. **Resync Playhead:**
   - Click timeline to reset
   - Use "Go to Start" (Home)
   - Restart playback

4. **Check Project Settings:**
   - Verify project sample rate
   - Check timebase settings
   - Review project configuration

---

## Performance Problems

### Application Slow/Unresponsive

**Symptoms:**
- UI freezes
- Slow response to clicks
- High CPU usage

**Solutions:**

1. **Close Other Applications:**
   - Free up system resources
   - Close unnecessary programs
   - Check Task Manager

2. **Reduce Project Complexity:**
   - Freeze tracks
   - Render effects
   - Use proxy files

3. **Check System Resources:**
   - Monitor RAM usage
   - Check disk space
   - Verify CPU not maxed

4. **Disable Real-Time Effects:**
   - Render effects instead
   - Reduce real-time processing
   - Use offline processing

5. **Update Drivers:**
   - Update GPU drivers
   - Update audio drivers
   - Check for system updates

### High Memory Usage

**Symptoms:**
- Application uses lots of RAM
- Out of memory errors
- System slowdown

**Solutions:**

1. **Close Unused Projects:**
   - Close projects not in use
   - Limit open projects
   - Save and close

2. **Clear Cache:**
   - Clear application cache
   - Delete temporary files
   - Restart application

3. **Reduce Timeline Complexity:**
   - Remove unused tracks
   - Delete unused clips
   - Simplify project

4. **Use Proxy Files:**
   - Enable proxy files for large projects
   - Reduce memory usage
   - Improve performance

5. **Increase Virtual Memory:**
   - Increase page file size
   - Add more RAM if possible
   - Check system limits

### Slow Synthesis

**Symptoms:**
- Synthesis takes very long
- Timeout errors
- Slow processing

**Solutions:**

1. **Reduce Quality Settings:**
   - Use "Fast" for previews
   - Use "High" only for final
   - Disable quality enhancement for previews

2. **Use Faster Engine:**
   - XTTS v2: Faster
   - Chatterbox: Balanced
   - Tortoise: Slowest (highest quality)

3. **Reduce Text Length:**
   - Shorter text = faster
   - Split long text
   - Process in chunks

4. **Enable GPU:**
   - Use GPU acceleration
   - Update GPU drivers
   - Check GPU compatibility

5. **Check System Resources:**
   - Close other applications
   - Free up CPU/GPU
   - Check for bottlenecks

---

## Memory and VRAM Issues

### High Memory Usage

**Symptoms:**
- Application uses excessive memory
- System becomes slow
- Out of memory errors

**Solutions:**

1. **Monitor Memory Usage:**
   - Open Diagnostics panel
   - Check "Current Memory" and "Peak Memory"
   - Review memory breakdown (UI, Audio, Engines)

2. **Reduce Memory Usage:**
   - Close unused projects
   - Unload unused engines
   - Clear logs if they're large
   - Restart application periodically

3. **Check for Memory Leaks:**
   - Monitor memory over time
   - If memory gradually increases, restart application
   - Report persistent memory leaks

### VRAM Warnings

**Symptoms:**
- VRAM warning appears in Diagnostics panel
- Orange warning banner: "VRAM Usage: X% used"
- Critical warning: "High VRAM Usage: X% used"

**Solutions:**

1. **For Warning Level (60-80%):**
   - Monitor VRAM usage
   - Close other GPU-intensive applications
   - Consider reducing engine quality settings

2. **For Critical Level (>80%):**
   - **Immediately close other GPU-intensive applications**
   - Reduce engine quality settings
   - Unload unused engines
   - Restart application if needed

3. **Prevent VRAM Issues:**
   - Use lower quality settings for multiple engines
   - Close other GPU applications before using VoiceStudio
   - Monitor VRAM usage in Diagnostics panel
   - Use CPU-based engines if VRAM is limited

**VRAM Monitoring:**
- Real-time VRAM usage displayed in Diagnostics panel
- Automatic warnings at 60% and 80% thresholds
- Suggestions provided in warning messages

**See Also:**
- [Performance Guide](PERFORMANCE_GUIDE.md) - Performance optimization
- [Diagnostics Panel](../user/USER_MANUAL.md#diagnostics-panel) - Monitoring tools

## Quality Features Issues

### Multi-Pass Synthesis Issues

**Symptoms:**
- Multi-pass synthesis takes too long
- Quality not improving with more passes
- Synthesis fails during multi-pass
- No quality improvement between passes

**Solutions:**

1. **Reduce Number of Passes:**
   - Start with 3 passes instead of 5-10
   - Enable adaptive stopping
   - Check if quality plateaus early

2. **Check Quality Metrics:**
   - Review quality scores per pass
   - If quality plateaus, stop early
   - Use adaptive stopping feature

3. **Check System Resources:**
   - Multi-pass uses more memory
   - Ensure sufficient RAM available
   - Close other applications

4. **Try Different Focus Preset:**
   - Naturalness focus for general use
   - Similarity focus for voice matching
   - Artifact focus for artifact reduction

5. **Check Reference Audio Quality:**
   - Poor reference audio limits improvement
   - Pre-process reference audio first
   - Ensure reference quality score ≥ 0.7

6. **Check Engine Compatibility:**
   - Some engines benefit more from multi-pass
   - Try different engine
   - Check engine-specific recommendations

### Reference Audio Pre-Processing Issues

**Symptoms:**
- Pre-processing fails
- No quality improvement after pre-processing
- Optimal segments not selected
- Recommendations not helpful

**Solutions:**

1. **Check Input Audio Quality:**
   - Ensure audio is in WAV format
   - Check sample rate (44.1 kHz or higher)
   - Verify audio is not corrupted

2. **Review Analysis Results:**
   - Check quality score (should be ≥ 7.0)
   - Review detected issues
   - Address recommendations

3. **Adjust Pre-Processing Settings:**
   - Increase max segments if needed
   - Adjust min segment duration
   - Enable auto-enhance

4. **Check Audio Duration:**
   - Minimum 5 seconds recommended
   - 10-30 seconds optimal
   - Too short audio may not process well

5. **Verify Processed Audio:**
   - Compare original and processed
   - Check quality improvement percentage
   - Use processed audio for cloning

### Artifact Removal Issues

**Symptoms:**
- Artifacts not detected
- Artifacts not removed
- Audio quality degraded after removal
- False positives (artifacts detected incorrectly)

**Solutions:**

1. **Use Preview Mode First:**
   - Always preview before applying
   - Review detected artifacts
   - Check severity and confidence

2. **Adjust Artifact Types:**
   - Select specific artifact types
   - Don't select all if not needed
   - Use comprehensive preset for all types

3. **Try Different Repair Presets:**
   - Click removal for clicks/pops
   - Distortion repair for distortion
   - Comprehensive for all artifacts

4. **Check Sensitivity:**
   - Lower sensitivity if false positives
   - Higher sensitivity if missing artifacts
   - Default sensitivity usually best

5. **Verify Quality Improvement:**
   - Check quality improvement percentage
   - Compare original and repaired audio
   - If quality degraded, don't apply

6. **Multiple Passes:**
   - Some artifacts require multiple passes
   - Apply removal again if needed
   - Check for remaining artifacts

### Voice Characteristic Analysis Issues

**Symptoms:**
- Analysis fails
- Similarity score too low
- Characteristics not preserved
- Recommendations not helpful

**Solutions:**

1. **Check Audio Quality:**
   - Ensure audio is clear
   - Check for artifacts
   - Remove artifacts before analysis

2. **Verify Reference Audio:**
   - Use high-quality reference audio
   - Ensure reference matches target voice
   - Pre-process reference if needed

3. **Review Analysis Results:**
   - Check similarity score (≥ 0.85 is good)
   - Review pitch/formant differences
   - Follow recommendations

4. **Adjust Synthesis Parameters:**
   - Try different engine
   - Adjust quality settings
   - Use multi-pass synthesis

5. **Use Prosody Control:**
   - If intonation doesn't match
   - Apply prosody control
   - Re-analyze after adjustment

### Prosody Control Issues

**Symptoms:**
- Prosody not applied correctly
- Intonation sounds unnatural
- Stress markers not working
- Quality degraded after prosody control

**Solutions:**

1. **Choose Correct Intonation Pattern:**
   - Rising for questions
   - Falling for statements
   - Flat for narration
   - Match pattern to content

2. **Review Stress Markers:**
   - Ensure words match audio
   - Use primary stress for emphasis
   - Don't over-stress words

3. **Check Pitch Contour:**
   - Custom pitch contour may conflict
   - Use intonation pattern instead
   - Simplify if too complex

4. **Preview Before Applying:**
   - Always preview prosody
   - Listen to adjustments
   - Adjust if unnatural

5. **Verify Quality:**
   - Check quality improvement
   - If quality degraded, don't apply
   - Try different settings

### Face Enhancement Issues

**Symptoms:**
- Face enhancement fails
- No quality improvement
- Face looks unnatural after enhancement
- Processing takes too long

**Solutions:**

1. **Choose Correct Preset:**
   - Portrait for headshots
   - Full body for full-body images
   - Close-up for extreme close-ups

2. **Check Image Quality:**
   - Ensure face is visible
   - Check image resolution
   - Verify image format

3. **Enable Multi-Stage:**
   - Multi-stage provides better quality
   - Takes longer but worth it
   - Disable if too slow

4. **Review Analysis:**
   - Check original quality scores
   - Review recommendations
   - Address issues before enhancement

5. **Verify Enhancement:**
   - Compare original and enhanced
   - Check quality improvement
   - If unnatural, try different preset

### Temporal Consistency Issues

**Symptoms:**
- Video still flickers after processing
- Too much smoothing (loses detail)
- Processing takes too long
- No quality improvement

**Solutions:**

1. **Adjust Smoothing Strength:**
   - Start with 0.5 (default)
   - Increase if flickering persists (0.7-0.8)
   - Decrease if losing detail (0.3-0.4)

2. **Check Original Video Quality:**
   - Poor input limits improvement
   - Ensure video is stable
   - Check frame rate consistency

3. **Enable Motion Consistency:**
   - Ensures motion continuity
   - Reduces jitter
   - Recommended for all videos

4. **Review Analysis:**
   - Check frame stability score
   - Review flicker/jitter scores
   - Address detected artifacts

5. **Multiple Passes:**
   - Severe flickering may need multiple passes
   - Apply temporal consistency again
   - Use stronger smoothing on second pass

### Training Data Optimization Issues

**Symptoms:**
- Optimization fails
- No quality improvement
- Optimal samples not selected
- Recommendations not helpful

**Solutions:**

1. **Check Dataset Quality:**
   - Ensure audio files are valid
   - Check file formats (WAV recommended)
   - Verify files not corrupted

2. **Review Analysis Results:**
   - Check quality/diversity scores
   - Review optimal samples selected
   - Follow recommendations

3. **Adjust Optimization Settings:**
   - Enable all analysis options
   - Adjust sample selection criteria
   - Review augmentation suggestions

4. **Verify Optimized Dataset:**
   - Check quality improvement estimate
   - Review sample count
   - Ensure diversity maintained

5. **Use Optimized Dataset:**
   - Use optimized dataset for training
   - Compare with original dataset
   - Verify training improvement

### Post-Processing Pipeline Issues

**Symptoms:**
- Post-processing fails
- No quality improvement
- Processing takes too long
- Quality degraded after processing

**Solutions:**

1. **Select Appropriate Stages:**
   - Don't select all stages if not needed
   - Use recommended stages
   - Preview before applying

2. **Enable Optimize Order:**
   - Automatically optimizes stage order
   - Better results
   - Recommended for all cases

3. **Preview First:**
   - Always preview before applying
   - Review stage-by-stage results
   - Check total quality improvement

4. **Check Stage Results:**
   - Review quality per stage
   - Remove stages that don't help
   - Keep only beneficial stages

5. **Verify Final Quality:**
   - Compare original and processed
   - Check total quality improvement
   - If degraded, adjust stages

6. **Reduce Stages:**
   - Too many stages may degrade quality
   - Use only needed stages
   - Less is sometimes more

### Real-Time Quality Preview Issues

**Symptoms:**
- Quality preview not showing
- Updates not appearing
- Preview shows incorrect data
- Preview slows down processing

**Solutions:**

1. **Check WebSocket Connection:**
   - Ensure backend is connected
   - Check WebSocket endpoint
   - Verify connection status

2. **Enable Quality Topic:**
   - Quality preview requires quality topic
   - Check WebSocket subscription
   - Verify topic is enabled

3. **Check Processing Status:**
   - Quality preview only during processing
   - Ensure operation is running
   - Check for errors

4. **Review Update Frequency:**
   - Updates may be infrequent
   - Wait for updates
   - Check if processing is stuck

5. **Disable if Causing Issues:**
   - Quality preview may slow processing
   - Disable if not needed
   - Re-enable when needed

### General Quality Features Tips

1. **Always Preview First:**
   - Preview artifacts/post-processing before applying
   - Saves time if improvement minimal
   - Helps understand changes

2. **Check Quality Scores:**
   - Monitor quality metrics
   - Verify improvements
   - Don't apply if quality degraded

3. **Start Simple:**
   - Use default settings first
   - Adjust only if needed
   - Don't over-configure

4. **Combine Features Wisely:**
   - Use features in recommended order
   - Don't over-process
   - Each feature adds time

5. **Check System Resources:**
   - Quality features use more resources
   - Ensure sufficient RAM/VRAM
   - Close other applications

6. **Review Logs:**
   - Check logs for errors
   - Review quality feature logs
   - Report issues if persistent

### Batch Processing Issues

**Symptoms:**
- Batch jobs not starting
- Jobs failing during processing
- Progress not updating
- Jobs stuck in "Pending" or "Running" state

**Solutions:**

1. **Check Job Configuration:**
   - Verify voice profile is valid and has reference audio
   - Ensure engine is available and loaded
   - Check quality settings are valid
   - Review job configuration before starting

2. **Check System Resources:**
   - Ensure sufficient RAM available
   - Check disk space for output files
   - Verify GPU memory if using GPU engines
   - Close other applications if needed

3. **Monitor Job Status:**
   - Check per-job status in batch panel
   - Review error messages for failed jobs
   - Check backend logs for detailed errors
   - Verify individual job settings

4. **Handle Failed Jobs:**
   - Review error message for failed job
   - Check if it's a transient error (retry)
   - Verify job settings are correct
   - Try processing failed text individually
   - Retry failed jobs after fixing issues

5. **Check Text Input:**
   - Verify all texts are valid (not empty, proper encoding)
   - Check text length within limits
   - Review special characters that might cause issues
   - Test individual texts if batch fails

6. **Large Batch Optimization:**
   - Process in smaller batches (50-100 texts at a time)
   - Monitor system resources during processing
   - Pause/resume as needed
   - Save progress frequently

### Training Module Issues

**Symptoms:**
- Training job fails to start
- Training crashes during execution
- Training doesn't improve quality
- Model export fails
- Training progress not updating

**Solutions:**

1. **Check Dataset:**
   - Verify audio files are valid WAV format
   - Check transcripts match audio files
   - Ensure minimum dataset size (30 minutes recommended)
   - Verify file paths are accessible
   - Check for corrupted files

2. **Check Training Configuration:**
   - Verify training settings (epochs, batch size, learning rate)
   - Ensure settings are within acceptable ranges
   - Check engine compatibility
   - Review advanced settings if configured

3. **Check System Resources:**
   - Ensure sufficient VRAM/GPU memory
   - Check available disk space (training requires significant space)
   - Verify sufficient RAM available
   - Close other GPU-intensive applications

4. **Monitor Training Progress:**
   - Check training logs for errors
   - Monitor loss values (should decrease)
   - Watch for overfitting signs
   - Check validation metrics

5. **Training Quality Issues:**
   - Increase training data if quality poor
   - Adjust learning rate if loss not decreasing
   - Try different batch sizes
   - Increase epochs if needed
   - Review training data quality

6. **Model Export Issues:**
   - Check disk space for export
   - Verify export format is valid
   - Check file permissions for export location
   - Review export logs for errors

### Transcription Issues

**Symptoms:**
- Transcription fails to start
- Transcription takes too long
- Transcription results are inaccurate
- Transcription times out
- No transcription results

**Solutions:**

1. **Check Audio File:**
   - Verify audio file format is supported
   - Check audio quality (clear speech, minimal noise)
   - Ensure file is not corrupted
   - Check file size (very large files may timeout)

2. **Check Transcription Settings:**
   - Verify language is correctly selected
   - Check transcription model is appropriate
   - Review timestamp settings if enabled
   - Ensure output format is valid

3. **Check System Resources:**
   - Transcription can be resource-intensive
   - Ensure sufficient RAM and CPU available
   - Close other applications if needed
   - Use smaller model if system is limited

4. **Improve Accuracy:**
   - Use high-quality audio with clear speech
   - Select correct language
   - Use larger transcription model for better accuracy
   - Remove background noise before transcription
   - Check for audio artifacts that might confuse transcription

5. **Handle Timeouts:**
   - Split large files into smaller segments
   - Use smaller transcription model
   - Process in batches if needed
   - Check system performance

### Timeline Editing Issues

**Symptoms:**
- Timeline is laggy or unresponsive
- Clips won't move or resize
- Playback is choppy
- Waveforms not displaying
- Snap-to-grid not working

**Solutions:**

1. **Performance Issues:**
   - Reduce number of visible tracks
   - Lower zoom level for better performance
   - Close other panels if needed
   - Simplify project (remove unused clips)
   - Disable real-time waveform rendering if slow

2. **Clip Manipulation Issues:**
   - Check if clips are locked
   - Verify snap-to-grid settings
   - Check for overlapping clips
   - Ensure sufficient timeline zoom level

3. **Playback Issues:**
   - Check audio device is selected
   - Verify audio files exist and are accessible
   - Check for corrupted audio files
   - Restart audio engine if needed

4. **Waveform Display:**
   - Waveforms generate on first view
   - Large files may take time to render
   - Check disk I/O performance
   - Clear waveform cache if corrupted

5. **Project Complexity:**
   - Large projects may be slower
   - Archive old tracks/clips
   - Use proxy files for large audio
   - Optimize project structure

### Effects and Mixer Issues

**Symptoms:**
- Effects not applying correctly
- Mixer controls not responding
- Audio routing not working
- Effects causing audio artifacts
- Sends/returns not functioning

**Solutions:**

1. **Effect Application Issues:**
   - Verify effect is enabled in chain
   - Check effect order (effects process top to bottom)
   - Ensure track is not muted
   - Verify effect parameters are valid
   - Try removing and re-adding effect

2. **Mixer Control Issues:**
   - Refresh mixer view
   - Check track routing is correct
   - Verify audio device is selected
   - Check track mute/solo state
   - Restart audio engine if needed

3. **Routing Issues:**
   - Verify send/return buses are created
   - Check routing destinations are correct
   - Ensure send levels are not zero
   - Verify return buses are active
   - Check sub-group routing

4. **Audio Artifacts from Effects:**
   - Check effect parameters (may be too extreme)
   - Try different effect presets
   - Adjust effect order in chain
   - Disable effects one by one to isolate issue
   - Review effect documentation for proper settings

5. **Performance with Effects:**
   - Reduce number of real-time effects
   - Render effects instead of real-time
   - Simplify effect chains
   - Close other applications
   - Use less CPU-intensive effects

---

## Additional Libraries and Tools Issues

### Library Installation Problems

**Symptoms:**
- Import errors for new libraries
- Quality features not working
- RVC engine fails to load
- Performance monitoring unavailable

**Solutions:**

1. **Install Missing Libraries:**
   ```powershell
   cd "C:\Program Files\VoiceStudio"
   .venv\Scripts\Activate.ps1
   pip install -r requirements_missing_libraries.txt
   ```

2. **Check Python Version:**
   - Ensure Python 3.10+ is installed
   - Verify virtual environment is activated
   - Test: `python --version`

3. **C++ Compiler Required:**
   - Some libraries (fairseq, pyworld) require C++ compiler
   - Install Visual Studio Build Tools
   - Or install Microsoft C++ Build Tools
   - Restart after installation

4. **faiss-cpu Installation Issues:**
   - May require conda environment
   - Try: `conda install -c pytorch faiss-cpu`
   - Or use pre-built wheel: `pip install faiss-cpu --no-cache-dir`

5. **fairseq Installation Issues:**
   - Requires C++ compiler
   - May need to install from source
   - Check fairseq GitHub for latest installation instructions

6. **pyworld Installation Issues:**
   - Requires C++ compiler
   - May need Visual Studio Build Tools
   - Try: `pip install pyworld --no-cache-dir`

### Library Import Errors

**Symptoms:**
- "ModuleNotFoundError" for new libraries
- Features unavailable
- Error messages about missing dependencies

**Solutions:**

1. **Verify Installation:**
   ```python
   python -c "import essentia_tensorflow; print('OK')"
   python -c "import voicefixer; print('OK')"
   python -c "import deepfilternet; print('OK')"
   ```

2. **Check Virtual Environment:**
   - Ensure you're in the correct virtual environment
   - Verify libraries are installed in `.venv`
   - Check: `pip list | grep essentia`

3. **Reinstall Problematic Libraries:**
   ```powershell
   pip uninstall <library_name>
   pip install <library_name> --no-cache-dir
   ```

4. **Check System Dependencies:**
   - Some libraries need system libraries
   - Check library documentation for requirements
   - Install missing system dependencies

### RVC Engine Library Issues

**Symptoms:**
- RVC engine fails to initialize
- "fairseq not found" errors
- "faiss not found" errors
- RVC synthesis fails

**Solutions:**

1. **Install RVC Dependencies:**
   ```powershell
   pip install fairseq==0.12.2
   pip install faiss-cpu==1.7.4
   pip install pyworld==0.3.2
   pip install praat-parselmouth>=0.4.3
   ```

2. **Verify faiss Installation:**
   - Test: `python -c "import faiss; print('OK')"`
   - If fails, try: `pip install faiss-cpu --no-cache-dir`
   - May need conda: `conda install -c pytorch faiss-cpu`

3. **Check fairseq Compatibility:**
   - Ensure Python 3.10+ (fairseq 0.12.2 requirement)
   - Verify PyTorch is installed
   - Check CUDA compatibility if using GPU

4. **pyworld Installation:**
   - Requires C++ compiler
   - Install Visual Studio Build Tools
   - Restart terminal after installation
   - Reinstall: `pip install pyworld --no-cache-dir`

### Quality Metrics Library Issues

**Symptoms:**
- Quality metrics unavailable
- "pesq not found" errors
- "pystoi not found" errors
- Quality scores not calculated

**Solutions:**

1. **Install Quality Libraries:**
   ```powershell
   pip install pesq>=0.0.4
   pip install pystoi>=0.3.3
   pip install essentia-tensorflow>=1.1.1
   ```

2. **Verify Installation:**
   ```python
   python -c "import pesq; print('pesq OK')"
   python -c "import pystoi; print('pystoi OK')"
   ```

3. **Check Audio Format:**
   - pesq requires specific sample rates (8000 or 16000 Hz)
   - Ensure audio is properly formatted
   - Check audio file compatibility

### Audio Enhancement Library Issues

**Symptoms:**
- Voice enhancement not working
- "voicefixer not found" errors
- "deepfilternet not found" errors
- Enhancement features unavailable

**Solutions:**

1. **Install Enhancement Libraries:**
   ```powershell
   pip install voicefixer>=0.1.2
   pip install deepfilternet>=0.5.0
   pip install resampy>=0.4.2
   pip install pyrubberband>=0.3.0
   ```

2. **Check GPU Availability:**
   - Some enhancement libraries benefit from GPU
   - Verify CUDA is installed (if using GPU)
   - Check GPU drivers are up to date

3. **Verify Audio Format:**
   - Ensure audio is in supported format
   - Check sample rate compatibility
   - Verify audio file is not corrupted

### Performance Monitoring Library Issues

**Symptoms:**
- GPU status unavailable
- System monitoring not working
- "GPUtil not found" errors
- Performance metrics missing

**Solutions:**

1. **Install Monitoring Libraries:**
   ```powershell
   pip install py-cpuinfo>=9.0.0
   pip install GPUtil>=1.4.0
   pip install nvidia-ml-py>=11.0.0
   ```

2. **Check NVIDIA GPU:**
   - nvidia-ml-py requires NVIDIA GPU
   - Verify NVIDIA drivers are installed
   - Check: `nvidia-smi` works in terminal

3. **Verify CPU Info:**
   - py-cpuinfo should work on all systems
   - Test: `python -c "import cpuinfo; print(cpuinfo.get_cpu_info())"`

### Tool Execution Issues

**Symptoms:**
- Tools not found
- Tool execution fails
- "File not found" errors for tools

**Solutions:**

1. **Verify Tool Location:**
   - Tools should be in `tools/` directory
   - Check: `ls tools/` or `dir tools\`
   - Verify tools were copied from old project

2. **Check Python Path:**
   - Ensure tools can import project modules
   - Verify PYTHONPATH includes project root
   - Test: `python tools/audio_quality_benchmark.py --help`

3. **Verify Dependencies:**
   - Tools require all libraries to be installed
   - Check tool imports work
   - Install missing dependencies

4. **Check Permissions:**
   - Ensure tools have execute permissions
   - Run as administrator if needed
   - Check file system permissions

### General Library Troubleshooting

**If all else fails:**

1. **Clean Install:**
   ```powershell
   pip uninstall -r requirements_missing_libraries.txt -y
   pip install -r requirements_missing_libraries.txt --no-cache-dir
   ```

2. **Check Logs:**
   - Review backend logs for import errors
   - Check Python error messages
   - Look for specific library errors

3. **Skip Optional Libraries:**
   - VoiceStudio works without optional libraries
   - Some features will be unavailable
   - Core functionality remains intact

4. **Contact Support:**
   - Report specific library errors
   - Include error messages and logs
   - Provide system information

---

## UI Features Issues

### Global Search Not Working

**Symptoms:**
- Search dialog doesn't open
- Search returns no results
- Search is slow

**Solutions:**

1. **Check Keyboard Shortcut:**
   - Press **Ctrl+F** to open search
   - Or click search icon in toolbar
   - Verify shortcut isn't conflicting

2. **Check Search Query:**
   - Minimum 2 characters required
   - Use type filters: `type:profile`, `type:project`
   - Use quotes for exact phrases: `"my voice"`

3. **Check Backend Connection:**
   - Verify backend is running
   - Check Diagnostics panel for connection status
   - Restart backend if needed

4. **Clear Search Cache:**
   - Restart VoiceStudio
   - Search index rebuilds automatically

### Context Menus Not Appearing

**Symptoms:**
- Right-click shows no menu
- Menu appears but is empty
- Menu items don't work

**Solutions:**

1. **Check Right-Click:**
   - Right-click on interactive elements
   - Try different elements (clips, profiles, files)
   - Use **Shift+F10** as alternative

2. **Check Context:**
   - Menus are context-sensitive
   - Some elements may not have menus
   - Try right-clicking on different areas

3. **Restart Application:**
   - Context menu service may need restart
   - Close and reopen VoiceStudio

### Multi-Select Not Working

**Symptoms:**
- Ctrl+Click doesn't select items
- Selection doesn't persist
- Batch operations don't work

**Solutions:**

1. **Check Selection Method:**
   - **Ctrl+Click:** Add to selection
   - **Shift+Click:** Select range
   - **Ctrl+A:** Select all

2. **Check Panel:**
   - Multi-select works per panel
   - Selection cleared when switching panels
   - Some panels may not support multi-select

3. **Check Visual Indicators:**
   - Selected items should be highlighted
   - Selection count badge in header
   - Verify selection is active

4. **Use Right-Click Menu:**
   - Right-click on selected items
   - Batch operations in context menu

### Toast Notifications Not Appearing

**Symptoms:**
- No notifications shown
- Notifications appear but disappear too quickly
- Notifications don't dismiss

**Solutions:**

1. **Check Notification Settings:**
   - Notifications enabled by default
   - Check Windows notification settings
   - Verify VoiceStudio has notification permission

2. **Check Notification Type:**
   - Success: Auto-dismiss 3 seconds
   - Error: Manual dismiss required
   - Warning/Info: Auto-dismiss 5 seconds

3. **Check Maximum Count:**
   - Maximum 4 toasts visible
   - Older toasts auto-dismiss when limit reached
   - Clear toasts manually if needed

### Panel Actions Not Appearing

**Symptoms:**
- No action buttons in panel header
- Actions don't change with context
- Actions don't work when clicked

**Solutions:**

1. **Check Panel Type:**
   - Not all panels have actions
   - Actions are context-sensitive
   - Actions appear based on selection

2. **Check Selection:**
   - Select an item to see actions
   - Actions change with selection
   - Some contexts may not have actions

3. **Check Panel Implementation:**
   - Panel must implement `IPanelActionable`
   - Actions defined in ViewModel
   - Maximum 4 actions supported

### Drag-and-Drop Not Working

**Symptoms:**
- Can't drag items
- No visual feedback during drag
- Drop doesn't work

**Solutions:**

1. **Check Drag Source:**
   - Some items may not be draggable
   - Try different items
   - Check item properties

2. **Check Drop Target:**
   - Drop targets highlight when valid
   - Invalid targets don't highlight
   - Try different drop locations

3. **Check Visual Feedback:**
   - Drag preview should appear
   - Drop target should highlight
   - Visual feedback confirms drop

4. **Restart Application:**
   - Drag-and-drop service may need restart
   - Close and reopen VoiceStudio

### Panel Resize Not Working

**Symptoms:**
- Can't resize panels
- Resize handles don't appear
- Panels don't remember size

**Solutions:**

1. **Check Resize Handles:**
   - Hover over panel edges
   - Handles appear on hover
   - Cursor changes to resize indicator

2. **Check Panel Type:**
   - Not all panels are resizable
   - Resize handles must be added
   - Check panel implementation

3. **Check Minimum Size:**
   - Panels have minimum sizes
   - Can't resize below minimum
   - Respects layout constraints

4. **Save Workspace Profile:**
   - Panel sizes saved in workspace profiles
   - Save profile after resizing
   - Load profile to restore sizes

### Undo/Redo Not Working

**Symptoms:**
- Ctrl+Z doesn't undo
- Ctrl+Y doesn't redo
- Visual indicator doesn't update

**Solutions:**

1. **Check Keyboard Shortcut:**
   - **Ctrl+Z:** Undo
   - **Ctrl+Y:** Redo
   - Verify shortcut isn't conflicting

2. **Check Action History:**
   - Some actions may not be undoable
   - Check visual indicator for available operations
   - Maximum 100 actions in history

3. **Check Undo/Redo Service:**
   - Service must be registered
   - Actions must implement `IUndoableAction`
   - Check service initialization

4. **Clear History:**
   - History cleared on project close
   - New project starts fresh
   - History size limited to 100 actions

---

## Error Messages

### Understanding Error Messages

VoiceStudio provides user-friendly error messages with recovery suggestions. See the [Error Handling Guide](ERROR_HANDLING_GUIDE.md) for complete information.

**Common Error Types:**
- **Connection Errors:** Backend server not reachable
- **Timeout Errors:** Operation took too long
- **Validation Errors:** Invalid input data
- **Server Errors:** Backend server issues
- **Authentication Errors:** Credential or permission issues

**Error Recovery:**
- Automatic retry for transient errors
- Circuit breaker prevents repeated failures
- Connection status monitoring
- User-friendly error messages with suggestions

**See Also:**
- [Error Handling Guide](ERROR_HANDLING_GUIDE.md) - Complete error handling documentation

### Common Error Messages

#### "Backend not connected"

**Cause:** Backend service not running or unreachable

**Solution:**
1. Restart VoiceStudio
2. Check backend logs
3. Verify Python installed
4. Check port 8000 available

#### "Engine not available"

**Cause:** Engine failed to load or not found

**Solution:**
1. Check engine directory
2. Verify engine manifest
3. Check engine dependencies
4. Try different engine

#### "Profile not found"

**Cause:** Voice profile missing or deleted

**Solution:**
1. Verify profile exists
2. Re-create profile if needed
3. Check profile storage location

#### "Synthesis failed"

**Cause:** Various (engine error, invalid input, etc.)

**Solution:**
1. Check backend logs
2. Verify text input valid
3. Check engine status
4. Try different settings

#### "Out of memory"

**Cause:** Insufficient RAM or memory leak

**Solution:**
1. Close other applications
2. Reduce project complexity
3. Restart application
4. Add more RAM if persistent

#### "File not found"

**Cause:** File moved, deleted, or path invalid

**Solution:**
1. Verify file exists
2. Check file path
3. Re-import file if needed

---

## How to Report Bugs

### Before Reporting

1. **Check Documentation:**
   - Review this troubleshooting guide
   - Check user manual
   - Search existing issues

2. **Reproduce Issue:**
   - Can you reproduce consistently?
   - What steps cause the issue?
   - Does it happen with all projects?

3. **Gather Information:**
   - Windows version
   - VoiceStudio version
   - Error messages
   - Log files

### Reporting a Bug

**Include:**

1. **Description:**
   - Clear description of issue
   - What you expected vs. what happened
   - When it occurs

2. **Steps to Reproduce:**
   - Detailed steps
   - Starting state
   - Exact actions taken

3. **System Information:**
   - Windows version (e.g., Windows 11 22H2)
   - VoiceStudio version (e.g., v1.0.0)
   - Hardware (CPU, RAM, GPU)

4. **Error Messages:**
   - Exact error text
   - Screenshots if applicable
   - When error occurs

5. **Log Files:**
   - Application logs
   - Backend logs
   - Any relevant logs

6. **Additional Context:**
   - Project files (if relevant)
   - Audio files (if relevant)
   - Settings configuration

### Where to Report

- **GitHub Issues:** Create an issue on the project repository (URL will be provided at release time)
- **Email:** Support email will be provided at release time (if available)
- **Forum/Discord:** Community support (if available)

---

## Log File Locations

### Application Logs

**Location:** `%LocalAppData%\VoiceStudio\logs\`

**Files:**
- `app-YYYY-MM-DD.log` - Application logs
- `backend-YYYY-MM-DD.log` - Backend logs (if available)

### Backend Logs

**Location:** `backend/logs/` (in installation directory)

**Files:**
- `api.log` - API request logs
- `engine.log` - Engine operation logs
- `error.log` - Error logs

### Installation Logs

**Location:** `%Temp%\VoiceStudio-Install.log`

**Content:** Installation process logs

### How to Access Logs

1. **Windows Explorer:**
   - Press `Windows + R`
   - Type: `%LocalAppData%\VoiceStudio\logs\`
   - Press Enter

2. **Command Line:**
   ```cmd
   cd %LocalAppData%\VoiceStudio\logs
   dir
   ```

3. **From Application:**
   - Open Diagnostics panel
   - View logs tab
   - Export logs if needed

### Log Levels

- **DEBUG:** Detailed debugging information
- **INFO:** General information
- **WARNING:** Warning messages
- **ERROR:** Error messages
- **CRITICAL:** Critical errors

### Sharing Logs

When reporting bugs:
1. Export relevant log files
2. Remove sensitive information
3. Attach to bug report
4. Include date/time of issue

---

## Project Management Issues

### Projects Won't Open

**Symptoms:**
- Project file appears corrupted
- "Project format not supported" error
- Project opens but is empty
- Missing files in project

**Solutions:**

1. **Check Project File:**
   - Verify `.voiceproj` file exists and is not corrupted
   - Try opening in a text editor (should be valid JSON)
   - Check file permissions
   - Verify file wasn't moved or renamed

2. **Check Project Version:**
   - Project may be from newer version
   - Check for upgrade prompts
   - Review migration guide if upgrading
   - Backup project before attempting to open

3. **Check Missing Files:**
   - Verify audio files referenced in project exist
   - Check file paths haven't changed
   - Relink missing files if prompted
   - Review project dependencies

4. **Recovery Options:**
   - Restore from backup if available
   - Check auto-save location: `%LocalAppData%\VoiceStudio\autosave\`
   - Try opening recent version
   - Export project data if accessible

### Project Corruption

**Symptoms:**
- Project won't save
- Project crashes when opening
- Data loss in project
- Inconsistent project state

**Solutions:**

1. **Prevention:**
   - Save projects regularly (auto-save enabled by default)
   - Keep project backups
   - Avoid interrupting saves
   - Close projects properly

2. **Recovery:**
   - Check auto-save files
   - Restore from backup
   - Try opening in safe mode (if available)
   - Export project data before closing

3. **Repair:**
   - Create new project
   - Import audio files from corrupted project
   - Rebuild timeline manually
   - Re-apply effects and settings

### Workspace Profile Issues

**Symptoms:**
- Panel layouts not saving
- Workspace profile won't load
- Panels reset to default positions
- Custom layouts lost

**Solutions:**

1. **Save Issues:**
   - Verify workspace profile name is valid
   - Check write permissions for settings
   - Ensure profile name doesn't contain invalid characters
   - Save profile explicitly after making changes

2. **Load Issues:**
   - Verify workspace profile exists
   - Check profile file is not corrupted
   - Try resetting to default layout first
   - Recreate profile if corrupted

3. **Panel State:**
   - Panels may reset if panel system changed
   - Some panels may not be available in all versions
   - Reconfigure layout after updates
   - Save multiple workspace profiles for different tasks

---

## Advanced Features Issues

### Multi-Engine Ensemble Issues

**Symptoms:**
- Ensemble synthesis fails
- No quality improvement with ensemble
- Ensemble takes too long
- Engines not combining properly

**Solutions:**

1. **Check Engine Availability:**
   - Ensure multiple engines are available
   - Verify engines are loaded and ready
   - Check engine compatibility for ensemble

2. **Reduce Number of Engines:**
   - Start with 2-3 engines instead of all
   - Test with different engine combinations
   - Find optimal engine set for your voice

3. **Check System Resources:**
   - Ensemble uses more memory and VRAM
   - Ensure sufficient resources available
   - Close other applications
   - Monitor resource usage in Diagnostics panel

4. **Adjust Ensemble Settings:**
   - Try different blending methods
   - Adjust quality weights
   - Use adaptive ensemble mode

5. **Check Quality Metrics:**
   - Review ensemble quality scores
   - Compare with single-engine results
   - If no improvement, use single engine

### Quality Degradation Detection Issues

**Symptoms:**
- Degradation not detected
- False positive detections
- No recommendations provided
- Detection too sensitive/not sensitive enough

**Solutions:**

1. **Check Detection Settings:**
   - Adjust sensitivity threshold
   - Configure quality thresholds
   - Enable/disable specific checks

2. **Review Quality History:**
   - Check quality trends over time
   - Identify when degradation occurred
   - Compare with historical data

3. **Verify Reference Audio:**
   - Check reference audio quality
   - Ensure reference hasn't changed
   - Re-upload reference if needed

4. **Check Engine Status:**
   - Verify engine is functioning correctly
   - Try different engine
   - Check engine-specific issues

5. **Review Recommendations:**
   - Follow provided recommendations
   - Try suggested fixes
   - Re-test after applying fixes

### Real-Time Quality Monitoring During Training Issues

**Symptoms:**
- Quality metrics not updating
- Monitoring stops during training
- Metrics inaccurate
- Performance impact from monitoring

**Solutions:**

1. **Check Monitoring Settings:**
   - Verify monitoring is enabled
   - Check update frequency
   - Ensure sufficient resources for monitoring

2. **Reduce Update Frequency:**
   - Lower update rate if performance impacted
   - Monitor at intervals instead of continuous
   - Disable monitoring if not needed

3. **Check Training Progress:**
   - Verify training is progressing
   - Check training logs for errors
   - Ensure training hasn't stalled

4. **Verify Metrics Calculation:**
   - Check metrics are being calculated
   - Review metric calculation settings
   - Ensure test data is available

5. **Performance Impact:**
   - Disable monitoring if training too slow
   - Use periodic monitoring instead
   - Monitor only critical metrics

---

## Additional Resources

- [Getting Started Guide](GETTING_STARTED.md)
- [User Manual](USER_MANUAL.md)
- [Installation Guide](INSTALLATION.md)
- [Tutorials](TUTORIALS.md)
- [FAQ](FAQ.md)
- [Performance Guide](PERFORMANCE_GUIDE.md)
- [Feature Comparison](FEATURE_COMPARISON.md)
- [Migration Guide](MIGRATION_GUIDE_TEMPLATE.md)

**Still having issues?** Report a bug with detailed information and logs.

---

**Last Updated:** 2025-01-28  
**Version:** 1.0

