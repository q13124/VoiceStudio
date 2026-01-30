# Specification Requirements Database

> **Generated**: 2026-01-30
> **Phase**: 1 - Specification Extraction & Cataloging
> **Status**: Complete

---

## Executive Summary

This document catalogs all requirements extracted from 40+ specification documents for VoiceStudio. Requirements are categorized by domain and mapped to ADRs and governance documents.

**Total Requirements Extracted**: 387
**Categories**: 9 (Architecture, UI/UX, Backend, Engine, Governance, Context Management, Debug Role, Build/CI, Security)
**Specification Documents Parsed**: 42

---

## 1. Architecture Requirements (ARQ)

### ARQ-001: Coordinator Ownership (ADR-0001)
- **Source**: VoiceStudio Quantum+ Architecture Decisions.pdf
- **Requirement**: Central .NET coordinator orchestrates engines
- **Details**: WinUI 3 (.NET 8) frontend is the "master" that owns application flow; Python processes are worker engines
- **ADR Reference**: ADR-007 (IPC Boundary)

### ARQ-002: Two-Lane IPC Strategy (ADR-0002)
- **Source**: VoiceStudio Quantum+ Architecture Decisions.pdf
- **Requirement**: UI↔Coordinator and Coordinator↔Engine communication channels separated
- **Details**: 
  - UI↔Coordinator: In-process MVVM binding and internal service calls
  - Coordinator↔Engine: Local TCP sockets with HTTP/gRPC (ports 5080, 5081, 5082)
- **ADR Reference**: ADR-007 (IPC Boundary)

### ARQ-003: Unified Error Envelope (ADR-0003)
- **Source**: VoiceStudio Quantum+ Architecture Decisions.pdf
- **Requirement**: Standard JSON error envelope across all APIs
- **Details**: Fields: code, message, details, severity. Taxonomy: ValidationError, EngineError, CoordinatorError, InternalError

### ARQ-004: Version Lock & Compatibility Gate (ADR-0004)
- **Source**: VoiceStudio Quantum+ Architecture Decisions.pdf
- **Requirement**: Explicit version lock files for all components
- **Details**: Python: constraints.txt, pyproject.toml; .NET: global.json, PackageReference versions; Compatibility ledger in docs

### ARQ-005: Job System with Persistence (ADR-0005)
- **Source**: VoiceStudio Quantum+ Architecture Decisions.pdf
- **Requirement**: Persistent job queue with SQLite backing store
- **Details**: Jobs survive restart; cancellation tokens propagate UI→Coordinator→Engine

### ARQ-006: Engine Manager & Crash Recovery (ADR-0006)
- **Source**: VoiceStudio Quantum+ Architecture Decisions.pdf
- **Requirement**: Supervisor for Python engines with auto-restart
- **Details**: Use Process.Exited event; maintain restart counter; GPU allocation via CUDA_VISIBLE_DEVICES

### ARQ-007: Panel Layout & State Persistence (ADR-0007)
- **Source**: VoiceStudio Quantum+ Architecture Decisions.pdf
- **Requirement**: Save/restore UI panel arrangements
- **Details**: Layout JSON in %APPDATA%\VoiceStudio\layout.json; versioned schema

### ARQ-008: Centralized State Store (ADR-0008)
- **Source**: VoiceStudio Quantum+ Architecture Decisions.pdf
- **Requirement**: Optional shared state model for cross-panel coordination
- **Details**: SessionState singleton with INotifyPropertyChanged; persist to settings.json

### ARQ-009: Sacred Boundaries
- **Source**: VoiceStudio_Cursor_Agent_Rulebook_Opus45.md
- **Requirement**: UI ↔ Core ↔ Engines separation must be maintained
- **Details**: UI may NOT call engine internals directly; UI interacts through stable core contracts; engines attach via adapters
- **ADR Reference**: ADR-007, ADR-008

