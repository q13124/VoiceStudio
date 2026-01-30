# Performance & Stability Safeguards
## VoiceStudio Quantum+ - Cursor Environment Protection

**Last Updated:** 2025-01-27  
**Purpose:** Guidelines to keep the Cursor environment stable and responsive during multi-agent development.

---

## 🛡️ Core Safeguards

**These measures ensure agents do not overload the system or each other.**

---

## 1. Monitor Resource Usage

### Tracking Requirements

**Monitor for Each Agent:**
- CPU usage per agent process
- GPU usage (if applicable)
- Memory usage per agent
- File I/O operations
- Network activity

**Tools:**
- Cursor's agent dashboard (if available)
- System resource monitors
- Process monitoring tools

### Response to High Usage

**If Agent Resource Usage Spikes:**
1. **Pause:** Agent should pause operations
2. **Reset:** Agent may need reset to avoid degradation
3. **Report:** Overseer notified of resource issues
4. **Throttle:** Reduce operation frequency if needed

**Thresholds:**
- CPU > 80% sustained → Pause and report
- Memory > 2GB per agent → Review and optimize
- GPU > 90% → Throttle operations

---

## 2. Staggered Access

### File/Resource Access Pattern

**When Multiple Agents Need Same Resource:**

1. **First Agent:**
   - Acquires lock (see FILE_LOCKING_PROTOCOL.md)
   - Begins work
   - Holds lock until complete

2. **Other Agents:**
   - Check lock status in TASK_LOG.md
   - Implement retry/backoff pattern
   - Sleep briefly before retrying (NOT tight loop)
   - Wait for unlock notification

### Retry/Backoff Implementation

**Example Pattern:**
```python
# Backend retry pattern
max_retries = 5
retry_delay = 2  # seconds

for attempt in range(max_retries):
    if file_is_unlocked(filename):
        acquire_lock(filename)
        break
    else:
        sleep(retry_delay * (attempt + 1))  # Exponential backoff
        if attempt == max_retries - 1:
            report_to_overseer("File locked, max retries reached")
```

**C# Pattern:**
```csharp
// Frontend retry pattern
int maxRetries = 5;
int retryDelay = 2000; // milliseconds

for (int attempt = 0; attempt < maxRetries; attempt++)
{
    if (IsFileUnlocked(filename))
    {
        AcquireLock(filename);
        break;
    }
    else
    {
        await Task.Delay(retryDelay * (attempt + 1)); // Exponential backoff
        if (attempt == maxRetries - 1)
        {
            ReportToOverseer("File locked, max retries reached");
        }
    }
}
```

**Key Principles:**
- ✅ Exponential backoff (increasing delay)
- ✅ Maximum retry limit
- ✅ Report to Overseer if stuck
- ✅ No tight loops (busy-waiting)
- ✅ Sleep between retries

---

## 3. Loop/Time Limits

### Infinite Loop Prevention

**Set Sensible Limits:**
- Maximum iterations per loop
- Maximum execution time per task
- Maximum retry attempts
- Maximum file operations

**Example Limits:**
```python
# Loop limit
max_iterations = 1000
for i in range(max_iterations):
    if not make_progress():
        break  # Exit if no progress
    if i == max_iterations - 1:
        report_error("Max iterations reached")
```

**Overseer Detection:**
- Overseer monitors agent progress
- If agent stuck repeating step → Intervene
- If no progress after N iterations → Pause agent
- If agent hangs → Terminate and restart

---

## 4. Logging Cooldowns

### Log Verbosity Limits

**Avoid:**
- ❌ Logging same message every second
- ❌ Verbose logs in tight loops
- ❌ Excessive debug output
- ❌ Redundant progress messages

**Implement:**
- ✅ Batch or throttle logs
- ✅ At most one update per few seconds
- ✅ Essential information only
- ✅ Readable log output

**Example Throttling:**
```python
# Log throttling
last_log_time = 0
log_cooldown = 5  # seconds

def log_progress(message):
    global last_log_time
    current_time = time.time()
    if current_time - last_log_time >= log_cooldown:
        logger.info(message)
        last_log_time = current_time
```

**Log Levels:**
- **ERROR:** Always log
- **WARNING:** Log with cooldown
- **INFO:** Batch updates (max 1 per 5 seconds)
- **DEBUG:** Disable in production

---

## 5. Fail-Safes

### Crash/Hang Handling

**If Agent Crashes or Hangs:**

1. **Overseer Detection:**
   - Monitor agent health
   - Detect crashes/hangs
   - Terminate stuck agents

2. **Graceful Failure:**
   - Roll back partial changes if commit fails
   - Preserve work in progress
   - Log error state
   - Report to Overseer

3. **Recovery:**
   - Overseer may restart agent
   - Agent resumes from last checkpoint
   - Partial work preserved
   - No data loss

### Implementation

**Agent Health Check:**
```python
# Agent health monitoring
def health_check():
    if agent_crashed():
        rollback_changes()
        report_to_overseer("Agent crashed, rolled back")
        return False
    if agent_hung():
        terminate_agent()
        report_to_overseer("Agent hung, terminated")
        return False
    return True
```

**Overseer Monitoring:**
- Check agent status every N seconds
- Detect unresponsive agents
- Terminate and restart if needed
- Preserve work state

---

## 📊 Resource Monitoring

### Metrics to Track

**Per Agent:**
- CPU usage percentage
- Memory usage (MB/GB)
- GPU usage (if applicable)
- File operations per second
- Network requests per second
- Execution time per task

**System-Wide:**
- Total CPU usage
- Total memory usage
- Disk I/O operations
- Network bandwidth

### Monitoring Tools

**Recommended:**
- Cursor's agent dashboard (if available)
- System Task Manager
- Process monitoring tools
- Resource usage logs

---

## 🚨 Emergency Procedures

### If System Overloaded

1. **Pause All Agents:**
   - Overseer pauses all operations
   - Assess resource usage
   - Identify bottleneck

2. **Throttle Operations:**
   - Reduce operation frequency
   - Increase delays between operations
   - Limit concurrent operations

3. **Restart if Needed:**
   - Restart overloaded agents
   - Clear resource caches
   - Resume with throttling

---

## 📋 Safeguard Checklist

**Before Starting Work:**
- [ ] Resource monitoring enabled
- [ ] Retry/backoff patterns implemented
- [ ] Loop limits set
- [ ] Logging throttled
- [ ] Fail-safes in place

**During Work:**
- [ ] Monitor resource usage
- [ ] Check for file locks before access
- [ ] Use retry/backoff for locked files
- [ ] Limit loop iterations
- [ ] Throttle log output

**After Work:**
- [ ] Release file locks
- [ ] Report resource usage
- [ ] Update task status
- [ ] Clean up resources

---

## 📚 Related Documents

- `FILE_LOCKING_PROTOCOL.md` - File access coordination
- `TASK_LOG.md` - Task and lock tracking
- `OVERSEER_SYSTEM_PROMPT_V2.md` - Overseer monitoring

---

**These safeguards ensure stable, responsive development environment for all agents.**

