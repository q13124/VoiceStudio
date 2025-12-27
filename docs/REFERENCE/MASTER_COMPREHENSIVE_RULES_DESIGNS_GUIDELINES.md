# VoiceStudio Quantum+ - MASTER COMPREHENSIVE RULES, DESIGNS & GUIDELINES

## Complete Compilation of Every Rule, Guideline, and Design Specification

**Date:** 2025-12-26  
**Status:** COMPREHENSIVE COMPILATION - Complete Reference Document  
**Purpose:** Single source of truth for ALL project rules, guidelines, and design specifications  
**Source:** All files in E:\VoiceStudio project, including governance, design, and documentation folders  
**Compiled By:** AI Assistant Overseer

---

## 📋 TABLE OF CONTENTS

### **PART 1: ABSOLUTE RULES & REQUIREMENTS**

1. [The Absolute Rule - 100% Complete](#1-the-absolute-rule---100-complete)
2. [Dependency Installation Rule](#2-dependency-installation-rule)
3. [UI Design Rules - ChatGPT Specification](#3-ui-design-rules---chatgpt-specification)
4. [Integration Rules](#4-integration-rules)
5. [Code Quality Rules](#5-code-quality-rules)
6. [No Mock Outputs Rule](#6-no-mock-outputs-rule)
7. [Architecture Rules](#7-architecture-rules)
8. [Worker Rules & Responsibilities](#8-worker-rules--responsibilities)
9. [Overseer Rules & Responsibilities](#9-overseer-rules--responsibilities)
10. [Enforcement Rules](#10-enforcement-rules)
11. [Periodic Refresh System](#11-periodic-refresh-system)

### **PART 2: DESIGN SPECIFICATIONS**

11. [UI Layout Structure](#11-ui-layout-structure)
12. [Design Tokens System](#12-design-tokens-system)
13. [PanelHost System](#13-panelhost-system)
14. [6 Core Panels Specification](#14-6-core-panels-specification)
15. [File Structure](#15-file-structure)
16. [Panel Registry System](#16-panel-registry-system)

### **PART 3: TECHNICAL ARCHITECTURE**

17. [Technology Stack](#17-technology-stack)
18. [Local-First Architecture](#18-local-first-architecture)
19. [Engine System Architecture](#19-engine-system-architecture)
20. [Backend Architecture](#20-backend-architecture)
21. [Performance & Stability Safeguards](#21-performance--stability-safeguards)

### **PART 4: DEVELOPMENT WORKFLOW**

22. [Task Management Rules](#22-task-management-rules)
23. [File Locking Protocol](#23-file-locking-protocol)
24. [Quality Assurance Process](#24-quality-assurance-process)
25. [Definition of Done](#25-definition-of-done)
26. [Worker Coordination](#26-worker-coordination)

### **PART 5: SPECIALIZED SYSTEMS**

27. [Brainstormer Protocol](#27-brainstormer-protocol)
28. [Engine Library Download Rules](#28-engine-library-download-rules)
29. [UI/UX Integrity Rules](#29-uiux-integrity-rules)
30. [Markdown Standards](#30-markdown-standards)
31. [Prompt System](#31-prompt-system)

---

## PART 1: ABSOLUTE RULES & REQUIREMENTS

## 1. THE ABSOLUTE RULE - 100% COMPLETE

### 🚨 HIGHEST PRIORITY RULE - MANDATORY - NO EXCEPTIONS

**EVERY task must be 100% complete before moving to the next task.**

**NO exceptions. NO shortcuts. NO placeholders. NO bookmarks. NO tags. NO stubs.**

**This rule applies to ALL code, ALL documentation, ALL files, ALL the time.**

### FORBIDDEN TERMS AND PATTERNS

#### Bookmarks (FORBIDDEN - ALL SYNONYMS):

- `TODO`, `FIXME`, `NOTE`, `HACK`, `REMINDER`, `XXX`, `WARNING`, `CAUTION`, `BUG`, `ISSUE`, `REFACTOR`, `OPTIMIZE`, `REVIEW`, `CHECK`, `VERIFY`, `TEST`, `DEBUG`, `DEPRECATED`, `OBSOLETE`
- `marker`, `flag`, `indicator`, `annotation`, `reference point`, `anchor`, `checkpoint`, `waypoint`, `signpost`, `milestone marker`, `pointer`, `reference`, `sticky note`
- `bookmark`, `bookmark marker`, `bookmark indicator`, `bookmark annotation`, `bookmark reference`, `bookmark pointer`
- `reminder marker`, `reminder flag`, `reminder indicator`, `reminder annotation`, `reminder note`
- `fix marker`, `fix flag`, `fix indicator`, `fix annotation`, `fix note`, `fix reminder`
- `work marker`, `work flag`, `work indicator`, `work annotation`, `work note`, `work reminder`
- `return marker`, `return flag`, `return indicator`, `return annotation`, `return note`, `return point`
- `later marker`, `later flag`, `later indicator`, `later annotation`, `later note`
- `revisit marker`, `revisit flag`, `revisit indicator`, `revisit annotation`, `revisit note`
- `follow-up marker`, `follow-up flag`, `follow-up indicator`, `follow-up annotation`, `follow-up note`
- `revisit point`, `follow-up point`, `return point`, `check point`, `review point`
- `bookmark`, `bookmark marker`, `bookmark indicator`, `bookmark annotation`, `bookmark reference`, `bookmark pointer`
- `reminder marker`, `reminder flag`, `reminder indicator`, `reminder annotation`, `reminder note`
- `fix marker`, `fix flag`, `fix indicator`, `fix annotation`, `fix note`, `fix reminder`
- `work marker`, `work flag`, `work indicator`, `work annotation`, `work note`, `work reminder`
- `return marker`, `return flag`, `return indicator`, `return annotation`, `return note`, `return point`
- `later marker`, `later flag`, `later indicator`, `later annotation`, `later note`
- `revisit marker`, `revisit flag`, `revisit indicator`, `revisit annotation`, `revisit note`
- `follow-up marker`, `follow-up flag`, `follow-up indicator`, `follow-up annotation`, `follow-up note`
- `revisit point`, `follow-up point`, `return point`, `check point`, `review point`

#### Placeholders (FORBIDDEN - ALL SYNONYMS):

- `NotImplementedError`, `NotImplementedException`, `[PLACEHOLDER]`, `{"mock": true}`, `return {}`, `return []`, `return null`
- `dummy`, `mock`, `fake`, `sample`, `temporary`, `test data`, `filler`, `placeholder`, `stub data`, `example data`, `demonstration data`, `pseudocode`, `skeleton data`, `empty data`, `null data`, `blank data`, `default data`, `example`, `sample`, `template`, `prototype`, `draft`, `rough`, `incomplete data`, `partial data`, `unfinished data`, `filler data`
- `dummy value`, `mock value`, `fake value`, `sample value`, `test value`, `placeholder value`, `stub value`, `example value`, `temporary value`
- `dummy code`, `mock code`, `fake code`, `sample code`, `test code`, `placeholder code`, `stub code`, `example code`, `temporary code`
- `dummy implementation`, `mock implementation`, `fake implementation`, `sample implementation`, `test implementation`, `placeholder implementation`, `stub implementation`, `example implementation`, `temporary implementation`
- `dummy function`, `mock function`, `fake function`, `sample function`, `test function`, `placeholder function`, `stub function`, `example function`, `temporary function`
- `dummy method`, `mock method`, `fake method`, `sample method`, `test method`, `placeholder method`, `stub method`, `example method`, `temporary method`
- `dummy class`, `mock class`, `fake class`, `sample class`, `test class`, `placeholder class`, `stub class`, `example class`, `temporary class`
- `dummy object`, `mock object`, `fake object`, `sample object`, `test object`, `placeholder object`, `stub object`, `example object`, `temporary object`
- `dummy response`, `mock response`, `fake response`, `sample response`, `test response`, `placeholder response`, `stub response`, `example response`, `temporary response`
- `dummy return`, `mock return`, `fake return`, `sample return`, `test return`, `placeholder return`, `stub return`, `example return`, `temporary return`
- `dummy output`, `mock output`, `fake output`, `sample output`, `test output`, `placeholder output`, `stub output`, `example output`, `temporary output`
- `dummy result`, `mock result`, `fake result`, `sample result`, `test result`, `placeholder result`, `stub result`, `example result`, `temporary result`
- `filler code`, `filler data`, `filler value`, `filler implementation`, `filler function`, `filler method`, `filler class`, `filler object`, `filler response`, `filler return`, `filler output`, `filler result`
- `test placeholder`, `test stub`, `test dummy`, `test mock`, `test fake`, `test sample`
- `non-functional code`, `non-functional data`, `non-functional value`, `non-functional implementation`, `non-functional function`, `non-functional method`, `non-functional class`, `non-functional object`
- `non-working code`, `non-working data`, `non-working value`, `non-working implementation`, `non-working function`, `non-working method`, `non-working class`, `non-working object`
- `non-operational code`, `non-operational data`, `non-operational value`, `non-operational implementation`, `non-operational function`, `non-operational method`, `non-operational class`, `non-operational object`
- `non-implemented code`, `non-implemented data`, `non-implemented value`, `non-implemented implementation`, `non-implemented function`, `non-implemented method`, `non-implemented class`, `non-implemented object`
- `incomplete code`, `incomplete data`, `incomplete value`, `incomplete implementation`, `incomplete function`, `incomplete method`, `incomplete class`, `incomplete object`
- `partial code`, `partial data`, `partial value`, `partial implementation`, `partial function`, `partial method`, `partial class`, `partial object`
- `unfinished code`, `unfinished data`, `unfinished value`, `unfinished implementation`, `unfinished function`, `unfinished method`, `unfinished class`, `unfinished object`
- `dummy value`, `mock value`, `fake value`, `sample value`, `test value`, `placeholder value`, `stub value`, `example value`, `temporary value`
- `dummy code`, `mock code`, `fake code`, `sample code`, `test code`, `placeholder code`, `stub code`, `example code`, `temporary code`
- `dummy implementation`, `mock implementation`, `fake implementation`, `sample implementation`, `test implementation`, `placeholder implementation`, `stub implementation`, `example implementation`, `temporary implementation`

#### Stubs (FORBIDDEN - ALL SYNONYMS):

- `skeleton`, `template`, `outline`, `empty function`, `pass statement`, `unimplemented`, `stub`, `empty method`, `blank function`, `void function`, `null implementation`, `no-op`, `no operation`
- `dummy function`, `mock function`, `fake function`, `placeholder function`, `incomplete function`, `partial implementation`
- `abstract method without implementation`, `interface without implementation`, `protocol without implementation`
- `skeleton function`, `skeleton method`, `skeleton class`, `skeleton implementation`, `skeleton code`
- `template function`, `template method`, `template class`, `template implementation`, `template code`
- `outline function`, `outline method`, `outline class`, `outline implementation`, `outline code`
- `empty function`, `empty method`, `empty class`, `empty implementation`, `empty code`
- `blank function`, `blank method`, `blank class`, `blank implementation`, `blank code`
- `void function`, `void method`, `void class`, `void implementation`, `void code`
- `null function`, `null method`, `null class`, `null implementation`, `null code`
- `no-op function`, `no-op method`, `no-op class`, `no-op implementation`, `no-op code`
- `no operation function`, `no operation method`, `no operation class`, `no operation implementation`, `no operation code`
- `pass-only function`, `pass-only method`, `pass-only class`, `pass-only implementation`, `pass-only code`
- `unimplemented function`, `unimplemented method`, `unimplemented class`, `unimplemented implementation`, `unimplemented code`
- `stub function`, `stub method`, `stub class`, `stub implementation`, `stub code`
- `incomplete function`, `incomplete method`, `incomplete class`, `incomplete implementation`, `incomplete code`
- `partial function`, `partial method`, `partial class`, `partial implementation`, `partial code`
- `unfinished function`, `unfinished method`, `unfinished class`, `unfinished implementation`, `unfinished code`
- `not implemented function`, `not implemented method`, `not implemented class`, `not implemented implementation`, `not implemented code`
- `function signature only`, `method signature only`, `class signature only`, `interface signature only`, `protocol signature only`
- `function declaration only`, `method declaration only`, `class declaration only`, `interface declaration only`, `protocol declaration only`
- `function definition only`, `method definition only`, `class definition only`, `interface definition only`, `protocol definition only`
- `function prototype only`, `method prototype only`, `class prototype only`, `interface prototype only`, `protocol prototype only`
- `function skeleton`, `method skeleton`, `class skeleton`, `interface skeleton`, `protocol skeleton`
- `function template`, `method template`, `class template`, `interface template`, `protocol template`
- `function outline`, `method outline`, `class outline`, `interface outline`, `protocol outline`
- `function stub`, `method stub`, `class stub`, `interface stub`, `protocol stub`

#### Tags (FORBIDDEN - ALL CATEGORIES):

- HTML/XML tags, Markdown tags, YAML tags, JSON tags, tags in markup languages, elements, attributes, properties, decorators, annotations, directives, metadata tags, schema tags, namespace tags
- Git tags, version tags, release tags, build tags, branch tags, commit tags, repository tags, revision tags (when used to mark incomplete work)
- JSDoc tags, DocString tags, comment tags, inline tags, block tags, annotation tags, attribute tags, decorator tags, metadata annotations, type hints, type annotations (when used to mark incomplete work)
- Status tags, progress tags, completion tags, work tags, issue tags, task tags, milestone tags, checkpoint tags, waypoint tags, anchor tags, reference tags, bookmark tags, flag tags, label tags, badge tags, stamp tags, seal tags, mark tags, signpost tags
- API tags, endpoint tags, route tags, service tags, microservice tags, container tags, deployment tags, environment tags, configuration tags, feature flags, toggle tags, switch tags (when used to mark incomplete work)

#### Status Words/Phrases (FORBIDDEN - ALL VARIATIONS):

- `pending`, `incomplete`, `unfinished`, `partial`, `in progress`, `to do`, `will be`, `coming soon`, `not yet`, `eventually`, `later`, `soon`, `planned`, `scheduled`, `assigned`, `open`, `active`, `ongoing`, `under construction`, `under development`, `in development`, `work in progress`, `WIP`, `draft`, `rough`, `prototype`, `experimental`, `alpha`, `beta`, `preview`, `pre-release`, `needs`, `requires`, `missing`, `absent`, `empty`, `blank`, `null`, `void`, `tbd`, `tba`, `tbc`
- `not implemented`, `not done`, `not complete`, `not finished`, `not ready`, `not working`, `not functional`, `not operational`
- `to be implemented`, `to be done`, `to be completed`, `to be finished`, `to be ready`, `to be working`, `to be functional`, `to be operational`
- `will be implemented`, `will be done`, `will be completed`, `will be finished`, `will be ready`, `will be working`, `will be functional`, `will be operational`
- `should be implemented`, `should be done`, `should be completed`, `should be finished`, `should be ready`, `should be working`, `should be functional`, `should be operational`
- `must be implemented`, `must be done`, `must be completed`, `must be finished`, `must be ready`, `should be working`, `should be functional`, `should be operational`
- `needs implementation`, `needs work`, `needs completion`, `needs finishing`, `needs to be done`, `needs to be implemented`, `needs to be completed`, `needs to be finished`
- `requires implementation`, `requires work`, `requires completion`, `requires finishing`, `requires to be done`, `requires to be implemented`, `requires to be completed`, `requires to be finished`
- `missing implementation`, `missing work`, `missing completion`, `missing finishing`, `missing functionality`
- `absent implementation`, `absent work`, `absent completion`, `absent finishing`, `absent functionality`
- `incomplete implementation`, `incomplete work`, `incomplete completion`, `incomplete finishing`, `incomplete functionality`
- `unfinished implementation`, `unfinished work`, `unfinished completion`, `unfinished finishing`, `unfinished functionality`
- `partial implementation`, `partial work`, `partial completion`, `partial finishing`, `partial functionality`
- `draft implementation`, `draft work`, `draft completion`, `draft finishing`, `draft functionality`
- `rough implementation`, `rough work`, `rough completion`, `rough finishing`, `rough functionality`
- `prototype implementation`, `prototype work`, `prototype completion`, `prototype finishing`, `prototype functionality`
- `experimental implementation`, `experimental work`, `experimental completion`, `experimental finishing`, `experimental functionality`
- `alpha implementation`, `alpha work`, `alpha completion`, `alpha finishing`, `alpha functionality`
- `beta implementation`, `beta work`, `beta completion`, `beta finishing`, `beta functionality`
- `preview implementation`, `preview work`, `preview completion`, `preview finishing`, `preview functionality`
- `pre-release implementation`, `pre-release work`, `pre-release completion`, `pre-release finishing`, `pre-release functionality`
- `work in progress`, `work in development`, `work in construction`, `work pending`, `work incomplete`, `work unfinished`, `work partial`
- `in progress`, `in development`, `in construction`, `in work`, `in process`, `in development phase`, `in construction phase`, `in work phase`, `in process phase`
- `under construction`, `under development`, `under work`, `under process`, `under review`, `under consideration`, `under planning`
- `coming soon`, `coming later`, `coming eventually`, `coming in future`, `coming next`, `coming up`
- `not yet`, `not now`, `not ready`, `not complete`, `not finished`, `not done`, `not implemented`, `not working`, `not functional`, `not operational`
- `eventually`, `later`, `soon`, `someday`, `sometime`, `in future`, `in the future`, `at some point`, `at some time`
- `for now`, `for the moment`, `for the time being`, `temporarily`, `temporary`, `temp`
- `planned`, `scheduled`, `assigned`, `queued`, `backlogged`, `on hold`, `on deck`, `on the list`, `on the agenda`, `on the roadmap`
- `open`, `active`, `ongoing`, `current`, `in queue`, `in backlog`, `in pipeline`, `in roadmap`
- `empty`, `blank`, `null`, `void`, `none`, `nothing`, `zero`, `nil`, `na`, `n/a`, `naught`
- `tbd (to be determined)`, `tba (to be announced)`, `tbc (to be confirmed)`, `tbr (to be reviewed)`, `tbs (to be specified)`, `tbt (to be tested)`, `tbu (to be updated)`
- `wip (work in progress)`, `wipd (work in progress - draft)`, `wipt (work in progress - testing)`, `wipr (work in progress - review)`
- `placeholder status`, `stub status`, `dummy status`, `mock status`, `fake status`, `sample status`, `test status`, `temporary status`
- `incomplete status`, `unfinished status`, `partial status`, `draft status`, `rough status`, `prototype status`, `experimental status`
- `alpha status`, `beta status`, `preview status`, `pre-release status`, `rc (release candidate) status`

### LOOPHOLE PREVENTION - NO WORKAROUNDS ALLOWED

**Capitalization Variations (FORBIDDEN):**

- `todo`, `Todo`, `TODO`, `ToDo`, `To-Do`, `to-do`, `TO-DO`
- `fixme`, `Fixme`, `FIXME`, `FixMe`, `Fix-Me`, `fix-me`, `FIX-ME`
- `wip`, `Wip`, `WIP`, `WiP`, `W-I-P`, `w-i-p`, `W-I-P`
- `tbd`, `Tbd`, `TBD`, `TbD`, `T-B-D`, `t-b-d`, `T-B-D`
- ALL forbidden terms in ANY capitalization variation

**Spacing Variations (FORBIDDEN):**

- `TO DO`, `TO-DO`, `TO_DO`, `TODO`, `TO DO`, `T O D O`
- `FIX ME`, `FIX-ME`, `FIX_ME`, `FIXME`, `FIX ME`, `F I X M E`
- `IN PROGRESS`, `IN-PROGRESS`, `IN_PROGRESS`, `INPROGRESS`, `IN PROGRESS`, `I N P R O G R E S S`
- ALL forbidden terms with ANY spacing variation (spaces, dashes, underscores, no spaces)

**Punctuation Variations (FORBIDDEN):**

- `TODO:`, `TODO.`, `TODO,`, `TODO;`, `TODO!`, `TODO?`, `TODO-`, `TODO_`, `TODO/`, `TODO\`, `TODO|`
- `[TODO]`, `(TODO)`, `{TODO}`, `<TODO>`, `"TODO"`, `'TODO'`, `` `TODO` ``, `*TODO*`, `_TODO_`, `~TODO~`
- `#TODO`, `@TODO`, `$TODO`, `%TODO`, `&TODO`, `*TODO`, `+TODO`, `=TODO`
- ALL forbidden terms with ANY punctuation variation

**Abbreviation Variations (FORBIDDEN):**

- `TBD`, `TBA`, `TBC`, `TBR`, `TBS`, `TBT`, `TBU` (all variations)
- `WIP`, `WIPD`, `WIPT`, `WIPR` (all variations)
- `N/A`, `NA`, `N/A`, `n/a`, `na` (when meaning "not applicable" or "not available" for incomplete work)
- `NIL`, `nil`, `NULL`, `null`, `NONE`, `none`, `VOID`, `void`, `ZERO`, `zero`, `NOTHING`, `nothing` (when meaning incomplete)

**Language Variations (FORBIDDEN):**

- Translations of forbidden terms in other languages
- Foreign language equivalents of "TODO", "FIXME", "placeholder", "stub", "incomplete", "not yet", etc.
- Code comments in other languages that mean the same thing

**Encoding Variations (FORBIDDEN):**

- Unicode variations: `ＴＯＤＯ` (full-width), `TODO` (normal), `TODO` (with invisible characters)
- HTML entities: `&lt;TODO&gt;`, `&#84;&#79;&#68;&#79;`
- URL encoding: `TODO`, `%54%4F%44%4F`
- Base64 or other encodings of forbidden terms

**Comment Style Variations (FORBIDDEN):**

- `// TODO`, `/* TODO */`, `# TODO`, `<!-- TODO -->`, `; TODO`, `' TODO`, `` ` TODO ` ``, `REM TODO`
- `//TODO`, `/*TODO*/`, `#TODO`, `<!--TODO-->`, `;TODO`, `'TODO`, `` `TODO` ``, `REMTODO`
- `// TODO:`, `/* TODO: */`, `# TODO:`, `<!-- TODO: -->`, `; TODO:`, `' TODO:`
- ALL comment styles in ALL programming languages

**String Concatenation Variations (FORBIDDEN):**

- `"TO" + "DO"`, `"TODO".substring(0, 4)`, `"T" + "O" + "D" + "O"`
- `"FIX" + "ME"`, `"FIXME".substring(0, 5)`, `"F" + "I" + "X" + "M" + "E"`
- Any string concatenation that results in forbidden terms

**Variable/Function Name Variations (FORBIDDEN):**

- Variable names: `todo`, `TODO`, `todoItem`, `todoList`, `todoTask`, `fixme`, `FIXME`, `wip`, `WIP`, `placeholder`, `stub`, `dummy`, `mock`
- Function names: `todo()`, `TODO()`, `fixme()`, `FIXME()`, `wip()`, `WIP()`, `placeholder()`, `stub()`, `dummy()`, `mock()`
- Class names: `Todo`, `TODO`, `Fixme`, `FIXME`, `Wip`, `WIP`, `Placeholder`, `Stub`, `Dummy`, `Mock`
- File names: `todo.md`, `TODO.md`, `fixme.md`, `FIXME.md`, `wip.md`, `WIP.md`, `placeholder.md`, `stub.md`, `dummy.md`, `mock.md`

**Emoji/Unicode Variations (FORBIDDEN):**

- `📝 TODO`, `🔧 FIXME`, `⚠️ WARNING`, `🚧 WIP`, `⏳ PENDING`, `📌 NOTE`, `🔖 BOOKMARK`
- `TODO 📝`, `FIXME 🔧`, `WARNING ⚠️`, `WIP 🚧`, `PENDING ⏳`, `NOTE 📌`, `BOOKMARK 🔖`
- Any emoji combined with forbidden terms

**Whitespace Variations (FORBIDDEN):**

- `TODO`, `TODO `, ` TODO`, `TODO`, `\tTODO\t`, `\nTODO\n`, `\rTODO\r`
- `TODO:`, `TODO: `, ` TODO:`, `TODO:`, `\tTODO:\t`, `\nTODO:\n`, `\rTODO:\r`
- All forbidden terms with ANY whitespace variation

**Regex/Pattern Variations (FORBIDDEN):**

- Using regex patterns that match forbidden terms: `.*TODO.*`, `.*FIXME.*`, `.*WIP.*`
- Using wildcards: `T*D*O`, `F*I*X*M*E`, `W*I*P`
- Using character classes: `[Tt][Oo][Dd][Oo]`, `[Ff][Ii][Xx][Mm][Ee]`, `[Ww][Ii][Pp]`

**Context Variations (FORBIDDEN):**

- Using forbidden terms in strings: `"This is a TODO item"`, `"FIXME: needs work"`, `"WIP: in progress"`
- Using forbidden terms in documentation: `See TODO section`, `Check FIXME list`, `Review WIP items`
- Using forbidden terms in error messages: `TODO: Error occurred`, `FIXME: Fix this error`, `WIP: Error handling`
- Using forbidden terms in log messages: `TODO: Logging this`, `FIXME: Log this later`, `WIP: Logging in progress`
- Using forbidden terms in UI text: `TODO Button`, `FIXME Label`, `WIP Status`
- Using forbidden terms in file paths: `/todo/`, `/fixme/`, `/wip/`, `/placeholder/`, `/stub/`
- Using forbidden terms in URLs: `?todo=1`, `&fixme=1`, `#wip`, `#placeholder`, `#stub`

**Negation Variations (FORBIDDEN):**

- `NOT TODO`, `NOT FIXME`, `NOT WIP`, `NOT PLACEHOLDER`, `NOT STUB`
- `NO TODO`, `NO FIXME`, `NO WIP`, `NO PLACEHOLDER`, `NO STUB`
- `NOT A TODO`, `NOT A FIXME`, `NOT A WIP`, `NOT A PLACEHOLDER`, `NOT A STUB`
- Using negation to claim something is not a forbidden term when it actually is

**Meta-References (FORBIDDEN):**

- `"TODO" (as a string)`, `'TODO' (as a string)`, `` `TODO` (as a string) ``
- `The word TODO`, `The term FIXME`, `The phrase WIP`
- `TODO-like`, `FIXME-like`, `WIP-like`, `TODO-style`, `FIXME-style`, `WIP-style`
- `TODO-ish`, `FIXME-ish`, `WIP-ish`, `TODO-esque`, `FIXME-esque`, `WIP-esque`

**Indirect References (FORBIDDEN):**

- `Similar to TODO`, `Like FIXME`, `Same as WIP`
- `TODO equivalent`, `FIXME equivalent`, `WIP equivalent`
- `TODO alternative`, `FIXME alternative`, `WIP alternative`
- `TODO substitute`, `FIXME substitute`, `WIP substitute`

**Time-Based Variations (FORBIDDEN):**

- `TODO for now`, `FIXME for now`, `WIP for now`, `PLACEHOLDER for now`, `STUB for now`
- `TODO temporarily`, `FIXME temporarily`, `WIP temporarily`, `PLACEHOLDER temporarily`, `STUB temporarily`
- `TODO until later`, `FIXME until later`, `WIP until later`, `PLACEHOLDER until later`, `STUB until later`

**Scope Variations (FORBIDDEN):**

- `TODO in this function`, `FIXME in this method`, `WIP in this class`
- `TODO here`, `FIXME here`, `WIP here`, `PLACEHOLDER here`, `STUB here`
- `TODO in code`, `FIXME in code`, `WIP in code`, `PLACEHOLDER in code`, `STUB in code`

**Priority Variations (FORBIDDEN):**

- `High priority TODO`, `Low priority FIXME`, `Medium priority WIP`
- `TODO (high)`, `FIXME (low)`, `WIP (medium)`
- `TODO - high`, `FIXME - low`, `WIP - medium`

**Status Variations (FORBIDDEN):**

- `TODO (pending)`, `FIXME (incomplete)`, `WIP (unfinished)`
- `TODO - pending`, `FIXME - incomplete`, `WIP - unfinished`
- `TODO status: pending`, `FIXME status: incomplete`, `WIP status: unfinished`

**REMEMBER:** If it means the same thing as a forbidden term, it's FORBIDDEN regardless of how it's written, formatted, encoded, or referenced.

**NO EXCEPTIONS. NO WORKAROUNDS. NO LOOPHOLES.**

### WHAT IS REQUIRED

**Code Requirements:**

- ✅ Full implementation of all methods
- ✅ All functionality working and tested
- ✅ All error cases handled
- ✅ All edge cases considered
- ✅ Tests written and passing (if applicable)
- ✅ Real values, real file I/O, real API wiring
- ✅ Complete function bodies, classes, or components
- ✅ UI and backend wired together with real bindings or API calls
- ✅ Verifiable and testable functionality
- ✅ Production-ready code
- ✅ No speculative implementations
- ✅ No "assume this works" comments
- ✅ No hardcoded filler data

**Documentation Requirements:**

- ✅ Complete content, not outlines
- ✅ All examples work and are tested
- ✅ All procedures tested
- ✅ All links verified
- ✅ No empty sections
- ✅ No "TODO: Add content here"
- ✅ No placeholder text

**UI Requirements:**

- ✅ All controls functional
- ✅ All interactions work
- ✅ All states implemented
- ✅ All animations complete
- ✅ No "Placeholder" text in UI
- ✅ No disabled buttons that never work
- ✅ No "Coming soon" messages
- ✅ No empty states that say "TODO"

**Exception for Testing:**

- ✅ If mocking is required for testing, wrap it in a clear `if TEST_MODE:` conditional
- ✅ Log mock usage clearly
- ✅ Never use mocks in production code paths
- ✅ Test mocks must be clearly marked and isolated

### VERIFICATION CHECKLIST

**Before Marking ANY Task Complete:**

1. **Search your code for ALL forbidden patterns:**

   - Bookmarks (TODO, FIXME, NOTE, HACK, REMINDER, XXX, WARNING, CAUTION, BUG, ISSUE, REFACTOR, OPTIMIZE, REVIEW, CHECK, VERIFY, TEST, DEBUG, DEPRECATED, OBSOLETE - all variations)
   - Placeholders (NotImplementedError, NotImplementedException, [PLACEHOLDER], {"mock": true}, dummy, mock, fake, sample, temporary - all variations)
   - Stubs (pass-only functions, empty methods, function signatures without implementation - all variations)
   - Tags (#TODO, #FIXME, [PLACEHOLDER], [WIP], [IN PROGRESS] - all variations)
   - Status Words ("pending", "incomplete", "unfinished", "coming soon", "not yet", "eventually", "later", "for now", "temporary", "needs", "requires", "missing", "WIP", "tbd", "tba", "tbc" - all variations)
   - Loophole Prevention Patterns (capitalization, spacing, punctuation, comment style, string concatenation, variable/function names, emoji, whitespace, regex, context, negation, meta-references, indirect references, time-based, scope, priority, status variations)

2. **Functional Testing:**
   - Does the code actually work?
   - Are all cases handled?
   - Are there any errors?
   - Is it production-ready?
   - Can it be tested?
   - Does it perform the actual intended function?

**If you find ANY of these patterns:**

- 🚨 **STOP IMMEDIATELY**
- 🚨 **COMPLETE THE IMPLEMENTATION**
- 🚨 **TEST IT**
- 🚨 **THEN** mark as complete

### CONSEQUENCES OF VIOLATION

**If Stubs/Placeholders/Bookmarks/Tags Found:**

1. **Task marked as INCOMPLETE**
2. **Worker must complete before moving on**
3. **No credit for partial work**
4. **May delay overall timeline**
5. **Commit rejected** (if using automated checks)
6. **Release blocked** (if found in release candidate)

**Why This Matters:**

- **Quality:** Stubs create technical debt
- **Reliability:** Placeholders can cause bugs
- **User Experience:** Incomplete features frustrate users
- **Maintainability:** Future workers waste time on stubs
- **Professionalism:** Production code must be complete
- **Trust:** Incomplete code erodes trust in the system
- **Efficiency:** Finding and fixing stubs later is more expensive than doing it right the first time

## 2. DEPENDENCY INSTALLATION RULE

**ALL dependencies MUST be installed for EVERY task. NO EXCEPTIONS.**

**This rule applies to:**

- ✅ Python packages (pip install)
- ✅ .NET packages (NuGet)
- ✅ System dependencies (FFmpeg, etc.)
- ✅ Engine-specific dependencies
- ✅ Development dependencies
- ✅ Testing dependencies
- ✅ **EVERY dependency required for the task**

**Requirements:**

- ✅ **BEFORE starting any task:** Check what dependencies are needed
- ✅ **BEFORE implementing code:** Install all required dependencies
- ✅ **BEFORE marking task complete:** Verify all dependencies are installed and working
- ✅ **NO EXCEPTIONS:** Even if a dependency seems optional, if it's needed for the task, install it
- ✅ **NO SKIPPING:** Do not skip dependency installation to save time
- ✅ **NO ASSUMPTIONS:** Do not assume dependencies are already installed - verify and install if needed

**Installation Process:**

1. Identify dependencies (check requirements files, documentation, code imports)
2. Check current installation (verify if dependencies are already installed)
3. Install missing dependencies (use appropriate package manager: pip, NuGet, etc.)
4. Verify installation (test that dependencies work correctly)
5. Document installation (update requirements files if new dependencies added)

**Forbidden:**

- ❌ Skipping dependency installation
- ❌ Assuming dependencies are installed
- ❌ Marking task complete without installing dependencies
- ❌ Leaving dependency installation for "later"
- ❌ Using "optional" as excuse to skip installation
- ❌ Creating code that requires dependencies without installing them

**Verification:**

- ✅ All imports work without errors
- ✅ All functionality that requires dependencies works
- ✅ No "module not found" errors
- ✅ No "package not installed" errors
- ✅ Requirements files updated with new dependencies

**Examples:**

- ✅ **CORRECT:** Task requires `librosa` → Install `librosa` → Verify import works → Implement code
- ✅ **CORRECT:** Task requires `fairseq` for RVC → Install `fairseq` → Test RVC engine → Complete task
- ❌ **WRONG:** Task requires `pesq` → Skip installation → Write code that imports `pesq` → Mark complete
- ❌ **WRONG:** Task requires `pedalboard` → Assume it's installed → Code fails → Mark complete anyway

**This rule is MANDATORY and has NO EXCEPTIONS.**

## 3. UI DESIGN RULES - CHATGPT SPECIFICATION

**THE UI DESIGN LAYOUT AND PLANS MUST STAY EXACTLY AS GIVEN FROM CHATGPT.**

### EXACT REQUIREMENTS (NON-NEGOTIABLE):

- 3-row grid structure (Top Command Deck, Main Workspace, Status Bar)
- 4 PanelHosts (Left, Center, Right, Bottom)
- 64px Nav Rail with 8 toggle buttons
- 48px Command Toolbar
- 26px Status Bar
- VSQ.\* design tokens (no hardcoded values)
- MVVM separation (separate .xaml, .xaml.cs, ViewModel.cs files)
- PanelHost UserControl (never replace with raw Grid)

### FORBIDDEN:

- ❌ Changing 3-row grid structure
- ❌ Removing PanelHost controls
- ❌ Merging View/ViewModel files
- ❌ Hardcoded colors, fonts, or spacing
- ❌ Simplifying layout
- ❌ Reducing panel count

## 4. INTEGRATION RULES

**Principles:**

- ✅ **ONLY** integrate what enhances the current project
- ✅ **EXTRACT CONCEPTS** from different frameworks and convert to WinUI 3/C#
- ✅ **MAINTAIN** exact ChatGPT UI specification (layout structure)
- ✅ **ENHANCE** functionality without changing UI structure
- ✅ **ADAPT** features, patterns, and logic from any framework to WinUI 3/C#
- ✅ **CONVERT** concepts and ideas from any language/framework to our current stack
- ✅ **LEARN FROM** all implementations regardless of framework - extract what's useful
- ✅ **NEVER EXCLUDE** based on framework - always consider conversion/adaptation
- ✅ **PRINCIPLE:** Different UI framework ≠ Exclusion. Extract concepts and implement in our stack.

**Convertible/Adaptable Items:**

- React/TypeScript frontend (`C:\OldVoiceStudio\frontend\`) - **CONVERTIBLE** (extract concepts, implement in WinUI 3/C#)
- Python GUI implementations (`C:\OldVoiceStudio\gui\`) - **CONVERTIBLE** (extract panel concepts, implement in WinUI 3/C#)

**Conversion Approach:**

- Extract concepts, features, patterns, and logic
- Implement in WinUI 3/C# following ChatGPT UI specification
- Maintain exact layout structure (3-row grid, 4 PanelHosts, Nav rail, etc.)
- Use MVVM pattern, DesignTokens.xaml, and PanelHost UserControl

## 5. CODE QUALITY RULES

### CORRECTNESS OVER SPEED RULE - HIGHEST PRIORITY

**THE FUNDAMENTAL PRINCIPLE:**
**Do not prioritize speed or task count. Your only priority is to produce the correct solution, even if it takes longer or results in fewer changes. Never rush or cut corners.**

**This rule applies to:**

- ✅ All code implementations
- ✅ All task completions
- ✅ All bug fixes
- ✅ All feature additions
- ✅ All refactoring
- ✅ All testing
- ✅ All documentation
- ✅ **EVERYTHING**

**Requirements:**

- ✅ **Take the time needed** to implement correctly
- ✅ **Do it right the first time** - no shortcuts
- ✅ **Quality over quantity** - fewer correct tasks is better than many incomplete tasks
- ✅ **Thoroughness over speed** - complete understanding before implementation
- ✅ **Verification before completion** - verify correctness before marking done
- ✅ **No rushing** - if it takes longer, it takes longer
- ✅ **No cutting corners** - implement fully, test thoroughly, verify completely

**Forbidden:**

- ❌ Rushing to complete more tasks
- ❌ Cutting corners to save time
- ❌ Skipping verification to move faster
- ❌ Incomplete implementations to increase task count
- ❌ "Good enough" solutions
- ❌ Quick fixes that don't address root causes
- ❌ Assuming something works without testing
- ❌ Marking tasks complete without verification

**Examples:**

- ✅ **CORRECT:** Take 2 days to implement correctly → Verify it works → Mark complete
- ✅ **CORRECT:** Implement 1 task perfectly → Test thoroughly → Document → Move to next
- ❌ **WRONG:** Rush through 5 tasks → Leave placeholders → Mark all complete
- ❌ **WRONG:** Quick implementation → Skip testing → Mark complete to move faster

**Remember:**

- **One correct implementation is worth more than ten incomplete ones**
- **Time spent doing it right is never wasted**

## 6. NO MOCK OUTPUTS RULE

**All Cursor agents must write complete, real code with working logic — no mock data, placeholders, stubs, or speculative interfaces unless explicitly instructed.**

### Must Avoid (🚫 Do NOT generate):

**Bookmarks:**

- ❌ `TODO` comments
- ❌ `pass`-only stubs
- ❌ `return {"mock": true}` or fake responses
- ❌ Empty class/function shells with no logic
- ❌ Unimplemented data flows ("assume this works")
- ❌ Mock protocols or fake API responses
- ❌ Hardcoded filler data
- ❌ Speculative implementations

### Required Output Format (✅ Agents must):

- ✅ Implement full function bodies, classes, or components
- ✅ Wire UI and backend code together with real bindings or API calls
- ✅ Return real values, real file I/O, real API wiring — not mock protocols
- ✅ If mocking is required for testing, wrap it in a clear `if TEST_MODE:` conditional and log its usage
- ✅ Use real engine routers, MCPs, or models
- ✅ Perform actual operations (e.g., saving audio, applying effects)

### Completion Criteria:

**Functionality must be:**

- ✅ Verifiable and testable
- ✅ UI panels display actual values or connect to real models, MCPs, or engine routers
- ✅ Backend code performs its intended effect or operation
- ✅ No component marked complete if its implementation is speculative or empty

### Examples - BAD ❌:

```python
def generate_audio(voice_id):
    # TODO: implement
    return {"mock_audio": true}
```

```csharp
public async Task<AudioResult> SynthesizeAsync(string text)
{
    // TODO: Implement synthesis
    return new AudioResult { Mock = true };
}
```

### Examples - GOOD ✅:

```python
def generate_audio(voice_id: str) -> dict:
    """Generate audio using real engine."""
    engine = router.get_engine("xtts_v2")
    result = engine.synthesize(
        text=text,
        voice_id=voice_id,
        language="en"
    )
    return {
        "audio_path": result.audio_path,
        "duration": result.duration,
        "quality_metrics": result.quality_metrics
    }
```

```csharp
public async Task<AudioResult> SynthesizeAsync(string text)
{
    var engine = _engineRouter.GetEngine("xtts_v2");
    var result = await engine.SynthesizeAsync(text, _currentVoiceProfile);

    return new AudioResult
    {
        AudioPath = result.AudioPath,
        Duration = result.Duration,
        QualityMetrics = result.QualityMetrics
    };
}
```

- **Quality cannot be rushed**
- **Correctness is the only metric that matters**

**This rule is MANDATORY and has NO EXCEPTIONS.**

### PRODUCTION-READY CODE

**All code must be:**

- ✅ Fully implemented (no stubs, placeholders, bookmarks, tags)
- ✅ Tested and working
- ✅ Error handling included
- ✅ Edge cases considered
- ✅ Production-ready quality
- ✅ Real implementations (no mocks in production)
- ✅ Verifiable and testable

### REAL IMPLEMENTATIONS ONLY

**Forbidden:**

- ❌ Mock outputs in return values
- ❌ `{"mock": true}` or similar fake responses
- ❌ `pass`-only stubs (Python)
- ❌ Hardcoded filler data
- ❌ Speculative implementations
- ❌ "Assume this works" comments

**Required:**

- ✅ Real API calls to backend services
- ✅ Real file I/O operations
- ✅ Real engine/router connections
- ✅ UI connected to real data sources
- ✅ All operations perform actual work

**Exception for Testing:**

- ✅ If mocking is required for testing, wrap it in a clear `if TEST_MODE:` conditional
- ✅ Log mock usage clearly
- ✅ Never use mocks in production code paths
- ✅ Test mocks must be clearly marked and isolated

## 6. ARCHITECTURE RULES

### WINDOWS NATIVE APPLICATION

**✅ YES - This is a Windows Native Program:**

- **Framework:** WinUI 3 (Windows App SDK)
- **Language:** C# (.NET 8)
- **UI Markup:** XAML
- **Platform:** Windows Desktop Application
- **Target:** Windows 10 17763+ / Windows 11
- **Architecture:** Native Windows application, NOT web-based

**❌ NOT:**

- ❌ NOT a web app (no Electron, no browser)
- ❌ NOT a cross-platform framework (WinUI 3 is Windows-only)
- ❌ NOT a hybrid app (fully native Windows)

### LOCAL-FIRST ARCHITECTURE

**Principle:** 100% Local-First - APIs only used for what cannot be done locally

**All engines run locally:**

- ✅ XTTS Engine (Coqui TTS) - Runs locally with PyTorch
- ✅ Chatterbox TTS Engine - Runs locally with PyTorch
- ✅ Tortoise TTS Engine - Runs locally for HQ mode
- ✅ All engines integrated, tested, and working locally

**All quality analysis runs locally:**

- ✅ MOS Score calculation (local)
- ✅ Voice similarity metrics (local)
- ✅ Naturalness analysis (local)
- ✅ SNR calculation (local)
- ✅ Artifact detection (local)

**Backend API runs locally:**

- ✅ All endpoints run locally
- ✅ No external API calls
- ✅ No API keys required
- ✅ No cloud services
- ✅ Communication: `localhost:8000` (internal)

### WORKSPACE SETUP

**Active Repository (Authoritative):**

- **`E:\VoiceStudio`** - **ONLY** place where code is written
- This is the **active, authoritative project directory**
- All modifications, creations, and updates happen here
- This is the **primary working directory**

**Reference Repository (Read-Only):**

- **`C:\VoiceStudio`** - **Read-only reference** (if present)
- **`C:\OldVoiceStudio`** - **Read-only reference** (if present)
- These directories are **archive/reference only**

**Rules:**

- All new code goes to E:\VoiceStudio
- All edits happen in E:\VoiceStudio
- May read from reference directories
- May NOT modify reference directories
- May NOT bulk copy from reference directories

## 7. WORKER RULES & RESPONSIBILITIES

### WORKER RESPONSIBILITIES

**Worker 1 (Backend/Engines):**

- Backend API development
- Engine integration
- Quality metrics implementation
- Performance optimization
- Audio processing

**Worker 2 (UI/UX):**

- WinUI 3/C# frontend development
- Panel implementation
- Design token usage
- MVVM pattern adherence
- UI/UX polish

**Worker 3 (Testing/Quality):**

- Testing implementation
- Quality verification
- Documentation
- Packaging and deployment

### WORKER REQUIREMENTS

**All Workers MUST:**

- ✅ Read `docs/governance/MASTER_RULES_COMPLETE.md` before starting
- ✅ Read `docs/design/ORIGINAL_UI_SCRIPT_CHATGPT.md` (if UI work)
- ✅ Follow the NO stubs/placeholders/bookmarks/tags rule
- ✅ **Install ALL dependencies for EVERY task (NO EXCEPTIONS)**
- ✅ Complete tasks 100% before moving on
- ✅ Verify completion before marking tasks done
- ✅ Use periodic refresh system (see Section 10)

**Dependency Installation (MANDATORY):**

- ✅ **BEFORE starting any task:** Identify and install all required dependencies
- ✅ **BEFORE implementing code:** Verify all dependencies are installed
- ✅ **BEFORE marking task complete:** Verify all dependencies work correctly
- ✅ **NO EXCEPTIONS:** Install dependencies even if they seem optional
- ✅ **NO SKIPPING:** Do not skip dependency installation
- ✅ **NO ASSUMPTIONS:** Verify dependencies are installed, don't assume

## 8. OVERSEER RULES & RESPONSIBILITIES

### OVERSEER RESPONSIBILITIES

**The Overseer MUST:**

- ✅ Enforce all rules and guardrails
- ✅ Verify workers have refreshed rules
- ✅ Check for rule violations
- ✅ Reject incomplete work
- ✅ Ensure UI specification compliance
- ✅ Coordinate worker tasks
- ✅ Maintain quality standards
- ✅ Verify 100% completion before task approval

### VIOLATION DETECTION

**If violations found:**

1. **Immediate:** Revert violating changes
2. **Reminder:** Refresh critical rules
3. **Verification:** Confirm understanding
4. **Prevention:** Strengthen refresh schedule if needed

## 9. ENFORCEMENT RULES

### AUTOMATED ENFORCEMENT

**Pre-Commit Checks:**

- Run automated checks before committing
- Reject commits containing forbidden patterns
- Provide clear error messages

**Pre-Release Checks:**

- Full codebase scan before release
- Block release if violations found
- Generate violation report

**Continuous Monitoring:**

- Regular automated scans
- Alert on violations
- Track violation trends

### MANUAL ENFORCEMENT

**Overseer Review:**

- Check all code changes
- Verify rule compliance
- Reject incomplete work

**Worker Self-Verification:**

- Workers must verify their own work
- Search for forbidden patterns
- Test functionality before marking complete

**Code Reviews:**

- Peer review of all changes
- Focus on rule compliance
- Verify 100% completion

## 10. PERIODIC REFRESH SYSTEM

**PRIMARY REFERENCE:** `docs/governance/MASTER_RULES_COMPLETE.md` - **ALL INSTANCES MUST USE THIS AS PRIMARY REFERENCE**

**This document contains ALL rules, ALL forbidden terms (including ALL synonyms and variations), and ALL loophole prevention patterns. This prevents instances from using similar-meaning words to bypass the rule.**

### REFRESH SCHEDULE

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
    - Section 1: The Absolute Rule - All Forbidden Patterns (complete list)
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
    - Section 1: The Absolute Rule - All Forbidden Patterns (complete check)
- **Check:**
  - All functionality implemented (no placeholders, including ALL synonyms)
  - No forbidden terms in ANY form (including ALL variations and workarounds)
  - UI follows exact ChatGPT specification
  - All rules followed

### CRITICAL DOCUMENTS TO REFRESH

**PRIMARY REFERENCE (MUST USE):**

- **`docs/governance/MASTER_RULES_COMPLETE.md`** - **PRIMARY REFERENCE FOR ALL INSTANCES**
  - Contains ALL rules in full
  - Contains ALL forbidden terms (bookmarks, placeholders, stubs, tags, status words)
  - Contains ALL synonyms and variations
  - Contains ALL loophole prevention patterns
  - Contains UI design rules
  - Contains integration rules
  - Contains code quality rules
  - Contains architecture rules
  - Contains worker rules
  - Contains overseer rules
  - Contains enforcement rules
  - Contains periodic refresh system

**Secondary References (For Specific Details):**

- `docs/design/ORIGINAL_UI_SCRIPT_CHATGPT.md` - Original ChatGPT UI specification (source of truth)
- `docs/design/VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md` - Complete original specification with full XAML code
- `docs/governance/COMPREHENSIVE_INTEGRATION_LOG_2025-01-28.md` - Integration priorities and guidelines
- `docs/governance/RULE_ENFORCEMENT_RECOMMENDATIONS.md` - Enforcement strategies

**See:** `docs/governance/PERIODIC_RULES_REFRESH_SYSTEM.md` for complete refresh system details

---

## PART 2: DESIGN SPECIFICATIONS

## 11. UI LAYOUT STRUCTURE

### MAINWINDOW STRUCTURE (CANONICAL - NEVER CHANGE)

**Structure (3-Row Grid):**

```
MainWindow.xaml
└── Grid (3 Rows)
    ├── Row 0: Top Command Deck (Auto height)
    │   ├── MenuBar
    │   │   └── MenuItems: File, Edit, View, Modules, Playback, Tools, AI, Help
    │   └── Command Toolbar (48px height)
    │       ├── Column 0: Transport (Play, Pause, Stop, Record, Loop)
    │       ├── Column 1: Project name + Engine selector
    │       ├── Column 2: Undo/Redo + Workspace dropdown
    │       └── Column 3: Performance HUD (CPU, GPU, Latency bars)
    │
    ├── Row 1: Main Workspace (*)
    │   └── Grid (4 Columns, 2 Rows)
    │       ├── Column 0: Nav Rail (64px width)
    │       │   └── Vertical Stack: 8 toggle buttons
    │       │       ├── Studio
    │       │       ├── Profiles
    │       │       ├── Library
    │       │       ├── Effects
    │       │       ├── Train
    │       │       ├── Analyze
    │       │       ├── Settings
    │       │       └── Logs
    │       │
    │       ├── Row 0, Column 1: LeftPanelHost (20% width)
    │       │   └── Default: ProfilesView
    │       │
    │       ├── Row 0, Column 2: CenterPanelHost (55% width)
    │       │   └── Default: TimelineView
    │       │
    │       ├── Row 0, Column 3: RightPanelHost (25% width)
    │       │   └── Default: EffectsMixerView
    │       │
    │       └── Row 1, Columns 0-3: BottomPanelHost (18% height, spans all)
    │           └── Default: MacroView
    │
    └── Row 2: Status Bar (26px height, Auto)
        └── Grid (3 Columns)
            ├── Column 0 (*): Status text ("Ready")
            ├── Column 1 (2*): Job progress (Job name + progress bar)
            └── Column 2 (*): Mini meters (CPU, GPU, RAM) + Clock
```

**Critical Dimensions:**

- **Window Default:** 1600×900
- **Nav Rail:** 64px width (fixed)
- **Command Toolbar:** 48px height (fixed)
- **Status Bar:** 26px height (fixed)
- **Left Panel:** 20% width (resizable)
- **Center Panel:** 55% width (resizable)
- **Right Panel:** 25% width (resizable)
- **Bottom Panel:** 18% height (resizable)

### COMPLETE UI IMPLEMENTATION SPECIFICATION (FROM VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md)

#### Complete Project Structure

```
VoiceStudio/
├── src/
│   ├── VoiceStudio.App/              # WinUI 3 frontend (C#/XAML)
│   │   ├── VoiceStudioApp.csproj
│   │   ├── App.xaml
│   │   ├── App.xaml.cs
│   │   ├── MainWindow.xaml
│   │   ├── MainWindow.xaml.cs
│   │   ├── Resources/
│   │   │   ├── DesignTokens.xaml
│   │   │   └── Styles/
│   │   │       ├── Controls.xaml
│   │   │       ├── Text.xaml
│   │   │       └── Panels.xaml
│   │   ├── Controls/
│   │   │   ├── PanelHost.xaml
│   │   │   ├── PanelHost.xaml.cs
│   │   │   └── NavIconButton.xaml
│   │   │   └── NavIconButton.xaml.cs
│   │   ├── Views/
│   │   │   └── Panels/
│   │   │       ├── ProfilesView.xaml
│   │   │       ├── ProfilesView.xaml.cs
│   │   │       ├── TimelineView.xaml
│   │   │       ├── TimelineView.xaml.cs
│   │   │       ├── EffectsMixerView.xaml
│   │   │       ├── EffectsMixerView.xaml.cs
│   │   │       ├── AnalyzerView.xaml
│   │   │       ├── AnalyzerView.xaml.cs
│   │   │       ├── MacroView.xaml
│   │   │       ├── MacroView.xaml.cs
│   │   │       ├── DiagnosticsView.xaml
│   │   │       └── DiagnosticsView.xaml.cs
│   │   ├── ViewModels/
│   │   │   └── Panels/
│   │   │       ├── ProfilesViewModel.cs
│   │   │       ├── TimelineViewModel.cs
│   │   │       ├── EffectsMixerViewModel.cs
│   │   │       ├── AnalyzerViewModel.cs
│   │   │       ├── MacroViewModel.cs
│   │   │       └── DiagnosticsViewModel.cs
│   │   ├── Services/
│   │   │   ├── IBackendClient.cs
│   │   │   ├── BackendClient.cs
│   │   │   ├── BackendClientConfig.cs
│   │   │   └── PluginManager.cs
│   │   └── Plugins/                  # Optional: UI plugin DLLs
│   ├── VoiceStudio.Core/             # Shared C# library
│   │   ├── Panels/
│   │   │   ├── IPanelView.cs
│   │   │   ├── PanelRegion.cs
│   │   │   ├── PanelDescriptor.cs
│   │   │   ├── IPanelRegistry.cs
│   │   │   └── PanelRegistry.cs
│   │   └── Models/
│   │       ├── VoiceProfile.cs
│   │       ├── AudioClip.cs
│   │       ├── Track.cs
│   │       ├── Project.cs
│   │       └── MeterReading.cs
│   └── VoiceStudio.sln
├── backend/
│   ├── api/                          # Python FastAPI
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   ├── core/
│   │   │   ├── engines/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_engine.py
│   │   │   │   ├── xtts_engine.py
│   │   │   │   ├── chatterbox_engine.py
│   │   │   │   ├── tortoise_engine.py
│   │   │   │   └── engine_factory.py
│   │   │   ├── quality/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── mos_predictor.py
│   │   │   │   ├── snr_calculator.py
│   │   │   │   ├── artifact_detector.py
│   │   │   │   └── quality_metrics.py
│   │   │   └── config/
│   │   │       └── settings.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── synthesize.py
│   │   │   ├── quality.py
│   │   │   ├── engines.py
│   │   │   └── clone.py
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── voice_profile.py
│   │       ├── audio_clip.py
│   │       └── quality_report.py
│   └── models/                       # ML models directory
│       ├── xtts/
│       ├── chatterbox/
│       └── tortoise/
├── docs/
│   ├── design/
│   │   ├── MEMORY_BANK.md
│   │   ├── ORIGINAL_UI_SCRIPT_CHATGPT.md
│   │   └── VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md
│   ├── governance/
│   │   ├── MASTER_RULES_COMPLETE.md
│   │   ├── ALL_PROJECT_RULES.md
│   │   └── TASK_LOG.md
│   └── api/
│       └── API_REFERENCE.md
├── tools/
│   ├── verify_non_mock.py
│   └── build_verifier.py
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

#### Complete MainWindow.xaml Implementation

```xml
<Window
    x:Class="VoiceStudio.App.MainWindow"
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
    xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
    xmlns:local="using:VoiceStudio.App"
    xmlns:controls="using:VoiceStudio.App.Controls"
    mc:Ignorable="d"
    Title="VoiceStudio Quantum+"
    Width="1600"
    Height="900"
    Background="{StaticResource VSQ.Window.Background}">

    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>

        <!-- TOP COMMAND DECK -->
        <Grid Grid.Row="0">
            <Grid.RowDefinitions>
                <RowDefinition Height="Auto"/>
                <RowDefinition Height="48"/>
            </Grid.RowDefinitions>

            <!-- MenuBar -->
            <MenuBar Grid.Row="0">
                <MenuBarItem Title="File">
                    <MenuFlyoutItem Text="New Project" Click="NewProjectMenuItem_Click"/>
                    <MenuFlyoutItem Text="Open Project" Click="OpenProjectMenuItem_Click"/>
                    <MenuFlyoutItem Text="Save Project" Click="SaveProjectMenuItem_Click"/>
                    <MenuFlyoutSeparator/>
                    <MenuFlyoutItem Text="Exit" Click="ExitMenuItem_Click"/>
                </MenuBarItem>
                <MenuBarItem Title="Edit">
                    <MenuFlyoutItem Text="Undo" Click="UndoMenuItem_Click"/>
                    <MenuFlyoutItem Text="Redo" Click="RedoMenuItem_Click"/>
                    <MenuFlyoutSeparator/>
                    <MenuFlyoutItem Text="Preferences" Click="PreferencesMenuItem_Click"/>
                </MenuBarItem>
                <MenuBarItem Title="View">
                    <MenuFlyoutItem Text="Zoom In" Click="ZoomInMenuItem_Click"/>
                    <MenuFlyoutItem Text="Zoom Out" Click="ZoomOutMenuItem_Click"/>
                    <MenuFlyoutItem Text="Reset Zoom" Click="ResetZoomMenuItem_Click"/>
                </MenuBarItem>
                <MenuBarItem Title="Modules">
                    <MenuFlyoutItem Text="Engine Manager" Click="EngineManagerMenuItem_Click"/>
                    <MenuFlyoutItem Text="Plugin Manager" Click="PluginManagerMenuItem_Click"/>
                </MenuBarItem>
                <MenuBarItem Title="Playback">
                    <MenuFlyoutItem Text="Play" Click="PlayMenuItem_Click"/>
                    <MenuFlyoutItem Text="Pause" Click="PauseMenuItem_Click"/>
                    <MenuFlyoutItem Text="Stop" Click="StopMenuItem_Click"/>
                </MenuBarItem>
                <MenuBarItem Title="Tools">
                    <MenuFlyoutItem Text="Batch Processor" Click="BatchProcessorMenuItem_Click"/>
                    <MenuFlyoutItem Text="Quality Analyzer" Click="QualityAnalyzerMenuItem_Click"/>
                </MenuBarItem>
                <MenuBarItem Title="AI">
                    <MenuFlyoutItem Text="AI Assistant" Click="AIAssistantMenuItem_Click"/>
                    <MenuFlyoutItem Text="Brainstormer" Click="BrainstormerMenuItem_Click"/>
                </MenuBarItem>
                <MenuBarItem Title="Help">
                    <MenuFlyoutItem Text="Documentation" Click="DocumentationMenuItem_Click"/>
                    <MenuFlyoutItem Text="About" Click="AboutMenuItem_Click"/>
                </MenuBarItem>
            </MenuBar>

            <!-- Command Toolbar -->
            <Border Grid.Row="1" Background="{StaticResource VSQ.Background.Dark}" BorderThickness="0,1,0,0" BorderBrush="{StaticResource VSQ.Border.Subtle}">
                <Grid Margin="16,0">
                    <Grid.ColumnDefinitions>
                        <ColumnDefinition Width="Auto"/>
                        <ColumnDefinition Width="*"/>
                        <ColumnDefinition Width="Auto"/>
                        <ColumnDefinition Width="Auto"/>
                    </Grid.ColumnDefinitions>

                    <!-- Transport Controls -->
                    <StackPanel Grid.Column="0" Orientation="Horizontal" Spacing="8">
                        <Button x:Name="PlayButton" Content="▶️" ToolTipService.ToolTip="Play" Style="{StaticResource VSQ.Button}" Click="PlayButton_Click"/>
                        <Button x:Name="PauseButton" Content="⏸️" ToolTipService.ToolTip="Pause" Style="{StaticResource VSQ.Button}" Click="PauseButton_Click"/>
                        <Button x:Name="StopButton" Content="⏹️" ToolTipService.ToolTip="Stop" Style="{StaticResource VSQ.Button}" Click="StopButton_Click"/>
                        <Button x:Name="RecordButton" Content="🔴" ToolTipService.ToolTip="Record" Style="{StaticResource VSQ.Button}" Click="RecordButton_Click"/>
                        <ToggleButton x:Name="LoopButton" Content="🔁" ToolTipService.ToolTip="Loop" Style="{StaticResource VSQ.Button}" IsChecked="False"/>
                    </StackPanel>

                    <!-- Project & Engine Selector -->
                    <StackPanel Grid.Column="1" Orientation="Horizontal" HorizontalAlignment="Center" Spacing="16">
                        <TextBlock Text="{Binding ProjectName, FallbackValue='Untitled Project'}" Style="{StaticResource VSQ.Text.Title}" VerticalAlignment="Center"/>
                        <ComboBox x:Name="EngineSelector" PlaceholderText="Select Engine" ItemsSource="{Binding AvailableEngines}" SelectedItem="{Binding SelectedEngine, Mode=TwoWay}" MinWidth="150"/>
                    </StackPanel>

                    <!-- Workspace & Undo/Redo -->
                    <StackPanel Grid.Column="2" Orientation="Horizontal" Spacing="8">
                        <Button x:Name="UndoButton" Content="↶" ToolTipService.ToolTip="Undo" Style="{StaticResource VSQ.Button}" Click="UndoButton_Click" IsEnabled="{Binding CanUndo}"/>
                        <Button x:Name="RedoButton" Content="↷" ToolTipService.ToolTip="Redo" Style="{StaticResource VSQ.Button}" Click="RedoButton_Click" IsEnabled="{Binding CanRedo}"/>
                        <ComboBox x:Name="WorkspaceSelector" PlaceholderText="Workspace" ItemsSource="{Binding AvailableWorkspaces}" SelectedItem="{Binding SelectedWorkspace, Mode=TwoWay}" MinWidth="120"/>
                    </StackPanel>

                    <!-- Performance HUD -->
                    <StackPanel Grid.Column="3" Orientation="Horizontal" Spacing="16">
                        <ProgressBar x:Name="CpuMeter" Value="{Binding CpuUsage}" Width="60" Height="4" Background="{StaticResource VSQ.Background.Darker}" Foreground="{StaticResource VSQ.Accent.Cyan}"/>
                        <TextBlock Text="{Binding CpuUsage, StringFormat='CPU: {0}%'}" Style="{StaticResource VSQ.Text.Caption}"/>

                        <ProgressBar x:Name="GpuMeter" Value="{Binding GpuUsage}" Width="60" Height="4" Background="{StaticResource VSQ.Background.Darker}" Foreground="{StaticResource VSQ.Accent.Lime}"/>
                        <TextBlock Text="{Binding GpuUsage, StringFormat='GPU: {0}%'}" Style="{StaticResource VSQ.Text.Caption}"/>

                        <TextBlock Text="{Binding Latency, StringFormat='Latency: {0}ms'}" Style="{StaticResource VSQ.Text.Caption}"/>
                    </StackPanel>
                </Grid>
            </Border>
        </Grid>

        <!-- MAIN WORKSPACE -->
        <Grid Grid.Row="1">
            <Grid.RowDefinitions>
                <RowDefinition Height="*"/>
                <RowDefinition Height="0.18*"/>
            </Grid.RowDefinitions>

            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="64"/>
                <ColumnDefinition Width="0.20*"/>
                <ColumnDefinition Width="0.55*"/>
                <ColumnDefinition Width="0.25*"/>
            </Grid.ColumnDefinitions>

            <!-- Navigation Rail -->
            <Border Grid.Column="0" Grid.RowSpan="2" Background="{StaticResource VSQ.Background.Dark}" BorderThickness="0,0,1,0" BorderBrush="{StaticResource VSQ.Border.Subtle}">
                <StackPanel Spacing="4" Margin="8,16">
                    <controls:NavIconButton Icon="Studio" Label="Studio" IsChecked="{Binding IsStudioSelected, Mode=TwoWay}" GroupName="nav"/>
                    <controls:NavIconButton Icon="Profiles" Label="Profiles" IsChecked="{Binding IsProfilesSelected, Mode=TwoWay}" GroupName="nav"/>
                    <controls:NavIconButton Icon="Library" Label="Library" IsChecked="{Binding IsLibrarySelected, Mode=TwoWay}" GroupName="nav"/>
                    <controls:NavIconButton Icon="Effects" Label="Effects" IsChecked="{Binding IsEffectsSelected, Mode=TwoWay}" GroupName="nav"/>
                    <controls:NavIconButton Icon="Train" Label="Train" IsChecked="{Binding IsTrainSelected, Mode=TwoWay}" GroupName="nav"/>
                    <controls:NavIconButton Icon="Analyze" Label="Analyze" IsChecked="{Binding IsAnalyzeSelected, Mode=TwoWay}" GroupName="nav"/>
                    <controls:NavIconButton Icon="Settings" Label="Settings" IsChecked="{Binding IsSettingsSelected, Mode=TwoWay}" GroupName="nav"/>
                    <controls:NavIconButton Icon="Logs" Label="Logs" IsChecked="{Binding IsLogsSelected, Mode=TwoWay}" GroupName="nav"/>
                </StackPanel>
            </Border>

            <!-- Left Panel Host -->
            <controls:PanelHost Grid.Column="1" Grid.Row="0" PanelRegion="Left" PanelType="{Binding LeftPanelType, Mode=TwoWay}"/>

            <!-- Center Panel Host -->
            <controls:PanelHost Grid.Column="2" Grid.Row="0" PanelRegion="Center" PanelType="{Binding CenterPanelType, Mode=TwoWay}"/>

            <!-- Right Panel Host -->
            <controls:PanelHost Grid.Column="3" Grid.Row="0" PanelRegion="Right" PanelType="{Binding RightPanelType, Mode=TwoWay}"/>

            <!-- Bottom Panel Host -->
            <controls:PanelHost Grid.Column="0" Grid.ColumnSpan="4" Grid.Row="1" PanelRegion="Bottom" PanelType="{Binding BottomPanelType, Mode=TwoWay}"/>
        </Grid>

        <!-- STATUS BAR -->
        <Border Grid.Row="2" Height="26" Background="{StaticResource VSQ.Background.Dark}" BorderThickness="0,1,0,0" BorderBrush="{StaticResource VSQ.Border.Subtle}">
            <Grid Margin="16,0">
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="2*"/>
                    <ColumnDefinition Width="*"/>
                </Grid.ColumnDefinitions>

                <!-- Status Text -->
                <TextBlock Grid.Column="0" Text="{Binding StatusText, FallbackValue='Ready'}" Style="{StaticResource VSQ.Text.Body}" VerticalAlignment="Center"/>

                <!-- Job Progress -->
                <StackPanel Grid.Column="1" Orientation="Vertical" VerticalAlignment="Center">
                    <TextBlock Text="{Binding CurrentJobName, FallbackValue='No active job'}" Style="{StaticResource VSQ.Text.Caption}"/>
                    <ProgressBar Value="{Binding JobProgress}" Height="4" Background="{StaticResource VSQ.Background.Darker}" Foreground="{StaticResource VSQ.Accent.Cyan}"/>
                </StackPanel>

                <!-- Mini Meters & Clock -->
                <StackPanel Grid.Column="2" Orientation="Horizontal" HorizontalAlignment="Right" Spacing="16">
                    <ProgressBar Value="{Binding CpuUsage}" Width="40" Height="3" Background="{StaticResource VSQ.Background.Darker}" Foreground="{StaticResource VSQ.Accent.Cyan}"/>
                    <ProgressBar Value="{Binding GpuUsage}" Width="40" Height="3" Background="{StaticResource VSQ.Background.Darker}" Foreground="{StaticResource VSQ.Accent.Lime}"/>
                    <ProgressBar Value="{Binding RamUsage}" Width="40" Height="3" Background="{StaticResource VSQ.Background.Darker}" Foreground="{StaticResource VSQ.Accent.Magenta}"/>
                    <TextBlock Text="{Binding CurrentTime, StringFormat='hh:mm:ss'}" Style="{StaticResource VSQ.Text.Caption}" VerticalAlignment="Center"/>
                </StackPanel>
            </Grid>
        </Border>
    </Grid>
</Window>
```

#### Complete PanelHost Implementation

```xml
<UserControl
    x:Class="VoiceStudio.App.Controls.PanelHost"
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
    xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
    xmlns:local="using:VoiceStudio.App.Controls"
    mc:Ignorable="d">

    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="32"/>
            <RowDefinition Height="*"/>
        </Grid.RowDefinitions>

        <!-- Panel Header -->
        <Border Grid.Row="0" Background="{StaticResource VSQ.Background.Darker}" BorderThickness="0,0,0,1" BorderBrush="{StaticResource VSQ.Border.Subtle}" CornerRadius="8,8,0,0">
            <Grid Margin="12,0">
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="Auto"/>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="Auto"/>
                    <ColumnDefinition Width="Auto"/>
                    <ColumnDefinition Width="Auto"/>
                </Grid.ColumnDefinitions>

                <!-- Panel Icon -->
                <TextBlock Grid.Column="0" Text="{Binding PanelIcon}" Style="{StaticResource VSQ.Text.Body}" VerticalAlignment="Center" Margin="0,0,8,0"/>

                <!-- Panel Title -->
                <TextBlock Grid.Column="1" Text="{Binding PanelTitle}" Style="{StaticResource VSQ.Text.Title}" VerticalAlignment="Center"/>

                <!-- Pop-out Button -->
                <Button Grid.Column="2" Content="⏏️" ToolTipService.ToolTip="Pop out panel" Style="{StaticResource VSQ.Button}" Click="PopOutButton_Click" Margin="4,0"/>

                <!-- Collapse Button -->
                <Button Grid.Column="3" Content="−" ToolTipService.ToolTip="Collapse panel" Style="{StaticResource VSQ.Button}" Click="CollapseButton_Click" Margin="4,0"/>

                <!-- Options Menu -->
                <Button Grid.Column="4" Content="⋮" ToolTipService.ToolTip="Panel options" Style="{StaticResource VSQ.Button}" Margin="4,0">
                    <Button.Flyout>
                        <MenuFlyout>
                            <MenuFlyoutItem Text="Reset Layout" Click="ResetLayoutMenuItem_Click"/>
                            <MenuFlyoutItem Text="Close Panel" Click="ClosePanelMenuItem_Click"/>
                            <MenuFlyoutSeparator/>
                            <MenuFlyoutItem Text="Panel Settings" Click="PanelSettingsMenuItem_Click"/>
                        </MenuFlyout>
                    </Button.Flyout>
                </Button>
            </Grid>
        </Border>

        <!-- Panel Content -->
        <Border Grid.Row="1" Background="{StaticResource VSQ.Panel.BackgroundBrush}" BorderThickness="1,0,1,1" BorderBrush="{StaticResource VSQ.Panel.BorderBrush}" CornerRadius="0,0,8,8">
            <ContentPresenter x:Name="PanelContent" Margin="12"/>
        </Border>
    </Grid>
</UserControl>
```

#### Complete NavIconButton Implementation

```xml
<UserControl
    x:Class="VoiceStudio.App.Controls.NavIconButton"
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
    xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
    xmlns:local="using:VoiceStudio.App.Controls"
    mc:Ignorable="d">

    <ToggleButton x:Name="NavButton" Style="{StaticResource NavIconButtonStyle}" IsChecked="{Binding IsChecked, RelativeSource={RelativeSource Mode=TemplatedParent}, Mode=TwoWay}">
        <ToggleButton.Content>
            <StackPanel Orientation="Vertical" Spacing="4">
                <!-- Icon (using Segoe MDL2 Assets) -->
                <TextBlock x:Name="IconText" Text="{Binding IconGlyph, RelativeSource={RelativeSource Mode=TemplatedParent}}" Style="{StaticResource NavIconStyle}" HorizontalAlignment="Center"/>

                <!-- Label -->
                <TextBlock x:Name="LabelText" Text="{Binding Label, RelativeSource={RelativeSource Mode=TemplatedParent}}" Style="{StaticResource NavLabelStyle}" HorizontalAlignment="Center"/>
            </StackPanel>
        </ToggleButton.Content>
    </ToggleButton>
</UserControl>
```

#### NavIconButton Code-Behind

```csharp
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.App.Controls
{
    public sealed partial class NavIconButton : UserControl
    {
        public NavIconButton()
        {
            this.InitializeComponent();
        }

        public string Icon
        {
            get => (string)GetValue(IconProperty);
            set => SetValue(IconProperty, value);
        }

        public static readonly DependencyProperty IconProperty =
            DependencyProperty.Register("Icon", typeof(string), typeof(NavIconButton), new PropertyMetadata(string.Empty, OnIconChanged));

        public string Label
        {
            get => (string)GetValue(LabelProperty);
            set => SetValue(LabelProperty, value);
        }

        public static readonly DependencyProperty LabelProperty =
            DependencyProperty.Register("Label", typeof(string), typeof(NavIconButton), new PropertyMetadata(string.Empty));

        public bool IsChecked
        {
            get => (bool)GetValue(IsCheckedProperty);
            set => SetValue(IsCheckedProperty, value);
        }

        public static readonly DependencyProperty IsCheckedProperty =
            DependencyProperty.Register("IsChecked", typeof(bool), typeof(NavIconButton), new PropertyMetadata(false));

        public string GroupName
        {
            get => (string)GetValue(GroupNameProperty);
            set => SetValue(GroupNameProperty, value);
        }

        public static readonly DependencyProperty GroupNameProperty =
            DependencyProperty.Register("GroupName", typeof(string), typeof(NavIconButton), new PropertyMetadata(string.Empty));

        private static void OnIconChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            var control = (NavIconButton)d;
            var iconName = (string)e.NewValue;

            // Map icon names to Segoe MDL2 glyphs
            control.IconGlyph = iconName switch
            {
                "Studio" => "\uE77B",      // Audio icon
                "Profiles" => "\uE716",    // People icon
                "Library" => "\uE8F1",     // Library icon
                "Effects" => "\uE9D9",     // Effects icon
                "Train" => "\uF6B8",       // Learning tools icon
                "Analyze" => "\uE9D2",     // Analytics icon
                "Settings" => "\uE713",    // Settings icon
                "Logs" => "\uE8C6",        // Diagnostic icon
                _ => "\uE8C6"              // Default to diagnostic
            };
        }

        public string IconGlyph
        {
            get => (string)GetValue(IconGlyphProperty);
            private set => SetValue(IconGlyphProperty, value);
        }

        public static readonly DependencyProperty IconGlyphProperty =
            DependencyProperty.Register("IconGlyph", typeof(string), typeof(NavIconButton), new PropertyMetadata("\uE8C6"));
    }
}
```

### HIGH PRIORITY PANEL SPECIFICATIONS (FROM HIGH_PRIORITY_PANEL_SPECIFICATIONS.md)

#### 1. VOICE CLONING WIZARD PANEL

**Priority:** ⭐⭐⭐⭐⭐ (Critical)

**Layout Structure:**

```
┌─────────────────────────────────────────────────────────────┐
│  Voice Cloning Wizard                                       │
│  ────────────────────────────────────────────────────────  │
│                                                             │
│  Step 1 of 4: Upload Reference Audio                       │
│  ────────────────────────────────────────────────────────  │
│                                                             │
│  [Progress Indicator: ████████░░░░░░░░░░ 40%]              │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Main Content Area (changes per step)                │   │
│  │                                                       │   │
│  │  [Step-specific content]                             │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Preview Panel (always visible)                       │   │
│  │  - Audio waveform                                    │   │
│  │  - Quality metrics                                   │   │
│  │  - Duration, sample rate                             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  [← Back]                    [Next →]  [Cancel]            │
└─────────────────────────────────────────────────────────────┘
```

**Step 1: Upload Reference Audio**

- Drag-and-drop zone (large, prominent)
- "Browse Files" button
- Supported formats: WAV, MP3, FLAC, M4A
- Max file size: 50MB
- Minimum duration: 3 seconds
- Recommended duration: 10-60 seconds

**Audio Requirements Display:**

- ✅/❌ Quality checklist
- Audio format supported
- Duration sufficient (≥3 seconds)
- Sample rate adequate (≥16kHz)
- Clear speech (no heavy noise)
- Single speaker
- No background music

#### 2. EMOTION CONTROL PANEL

**Priority:** ⭐⭐⭐⭐⭐ (High)

**Layout Structure:**

```
┌─────────────────────────────────────────────────────────────┐
│  Emotion & Style Control                                    │
│  ────────────────────────────────────────────────────────  │
│                                                             │
│  ┌─────────────────────────────────┬─────────────────────┐ │
│  │  Emotion Controls               │  Style Controls      │ │
│  │  ─────────────────────────────  │  ──────────────────  │ │
│  │  Happy:     ████████░░ 80%      │  Formal: ████████░░  │ │
│  │  Sad:       ███░░░░░░░ 30%      │  Casual: ████░░░░░░  │ │
│  │  Angry:     █░░░░░░░░░ 10%      │  Professional: ████ │ │
│  │  Excited:   ███████░░░ 70%      │                     │ │
│  │  Calm:      ████████░░ 80%      │  [Style Presets ▼]  │ │
│  │                                 │                     │ │
│  │  [Reset Emotions]               │  [Save Style]       │ │
│  └─────────────────────────────────┴─────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Preview & Test                                       │   │
│  │  ──────────────────────────────────────────────────  │   │
│  │  [Sample Text Input]                                 │   │
│  │  [Generate Preview]  [Play]  [Stop]                  │   │
│  │                                                       │   │
│  │  [Waveform Display]                                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### 3. MULTI-VOICE GENERATOR PANEL

**Priority:** ⭐⭐⭐⭐⭐ (High)

**Layout Structure:**

```
┌─────────────────────────────────────────────────────────────┐
│  Multi-Voice Generator                                      │
│  ────────────────────────────────────────────────────────  │
│                                                             │
│  ┌─────────────────────────────────┬─────────────────────┐ │
│  │  Voice Selection                │  Batch Settings      │ │
│  │  ─────────────────────────────  │  ──────────────────  │ │
│  │  [Voice 1 ▼] [Add Voice +]      │  Output Format: MP3  │ │
│  │  [Voice 2 ▼] [Remove]           │  Sample Rate: 44100 │ │
│  │  [Voice 3 ▼]                    │  Channels: Stereo    │ │
│  │  [Voice 4 ▼]                    │  Quality: High       │ │
│  │                                 │                     │ │
│  │  [Load Voice Set]               │  [Advanced ▼]       │ │
│  └─────────────────────────────────┴─────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Text Input & Generation                            │   │
│  │  ──────────────────────────────────────────────────  │   │
│  │  [Multi-line text input with speaker labels]       │   │
│  │                                                       │   │
│  │  Voice 1: Hello everyone!                           │   │
│  │  Voice 2: Welcome to the show.                      │   │
│  │  Voice 1: I'm excited to be here.                   │   │
│  │                                                       │   │
│  │  [Generate All]  [Preview]  [Export]                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### 4. VOICE QUICK CLONE PANEL

**Priority:** ⭐⭐⭐⭐⭐ (High)

**Layout Structure:**

```
┌─────────────────────────────────────────────────────────────┐
│  Voice Quick Clone                                          │
│  ────────────────────────────────────────────────────────  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Quick Clone Process                                 │   │
│  │  ──────────────────────────────────────────────────  │   │
│  │                                                       │   │
│  │  1. [Select Base Voice ▼]                            │   │
│  │                                                       │   │
│  │  2. [Upload Reference Audio]                         │   │
│  │     Drag & drop or browse                            │   │
│  │                                                       │   │
│  │  3. [Clone Settings]                                 │   │
│  │     Similarity: ████████░░ 80%                      │   │
│  │     Speed: ███████░░░ 70%                           │   │
│  │                                                       │   │
│  │  [Start Clone]                                       │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Results & Preview                                  │   │
│  │  ──────────────────────────────────────────────────  │   │
│  │  [Cloned Voice Name]                                │   │
│  │  [Test Text Input]                                  │   │
│  │  [Generate Sample]  [Play]  [Save Voice]            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### 5. TEXT-BASED SPEECH EDITOR PANEL

**Priority:** ⭐⭐⭐⭐⭐ (High)

**Layout Structure:**

```
┌─────────────────────────────────────────────────────────────┐
│  Text-Based Speech Editor                                  │
│  ────────────────────────────────────────────────────────  │
│                                                             │
│  ┌─────────────────────────────────┬─────────────────────┐ │
│  │  Text Editor                    │  Voice Settings      │ │
│  │  ─────────────────────────────  │  ──────────────────  │ │
│  │  [Rich text editor with         │  Voice: [Dropdown]   │ │
│  │   formatting controls]          │  Speed: ███████░░░   │ │
│  │                                 │  Pitch: ████████░░   │ │
│  │  [Word-level controls]          │  Volume: █████████░  │ │
│  │  [Phoneme editor]               │                     │ │
│  │                                 │  [Voice Presets ▼]  │ │
│  └─────────────────────────────────┴─────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Timeline & Playback                                │   │
│  │  ──────────────────────────────────────────────────  │   │
│  │  [Audio waveform with text alignment]               │   │
│  │  [Playback controls]  [Export]  [Save Project]      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 12. DESIGN TOKENS SYSTEM

**File:** `src/VoiceStudio.App/Resources/DesignTokens.xaml`

**Critical Resources - MUST USE:**

#### Colors (VSQ.\*)

```
VSQ.Background.Darker: #FF0A0F15
VSQ.Background.Dark: #FF121A24
VSQ.Accent.Cyan: #FF00B7C2
VSQ.Accent.Lime: #FF9AFF33
VSQ.Accent.Magenta: #FFB040FF
VSQ.Text.Primary: #FFCDD9E5
VSQ.Text.Secondary: #FF8A9BB3
VSQ.Border.Subtle: #26FFFFFF
VSQ.Warn: #FFFFB540
VSQ.Error: #FFFF4060
```

#### Brushes (VSQ.\*Brush)

```
VSQ.Window.Background: LinearGradientBrush (Dark → Darker)
VSQ.Text.PrimaryBrush: SolidColorBrush
VSQ.Text.SecondaryBrush: SolidColorBrush
VSQ.Accent.CyanBrush: SolidColorBrush
VSQ.Panel.BackgroundBrush: SolidColorBrush
VSQ.Panel.BorderBrush: SolidColorBrush
```

#### Typography (VSQ.Font.\*)

```
VSQ.Font.Caption: 10
VSQ.Font.Body: 12
VSQ.Font.Title: 16
VSQ.Font.Heading: 20
```

#### Styles (VSQ.Text.\*)

```
VSQ.Text.Body: FontSize=12, Foreground=Primary
VSQ.Text.Caption: FontSize=10, Foreground=Secondary
VSQ.Text.Title: FontSize=16, Foreground=Primary, SemiBold
VSQ.Text.Heading: FontSize=20, Foreground=Primary, Bold
```

#### Constants (VSQ.\*)

```
VSQ.CornerRadius.Panel: 8
VSQ.CornerRadius.Button: 4
VSQ.Animation.Duration.Fast: 100ms
VSQ.Animation.Duration.Medium: 150ms
VSQ.Animation.Duration.Slow: 300ms
```

**Rule:** ALL styling must reference these tokens. NO hardcoded values.

## 13. PANELHOST SYSTEM

**Each PanelHost MUST have:**

- **Header Bar:** 32px height
  - Icon (Segoe MDL2 glyph)
  - Title text
  - Pop-out button (stub)
  - Collapse button
  - Options button (MenuFlyout)
- **Body:** ContentPresenter with Border
  - CornerRadius: 8px (VSQ.CornerRadius.Panel)
  - BorderBrush: VSQ.Panel.BorderBrush
  - BorderThickness: 1px

## 14. 6 CORE PANELS SPECIFICATION

1. **ProfilesView** - LeftPanelHost default

   - Tabs: Profiles / Library (32px header)
   - Left: Profiles grid (WrapGrid, 180×120 cards)
   - Right: Detail inspector (260px width)

2. **TimelineView** - CenterPanelHost default

   - Toolbar (32px): Add Track, Zoom, Grid settings
   - Tracks area (\*): ItemsControl with track templates
   - Visualizer (160px): Spectrogram/visualizer placeholder

3. **EffectsMixerView** - RightPanelHost default

   - Mixer (60%): Horizontal ItemsControl with mixer strips
   - FX Chain (40%): Node view / FX chain placeholder

4. **AnalyzerView** - RightPanelHost alternative

   - Tabs (32px): Waveform, Spectral, Radar, Loudness, Phase
   - Chart area (\*): Placeholder for chart rendering

5. **MacroView** - BottomPanelHost default

   - Tabs (32px): Macros / Automation
   - Node graph canvas (\*): Placeholder for node-based macro system

6. **DiagnosticsView** - BottomPanelHost alternative
   - Logs (60%): ListView with log entries
   - Metrics charts (40%): CPU, GPU, RAM progress bars

**Each panel must have:**

- `PanelNameView.xaml`
- `PanelNameView.xaml.cs`
- `PanelNameViewModel.cs` (implements `IPanelView`)

## 15. FILE STRUCTURE

### Canonical Structure:

```
VoiceStudio/
├── src/
│   ├── VoiceStudio.App/              # WinUI 3 frontend
│   │   ├── App.xaml                  # Merges DesignTokens.xaml
│   │   ├── MainWindow.xaml          # 3-row grid with 4 PanelHosts
│   │   ├── Resources/
│   │   │   └── DesignTokens.xaml    # All VSQ.* resources
│   │   ├── Controls/
│   │   │   └── PanelHost.xaml        # Reusable panel container
│   │   └── Views/Panels/
│   │       └── [6 core panels, each with .xaml, .xaml.cs, ViewModel.cs]
│   │
│   └── VoiceStudio.Core/             # Shared library
│       └── Panels/
│           └── [Panel registry types]
│
└── backend/
    └── api/                          # Python FastAPI
        └── [Backend services]
```

**Rule:** This structure is CANONICAL. Do not simplify or merge files.

## 16. PANEL REGISTRY SYSTEM

**Location:** `VoiceStudio.Core/Panels/`

**Types:**

- `PanelRegion` enum (Left, Center, Right, Bottom, Floating)
- `IPanelView` interface
- `PanelDescriptor` class
- `IPanelRegistry` interface
- `PanelRegistry` implementation

---

## PART 3: TECHNICAL ARCHITECTURE

## 17. TECHNOLOGY STACK

- **Frontend:** WinUI 3 (.NET 8, C#/XAML)
- **Backend:** Python FastAPI
- **Communication:** REST/WebSocket
- **Pattern:** MVVM (strict separation)
- **Platform:** Windows 10 17763+ / Windows 11

## 18. LOCAL-FIRST ARCHITECTURE

**CRITICAL:** VoiceStudio uses APIs ONLY for what cannot be done locally.

**What Runs Locally (100%):**

- ✅ All voice cloning engines (XTTS, Chatterbox, Tortoise)
- ✅ All quality metrics calculation
- ✅ All audio processing
- ✅ All file I/O
- ✅ All model inference
- ✅ All data storage

**What We DON'T Use:**

- ❌ External voice synthesis APIs (OpenAI, ElevenLabs, etc.)
- ❌ Cloud-based processing
- ❌ Online model inference
- ❌ External API keys
- ❌ Remote services

**Architecture:**

- Frontend: Native Windows (WinUI 3)
- Backend: Local Python FastAPI (localhost)
- Engines: Local PyTorch models
- Storage: Local filesystem
- Communication: localhost only

## 19. ENGINE SYSTEM ARCHITECTURE

**Unlimited Extensibility**

- **Manifest-based discovery** - Engines automatically discovered from `engine.manifest.json` files
- **No code changes** - Just add manifest and engine class
- **Dynamic API** - Lists engines automatically, no hardcoded lists
- **Plugin architecture** - Each engine is independent
- **Protocol-based** - All engines implement `EngineProtocol` interface

**Recommended Engines:**

- **Primary TTS Engines:** Chatterbox TTS, Coqui TTS (XTTS), Tortoise TTS
- **Primary Transcription Engines:** Whisper (faster-whisper), Vosk, WhisperX
- **Optimization:** PyTorch, ONNX Runtime, CTranslate2

**All engines are offline, local-first, no API keys required.**

## 20. BACKEND ARCHITECTURE

**Backend API runs locally:**

- ✅ All endpoints run locally
- ✅ No external API calls
- ✅ No API keys required
- ✅ No cloud services
- ✅ Communication: `localhost:8000` (internal)

## 21. PERFORMANCE & STABILITY SAFEGUARDS

**CRITICAL:** These safeguards ensure the Cursor environment remains stable and responsive during multi-agent development.

### 1. Monitor Resource Usage

**Requirements:**

- Track CPU/GPU/memory usage for each agent process
- Use Cursor's agent dashboard (if available) to monitor resource stats
- If agent's resource usage spikes abnormally → Pause or reset to avoid degradation

**Thresholds:**

- CPU > 80% sustained → Pause and report
- Memory > 2GB per agent → Review and optimize
- GPU > 90% → Throttle operations

### 2. Staggered Access

**File/Resource Access:**

- If multiple agents need same file → Implement retries/backoff
- If Agent A has locked file → Agent B should sleep briefly before retrying (NOT tight loop)
- Prevents busy-waiting and race conditions

**Retry Pattern:**

- Exponential backoff (increasing delay)
- Maximum retry limit (e.g., 5 attempts)
- Report to Overseer if stuck
- No tight loops (busy-waiting)

### 3. Loop/Time Limits

**Prevent Infinite Loops:**

- Set sensible limits in prompts/tasks
- Instruct agents to break if no progress after N iterations
- Overseer detects and intervenes if agent stuck repeating step

**Example Limits:**

- Maximum iterations per loop: 1000
- Maximum execution time per task: 30 minutes
- Maximum retry attempts: 5

### 4. Logging Cooldowns

**Limit Log Verbosity:**

- Avoid logging same progress message every second
- Batch or throttle logs (e.g., at most one update per few seconds)
- Keep logs readable and essential information only

**Log Throttling:**

- ERROR: Always log
- WARNING: Log with cooldown
- INFO: Batch updates (max 1 per 5 seconds)
- DEBUG: Disable in production

### 5. Fail-Safes

**Crash/Hang Handling:**

- If agent crashes or hangs → Overseer terminates and possibly restarts
- System should fail gracefully (e.g., roll back partial changes if commit fails)
- Preserve work in progress
- No data loss

---

## PART 4: DEVELOPMENT WORKFLOW

## 22. TASK MANAGEMENT RULES

### Task Assignment:

1. Check `TASK_LOG.md` for assignments
2. Check file locks before starting work
3. Acquire file lock before editing
4. Update progress in `TASK_TRACKER_3_WORKERS.md`
5. Mark complete in `TASK_LOG.md` when done

### Task Completion:

1. Verify Definition of Done criteria met
2. Remove file locks
3. Update task status
4. Create status report
5. Notify Overseer for review

### Task Handoff:

1. Worker marks task complete
2. Worker removes file locks
3. Overseer reviews work
4. Overseer approves and assigns next task
5. Next worker takes ownership

## 23. FILE LOCKING PROTOCOL

### Before Editing Any File:

1. **Check TASK_LOG.md** for existing file locks
2. **If file is locked:**
   - Wait for unlock (if task nearly complete)
   - Request handoff from current worker
   - Work on different file
3. **If file is unlocked:**
   - Add file to lock list in `TASK_LOG.md`
   - Include task ID, worker name, timestamp
   - Begin work

### After Completing Work:

1. Complete all edits
2. Test changes
3. Remove file from lock list in `TASK_LOG.md`
4. Mark task as complete
5. Notify Overseer for review

**See:** `docs/governance/FILE_LOCKING_PROTOCOL.md` for complete protocol

## 24. QUALITY ASSURANCE PROCESS

**Before Marking ANY Task Complete:**

1. All dependencies installed and verified
2. Code is 100% complete and functional
3. All functionality implemented and tested
4. No placeholders, stubs, bookmarks, or tags in ANY form
5. No loophole attempts
6. Code actually works (not just exists)
7. All error cases handled
8. All edge cases considered
9. Production-ready quality

**UI Compliance (if UI task):**

1. 3-row grid structure maintained
2. 4 PanelHosts used (not raw Grid)
3. VSQ.\* design tokens used (no hardcoded values)
4. MVVM separation maintained
5. ChatGPT UI specification followed exactly

## 25. DEFINITION OF DONE

**A feature is "Done" ONLY when ALL criteria are met:**

1. **Windows Installer**

   - ✅ Native Windows installer created
   - ✅ Tested on clean Windows systems
   - ✅ Uninstaller works correctly
   - ✅ File associations configured

2. **Pixel-Perfect UI**

   - ✅ Interface matches approved design spec
   - ✅ All UI elements pixel-accurate
   - ✅ Colors, fonts, icons, layouts match spec

3. **All Panels Functional**

   - ✅ Every panel fully implemented
   - ✅ Real functionality (not placeholders)
   - ✅ All features wired and operational

4. **No Placeholders or TODOs**

   - ✅ No temporary stubs
   - ✅ No placeholder code
   - ✅ No "TODO" comments
   - ✅ All features fully implemented

5. **Tested and Documented**
   - ✅ All code tested
   - ✅ UI behavior verified
   - ✅ All functionality documented

## 26. WORKER COORDINATION

**All workers must reference:**

- `docs\governance\WORKER_COMPLETION_CHECKLIST.md` - **CRITICAL** - 100% completion checklist (260 tasks with checkboxes)

  - Explicit completion criteria for each worker
  - Task-by-task tracking
  - Progress percentage calculation
  - Phase 0 success criteria

- `docs\governance\WORKER_ROADMAP_DETAILED.md` - **COMPLETE DETAILED PLAN** for all 6 workers
  - Day-by-day task breakdown
  - Step-by-step instructions
  - Dependencies and timelines
  - Success criteria for each task
  - Inter-worker coordination

**Additional planning documents:**

- `docs\governance\WORKER_BRIEFING.md` - Worker briefing with priorities
- `docs\governance\WORKER_PROMPTS_LAUNCH.md` - Launch instructions
- `docs\governance\DEVELOPMENT_ROADMAP.md` - Overall development plan

---

## PART 5: SPECIALIZED SYSTEMS

## 27. BRAINSTORMER PROTOCOL

### Brainstormer is READ-ONLY

**What Brainstormer Does:**

- ✅ Generates UX/UI enhancement ideas
- ✅ Submits ideas to Overseer
- ✅ Suggests improvements

**What Brainstormer Does NOT Do:**

- ❌ Edit code files
- ❌ Modify documentation
- ❌ Update roadmap directly
- ❌ Implement features
- ❌ Fix bugs

### Design Compliance Requirements:

All ideas must:

- ✅ Respect WinUI 3 native requirement
- ✅ Maintain DAW-style layout
- ✅ Preserve information density
- ✅ Enhance without simplifying

**Prohibited Ideas:**

- ❌ Switching to web technologies
- ❌ Simplifying layout
- ❌ Reducing complexity
- ❌ Framework changes

## 28. ENGINE LIBRARY DOWNLOAD RULES

### Offline-First Model Management

**REQUIRED:**

- ✅ All models must be downloadable and installable offline
- ✅ Use local mirrors, pre-downloaded archives, or bundled ZIPs
- ✅ Verify SHA-256 checksums for all downloaded models
- ✅ Store models in `%PROGRAMDATA%\VoiceStudio\models\{engine}\`
- ✅ Only download models with permissive licenses (MIT, Apache-2.0, BSD, CC-BY, etc.)
- ✅ Update `models.index.json` after successful downloads
- ✅ Support air-gapped/restricted environments

**FORBIDDEN:**

- ❌ Rely on runtime HTTP fetch unless explicitly marked `auto_update=true`
- ❌ Download models with restricted licenses (non-commercial, research-only)
- ❌ Skip checksum verification
- ❌ Store models in application directory (use %PROGRAMDATA%)
- ❌ Use `pip install` for models (download manually)

**Implementation:**

- See `docs/developer/ENGINE_LIBRARY_DOWNLOAD_GUIDE.md` for complete guide
- Use `tools/download_all_free_models.py` for batch downloads
- All Cursor agents must verify model completeness before marking DONE

## 29. UI/UX INTEGRITY RULES

### Design Language Requirements:

1. **WinUI 3 Native Only**

   - Use only WinUI 3 controls and XAML
   - No web technologies
   - Full native performance

2. **Docked, Modular Panels**

   - Panels must be dockable
   - Panels must be resizable and rearrangeable
   - PanelHost system for all panels
   - 3-column + nav + bottom deck layout maintained

3. **Design Consistency**

   - Use DesignTokens.xaml for ALL styling
   - Consistent fonts and spacings
   - Uniform look & feel
   - Visual hierarchy matches style guidelines

4. **Premium Details**
   - High-quality polish (subtle animations)
   - No generic stock imagery
   - Consistent alignments
   - Smooth transitions
   - Professional DAW-grade appearance

## 30. MARKDOWN STANDARDS

### Recommended Markdown Standards Rule

**Purpose:** Establish consistent markdown formatting and structure across all documentation.

#### File Structure Standards:

````
# Document Title
## Section Header
### Subsection Header

**Bold text**
*Italic text*
`code`
> Blockquote

- List item
- Another item

1. Numbered list
2. Another item

| Table | Header |
|-------|--------|
| Data  | Here   |

```language
code block
````

```

#### Content Standards:
- Use H1 (#) for document title only
- Use H2 (##) for major sections
- Use H3 (###) for subsections
- Use H4 (####) for sub-subsections when needed
- Use consistent heading capitalization (Title Case)
- Use blank lines between sections
- Use consistent code block formatting
- Use consistent table formatting
- Use consistent list formatting

#### Link Standards:
- Use reference-style links when possible
- Use descriptive link text
- Keep links organized at bottom of document
- Use relative paths for internal links

#### Code Standards:
- Use appropriate language identifiers for code blocks
- Use consistent indentation
- Include comments in code examples
- Use consistent naming conventions

#### Table Standards:
- Use consistent column widths
- Left-align text columns
- Center-align numeric columns
- Right-align when appropriate
- Use header separators consistently

## 31. PROMPT SYSTEM

### Ready-to-Use Prompts:

**All agents must use these ready-to-use prompts:**
- `docs/governance/QUICK_START_GUIDE.md` - **START HERE** - Complete quick start for all agents
- `docs/governance/OVERSEER_PROMPT.md` - Ready-to-use Overseer system prompt
- `docs/governance/WORKER_PROMPT.md` - Ready-to-use Worker system prompt
- `docs/governance/BRAINSTORMER_PROMPT.md` - Ready-to-use Brainstormer system prompt

**All agents must follow these workflows:**
1. Read Memory Bank first (`docs/design/MEMORY_BANK.md`)
2. Load appropriate system prompt
3. Check `TASK_LOG.md` for assignments
4. Follow file locking protocol
5. Update progress daily
6. Verify Definition of Done before completion

---

## FINAL REMINDERS

**The UI design layout and plans MUST stay exactly as given from ChatGPT.**

**EVERY task must be 100% complete before moving to the next task.**

**NO exceptions. NO shortcuts. NO placeholders. NO bookmarks. NO tags. NO stubs.**

**Quality over speed. Completeness over progress. Correctness over task count.**

**This is a professional DAW-grade application. Complexity and modularity are features, not bugs.**

**ALL rules apply to ALL workers, ALL tasks, ALL the time. NO EXCEPTIONS.**

---

**Last Updated:** 2025-12-26
**Status:** COMPREHENSIVE COMPILATION - Complete Reference Document
**Source:** All files in E:\VoiceStudio project
**Compiled By:** AI Assistant Overseer
```
