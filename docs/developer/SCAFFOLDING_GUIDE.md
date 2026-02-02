# VoiceStudio Scaffolding Guide

> **Last Updated**: 2026-02-02  
> **Owner**: Build & Tooling (Role 2)  
> **Purpose**: Guide for using scaffolding tools to generate new components

---

## Overview

VoiceStudio provides CLI scaffolding tools that generate new components with correct
patterns, including:
- Proper directory structure
- Required imports and base classes
- Test file stubs
- TODO markers for customization

Using scaffolds ensures consistency across the codebase and speeds up development.

---

## Available Scaffolds

### 1. Panel Scaffold

Generates a new UI panel with View, ViewModel, and test file.

```bash
python tools/scaffolds/generate_panel.py --name <PanelName> [--region <Region>]
```

**Arguments:**
- `--name`: PascalCase panel name (e.g., `QualityMonitor`)
- `--region`: Panel region (default: `Center`). Options: `Center`, `Left`, `Right`, `Bottom`
- `--description`: Optional description for help text
- `--dry-run`: Show what would be created without creating files

**Generated Files:**
- `src/VoiceStudio.App/Views/Panels/{Name}View.xaml`
- `src/VoiceStudio.App/Views/Panels/{Name}View.xaml.cs`
- `src/VoiceStudio.App/ViewModels/{Name}ViewModel.cs`
- `tests/ui/test_{name}.py`

**Example:**
```bash
python tools/scaffolds/generate_panel.py --name QualityMonitor --region Center
```

---

### 2. Route Scaffold

Generates a new FastAPI route with router, models, and test file.

```bash
python tools/scaffolds/generate_route.py --name <route_name> [--methods <METHODS>]
```

**Arguments:**
- `--name`: snake_case route name (e.g., `quality_metrics`)
- `--methods`: Comma-separated HTTP methods (default: `GET,POST`)
- `--dry-run`: Show what would be created without creating files

**Generated Files:**
- `backend/api/routes/{name}.py`
- `backend/api/models/{name}_models.py`
- `tests/unit/backend/api/routes/test_{name}.py`

**Example:**
```bash
python tools/scaffolds/generate_route.py --name quality_metrics --methods GET,POST,DELETE
```

---

### 3. Engine Scaffold

Generates a new engine adapter with manifest, implementation, and test file.

```bash
python tools/scaffolds/generate_engine.py --name <engine_name> --type <type> --subtype <subtype>
```

**Arguments:**
- `--name`: snake_case engine name (e.g., `cosyvoice`)
- `--type`: Engine type (`audio`, `image`, `video`)
- `--subtype`: Engine subtype (e.g., `tts`, `stt`, `cloning`, `generation`)
- `--description`: Optional description
- `--dry-run`: Show what would be created without creating files

**Generated Files:**
- `engines/{type}/{name}/engine.manifest.json`
- `app/core/engines/{name}_engine.py`
- `tests/unit/engines/test_{name}.py`

**Example:**
```bash
python tools/scaffolds/generate_engine.py --name cosyvoice --type audio --subtype tts
```

---

## Post-Generation Steps

Each scaffold outputs a list of manual steps required after generation.

### For Panels

1. Register in `PanelRegistry.cs` or `AdvancedPanelRegistrationService.cs`
2. Add resource string `Panel.{Name}.DisplayName` to `Resources.resw`
3. Build and test

### For Routes

1. Import and register router in `backend/api/main.py`
2. Implement route logic
3. Test endpoint

### For Engines

1. Add engine to `backend/config/engine_config.json`
2. Add dependencies to manifest
3. Implement engine methods
4. Test health check

---

## Dry Run Mode

All scaffolds support `--dry-run` to preview files without creating them:

```bash
python tools/scaffolds/generate_panel.py --name TestPanel --dry-run
```

Output:
```
============================================================
VOICESTUDIO PANEL SCAFFOLD
============================================================

Files created:
  [OK] [DRY RUN] .../TestPanelView.xaml
  [OK] [DRY RUN] .../TestPanelView.xaml.cs
  [OK] [DRY RUN] .../TestPanelViewModel.cs
  [OK] [DRY RUN] .../test_test_panel.py

Manual steps required:
  1. Register panel in PanelRegistry.cs...
  ...
```

---

## Template Customization

Templates are located in `tools/scaffolds/templates/`:

| Template | Purpose |
|----------|---------|
| `panel_view.xaml.template` | XAML View |
| `panel_view.xaml.cs.template` | View code-behind |
| `panel_viewmodel.cs.template` | ViewModel |
| `panel_test.py.template` | Panel test |
| `route_router.py.template` | FastAPI router |
| `route_models.py.template` | Pydantic models |
| `route_test.py.template` | Route test |
| `engine_manifest.json.template` | Engine manifest |
| `engine_adapter.py.template` | Engine adapter |
| `engine_test.py.template` | Engine test |

Placeholders use `{{NAME}}` syntax and are replaced during generation.

---

## When NOT to Use Scaffolds

Scaffolds may not be appropriate for:

1. **Modifying existing components** - Use scaffolds only for new components
2. **Highly specialized components** - If scaffold patterns don't fit
3. **Quick prototypes** - For throwaway code during exploration

When skipping scaffolds, add a comment explaining why and ensure patterns are consistent.

---

## References

- ADR-025: Compatibility Matrix and Scaffolding System
- AI Agent Development Guide: `docs/developer/AI_AGENT_DEVELOPMENT_GUIDE.md`
- Compatibility Matrix: `config/compatibility_matrix.yml`

---

## Changelog

| Date | Change |
|------|--------|
| 2026-02-02 | Initial guide created (Phase 2) |
