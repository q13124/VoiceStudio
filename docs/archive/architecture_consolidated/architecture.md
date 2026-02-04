# VoiceStudio Architecture

## System Architecture Overview

```
[ Figma / MCP servers / AI engines ]
         ↓   (design tokens, model calls)

[ Backend service layer (Python/Node) ]
         ↓   (REST or WebSocket)

[ Native frontend (WinUI3, Qt, SwiftUI) ]
```

## Layer Descriptions

### Design + MCP Layer
- **Components**: Figma, MCP servers, AI engines
- **Communication**: Design tokens, model calls
- **Purpose**: Design system integration and AI model orchestration

### Backend Service Layer
- **Technology**: Python or Node.js
- **Communication**: REST or WebSocket to frontend
- **Purpose**: Core business logic, API services, and data processing

### Native Frontend
- **Technology Options**: 
  - WinUI3 (Windows - C#/XAML)
  - Qt (Cross-platform - C++/QML)
  - SwiftUI (macOS/iOS - Swift)
- **Purpose**: Native user interface for each platform

## Communication Flow

1. **Design/MCP/AI → Backend**: Design tokens, model calls
2. **Backend → Frontend**: REST or WebSocket

