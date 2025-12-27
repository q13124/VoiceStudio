# Deep Research Prompts for VoiceStudio

## When to Use Deep Research

Deep Research points are worth spending when you need:
- Best practices for complex integrations
- Library selection guidance
- Architecture patterns
- Performance optimization strategies

## Phase 5: Backend API Skeleton

### Prompt (Optional but Recommended)

```
Research best practices and code examples for a WinUI 3 (.NET 8) desktop app 
communicating with a local Python FastAPI backend over HTTP and optionally WebSockets. 

Focus on:
- Robust HttpClient usage
- Error handling patterns
- Auto-reconnect to a local service
- Request/response serialization
- WebSocket connection management

Provide minimal example code in C# and Python.
```

### Why This Helps

- Establishes proper HTTP client patterns
- Handles connection failures gracefully
- Sets up WebSocket infrastructure early
- Avoids common pitfalls

### Expected Output

- HttpClient configuration best practices
- Error handling strategies
- Reconnection patterns
- Example FastAPI endpoints
- Example C# client code

---

## Phase 7: Audio Engines & I/O Integration

### Prompt (Recommended)

```
Research recommended approaches for audio playback and low-latency audio routing 
for a WinUI 3 (.NET 8) application on Windows, including:

1. Whether to use NAudio, WASAPI directly, or a Python-based audio playback service 
   (e.g., PortAudio) with a local API

2. Trade-offs between each approach:
   - Latency
   - Complexity
   - Cross-platform compatibility
   - Integration with existing Python audio stack

3. Minimal code snippets for:
   - Audio playback in C# (NAudio/WASAPI)
   - Audio playback in Python (PortAudio/pyaudio)
   - Streaming audio from backend to frontend

4. Best practices for:
   - Low-latency audio streaming
   - Audio buffer management
   - Sample rate conversion
   - Multi-channel audio handling
```

### Why This Helps

- Critical architectural decision
- Affects entire audio pipeline
- Performance implications
- Integration complexity

### Expected Output

- Library recommendations with trade-offs
- Code examples for each approach
- Performance characteristics
- Integration patterns

---

## Phase 8: Visuals - Waveforms, Spectrograms, Meters

### Prompt (Recommended)

```
Research examples and best practices for implementing real-time audio waveforms, 
spectrograms, and level meters in a WinUI 3 app, using Win2D or other compatible 
drawing libraries. Include guidance on:

1. Win2D integration with WinUI 3
2. Performance optimization for real-time rendering
3. Downsampling strategies for large audio files
4. How to feed FFT data from a backend into visuals
5. Best practices for:
   - Waveform rendering (peak/RMS)
   - Spectrogram rendering (FFT visualization)
   - Real-time meter updates
   - Memory management for large audio buffers

Provide minimal working code examples for:
- Win2D CanvasControl for waveform rendering
- FFT data visualization
- Real-time meter updates
```

### Why This Helps

- Critical for professional audio visualization
- Performance is key for real-time rendering
- Win2D integration patterns
- FFT data handling

### Expected Output

- Win2D integration examples
- Performance optimization strategies
- Waveform rendering code
- Spectrogram implementation
- Meter update patterns

---

## Phase 9: Macros & Automation (Optional)

### Prompt (Optional but Helpful)

```
Research best practices and code examples for implementing a visual node-based editor 
in WinUI 3, including:

1. Canvas-based node positioning and dragging
2. Connection drawing between nodes
3. Port/connector system for node inputs/outputs
4. Zoom and pan functionality
5. Node selection and multi-selection
6. Serialization of node graphs to JSON

Provide minimal working examples for:
- Draggable nodes on Canvas
- Connection lines between nodes
- Port interaction (drag to connect)
- Graph serialization/deserialization
```

### Why This Helps

- Node editor is complex UI component
- Connection system needs careful design
- Performance for large graphs
- Serialization patterns

### Expected Output

- Node editor architecture
- Connection system design
- Drag-and-drop patterns
- Graph serialization examples

---

## Phase 10: Packaging & Distribution (Optional)

### Prompt (Optional)

```
Research best practices for packaging a WinUI 3 (.NET 8) desktop application with 
a Python backend service for Windows distribution, including:

1. MSIX vs traditional installer trade-offs
2. Bundling Python runtime and dependencies
3. File association registration
4. Auto-start backend service
5. Update mechanisms

Provide guidance on:
- MSIX packaging tools
- Python bundling (PyInstaller, cx_Freeze, etc.)
- Installer creation (WiX, Inno Setup, etc.)
- File association setup
```

### Why This Helps

- Distribution strategy
- Python bundling challenges
- File associations
- Update mechanisms

### Expected Output

- Packaging tool recommendations
- Python bundling strategies
- Installer creation guidance
- File association setup

---

## Phase 6: MCP Bridge (Optional)

### Prompt (Only if MCP-Specific Help Needed)

```
Research Model Context Protocol (MCP) implementation patterns for integrating 
multiple MCP servers (Figma, TTS, VC, Whisper) into a unified backend bridge layer.

Focus on:
- MCP protocol implementation
- Server connection management
- Request routing strategies
- Response normalization
- Error handling across multiple servers

Provide Python code examples for an MCP bridge that:
- Connects to multiple MCP servers
- Routes requests to appropriate servers
- Normalizes responses to a common format
- Handles server failures gracefully
```

### Why This Helps

- If you're new to MCP
- Need multi-server patterns
- Want best practices

### Expected Output

- MCP implementation patterns
- Multi-server routing strategies
- Error handling approaches
- Code examples

---

## When NOT to Use Deep Research

### Phase 2: Styling
- **Not needed** - Pure WinUI 3 styling, well-documented

### Phase 3: Layout Persistence
- **Not needed** - Custom logic, straightforward JSON serialization

### Phase 4: Data Models
- **Not needed** - Standard C# modeling patterns

### Phase 6: MCP Bridge (General)
- **Not needed** - If you already have MCP documentation

---

## Deep Research Best Practices

1. **Be Specific**
   - Ask for concrete code examples
   - Request trade-off analysis
   - Ask for minimal working examples

2. **Focus on Integration**
   - How to connect technologies
   - Patterns for communication
   - Error handling strategies

3. **Request Code Snippets**
   - Minimal working examples
   - Both sides of integration (C# and Python)
   - Real-world patterns

4. **Ask for Trade-offs**
   - Performance implications
   - Complexity vs. features
   - Maintenance considerations

---

## Summary

| Phase | Deep Research? | Focus |
|-------|----------------|-------|
| Phase 1 | ❌ | Already complete |
| Phase 2 | ❌ | WinUI 3 styling |
| Phase 3 | ❌ | Custom logic |
| Phase 4 | ❌ | C# modeling |
| Phase 5 | ✅ Optional | HTTP/WebSocket patterns |
| Phase 6 | ⚠️ Only if needed | MCP-specific help |
| Phase 7 | ✅ Recommended | Audio library selection |
| Phase 8 | ✅ Recommended | Win2D & FFT visualization |
| Phase 9 | ⚠️ Optional | Node editor patterns |
| Phase 10 | ⚠️ Optional | Packaging tools |

**Use Deep Research strategically - it's valuable for complex integrations, not for straightforward implementation.**

