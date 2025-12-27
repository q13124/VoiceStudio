# Periodic Rules Refresh System
## VoiceStudio Quantum+ - Automated Rule Reminder System

**Date:** 2025-01-28  
**Status:** ACTIVE  
**Purpose:** Ensure all AI instances (especially the three workers) periodically refresh themselves on rules, guidelines, roles, and expectations

**PRIMARY REFERENCE:** `docs/governance/MASTER_RULES_COMPLETE.md` - **ALL INSTANCES MUST USE THIS AS PRIMARY REFERENCE**

---

## 🎯 SYSTEM OVERVIEW

This system ensures that all AI instances working on the VoiceStudio project periodically refresh their understanding of:
- **Rules and Guidelines** - All project rules, especially the NO stubs/placeholders rule
- **UI Design Specifications** - Original ChatGPT UI specification that must be followed exactly
- **Roles and Responsibilities** - Worker assignments and expectations
- **Project Standards** - Code quality, architecture, and implementation standards

**CRITICAL:** All instances must use `MASTER_RULES_COMPLETE.md` which contains ALL synonyms, variations, and loophole prevention patterns to prevent bypass attempts.

---

## 📋 REFRESH SCHEDULE

### Automatic Refresh Triggers

**1. Session Start Refresh**
- **When:** At the beginning of every new AI session
- **Action:** Read the master rules document
- **PRIMARY DOCUMENT:**
  - **`docs/governance/MASTER_RULES_COMPLETE.md`** - **MUST READ FIRST AND COMPLETELY**
    - Contains ALL rules in full
    - Contains ALL forbidden terms, synonyms, and variations
    - Contains ALL loophole prevention patterns
    - Contains UI design rules
    - Contains integration rules
    - Contains all other project rules

**2. Task Start Refresh**
- **When:** Before starting any new task
- **Action:** Review relevant sections of master rules document
- **PRIMARY DOCUMENT:**
  - **`docs/governance/MASTER_RULES_COMPLETE.md`** - Review relevant sections:
    - Section 1: The Absolute Rule (for all tasks)
    - Section 2: UI Design Rules (for UI tasks)
    - Section 3: Integration Rules (for integration tasks)
    - Section 4: Code Quality Rules (for all code tasks)
    - Section 5: Architecture Rules (for architecture tasks)

**3. Periodic Refresh (Every 30 Minutes)**
- **When:** During long sessions, refresh every 30 minutes
- **Action:** Quick review of critical sections
- **PRIMARY DOCUMENT:**
  - **`docs/governance/MASTER_RULES_COMPLETE.md`** - Quick review:
    - Section 1: The Absolute Rule (forbidden terms and patterns)
    - Section 2: UI Design Rules (if UI work)
    - Section 9: Periodic Refresh System (this section)

**4. Before Code Changes**
- **When:** Before making any code changes
- **Action:** Verify compliance with rules
- **PRIMARY DOCUMENT:**
  - **`docs/governance/MASTER_RULES_COMPLETE.md`** - Review:
    - Section 1: The Absolute Rule - Verification Checklist
    - Section 1: The Absolute Rule - Loophole Prevention
    - Section 1: The Absolute Rule - All Forbidden Terms (complete list)
- **Check:**
  - No stubs, placeholders, bookmarks, or tags (including ALL synonyms and variations)
  - No loophole attempts (capitalization, spacing, punctuation, etc.)
  - UI changes follow ChatGPT specification exactly
  - Code is 100% complete and functional

**5. Before Task Completion**
- **When:** Before marking a task as complete
- **Action:** Final verification against all rules
- **PRIMARY DOCUMENT:**
  - **`docs/governance/MASTER_RULES_COMPLETE.md`** - Final verification:
    - Section 1: The Absolute Rule - Verification Checklist (complete all checks)
    - Section 1: The Absolute Rule - All Forbidden Terms (search for ALL variations)
    - Section 1: The Absolute Rule - Loophole Prevention (check for ALL workarounds)
- **Check:**
  - All functionality implemented (no placeholders, including ALL synonyms)
  - No forbidden terms in ANY form (including ALL variations and workarounds)
  - UI follows exact ChatGPT specification
  - All rules followed

---

## 📚 CRITICAL DOCUMENTS TO REFRESH

### PRIMARY REFERENCE (MUST USE)

**`docs/governance/MASTER_RULES_COMPLETE.md`** - **PRIMARY REFERENCE FOR ALL INSTANCES**

**This document contains:**
- ✅ **ALL rules in full** - Complete ruleset in one place
- ✅ **ALL forbidden terms** - Complete list of bookmarks, placeholders, stubs, tags, status words
- ✅ **ALL synonyms and variations** - Every possible variation to prevent bypass attempts
- ✅ **ALL loophole prevention patterns** - Capitalization, spacing, punctuation, encoding, context variations
- ✅ **UI design rules** - Complete ChatGPT UI specification requirements
- ✅ **Integration rules** - Complete integration policy and guidelines
- ✅ **Code quality rules** - Complete production-ready code requirements
- ✅ **Architecture rules** - Complete architecture requirements
- ✅ **Worker rules** - Complete worker responsibilities
- ✅ **Overseer rules** - Complete overseer responsibilities
- ✅ **Enforcement rules** - Complete enforcement strategies
- ✅ **Periodic refresh system** - This system