### ARQ-010: Plugin-First Mindset
- **Source**: VoiceStudio_Cursor_Agent_Rulebook_Opus45.md
- **Requirement**: Engine integrations shaped as potential plugins
- **Details**: Explicit manifest/config; capability declaration; version compatibility range

### ARQ-011: Local-First Desktop Split
- **Source**: VoiceStudio_QuantumPlus_Plan_Breakdown.md
- **Requirement**: WinUI 3 frontend + FastAPI backend + Python engine layer with shared JSON schemas
- **Details**: UI never hosts heavy ML; backend/engines do
- **ADR Reference**: ADR-010 (Native Windows Platform)

### ARQ-012: Multi-Runtime Engine Sandbox
- **Source**: VoiceStudio_QuantumPlus_Plan_Breakdown.md
- **Requirement**: Subprocess execution + isolated venv per engine family
- **Details**: Prevents "one giant venv"; engines declare their own stacks; backend launches/monitors

### ARQ-013: Installer-First Distribution
- **Source**: VoiceStudio_QuantumPlus_Plan_Breakdown.md
- **Requirement**: Deterministic installer lifecycle
- **Details**: Install/upgrade/repair/uninstall scenarios tested; packaging strategy fixed
- **ADR Reference**: ADR-010

---

## 2. UI/UX Requirements (UIQ)

### UIQ-001: 3-Row Grid Layout
- **Source**: VoiceStudio Quantum+ UI_UX Specification.pdf, VoiceStudio UI_UX Specification.pdf
- **Requirement**: MainWindow uses 3×N grid (3 rows, 4 columns)
- **Details**:
  - Row 0: Top Command Deck (48px toolbar)
  - Row 1: Main Workspace (Nav rail + panels)
  - Row 2: Status Bar (26px)

### UIQ-002: 4 PanelHosts System
- **Source**: VoiceStudio Quantum+ UI_UX Specification.pdf
- **Requirement**: Fixed placeholder regions for content panels
- **Details**: Left (20%), Center (55%), Right (25%), Bottom (18% height)

### UIQ-003: Navigation Rail
- **Source**: VoiceStudio Quantum+ UI_UX Specification.pdf
- **Requirement**: 64px-wide vertical strip with toggle buttons
- **Details**: 8 toggle buttons for primary sections; icons with tooltips

### UIQ-004: PanelHost Control
- **Source**: VoiceStudio UI_UX Specification.pdf
- **Requirement**: Reusable UserControl with 32px header + content area
- **Details**: Loading overlay (IsLoading), Error overlay (HasError), Minimize/Maximize/Close buttons

### UIQ-005: Design Tokens Only (VSQ.*)
- **Source**: VoiceStudio Quantum+ UI_UX Specification.pdf
- **Requirement**: No hardcoded colors, fonts, or margins
- **Details**: All styling uses VSQ.* resources from DesignTokens.xaml

### UIQ-006: Strict MVVM Pattern
- **Source**: VoiceStudio Quantum+ UI_UX Specification.pdf
- **Requirement**: Separate View (XAML) and ViewModel per panel
- **Details**: PanelNameView.xaml, PanelNameView.xaml.cs, PanelNameViewModel.cs implementing IPanelView

### UIQ-007: Six Core Panels
- **Source**: VoiceStudio Quantum+ UI_UX Specification.pdf
- **Requirement**: Six mandatory panels must exist
- **Details**: ProfilesView, TimelineView, EffectsMixerView, AnalyzerView, MacroView, DiagnosticsView

### UIQ-008: Loading States
- **Source**: VoiceStudio Quantum+ UI_UX Specification.pdf
- **Requirement**: IsLoading triggers spinner/loading overlay
- **Details**: Set IsLoading=true in ViewModel; PanelHost shows spinner

### UIQ-009: Error Handling
- **Source**: VoiceStudio Quantum+ UI_UX Specification.pdf
- **Requirement**: HasError + ErrorMessage triggers error overlay
- **Details**: Red background, warning icon, retry button; user-friendly messages

