# MASTER RULES COMPLETE - ALL CONTENT EMBEDDED

## VoiceStudio Quantum+ Complete Ruleset - All Content Embedded

**Date:** 2025-12-26
**Status:** COMPLETE - All Rules Content Embedded
**Purpose:** Single file with ALL rules, no external references

---

## TABLE OF CONTENTS

1. [Task Completion Expectations](#1-task-completion-expectations)
2. [Dependency Installation Rule - ALWAYS Install Dependencies](#2-dependency-installation-rule)
3. [UI Design Rules - ChatGPT Specification](#3-ui-design-rules)
4. [Integration Rules](#4-integration-rules)
5. [Code Quality Rules](#5-code-quality-rules)
6. [Architecture Rules](#6-architecture-rules)
7. [Worker Rules](#7-worker-rules)
8. [Overseer Rules](#8-overseer-rules)
9. [Enforcement Rules](#9-enforcement-rules)
10. [Periodic Refresh System](#10-periodic-refresh-system)

---

## 1. TASK COMPLETION EXPECTATIONS

### Deliver complete work before moving on

- Complete the intended functionality before marking a task done.
- Track remaining work in the project tracker or ledger instead of leaving incomplete behavior in shipping paths.
- Keep documentation and UI text accurate about what is implemented.

---

## 2. DEPENDENCY INSTALLATION RULE

### 🚨 DEPENDENCY INSTALLATION - ALWAYS REQUIRED

**ALL dependencies MUST be identified, installed, and verified before starting and completing ANY task.**

**NO exceptions. NO shortcuts.**

**This applies to:**

- ✅ Python packages (`pip install`, `conda install`, etc.)
- ✅ NuGet packages (`.csproj` dependencies)
- ✅ System libraries (audio libraries, CUDA, etc.)
- ✅ Build tools (MSBuild, dotnet CLI, etc.)
- ✅ Development tools (IDEs, extensions, etc.)

### Dependency Installation Process:

1. **Identify ALL dependencies** required for the task
2. **Install ALL dependencies** completely
3. **Verify ALL installations** work correctly
4. **Test dependency integration** in code
5. **Document dependency versions** and sources

### 🚫 FORBIDDEN: Starting work without dependencies

- ❌ "I'll install dependencies later"
- ❌ "Dependencies are optional"
- ❌ "It should work without them"
- ❌ "Dependencies are someone else's problem"

---

## 3. UI DESIGN RULES

### 🎨 CHATGPT UI SPECIFICATION - NON-NEGOTIABLE

**The UI design MUST follow the ChatGPT-generated specification EXACTLY.**

**Key Requirements:**

- ✅ **3-row grid structure** (Navigation Rail, Main Content, Status Bar)
- ✅ **4 PanelHosts** for dynamic content
- ✅ **Navigation Rail:** 320px width, dark theme
- ✅ **Command Toolbar:** 48px height, light theme
- ✅ **Status Bar:** 32px height, dark theme
- ✅ **VSQ.\* design tokens** used exclusively (NO hardcoded colors)
- ✅ **MVVM separation** maintained perfectly

### 🚫 FORBIDDEN UI Changes:

- ❌ Changing the 3-row grid structure
- ❌ Removing or changing PanelHost usage
- ❌ Using hardcoded colors instead of VSQ.\* tokens
- ❌ Breaking MVVM separation
- ❌ Modifying Navigation Rail/Command Toolbar/Status Bar dimensions

---

## 4. INTEGRATION RULES

### 🔗 CONCEPT EXTRACTION AND CONVERSION

**Concepts from other frameworks MUST be extracted and converted to WinUI 3/C#.**

**Examples:**

- ✅ React/TypeScript concepts → WinUI 3/C# equivalents
- ✅ Python GUI concepts → WinUI 3/C# equivalents
- ✅ Web development patterns → WinUI 3/C# equivalents

### Integration Process:

1. **Identify source framework** concepts
2. **Extract core functionality** requirements
3. **Map to WinUI 3/C#** equivalents
4. **Implement using native** WinUI 3/C# patterns
5. **Test integration** thoroughly

---

## 5. CODE QUALITY RULES

### ✅ CORRECTNESS OVER SPEED RULE - HIGHEST PRIORITY

**Code MUST be correct first, then optimized.**

**Priority Order:**

1. ✅ **Correctness** - Code works correctly
2. ✅ **Completeness** - All features implemented
3. ✅ **Reliability** - No crashes, handles edge cases
4. ✅ **Maintainability** - Clean, readable code
5. ⚡ **Performance** - Only after correctness achieved

### 🚫 FORBIDDEN: Performance-first development

- ❌ "It works, ship it" (must be correct first)
- ❌ "Performance is more important than correctness"
- ❌ "We'll fix bugs later"

---

## 6. ARCHITECTURE RULES

### 🏗️ LOCAL-FIRST ARCHITECTURE

**All engines, quality analysis, and backend API MUST run locally.**

**NO external API calls for core features:**

- ❌ Cloud APIs for TTS/STT
- ❌ External services for audio processing
- ❌ Remote servers for core functionality

### MVVM Separation

- ✅ **View (XAML):** UI layout and styling only
- ✅ **ViewModel (C#):** UI logic, commands, data binding
- ✅ **Model (C#):** Business logic, data access

### File Structure

```
src/
├── VoiceStudio.App/          # WinUI 3 frontend
│   ├── Views/                 # XAML views
│   ├── ViewModels/           # ViewModels
│   └── Services/             # Services
└── backend/                  # Python FastAPI
    ├── api/                  # API routes
    └── core/                 # Core functionality
```

---

## 7. WORKER RULES

### 👷 WORKER RESPONSIBILITIES

**Workers MUST:**

- ✅ Work 100% autonomously (no waiting for approval)
- ✅ Complete tasks to 100% standards
- ✅ Install all dependencies for every task
- ✅ Update progress after each task completion
- ✅ Follow all rules with zero tolerance

**Workers MUST NOT:**

- ❌ Pause work waiting for approval
- ❌ Start work without dependencies installed
- ❌ Leave incomplete implementations
- ❌ Ignore rule violations

### Worker Specialization:

- **Worker 1:** Backend/Engines/Audio Processing (Python, ML, audio)
- **Worker 2:** UI/UX/Frontend (WinUI 3, XAML, ViewModels)
- **Worker 3:** Testing/Quality/Documentation (Testing, QA, docs)

---

## 8. OVERSEER RULES

### 🎯 OVERSEER AUTHORITY

**The Overseer has COMPLETE authority to:**

- ✅ Reject incomplete work immediately
- ✅ Revert violating changes
- ✅ Assign punishment tasks for violations
- ✅ Block workers from proceeding
- ✅ Require rework before approval

### Overseer Responsibilities:

- ✅ Monitor all worker progress
- ✅ Verify rule compliance on all changes
- ✅ Enforce 100% completion standards
- ✅ Coordinate task assignments
- ✅ Escalate critical issues

---

## 9. ENFORCEMENT RULES

### 🚨 VIOLATION CONSEQUENCES

**Level 1 - Minor Violation:**

- Detection: Found forbidden term in comment
- Response: Immediate correction required
- Action: Worker fixes immediately

**Level 2 - Moderate Violation:**

- Detection: Incomplete implementation
- Response: Task rejection and rework
- Action: Revert changes, reassign task

**Level 3 - Critical Violation:**

- Detection: Multiple violations, rule ignorance
- Response: Full stop, punishment assignment
- Action: Block progress, assign cleanup tasks

### Zero Tolerance Policy:

- **NO exceptions** to any rule
- **ALL violations** addressed immediately
- **Systematic enforcement** across all workers

---

## 10. PERIODIC REFRESH SYSTEM

### 📅 RULE REFRESH REQUIREMENTS

**AI agents MUST refresh rules:**

- ✅ **Before starting work** each session
- ✅ **After major updates** to rules
- ✅ **When encountering conflicts** between rules
- ✅ **Weekly minimum** refresh schedule

### Refresh Process:

1. Read `MASTER_RULES_COMPLETE.md`
2. Verify understanding of all rules
3. Confirm no conflicts between rules
4. Update local rule knowledge
5. Proceed with work

---

**ALL RULES CONTENT EMBEDDED ABOVE - NO EXTERNAL REFERENCES**