**Why This Document:**
- **Prevents bypass attempts** - Contains ALL synonyms and variations
- **Single source of truth** - All rules in one place
- **Complete coverage** - Nothing is missing
- **Easy reference** - One document to read
- **Comprehensive** - Includes all loophole prevention patterns

### Secondary References (For Specific Details)

**Tier 2: Detailed Specifications (Reference as Needed)**
1. **`docs/design/ORIGINAL_UI_SCRIPT_CHATGPT.md`**
   - Original ChatGPT UI specification (source of truth)
   - Exact layout structure details
   - Complete XAML code examples

2. **`docs/design/VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md`**
   - Complete original specification with full XAML code
   - Exact MainWindow structure
   - Complete PanelHost structure
   - Complete 6 core panels XAML code

3. **`docs/governance/COMPREHENSIVE_INTEGRATION_LOG_2025-01-28.md`**
   - Integration priorities and guidelines
   - Detailed integration analysis
   - Conversion strategies

4. **`docs/governance/RULE_ENFORCEMENT_RECOMMENDATIONS.md`**
   - Enforcement strategies
   - Verification methods
   - Quality control processes

---

## 🔄 REFRESH PROCEDURE

### For All AI Instances (Overseer + Workers)

**Step 1: Read Master Rules Document**
```markdown
1. Read `docs/governance/MASTER_RULES_COMPLETE.md` - COMPLETE AND THOROUGH READ
   - Section 1: The Absolute Rule (read ALL forbidden terms, synonyms, variations, loophole prevention)
   - Section 2: UI Design Rules (if UI work)
   - Section 3: Integration Rules (if integration work)
   - Section 4: Code Quality Rules (for all code work)
   - Section 5: Architecture Rules (for architecture work)
   - Section 6: Worker Rules (for workers)
   - Section 7: Overseer Rules (for overseer)
   - Section 8: Enforcement Rules
   - Section 9: Periodic Refresh System (this section)
```

**Step 2: Verify Understanding of ALL Forbidden Terms**
```markdown
- Do I understand ALL forbidden bookmarks? (TODO, FIXME, NOTE, HACK, REMINDER, XXX, WARNING, CAUTION, BUG, ISSUE, REFACTOR, OPTIMIZE, REVIEW, CHECK, VERIFY, TEST, DEBUG, DEPRECATED, OBSOLETE, and ALL synonyms)
- Do I understand ALL forbidden placeholders? (dummy, mock, fake, sample, temporary, test data, filler, placeholder, stub data, example data, demonstration data, pseudocode, skeleton data, empty data, null data, blank data, default data, and ALL synonyms)
- Do I understand ALL forbidden stubs? (skeleton, template, outline, empty function, pass statement, unimplemented, stub, empty method, blank function, void function, null implementation, no-op, no operation, and ALL synonyms)
- Do I understand ALL forbidden tags? (ALL categories: markup, version/control, code/documentation, status/indicator, system/metadata, API/service, tracking/monitoring, social/collaboration, content/organizational)
- Do I understand ALL forbidden status words? (pending, incomplete, unfinished, partial, in progress, to do, will be, coming soon, not yet, eventually, later, soon, planned, scheduled, assigned, open, active, ongoing, under construction, under development, in development, work in progress, WIP, draft, rough, prototype, experimental, alpha, beta, preview, pre-release, needs, requires, missing, absent, empty, blank, null, void, tbd, tba, tbc, and ALL synonyms)
- Do I understand ALL loophole prevention patterns? (capitalization, spacing, punctuation, abbreviation, language, encoding, comment style, string concatenation, variable/function names, emoji/unicode, whitespace, regex/pattern, context, negation, meta-references, indirect references, time-based, scope, priority, status variations)
- Do I understand the exact UI layout requirements?
- Do I know what is required (100% complete, functional code)?
```

**Step 3: Apply to Current Work with Complete Verification**
```markdown
- Am I following all rules in my current work?
- Am I maintaining the exact UI structure?
- Am I avoiding ALL forbidden patterns (including ALL synonyms and variations)?
- Am I avoiding ALL loophole attempts (capitalization, spacing, punctuation, etc.)?
- Is my code 100% complete (no placeholders, stubs, bookmarks, tags in ANY form)?
- Have I searched for ALL forbidden terms and variations?
```

### For Worker 1 (Backend/Engines)
**Additional Refresh:**
- `docs/governance/WORKER_1_PROMPT.md` (if exists)
- Backend API standards
- Engine implementation requirements

