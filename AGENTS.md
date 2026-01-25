# AGENTS

## Required Rules (alwaysApply)
- `.cursor/rules/core/rule-governance.mdc` ⚠️ AGENTS CANNOT MODIFY RULES WITHOUT USER CONSENT
- `.cursor/rules/core/project-context.mdc`
- `.cursor/rules/core/architecture.mdc`
- `.cursor/rules/core/anti-drift.mdc`
- `.cursor/rules/security/api-key-management.mdc`
- `.cursor/rules/security/secure-coding.mdc`
- `.cursor/rules/security/mcp-security.mdc`
- `.cursor/rules/workflows/git-conventions.mdc`
- `.cursor/rules/workflows/planning.mdc` — Multi-phase execution plan standards
- `.cursor/rules/mcp/mcp-usage.mdc`
- `.cursor/rules/quality/repo-hygiene.mdc`
- `.cursor/rules/workflows/state-gate.mdc`
- `.cursor/rules/workflows/closure-protocol.mdc`
- `.cursor/rules/workflows/verifier-subagent.mdc`
- Extra subproject rules: `runtime/external/invokeai/invokeai/frontend/web/CLAUDE.md` and `runtime/external/localai/AGENTS.md`

## Professional Standard
- Operate as a senior executive professional software engineer and architect.
- Prefer correctness, maintainability, and verification over speed.
- Document decisions, risks, and rollback steps for non-trivial changes.
- Follow `.cursor/STATE.md` context protocol before code modifications.

## Build and test commands
- Build (WinUI/C#): `dotnet build VoiceStudio.sln -c Debug -p:Platform=x64`
- Test (C#): `dotnet test src/VoiceStudio.App.Tests/VoiceStudio.App.Tests.csproj -c Debug -p:Platform=x64`
- Test (Python): `python -m pytest tests`
- Single pytest: `python -m pytest tests/path/to/test_file.py::TestClass::test_name`
- Single MSTest: `dotnet test src/VoiceStudio.App.Tests/VoiceStudio.App.Tests.csproj -c Debug -p:Platform=x64 --filter "FullyQualifiedName~Namespace.Class.Test"`

## Project structure
- Frontend: `src/VoiceStudio.App/` (WinUI 3 MVVM).
- Core library: `src/VoiceStudio.Core/`.
- Backend: `backend/api/` and `backend/services/`.
- Engine layer: `app/core/` with manifests in `engines/`.
- Tests: `tests/` and `src/VoiceStudio.App.Tests/`.
- Packaging: `installer/`.

## Code style
- Follow `.editorconfig` and language-specific rules under `.cursor/rules/languages/`.
