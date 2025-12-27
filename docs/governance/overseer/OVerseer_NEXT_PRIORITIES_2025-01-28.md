# Overseer: Next Task Priorities

## VoiceStudio Quantum+ - What's Next on the Task List

**Date:** 2025-01-28  
**Status:** 🎯 **PRIORITY TASKS IDENTIFIED**  
**Overall Progress:** ~65% complete (17/26 tasks)

---

## 🚀 IMMEDIATE NEXT PRIORITIES

### Priority 1: HIGH PRIORITY TASKS (4 tasks, 26-34 hours)

#### **Worker 1 - Backend (2 HIGH priority tasks, 6-9 hours)**

1. **TASK 1.15: BackendClient Duplicate Code Removal** (2-3 hours) ⭐ **START HERE**

   - **What:** Remove duplicate method definitions in BackendClient.cs
   - **Impact:** Code quality improvement, reduced maintenance burden
   - **Files:** `src/VoiceStudio.App/Services/BackendClient.cs`
   - **Why First:** Quick win, improves code quality, unblocks future refactoring

2. **TASK 1.16: Exponential Backoff Retry Logic** (4-6 hours)
   - **What:** Enhance retry logic with exponential backoff
   - **Impact:** Improved network resilience, better error handling
   - **Files:** `src/VoiceStudio.App/Services/BackendClient.cs`
   - **Why Next:** Builds on TASK 1.15, improves reliability

#### **Worker 2 - UI/UX (2 HIGH priority tasks, 10-14 hours)**

3. **TASK 2.3: Toast Styles & Standardization** (4-6 hours) ⭐ **START HERE**

   - **What:** Create standardized toast styles and enhance ToastNotificationService
   - **Files:** `ToastStyles.xaml`, update `ToastNotificationService.cs`, update 50+ files
   - **Impact:** UX consistency across the app
   - **Why First:** High visibility, improves user experience

4. **TASK 2.6: Packaging Script & Smoke Checklist** (6-8 hours)
   - **What:** Create repeatable packaging script and comprehensive smoke checklist
   - **Files:** `scripts/package_release.ps1`, `Package.appxmanifest`, `docs/release/SMOKE_CHECKLIST.md`
   - **Impact:** Release readiness - critical for deployment
   - **Why Next:** Essential for release, can be done in parallel with other tasks

#### **Worker 3 - Testing/QA (1 HIGH priority task in progress)**

5. **TASK 3.3: Async/UX Safety Patterns** (8-10 hours) 🚧 **IN PROGRESS**
   - **Status:** Foundation complete, ViewModel updates pending
   - **What:** Standardize async patterns in ViewModels
   - **Progress:**
     - ✅ Async patterns documentation created
     - ✅ Audit checklist created (72 ViewModels, 432 AsyncRelayCommand instances)
     - ✅ Migration pattern documented
     - ⏳ High-priority ViewModels update pending (5 ViewModels, ~40 commands)
     - ⏳ Remaining ViewModels update pending (67 ViewModels, ~392 commands)
   - **Impact:** UX safety - prevents duplicate operations
   - **Why Continue:** Prevents user-facing bugs, improves reliability

---

## 📋 RECOMMENDED EXECUTION ORDER

### **Week 1 Focus: Quick Wins & High Impact**

**Day 1-2:**

- ✅ **Worker 1:** TASK 1.15 (BackendClient Duplicate Code Removal) - 2-3 hours
- ✅ **Worker 2:** TASK 2.3 (Toast Styles) - 4-6 hours
- ✅ **Worker 3:** Continue TASK 3.3 (Async Safety) - High-priority ViewModels

**Day 3-4:**

- ✅ **Worker 1:** TASK 1.16 (Exponential Backoff) - 4-6 hours
- ✅ **Worker 2:** Continue TASK 2.3 or start TASK 2.6 (Packaging) - 6-8 hours
- ✅ **Worker 3:** Continue TASK 3.3 (Async Safety) - Remaining ViewModels

**Day 5:**

- ✅ **Worker 1:** TASK 1.17 (Dependency Injection Migration) - 4-6 hours (MEDIUM priority)
- ✅ **Worker 2:** TASK 2.6 (Packaging Script) - 6-8 hours
- ✅ **Worker 3:** TASK 3.6 (UI Smoke Tests) - 8-10 hours (HIGH priority)

---

## 🎯 MEDIUM PRIORITY TASKS (Can be done in parallel)

### **Worker 1 (2 tasks, 6-9 hours)**

1. **TASK 1.17: Dependency Injection Migration** (4-6 hours)

   - Migrate from static ServiceProvider to Microsoft.Extensions.DependencyInjection
   - Better testability, industry-standard pattern