### For Worker 2 (UI/UX)
**Additional Refresh:**
- `docs/governance/WORKER_2_PROMPT_UIUX.md`
- `docs/design/UI_IMPLEMENTATION_SPEC.md`
- `docs/design/VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md`
- Design token usage requirements

### For Worker 3 (Testing/Quality)
**Additional Refresh:**
- Testing standards
- Quality verification requirements
- Completion verification procedures

---

## 🚨 CRITICAL REMINDERS

### Rule 1: NO Stubs, Placeholders, Bookmarks, or Tags (ALL SYNONYMS FORBIDDEN)

**EVERY task must be 100% complete. NO exceptions, shortcuts, placeholders, bookmarks, tags, or stubs.**

**ALL synonyms and variations are FORBIDDEN. Using similar-meaning words to bypass the rule is FORBIDDEN.**

**Forbidden Bookmarks (ALL Synonyms):**
- TODO, FIXME, NOTE, HACK, REMINDER, XXX, WARNING, CAUTION, BUG, ISSUE, REFACTOR, OPTIMIZE, REVIEW, CHECK, VERIFY, TEST, DEBUG, DEPRECATED, OBSOLETE
- marker, flag, indicator, annotation, reference point, anchor, checkpoint, waypoint, signpost, milestone marker, pointer, reference, sticky note
- bookmark, bookmark marker, bookmark indicator, bookmark annotation, bookmark reference, bookmark pointer
- reminder marker, reminder flag, reminder indicator, reminder annotation, reminder note
- fix marker, fix flag, fix indicator, fix annotation, fix note, fix reminder
- work marker, work flag, work indicator, work annotation, work note, work reminder
- return marker, return flag, return indicator, return annotation, return note, return point
- later marker, later flag, later indicator, later annotation, later note
- revisit marker, revisit flag, revisit indicator, revisit annotation, revisit note
- follow-up marker, follow-up flag, follow-up indicator, follow-up annotation, follow-up note
- revisit point, follow-up point, return point, check point, review point
- **AND ALL OTHER SYNONYMS AND VARIATIONS**

**Forbidden Placeholders (ALL Synonyms):**
- dummy, mock, fake, sample, temporary, test data, filler, placeholder, stub data, example data, demonstration data, pseudocode, skeleton data, empty data, null data, blank data, default data, example, sample, template, prototype, draft, rough, incomplete data, partial data, unfinished data, filler data
- dummy value, mock value, fake value, sample value, test value, placeholder value, stub value, example value, temporary value
- dummy code, mock code, fake code, sample code, test code, placeholder code, stub code, example code, temporary code
- dummy implementation, mock implementation, fake implementation, sample implementation, test implementation, placeholder implementation, stub implementation, example implementation, temporary implementation
- dummy function, mock function, fake function, sample function, test function, placeholder function, stub function, example function, temporary function
- dummy method, mock method, fake method, sample method, test method, placeholder method, stub method, example method, temporary method
- dummy class, mock class, fake class, sample class, test class, placeholder class, stub class, example class, temporary class
- dummy object, mock object, fake object, sample object, test object, placeholder object, stub object, example object, temporary object
- dummy response, mock response, fake response, sample response, test response, placeholder response, stub response, example response, temporary response
- dummy return, mock return, fake return, sample return, test return, placeholder return, stub return, example return, temporary return
- dummy output, mock output, fake output, sample output, test output, placeholder output, stub output, example output, temporary output
- dummy result, mock result, fake result, sample result, test result, placeholder result, stub result, example result, temporary result
- dummy data, mock data, fake data, sample data, test data, placeholder data, stub data, example data, temporary data
- filler code, filler data, filler value, filler implementation, filler function, filler method, filler class, filler object, filler response, filler return, filler output, filler result
- test placeholder, test stub, test dummy, test mock, test fake, test sample
- non-functional code, non-functional data, non-functional value, non-functional implementation, non-functional function, non-functional method, non-functional class, non-functional object
- non-working code, non-working data, non-working value, non-working implementation, non-working function, non-working method, non-working class, non-working object
- non-operational code, non-operational data, non-operational value, non-operational implementation, non-operational function, non-operational method, non-operational class, non-operational object
- non-implemented code, non-implemented data, non-implemented value, non-implemented implementation, non-implemented function, non-implemented method, non-implemented class, non-implemented object
- incomplete code, incomplete data, incomplete value, incomplete implementation, incomplete function, incomplete method, incomplete class, incomplete object
- partial code, partial data, partial value, partial implementation, partial function, partial method, partial class, partial object
- unfinished code, unfinished data, unfinished value, unfinished implementation, unfinished function, unfinished method, unfinished class, unfinished object
- not implemented, not implemented code, not implemented data, not implemented value, not implemented implementation, not implemented function, not implemented method, not implemented class, not implemented object
- **AND ALL OTHER SYNONYMS AND VARIATIONS**

