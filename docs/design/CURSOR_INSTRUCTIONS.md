# Cursor Implementation Instructions

## System Context

This document provides explicit instructions for implementing the VoiceStudio application. **Read this entire document before making any changes.**

## Core Principle

**This is a professional-grade studio application, not a toy.**

The architecture is intentionally complex and modular to support:
- 100+ panels
- Enterprise-level functionality
- Professional audio production workflows
- Team collaboration
- Future extensibility

## Implementation Command

When implementing this project, use this exact command:

```
Implement exactly this layout and panel structure. Don't simplify anything, 
don't reduce panel count, and don't merge files. Treat this UI as a pro-grade 
studio application, not a toy.
```

## Critical Rules

### 1. Panel Structure
- **MUST** implement all 6 primary panels
- **MUST** maintain separate View/ViewModel files for each
- **MUST** use PanelHost control for all panels
- **MUST** keep 3×2 grid layout in MainWindow

### 2. File Organization
- **MUST** follow the canonical file tree exactly
- **MUST** maintain MVVM separation
- **MUST** keep Core library separate from App
- **MUST NOT** merge files "for simplicity"

### 3. Design System
- **MUST** use VSQ.* design tokens only
- **MUST** keep all placeholder regions visible
- **MUST** follow the design system consistently

### 4. Architecture
- **MUST** maintain backend/frontend separation
- **MUST** use shared contract schemas
- **MUST** follow the data flow architecture

## Reference Documents

1. **GUARDRAILS.md** - Absolute rules that must not be violated
2. **architecture-detailed.md** - Complete architecture specification
3. **file-structure.md** - Canonical file tree
4. **roadmap.md** - Implementation phases

## Before Making Changes

1. Read GUARDRAILS.md
2. Check the canonical file structure
3. Verify design token usage
4. Ensure MVVM separation
5. Confirm panel count (6 panels minimum)

## Common Mistakes to Avoid

❌ Reducing panel count "to simplify"  
❌ Merging View and ViewModel files  
❌ Replacing PanelHost with direct Grids  
❌ Removing placeholder regions  
❌ Using hardcoded colors instead of design tokens  
❌ Moving files without permission  
❌ Simplifying the 3×2 grid layout  

## Success Criteria

✅ All 6 panels implemented with separate files  
✅ MainWindow uses 3×2 grid with PanelHost controls  
✅ All placeholders visible and distinct  
✅ All colors use VSQ.* design tokens  
✅ Core library separate and properly referenced  
✅ File structure matches canonical tree  
✅ No simplifications or "helpful" reductions  

## Questions?

If you're unsure about any change:
1. Check GUARDRAILS.md first
2. Refer to the architecture specification
3. Maintain the structure as-is
4. Ask for explicit permission before simplifying

Remember: **Complexity is intentional. Do not simplify.**