2. **TASK 1.18: BackendClient Refactoring Phase 1** (2-3 hours)
   - Create base client interface and implementation
   - Foundation for future BackendClient decomposition

### **Worker 2 (2 tasks, 10-14 hours)**

3. **TASK 2.2: Locale Switch Toggle** (4-6 hours)

   - ✅ **UNBLOCKED** - TASK 2.1 complete!
   - Implement locale switching with UI toggle and persistence
   - Internationalization support

4. **TASK 2.4: Empty States & Loading Skeletons Standardization** (6-8 hours)
   - Standardize empty states and loading skeletons across all panels
   - UX consistency

### **Worker 3 (4 tasks, 24-32 hours)**

5. **TASK 3.6: UI Smoke Tests** (8-10 hours) - HIGH priority

   - Create golden-path UI smoke tests
   - Automated UI testing

6. **TASK 3.7: ViewModel Contract Tests** (8-10 hours) - HIGH priority

   - Expand ViewModel contract tests with mocks
   - > 80% test coverage

7. **TASK 3.2: Panel Lifecycle Documentation** (4-6 hours)

   - Document panel lifecycle (init/activate/deactivate)
   - Developer documentation

8. **TASK 3.4: Diagnostics Pane Enhancements** (6-8 hours)

   - Enhance DiagnosticsView with tabs
   - Developer tooling

9. **TASK 3.5: Analytics Events Integration** (6-8 hours)

   - Integrate analytics events into key flows
   - Observability

10. **TASK 3.8: Snapshot Tests** (6-8 hours)
    - Add snapshot tests for analytics/visualization outputs
    - Detect regressions

---

## 🐛 KNOWN ISSUES TO FIX

### **Linter Errors** (275 total across 8 files) - MEDIUM Priority

**Status:** ⚠️ **VERIFICATION NEEDED** - `read_lints` shows 0 errors, but task document lists 275

**Files with Reported Errors:**

1. VoiceStyleTransferViewModel.cs - 13 errors
2. MCPDashboardViewModel.cs - 48 errors
3. JobProgressViewModel.cs - 59 errors
4. QualityOptimizationWizardViewModel.cs - 21 errors
5. SpatialStageViewModel.cs - 37 errors
6. MixAssistantViewModel.cs - 66 errors
7. AdvancedSettingsViewModel.cs - 17 errors
8. EmbeddingExplorerViewModel.cs - 2 errors (reported fixed)

**Action:** Verify current linter error status and fix remaining issues

---

## ✅ COMPLETED MILESTONES

- ✅ **TASK 2.1:** Resource Files for Localization - **100% COMPLETE!** 🎉
  - 1,313 resource entries
  - 69/69 ViewModels using ResourceHelper (100% compliance!)
- ✅ **TemplateLibraryViewModel:** All 50 linter errors fixed! 🎉
- ✅ **ScriptEditorViewModel:** All 62 linter errors fixed! 🎉
- ✅ **EmbeddingExplorerViewModel:** All linter errors fixed! 🎉

---

## 📊 PROGRESS SUMMARY

**Overall:** 17/26 tasks complete (~65%)

**By Worker:**

- **Worker 1:** 14/18 tasks (78%) - 4 remaining
- **Worker 2:** 2/6 tasks (33%) - 4 remaining (TASK 2.1 complete!)
- **Worker 3:** 7/12 tasks (58%) - 5 remaining (1 in progress)

**Estimated Time Remaining:** 40-58 hours

---

## 🎯 RECOMMENDED STARTING POINT

### **For Worker 1:**

**Start with:** TASK 1.15 (BackendClient Duplicate Code Removal) - 2-3 hours

- Quick win
- Improves code quality
- Unblocks future refactoring

### **For Worker 2:**

**Start with:** TASK 2.3 (Toast Styles & Standardization) - 4-6 hours

- High visibility
- Improves UX consistency
- Can be done in parallel with Worker 1

### **For Worker 3:**

**Continue with:** TASK 3.3 (Async/UX Safety Patterns) - High-priority ViewModels

- Foundation already complete
- Prevents user-facing bugs
- High impact on reliability

---

## 📝 NOTES

- **Linter Status:** Needs verification - `read_lints` shows 0 errors, but task document lists 275. May have been fixed.
- **Resource Files:** Stable at 1,313 entries - TASK 2.1 complete!
- **Design System:** 66% compliance (286 EnhancedAsyncRelayCommand vs 146 AsyncRelayCommand)
- **Build System:** OmniSharp warning documented - non-blocking, no action needed

---

**Last Updated:** 2025-01-28  
**Status:** 🎯 **READY TO PROCEED - PRIORITIES IDENTIFIED**