**Forbidden Stubs (ALL Synonyms):**
- skeleton, template, outline, empty function, pass statement, unimplemented, stub, empty method, blank function, void function, null implementation, no-op, no operation
- dummy function, mock function, fake function, placeholder function, incomplete function, partial implementation
- abstract method without implementation, interface without implementation, protocol without implementation
- skeleton function, skeleton method, skeleton class, skeleton implementation, skeleton code
- template function, template method, template class, template implementation, template code
- outline function, outline method, outline class, outline implementation, outline code
- empty function, empty method, empty class, empty implementation, empty code
- blank function, blank method, blank class, blank implementation, blank code
- void function, void method, void class, void implementation, void code
- null function, null method, null class, null implementation, null code
- no-op function, no-op method, no-op class, no-op implementation, no-op code
- no operation function, no operation method, no operation class, no operation implementation, no operation code
- pass-only function, pass-only method, pass-only class, pass-only implementation, pass-only code
- unimplemented function, unimplemented method, unimplemented class, unimplemented implementation, unimplemented code
- stub function, stub method, stub class, stub implementation, stub code
- incomplete function, incomplete method, incomplete class, incomplete implementation, incomplete code
- partial function, partial method, partial class, partial implementation, partial code
- unfinished function, unfinished method, unfinished class, unfinished implementation, unfinished code
- not implemented function, not implemented method, not implemented class, not implemented implementation, not implemented code
- function signature only, method signature only, class signature only, interface signature only, protocol signature only
- function declaration only, method declaration only, class declaration only, interface declaration only, protocol declaration only
- function definition only, method definition only, class definition only, interface definition only, protocol definition only
- function prototype only, method prototype only, class prototype only, interface prototype only, protocol prototype only
- function skeleton, method skeleton, class skeleton, interface skeleton, protocol skeleton
- function template, method template, class template, interface template, protocol template
- function outline, method outline, class outline, interface outline, protocol outline
- function stub, method stub, class stub, interface stub, protocol stub
- abstract function without body, abstract method without body, abstract class without body, abstract interface without body, abstract protocol without body
- virtual function without body, virtual method without body, virtual class without body, virtual interface without body, virtual protocol without body
- pure virtual function, pure virtual method, pure virtual class, pure virtual interface, pure virtual protocol
- function with pass only, method with pass only, class with pass only, interface with pass only, protocol with pass only
- function with return only, method with return only, class with return only, interface with return only, protocol with return only
- function with throw only, method with throw only, class with throw only, interface with throw only, protocol with throw only
- function with NotImplementedException only, method with NotImplementedException only, class with NotImplementedException only
- function with NotImplementedError only, method with NotImplementedError only, class with NotImplementedError only
- function with raise NotImplementedError only, method with raise NotImplementedError only, class with raise NotImplementedError only
- **AND ALL OTHER SYNONYMS AND VARIATIONS**

**Forbidden Tags (ALL Categories):**
- Markup/Structural Tags: HTML tags, XML tags, Markdown tags, YAML tags, JSON tags, tags in markup languages, elements, attributes, properties, decorators, annotations, directives, metadata tags, schema tags, namespace tags
- Version/Control Tags: Git tags, version tags, release tags, build tags, branch tags, commit tags, repository tags, revision tags (when used to mark incomplete work)
- Code/Documentation Tags: JSDoc tags, DocString tags, comment tags, inline tags, block tags, annotation tags, attribute tags, decorator tags, metadata annotations, type hints, type annotations (when used to mark incomplete work)
- Status/Indicator Tags: Status tags, progress tags, completion tags, work tags, issue tags, task tags, milestone tags, checkpoint tags, waypoint tags, anchor tags, reference tags, bookmark tags, flag tags, label tags, badge tags, stamp tags, seal tags, mark tags, signpost tags
- System/Metadata Tags: File tags, folder tags, system tags, metadata tags, index tags, catalog tags, library tags, collection tags, category tags, classification tags, taxonomy tags, ontology tags (when used to mark incomplete work)
- API/Service Tags: API tags, endpoint tags, route tags, service tags, microservice tags, container tags, deployment tags, environment tags, configuration tags, feature flags, toggle tags, switch tags (when used to mark incomplete work)
- Tracking/Monitoring Tags: Tracking tags, analytics tags, monitoring tags, logging tags, event tags, metric tags, performance tags, diagnostic tags, debug tags, trace tags (when used to mark incomplete work)
- Social/Collaboration Tags: Hashtags, mention tags, notification tags, alert tags, reminder tags, assignment tags, ownership tags, responsibility tags (when used to mark incomplete work)
- Content/Organizational Tags: Content tags, topic tags, subject tags, keyword tags, search tags, filter tags, sort tags, group tags, category tags, tag clouds, tag lists, tag sets (when used to mark incomplete work)
- **AND ALL OTHER TAG CATEGORIES AND VARIATIONS**

