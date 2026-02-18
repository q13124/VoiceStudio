# Engine Adapter Pattern

## Goal

Integrate existing `EngineProtocol` implementations into the plugin system
without moving or rewriting engine internals.

## Architecture

1. Existing engine remains in `app/core/engines/<engine>.py`.
2. Plugin adapter lives in `plugins/engine_<engine>/`.
3. Adapter maps plugin API to engine API.

## Lifecycle Mapping

- Plugin `initialize()` -> engine `initialize()`
- Plugin route `/synthesize` -> engine `synthesize(...)`
- Plugin `cleanup()` -> engine `cleanup()`

## Design Rules

- Keep adapter thin; no model logic duplication.
- Keep plugin boundary explicit and observable.
- Return clear failure payloads on synthesis errors.
- Register adapter metadata with engine registry at plugin startup.

## Current Adapter Implementations

- `plugins/engine_xtts_v2`
- `plugins/engine_piper`
- `plugins/engine_bark`
