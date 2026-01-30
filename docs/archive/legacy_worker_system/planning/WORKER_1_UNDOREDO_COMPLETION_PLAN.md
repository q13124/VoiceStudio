# UndoRedoService Integration Completion Plan

**Date:** 2025-01-28  
**Goal:** Complete all remaining UndoRedoService integrations  
**Status:** 🔄 **IN PROGRESS**

---

## Strategy

1. **Identify all panels** that need UndoRedoService but don't have it yet
2. **Focus on panels with collection operations** (create/delete that modify ObservableCollections)
3. **Skip read-only panels** or panels that don't modify collections
4. **Integrate systematically** following the established pattern

---

## Panels to Check/Integrate

### High Priority - Need Immediate Integration

1. **TranscribeViewModel** ⚠️ **NEEDS INTEGRATION**
   - Has: ObservableCollection<TranscriptionResponse> transcriptions
   - Has: DeleteTranscriptionAsync method
   - Missing: UndoRedoService initialization and action registration

### Medium Priority - Check and Integrate

2. **AnalyzerViewModel** - Check if it has collection operations
3. **QualityBenchmarkViewModel** - Check if it has collection operations
4. **EngineRecommendationViewModel** - Check if it has collection operations
5. **ABTestingViewModel** - Check if it has collection operations
6. **MiniTimelineViewModel** - Check if it has collection operations

### Low Priority - Verify They Don't Need It

7. **DiagnosticsViewModel** - Read-only logs (may not need)
8. **VoiceSynthesisViewModel** - Already checked - doesn't need (no collection operations)
9. **AudioAnalysisViewModel** - Already verified - read-only

---

## Integration Pattern

For each panel that needs integration:

1. Add `_undoRedoService` field
2. Initialize in constructor with try-catch
3. Create action class if needed
4. Register action after collection modification operations
5. Handle selection state in undo/redo callbacks

---

## Next Steps

1. ✅ Create this plan
2. ⏭️ Integrate TranscribeViewModel
3. ⏭️ Check and integrate remaining panels systematically
4. ⏭️ Verify all panels are complete
5. ⏭️ Create final completion document

---

**Status:** Starting with TranscribeViewModel integration...