**Forbidden Status Words (ALL Synonyms):**
- pending, incomplete, unfinished, partial, in progress, to do, will be, coming soon, not yet, eventually, later, soon, planned, scheduled, assigned, open, active, ongoing, under construction, under development, in development, work in progress, WIP, draft, rough, prototype, experimental, alpha, beta, preview, pre-release, needs, requires, missing, absent, empty, blank, null, void, tbd, tba, tbc
- not implemented, not done, not complete, not finished, not ready, not working, not functional, not operational
- to be implemented, to be done, to be completed, to be finished, to be ready, to be working, to be functional, to be operational
- will be implemented, will be done, will be completed, will be finished, will be ready, will be working, will be functional, will be operational
- should be implemented, should be done, should be completed, should be finished, should be ready, should be working, should be functional, should be operational
- must be implemented, must be done, must be completed, must be finished, must be ready, must be working, must be functional, must be operational
- needs implementation, needs work, needs completion, needs finishing, needs to be done, needs to be implemented, needs to be completed, needs to be finished
- requires implementation, requires work, requires completion, requires finishing, requires to be done, requires to be implemented, requires to be completed, requires to be finished
- missing implementation, missing work, missing completion, missing finishing, missing functionality
- absent implementation, absent work, absent completion, absent finishing, absent functionality
- incomplete implementation, incomplete work, incomplete completion, incomplete finishing, incomplete functionality
- unfinished implementation, unfinished work, unfinished completion, unfinished finishing, unfinished functionality
- partial implementation, partial work, partial completion, partial finishing, partial functionality
- draft implementation, draft work, draft completion, draft finishing, draft functionality
- rough implementation, rough work, rough completion, rough finishing, rough functionality
- prototype implementation, prototype work, prototype completion, prototype finishing, prototype functionality
- experimental implementation, experimental work, experimental completion, experimental finishing, experimental functionality
- alpha implementation, alpha work, alpha completion, alpha finishing, alpha functionality
- beta implementation, beta work, beta completion, beta finishing, beta functionality
- preview implementation, preview work, preview completion, preview finishing, preview functionality
- pre-release implementation, pre-release work, pre-release completion, pre-release finishing, pre-release functionality
- work in progress, work in development, work in construction, work pending, work incomplete, work unfinished, work partial
- in progress, in development, in construction, in work, in process, in development phase, in construction phase, in work phase, in process phase
- under construction, under development, under work, under process, under review, under consideration, under planning
- coming soon, coming later, coming eventually, coming in future, coming next, coming up
- not yet, not now, not ready, not complete, not finished, not done, not implemented, not working, not functional, not operational
- eventually, later, soon, someday, sometime, in future, in the future, at some point, at some time
- for now, for the moment, for the time being, temporarily, temporary, temp
- planned, scheduled, assigned, queued, backlogged, on hold, on deck, on the list, on the agenda, on the roadmap
- open, active, ongoing, current, in queue, in backlog, in pipeline, in roadmap
- empty, blank, null, void, none, nothing, zero, nil, na, n/a, naught
- tbd (to be determined), tba (to be announced), tbc (to be confirmed), tbr (to be reviewed), tbs (to be specified), tbt (to be tested), tbu (to be updated)
- wip (work in progress), wipd (work in progress - draft), wipt (work in progress - testing), wipr (work in progress - review)
- placeholder status, stub status, dummy status, mock status, fake status, sample status, test status, temporary status
- incomplete status, unfinished status, partial status, draft status, rough status, prototype status, experimental status
- alpha status, beta status, preview status, pre-release status, rc (release candidate) status
- **AND ALL OTHER SYNONYMS AND VARIATIONS**