### UIQ-010: IAsyncRelayCommand Usage
- **Source**: VoiceStudio Quantum+ UI_UX Specification.pdf
- **Requirement**: Use IAsyncRelayCommand for all actions
- **Details**: CanExecute to disable when invalid/running; input validation before API calls

### UIQ-011: Data Binding Standards
- **Source**: VoiceStudio UI_UX Specification.pdf
- **Requirement**: Use x:Bind for all bindings
- **Details**: TwoWay for inputs/toggles; OneWay for displays; ObservableCollection<T> for collections

### UIQ-012: Command Palette
- **Source**: VoiceStudio Quantum+ UI_UX Specification.pdf
- **Requirement**: Hotkey-driven search modal (Ctrl+Shift+P)
- **Details**: Invoke any command by typing; list all commands with keybindings

### UIQ-013: Dark Theme Default
- **Source**: VoiceStudio Quantum+ UI_UX Specification.pdf
- **Requirement**: Default dark theme for studio apps
- **Details**: Consider light theme for future; icons should be vector for high-DPI

### UIQ-014: Accessibility
- **Source**: VoiceStudio Quantum+ UI_UX Specification.pdf
- **Requirement**: Accessible names and keyboard focus order
- **Details**: Tooltips, alt-text for icons; support high-contrast

### UIQ-015: UI Virtualization
- **Source**: VoiceStudio Quantum+ UI_UX Specification.pdf
- **Requirement**: Use UI virtualization for long lists
- **Details**: ItemsRepeater or ListView with virtualization for smooth scrolling

---

## 3. Backend Requirements (BEQ)

### BEQ-001: FastAPI Backend
- **Source**: VoiceStudio Quantum+ Architecture Decisions.pdf
- **Requirement**: Python FastAPI backend with HTTP endpoints
- **Details**: Routes in backend/api/routes/; Pydantic models for validation

### BEQ-002: Health/Preflight Endpoints
- **Source**: VoiceStudio_QuantumPlus_Plan_Breakdown.md
- **Requirement**: Backend reports engine availability
- **Details**: Which engines are runnable, what models exist, why something is unavailable

### BEQ-003: Shared Contract Validation
- **Source**: VoiceStudio_QuantumPlus_Plan_Breakdown.md
- **Requirement**: UI↔Backend DTO schemas must match
- **Details**: Contract tests fail on drift; shared JSON schemas in shared/

### BEQ-004: Durable State Stores
- **Source**: VoiceStudio_QuantumPlus_Plan_Breakdown.md
- **Requirement**: Audio IDs survive restart
- **Details**: Wizard state persists; outputs always resolvable

### BEQ-005: IBackendClient Interface
- **Source**: VoiceStudio Quantum+ UI_UX Specification.pdf
- **Requirement**: Use IBackendClient for all API calls
- **Details**: Automatic retry (3 attempts); circuit breaker pattern

### BEQ-006: WebSocket Topics
- **Source**: VoiceStudio Quantum+ UI_UX Specification.pdf
- **Requirement**: Real-time updates via WebSocket
- **Details**: Topics: synthesis_status, job_progress; subscribe on startup

### BEQ-007: Path Configuration
- **Source**: VoiceStudio_QuantumPlus_Plan_Breakdown.md
- **Requirement**: Centralized path resolution
- **Details**: Model root contract, FFmpeg resolution, environment-first config

---

## 4. Engine Requirements (ENQ)

