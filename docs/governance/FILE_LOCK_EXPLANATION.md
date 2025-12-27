# File Lock Explanation - Why It Exists

**Date:** 2025-01-28  
**Question:** Why is the file lock there? What will unlock it?

## Root Cause

The file lock on `Microsoft.Bcl.AsyncInterfaces.dll` is **NOT from a previous plan or roadmap**. It's **normal IDE behavior**.

### The Locking Process

**Process:** dotnet.exe (PID 27988)  
**What It Is:** OmniSharp - C# language server  
**Part Of:** Cursor IDE's C# extension  
**Purpose:** Provides IntelliSense, code completion, error checking

### Why It Locks Files

1. **OmniSharp loads DLLs** from NuGet cache to analyze your code
2. **Keeps file handles open** for performance (avoids repeated file I/O)
3. **Prevents NuGet from modifying** those files during restore/update
4. **This is standard behavior** for all IDEs with language servers

## What Will Unlock It

The lock will release when:

1. ✅ **Cursor IDE is closed** → OmniSharp terminates automatically
2. ✅ **Computer is restarted** → All processes terminate
3. ✅ **OmniSharp process is killed** → `Stop-Process -Id 27988 -Force`
4. ✅ **Language server restarts** → Can be triggered from Cursor command palette

## This Is NOT From a Previous Plan

The project has a **File Locking Protocol** (`docs/governance/FILE_LOCKING_PROTOCOL.md`), but that's for:

- **Coordinating multi-agent file edits** (preventing merge conflicts)
- **NOT about NuGet cache locks**

The NuGet cache lock is a **side effect of IDE operation**, not a project configuration.

## Why It Persists

- **OmniSharp stays running** while Cursor IDE is open
- **File handles remain open** for performance
- **This is expected behavior** - not a bug or configuration issue

## After Restart

When you restart your computer:

1. ✅ All file locks will be released
2. ✅ `dotnet restore` will succeed
3. ✅ `dotnet build` should succeed (all errors are fixed)
4. ⚠️ When you reopen Cursor IDE, OmniSharp will restart and create new locks (normal)

## Important Note

**File locks from OmniSharp are normal and expected.** They:

- ✅ Don't prevent builds run from terminal
- ✅ Don't prevent CI/CD builds
- ✅ Only affect NuGet restore when IDE is open
- ✅ Are automatically released when IDE closes

**Solution:** Run builds from terminal outside the IDE, or close IDE before restore.