**Forbidden Phrases (ALL Variations):**
- "to be done", "to be implemented", "to be completed", "to be finished", "to be ready", "to be working", "to be functional", "to be operational"
- "will be done", "will be implemented", "will be completed", "will be finished", "will be ready", "will be working", "will be functional", "will be operational"
- "should be done", "should be implemented", "should be completed", "should be finished", "should be ready", "should be working", "should be functional", "should be operational"
- "must be done", "must be implemented", "must be completed", "must be finished", "must be ready", "must be working", "must be functional", "must be operational"
- "coming soon", "coming later", "coming eventually", "coming in future", "coming next", "coming up"
- "not yet", "not now", "not ready", "not complete", "not finished", "not done", "not implemented", "not working", "not functional", "not operational"
- "eventually", "later", "soon", "someday", "sometime", "in future", "in the future", "at some point", "at some time"
- "for now", "for the moment", "for the time being", "temporarily", "temporary", "temp"
- "needs", "needs to be done", "needs to be implemented", "needs to be completed", "needs to be finished", "needs work", "needs implementation", "needs completion", "needs finishing"
- "requires", "requires to be done", "requires to be implemented", "requires to be completed", "requires to be finished", "requires work", "requires implementation", "requires completion", "requires finishing"
- "missing", "missing implementation", "missing work", "missing completion", "missing finishing", "missing functionality"
- "absent", "absent implementation", "absent work", "absent completion", "absent finishing", "absent functionality"
- "empty", "blank", "null", "void", "none", "nothing", "zero", "nil", "na", "n/a", "naught"
- "tbd" (to be determined), "tba" (to be announced), "tbc" (to be confirmed), "tbr" (to be reviewed), "tbs" (to be specified), "tbt" (to be tested), "tbu" (to be updated)
- "in progress", "in development", "in construction", "in work", "in process", "in development phase", "in construction phase", "in work phase", "in process phase"
- "under development", "under construction", "under work", "under process", "under review", "under consideration", "under planning"
- "work in progress", "work in development", "work in construction", "work pending", "work incomplete", "work unfinished", "work partial"
- "WIP", "wip", "wipd" (work in progress - draft), "wipt" (work in progress - testing), "wipr" (work in progress - review)
- "placeholder", "stub", "dummy", "mock", "fake", "sample", "test", "temporary"
- "incomplete", "unfinished", "partial", "draft", "rough", "prototype", "experimental"
- "alpha", "beta", "preview", "pre-release", "rc" (release candidate)
- "fix this later", "needs work", "come back here", "return here", "revisit this", "follow up on this", "check this later", "review this later"
- "assume this works", "assume this is implemented", "assume this is done", "assume this is complete", "assume this is finished"
- "this will work", "this should work", "this might work", "this may work", "this could work"
- "implement later", "do later", "complete later", "finish later", "work on later", "fix later", "add later", "update later"
- "not implemented yet", "not done yet", "not complete yet", "not finished yet", "not ready yet", "not working yet", "not functional yet", "not operational yet"
- "to be added", "to be fixed", "to be updated", "to be changed", "to be modified", "to be improved", "to be enhanced", "to be optimized", "to be refactored"
- "will be added", "will be fixed", "will be updated", "will be changed", "will be modified", "will be improved", "will be enhanced", "will be optimized", "will be refactored"
- "should be added", "should be fixed", "should be updated", "should be changed", "should be modified", "should be improved", "should be enhanced", "should be optimized", "should be refactored"
- "must be added", "must be fixed", "must be updated", "must be changed", "must be modified", "must be improved", "must be enhanced", "must be optimized", "must be refactored"
- "needs to be added", "needs to be fixed", "needs to be updated", "needs to be changed", "needs to be modified", "needs to be improved", "needs to be enhanced", "needs to be optimized", "needs to be refactored"
- "requires to be added", "requires to be fixed", "requires to be updated", "requires to be changed", "requires to be modified", "requires to be improved", "requires to be enhanced", "requires to be optimized", "requires to be refactored"
- **AND ALL OTHER PHRASE VARIATIONS**

**Loophole Prevention (ALL Variations FORBIDDEN):**
- Capitalization variations: todo, Todo, TODO, ToDo, To-Do, to-do, TO-DO (ALL variations)
- Spacing variations: TO DO, TO-DO, TO_DO, TODO, TO DO, T O D O (ALL variations)
- Punctuation variations: TODO:, TODO., TODO,, TODO;, TODO!, TODO?, TODO-, TODO_, TODO/, TODO\, TODO| (ALL variations)
- Abbreviation variations: TBD, TBA, TBC, TBR, TBS, TBT, TBU, WIP, WIPD, WIPT, WIPR (ALL variations)
- Language variations: Translations of forbidden terms in other languages (ALL variations)
- Encoding variations: Unicode variations, HTML entities, URL encoding, Base64 (ALL variations)
- Comment style variations: // TODO, /* TODO */, # TODO, <!-- TODO -->, ; TODO, ' TODO (ALL variations)
- String concatenation variations: "TO" + "DO", "TODO".substring(0, 4), "T" + "O" + "D" + "O" (ALL variations)
- Variable/Function name variations: todo, TODO, todoItem, todoList, todoTask, fixme, FIXME, wip, WIP, placeholder, stub, dummy, mock (ALL variations)
- Emoji/Unicode variations: 📝 TODO, 🔧 FIXME, ⚠️ WARNING, 🚧 WIP, ⏳ PENDING, 📌 NOTE, 🔖 BOOKMARK (ALL variations)
- Whitespace variations:  TODO , TODO ,  TODO  , \tTODO\t, \nTODO\n, \rTODO\r (ALL variations)
- Regex/Pattern variations: .*TODO.*, .*FIXME.*, .*WIP.*, T*D*O, F*I*X*M*E, W*I*P (ALL variations)
- Context variations: In strings, documentation, error messages, log messages, UI text, file paths, URLs (ALL variations)
- Negation variations: NOT TODO, NO TODO, NOT A TODO (ALL variations)
- Meta-references: "TODO" (as a string), The word TODO, TODO-like, TODO-ish (ALL variations)
- Indirect references: Similar to TODO, TODO equivalent, TODO alternative, TODO substitute (ALL variations)
- Time-based variations: TODO for now, TODO temporarily, TODO until later (ALL variations)
- Scope variations: TODO in this function, TODO here, TODO in code (ALL variations)
- Priority variations: High priority TODO, TODO (high), TODO - high (ALL variations)
- Status variations: TODO (pending), TODO - pending, TODO status: pending (ALL variations)
- **AND ALL OTHER WORKAROUNDS AND LOOPHOLES**