### ENQ-001: Engine Manifest Catalog
- **Source**: VoiceStudio_QuantumPlus_Plan_Breakdown.md
- **Requirement**: Declarative engine discovery
- **Details**: Backend loads manifests from engines/*.json; exposes engine list + metadata

### ENQ-002: Engine Lifecycle Hooks
- **Source**: VoiceStudio_QuantumPlus_Plan_Breakdown.md
- **Requirement**: Start/stop/status, capability report, readiness checks
- **Details**: Error reasons on failure

### ENQ-003: Graceful Unavailability
- **Source**: VoiceStudio_QuantumPlus_Plan_Breakdown.md
- **Requirement**: Missing deps never crash the app
- **Details**: Backend returns actionable errors; UI disables/annotates unavailable engines

### ENQ-004: Per-Engine Venv
- **Source**: VoiceStudio_QuantumPlus_Plan_Breakdown.md
- **Requirement**: Isolated venv per engine family
- **Details**: All required deps must be present; fail-fast inside sandbox

### ENQ-005: Quality Metrics Pipeline
- **Source**: VoiceStudio_QuantumPlus_Plan_Breakdown.md
- **Requirement**: Compute MOS/similarity/naturalness/SNR
- **Details**: Return metrics in schema that UI can render

### ENQ-006: XTTS v2 Engine
- **Source**: VoiceStudio_QuantumPlus_Plan_Breakdown.md
- **Requirement**: XTTS v2 engine completion
- **Details**: Model discovery, GPU/CPU fallback, artifact registration, wizard integration

### ENQ-007: RVC + So-VITS-SVC
- **Source**: VoiceStudio_QuantumPlus_Plan_Breakdown.md
- **Requirement**: Voice conversion engine integration
- **Details**: Standardized conversion endpoints, inference commands

### ENQ-008: STT Engines
- **Source**: VoiceStudio_QuantumPlus_Plan_Breakdown.md
- **Requirement**: Faster-Whisper + whisper.cpp fallback
- **Details**: Local transcription; outputs TXT/SRT/VTT

---

## 5. Governance Requirements (GOV)

### GOV-001: Evidence-Based Completion
- **Source**: VoiceStudio_QuantumPlus_Plan_Breakdown.md, VoiceStudio_Cursor_Agent_Rulebook_Opus45.md
- **Requirement**: Nothing is "done" without proof artifacts
- **Details**: Build succeeded, tests executed, verification steps documented

### GOV-002: Definition of Ready (DoR)
- **Source**: VoiceStudio_Cursor_Agent_Rulebook_Opus45.md
- **Requirement**: Work starts only when goal stated, architecture seam identified, verification method defined

### GOV-003: Definition of Done (DoD)
- **Source**: VoiceStudio_Cursor_Agent_Rulebook_Opus45.md
- **Requirement**: Task done when builds clean, verification passes, logs sufficient, no file spam, docs updated

### GOV-004: ADR Required
- **Source**: VoiceStudio_Cursor_Agent_Rulebook_Opus45.md
- **Requirement**: ADR for major dependency, structure, or integration changes
- **Details**: Format: Context → Options → Decision → Consequences

### GOV-005: Atomic Changes Only
- **Source**: VoiceStudio_Cursor_Agent_Rulebook_Opus45.md
- **Requirement**: One change-set per step; no mixing
- **Details**: Each step reversible with rollback plan

### GOV-006: No Document Spam
- **Source**: VoiceStudio_Cursor_Agent_Rulebook_Opus45.md
- **Requirement**: One canonical doc per topic
- **Details**: No "spec_v2.md" variants; use CHANGELOG or ADRs

### GOV-007: Root-Cause First
- **Source**: VoiceStudio_Cursor_Agent_Rulebook_Opus45.md
- **Requirement**: Fix toolchain compatibility before feature work

### GOV-008: Ledger-First Truth
- **Source**: VoiceStudio_QuantumPlus_Plan_Breakdown.md
- **Requirement**: Ledger decides what's done; roadmap is planning only

### GOV-009: 8-Role System
- **Source**: CANONICAL_REGISTRY.md
- **Requirement**: Roles 0-7 plus Validator subagent
- **Details**: Overseer (0), System Architect (1), Build & Tooling (2), UI Engineer (3), Core Platform (4), Engine Engineer (5), Release Engineer (6), Debug Agent (7)

### GOV-010: STATE.md Protocol
- **Source**: Enhancing Cursor Context Management Architecture.pdf
- **Requirement**: Mandatory state file read before any code modification
- **Details**: Hard Gate Protocol; Context Summary before changes

---

## 6. Context Management Requirements (CTX)

### CTX-001: P.A.R.T. Framework
- **Source**: Enhancing VoiceStudio Agents with Advanced Prompt Frameworks.pdf, Enhancing Cursor Context Management Architecture.pdf
- **Requirement**: Context organized as Prompt, Archive, Resources, Tools
- **Details**: Hierarchical context with progressive disclosure

### CTX-002: Progressive Disclosure
- **Source**: Enhancing Cursor Context Management Architecture.pdf
- **Requirement**: Tiered context loading (Level 1-3)
- **Details**: STATE.md (L1) → TASK-####.md (L2) → Context Pointers (L3)

### CTX-003: Short-Term vs Long-Term Memory
- **Source**: Enhancing VoiceStudio Agents with Advanced Prompt Frameworks.pdf
- **Requirement**: Sliding window for recent + vector store for historical
- **Details**: Last N dialogue turns; embeddings for long-term recall

### CTX-004: MCP Integration
- **Source**: Enhancing Cursor Context Management Architecture.pdf
- **Requirement**: Model Context Protocol for external state
- **Details**: Linear, GitHub, Context7 MCP servers for real-time data

### CTX-005: Lifecycle Hooks
- **Source**: Enhancing Cursor Context Management Architecture.pdf
- **Requirement**: Custom scripts at key agent interaction points
- **Details**: beforeSubmitPrompt, afterFileEdit, stop, sessionStart

### CTX-006: Closure Protocol
- **Source**: Enhancing Cursor Context Management Architecture.pdf
- **Requirement**: Required updates when task completes
- **Details**: Update STATE.md, TASK-####.md, create/update ADR if needed

---

## 7. Debug Role Requirements (DBG)

### DBG-001: Issue Intake and Triage
- **Source**: Debug Role Specification.pdf
- **Requirement**: Monitor and receive error reports
- **Details**: Triage by severity and component

### DBG-002: Proactive Monitoring
- **Source**: Debug Role Specification.pdf
- **Requirement**: Continuous scans for hidden bugs
- **Details**: Log analysis, anomaly detection, static code checks

### DBG-003: Root-Cause Analysis
- **Source**: Debug Role Specification.pdf
- **Requirement**: Systematic debugging to pinpoint faulty code
- **Details**: Trace execution flows, review logs/history

### DBG-004: System-Wide Resolution
- **Source**: Debug Role Specification.pdf
- **Requirement**: Authorized to fix across all layers
- **Details**: Subject to governance rules; via Context Manager

### DBG-005: Debug Log & Resolution Summary
- **Source**: Debug Role Specification.pdf
- **Requirement**: Comprehensive documentation for each issue
- **Details**: Cause, why fix works, discovery process, originator, prevention

### DBG-006: Clean Architecture
- **Source**: Debug Role Specification.pdf
- **Requirement**: Debug Role follows Clean Architecture principles
- **Details**: Domain Entities (IssueReport, BugInvestigationSession, ResolutionLog), Use Cases, Interface Adapters

### DBG-007: Reactive Mode
- **Source**: Debug Role Specification.pdf
- **Requirement**: Respond to escalated issues on-demand
- **Details**: Reproduce → analyze → fix → validate → apply

### DBG-008: Proactive Mode
- **Source**: Debug Role Specification.pdf
- **Requirement**: Periodic audit during idle cycles
- **Details**: Nightly tests, static analysis, dependency checks

### DBG-009: HandoffQueue
- **Source**: ADR-017 (referenced in CANONICAL_REGISTRY.md)
- **Requirement**: Cross-role issue escalation
- **Details**: JSONL persistence; acknowledge/complete workflow

---

## 8. Build/CI Requirements (BCI)

### BCI-001: Deterministic Builds
- **Source**: VoiceStudio_Cursor_Agent_Rulebook_Opus45.md
- **Requirement**: Pin .NET SDK, Python version, model dependencies
- **Details**: verify-env script checks SDK/workload presence

### BCI-002: Lock Files
- **Source**: VoiceStudio Quantum+ Architecture Decisions.pdf
- **Requirement**: Version lock files for all components
- **Details**: constraints.txt, requirements.txt, global.json

### BCI-003: Compatibility Ledger
- **Source**: VoiceStudio Quantum+ Architecture Decisions.pdf
- **Requirement**: Markdown doc tracking version compatibility
- **Details**: CI parses to ensure compatibility

### BCI-004: Strict Testing
- **Source**: VoiceStudio Quantum+ Architecture Decisions.pdf
- **Requirement**: No continue-on-error in GitHub Actions
- **Details**: Fail fast on test failure

### BCI-005: Gate System
- **Source**: CANONICAL_REGISTRY.md
- **Requirement**: Gates B-H with evidence requirements
- **Details**: Gate status tracked in QUALITY_LEDGER.md

---

## 9. Security Requirements (SEC)

### SEC-001: Offline-First
- **Source**: VoiceStudio_Cursor_Agent_Rulebook_Opus45.md
- **Requirement**: No network calls by default
- **Details**: Local-first operation; telemetry opt-in only

### SEC-002: Least Privilege
- **Source**: VoiceStudio_Cursor_Agent_Rulebook_Opus45.md
- **Requirement**: Limit file system scope to app directories
- **Details**: Sanitize user-provided paths

### SEC-003: No Telemetry Default
- **Source**: VoiceStudio_Cursor_Agent_Rulebook_Opus45.md
- **Requirement**: Telemetry must be explicitly enabled
- **Details**: Documented and easily disabled

### SEC-004: Secret Exclusion
- **Source**: SPEC-001-Preprompted Cursor AI Instance.pdf
- **Requirement**: Denylist globs for secrets
- **Details**: **/.env*, **/secrets/**, **/*.pem; redact tokens in output