**ALL code must be production-ready and functional. ALL functionality must be implemented and tested.**

### Rule 2: UI Design Must Match ChatGPT Specification Exactly
- **MUST** maintain 3-row grid structure
- **MUST** have 4 PanelHosts (Left, Center, Right, Bottom)
- **MUST** have 64px Nav Rail with 8 toggle buttons
- **MUST** have 48px Command Toolbar
- **MUST** have 26px Status Bar
- **MUST** use VSQ.* design tokens (no hardcoded values)
- **MUST** maintain MVVM separation (separate .xaml, .xaml.cs, ViewModel.cs files)
- **MUST** use PanelHost UserControl (never replace with raw Grid)
- **MUST NOT** simplify layout, merge files, or reduce panel count

### Rule 3: Integration Must Enhance Only
- **ONLY** integrate what enhances the current project
- **EXTRACT CONCEPTS** from different frameworks and convert to WinUI 3/C#
- **MAINTAIN** exact ChatGPT UI specification
- **ENHANCE** functionality without changing UI structure

---

## 📝 REFRESH CHECKLIST

Before starting any work, verify:

- [ ] I have read `docs/governance/MASTER_RULES_COMPLETE.md` - **COMPLETE AND THOROUGH READ**
- [ ] I understand ALL forbidden bookmarks (TODO, FIXME, NOTE, HACK, REMINDER, XXX, WARNING, CAUTION, BUG, ISSUE, REFACTOR, OPTIMIZE, REVIEW, CHECK, VERIFY, TEST, DEBUG, DEPRECATED, OBSOLETE, and ALL synonyms)
- [ ] I understand ALL forbidden placeholders (dummy, mock, fake, sample, temporary, test data, filler, placeholder, stub data, example data, demonstration data, pseudocode, skeleton data, empty data, null data, blank data, default data, and ALL synonyms)
- [ ] I understand ALL forbidden stubs (skeleton, template, outline, empty function, pass statement, unimplemented, stub, empty method, blank function, void function, null implementation, no-op, no operation, and ALL synonyms)
- [ ] I understand ALL forbidden tags (ALL categories: markup, version/control, code/documentation, status/indicator, system/metadata, API/service, tracking/monitoring, social/collaboration, content/organizational)
- [ ] I understand ALL forbidden status words (pending, incomplete, unfinished, partial, in progress, to do, will be, coming soon, not yet, eventually, later, soon, planned, scheduled, assigned, open, active, ongoing, under construction, under development, in development, work in progress, WIP, draft, rough, prototype, experimental, alpha, beta, preview, pre-release, needs, requires, missing, absent, empty, blank, null, void, tbd, tba, tbc, and ALL synonyms)
- [ ] I understand ALL forbidden phrases ("to be done", "will be implemented", "coming soon", "not yet", "eventually", "later", "for now", "temporary", "in progress", "under development", "work in progress", and ALL variations)
- [ ] I understand ALL loophole prevention patterns (capitalization, spacing, punctuation, abbreviation, language, encoding, comment style, string concatenation, variable/function names, emoji/unicode, whitespace, regex/pattern, context, negation, meta-references, indirect references, time-based, scope, priority, status variations)
- [ ] I understand the exact UI layout requirements (3-row grid, 4 PanelHosts, Nav rail, Command toolbar, Status bar)
- [ ] I know what is forbidden (ALL stubs, placeholders, bookmarks, tags, status words, phrases, and ALL synonyms and variations)
- [ ] I know what is required (100% complete, functional code, production-ready)
- [ ] I will maintain the exact ChatGPT UI specification
- [ ] I will only integrate what enhances the project
- [ ] I will avoid ALL forbidden patterns (including ALL synonyms, variations, and loophole attempts)
- [ ] I will verify completion before marking tasks done (search for ALL forbidden terms and variations)

---

## 🔧 IMPLEMENTATION

### For AI Instances

**At Session Start:**
1. Read `docs/governance/MASTER_RULES_COMPLETE.md` - **COMPLETE AND THOROUGH READ**
   - Read Section 1: The Absolute Rule (ALL forbidden terms, synonyms, variations, loophole prevention)
   - Read Section 2: UI Design Rules (if UI work)
   - Read Section 3: Integration Rules (if integration work)
   - Read Section 4: Code Quality Rules (for all code work)
   - Read Section 5: Architecture Rules (for architecture work)
   - Read Section 6: Worker Rules (for workers)
   - Read Section 7: Overseer Rules (for overseer)
   - Read Section 8: Enforcement Rules
   - Read Section 9: Periodic Refresh System (this section)
2. Verify understanding of ALL forbidden terms (including ALL synonyms and variations)
3. Verify understanding of ALL loophole prevention patterns
4. Apply to current work

**Before Task Start:**
1. Review relevant sections of `docs/governance/MASTER_RULES_COMPLETE.md`
2. Check task-specific requirements
3. Verify compliance with ALL rules (including ALL forbidden terms and variations)

**During Work:**
1. Periodic refresh every 30 minutes (long sessions)
   - Quick review of Section 1: The Absolute Rule (forbidden terms and patterns)
   - Quick review of Section 2: UI Design Rules (if UI work)
2. Before code changes, verify compliance
   - Search for ALL forbidden terms (including ALL synonyms and variations)
   - Check for ALL loophole attempts
3. Before task completion, final verification
   - Complete verification checklist from Section 1
   - Search for ALL forbidden patterns

**At Task Completion:**
1. Final verification against ALL rules in `docs/governance/MASTER_RULES_COMPLETE.md`
   - Complete verification checklist (Section 1)
   - Search for ALL forbidden terms, synonyms, variations, and loophole attempts
2. Confirm 100% completion (no placeholders, stubs, bookmarks, tags in ANY form)
3. Confirm UI compliance (if UI task) - exact ChatGPT specification
4. Confirm all rules followed (including ALL forbidden terms and variations)

### For Overseer

**Responsibilities:**
1. Enforce refresh schedule
2. Verify workers have refreshed
3. Check for rule violations
4. Reject incomplete work
5. Ensure UI specification compliance

---

## 📊 MONITORING

### Refresh Tracking
- Document when refreshes occur
- Track rule violations
- Monitor compliance rates
- Identify patterns of violations

### Violation Response
1. **Immediate:** Revert violating changes
2. **Reminder:** Refresh critical rules
3. **Verification:** Confirm understanding
4. **Prevention:** Strengthen refresh schedule if needed

---

## ✅ SUCCESS CRITERIA

**System is working when:**
- All AI instances refresh rules at session start
- No rule violations occur
- UI specification is maintained exactly
- All code is 100% complete (no placeholders)
- Workers remember and follow all rules

**If violations occur:**
- Increase refresh frequency
- Add more explicit reminders
- Strengthen enforcement
- Review and update refresh documents

---

## 🎯 REMEMBER

**The UI design layout and plans MUST stay exactly as given from ChatGPT.**

**EVERY task must be 100% complete before moving to the next task.**

**NO exceptions. NO shortcuts. NO placeholders. NO bookmarks. NO tags. NO stubs.**

**Refresh yourself on these rules regularly. Don't forget. Don't deviate.**

---

## 🚨 CRITICAL: PREVENTING BYPASS ATTEMPTS

**ALL instances MUST use `MASTER_RULES_COMPLETE.md` which contains:**
- ✅ **ALL forbidden bookmarks** (including ALL synonyms: marker, flag, indicator, annotation, reference point, anchor, checkpoint, waypoint, signpost, milestone marker, pointer, reference, sticky note, bookmark, reminder marker, fix marker, work marker, return marker, later marker, revisit marker, follow-up marker, and ALL other synonyms)
- ✅ **ALL forbidden placeholders** (including ALL synonyms: dummy, mock, fake, sample, temporary, test data, filler, placeholder, stub data, example data, demonstration data, pseudocode, skeleton data, empty data, null data, blank data, default data, and ALL other synonyms)
- ✅ **ALL forbidden stubs** (including ALL synonyms: skeleton, template, outline, empty function, pass statement, unimplemented, stub, empty method, blank function, void function, null implementation, no-op, no operation, and ALL other synonyms)
- ✅ **ALL forbidden tags** (including ALL categories: markup, version/control, code/documentation, status/indicator, system/metadata, API/service, tracking/monitoring, social/collaboration, content/organizational)
- ✅ **ALL forbidden status words** (including ALL synonyms: pending, incomplete, unfinished, partial, in progress, to do, will be, coming soon, not yet, eventually, later, soon, planned, scheduled, assigned, open, active, ongoing, under construction, under development, in development, work in progress, WIP, draft, rough, prototype, experimental, alpha, beta, preview, pre-release, needs, requires, missing, absent, empty, blank, null, void, tbd, tba, tbc, and ALL other synonyms)
- ✅ **ALL forbidden phrases** (including ALL variations: "to be done", "will be implemented", "coming soon", "not yet", "eventually", "later", "for now", "temporary", "in progress", "under development", "work in progress", and ALL other variations)
- ✅ **ALL loophole prevention patterns** (capitalization, spacing, punctuation, abbreviation, language, encoding, comment style, string concatenation, variable/function names, emoji/unicode, whitespace, regex/pattern, context, negation, meta-references, indirect references, time-based, scope, priority, status variations)

**This prevents instances from using similar-meaning words to bypass the rule.**

**If an instance uses ANY synonym or variation of a forbidden term, it is a VIOLATION.**

**NO EXCEPTIONS. NO WORKAROUNDS. NO LOOPHOLES.**

---

**Last Updated:** 2025-01-28  
**Status:** ACTIVE  
**Primary Reference:** `docs/governance/MASTER_RULES_COMPLETE.md`  
**Next Review:** 2025-02-01