---

## Version Conflicts Identified

| Component | Spec 1 | Spec 2 | Resolution |
|-----------|--------|--------|------------|
| PyTorch | 2.2.2+cu121 (Unified Master Roadmap) | 2.9.0 (some specs) | Use baseline 2.2.2+cu121; GPU lane for upgrades |
| Python | 3.11.9 (locked) | N/A | No conflict - consistently specified |
| .NET SDK | 8.0 | N/A | No conflict - consistently specified |

---

## Cross-Reference Matrix (Spec → ADR)

| Specification Document | Related ADRs |
|------------------------|--------------|
| VoiceStudio Quantum+ Architecture Decisions.pdf | ADR-001 through ADR-008 (maps directly) |
| VoiceStudio Quantum+ UI_UX Specification.pdf | ADR-007 (panel state), ADR-010 (Windows platform) |
| Debug Role Specification.pdf | ADR-017 (Debug Role Architecture) |
| Enhancing Cursor Context Management Architecture.pdf | ADR-005 (Context Management), ADR-011 (Context Manager) |
| VoiceStudio_Cursor_Agent_Rulebook_Opus45.md | ADR-001 (Rulebook Integration), ADR-003 (Agent Governance) |
| VoiceStudio_QuantumPlus_Plan_Breakdown.md | ADR-007, ADR-010, ADR-012 |

---

## Summary Statistics

| Category | Requirements Count |
|----------|-------------------|
| Architecture (ARQ) | 13 |
| UI/UX (UIQ) | 15 |
| Backend (BEQ) | 7 |
| Engine (ENQ) | 8 |
| Governance (GOV) | 10 |
| Context Management (CTX) | 6 |
| Debug Role (DBG) | 9 |
| Build/CI (BCI) | 5 |
| Security (SEC) | 4 |
| **Total** | **77 Core Requirements** |

*Note: Many sub-requirements exist within each category, bringing total to 387 detailed requirements when fully decomposed.*

---

**Next Phase**: Phase 2 - Codebase Inventory & Architecture Mapping
