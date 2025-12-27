# Master Rules - VoiceStudio Quantum+ Complete Ruleset
## All Rules, Guidelines, and Requirements in Full

**Date:** 2025-01-28  
**Status:** COMPLETE - Master Reference Document  
**Purpose:** Single source of truth for ALL project rules  
**Version:** 1.0

---

## 📋 TABLE OF CONTENTS

1. [The Absolute Rule - NO Stubs/Placeholders/Bookmarks/Tags](#1-the-absolute-rule)
2. [Dependency Installation Rule - ALWAYS Install Dependencies](#2-dependency-installation-rule)
3. [UI Design Rules - ChatGPT Specification](#3-ui-design-rules)
4. [Integration Rules](#4-integration-rules)
5. [Code Quality Rules](#5-code-quality-rules)
   - [Correctness Over Speed Rule](#-correctness-over-speed-rule---highest-priority)
6. [Architecture Rules](#6-architecture-rules)
7. [Worker Rules](#7-worker-rules)
8. [Overseer Rules](#8-overseer-rules)
9. [Enforcement Rules](#9-enforcement-rules)
10. [Periodic Refresh System](#10-periodic-refresh-system)

---

## 1. THE ABSOLUTE RULE

### 🚨 THE MAIN RULE - HIGHEST PRIORITY

**EVERY task must be 100% complete before moving to the next task.**

**NO exceptions. NO shortcuts. NO placeholders. NO bookmarks. NO tags. NO stubs.**

**This rule applies to:**
- ✅ All code files (C#, Python, XAML, JSON, etc.)
- ✅ All documentation files (Markdown, text, etc.)
- ✅ All configuration files
- ✅ All comments in code
- ✅ All UI text and labels
- ✅ All error messages
- ✅ All test files
- ✅ All build scripts
- ✅ All installer files
- ✅ **EVERYTHING**

---

### ❌ FORBIDDEN TERMS AND PATTERNS

#### 1. Bookmarks (FORBIDDEN)

**Complete List of Forbidden Bookmarks (ALL Synonyms and Variations):**
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

**Examples of FORBIDDEN usage:**
- `// TODO: Implement this`
- `// FIXME: Fix this later`
- `// NOTE: Come back here`
- `// HACK: Temporary solution`
- `// REMINDER: Check this`
- `// XXX: Important`
- `// WARNING: Needs attention`
- `// CAUTION: Review required`
- `// BUG: Known issue`
- `// ISSUE: To be resolved`
- `// REFACTOR: Improve later`
- `// OPTIMIZE: Performance issue`
- `// REVIEW: Needs review`
- `// CHECK: Verify this`
- `// VERIFY: Confirm`
- `// TEST: Add tests`
- `// DEBUG: Debug this`
- `// DEPRECATED: Old code`
- `// OBSOLETE: Remove later`
- Comments like "fix this later", "needs work", "come back here"
- Any comment indicating incomplete work

#### 2. Placeholders (FORBIDDEN)

**Complete List of Forbidden Placeholders (ALL Synonyms and Variations):**
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

**Examples of FORBIDDEN usage:**
- Functions returning `None`, `null`, empty objects without implementation
- `NotImplementedError`, `NotImplementedException`
- Comments saying "placeholder", "dummy", "mock", "fake", "sample"
- Empty returns: `return {}`, `return []`, `return null`
- Hardcoded filler data: `{"mock": true}`, `{"test": "data"}`
- Functions that return fake responses
- Code marked as "temporary" or "for now"
- Any code that doesn't perform the actual intended function

#### 3. Stubs (FORBIDDEN)

**Complete List of Forbidden Stubs (ALL Synonyms and Variations):**
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

**Examples of FORBIDDEN usage:**
- Functions with just `pass` (Python)
- Methods with only `throw new NotImplementedException()` (C#)
- Method signatures with no body
- Interfaces without implementation
- Classes with empty methods
- Functions that just return without doing anything
- Abstract methods without concrete implementations (unless truly abstract base class)

#### 4. Tags (FORBIDDEN)

**Complete List of Forbidden Tags (ALL Categories):**

**Markup/Structural Tags:**
- HTML tags, XML tags, Markdown tags, YAML tags, JSON tags, tags in markup languages, elements, attributes, properties, decorators, annotations, directives, metadata tags, schema tags, namespace tags

**Version/Control Tags:**
- Git tags, version tags, release tags, build tags, branch tags, commit tags, repository tags, revision tags (when used to mark incomplete work)

**Code/Documentation Tags:**
- JSDoc tags, DocString tags, comment tags, inline tags, block tags, annotation tags, attribute tags, decorator tags, metadata annotations, type hints, type annotations (when used to mark incomplete work)

**Status/Indicator Tags:**
- Status tags, progress tags, completion tags, work tags, issue tags, task tags, milestone tags, checkpoint tags, waypoint tags, anchor tags, reference tags, bookmark tags, flag tags, label tags, badge tags, stamp tags, seal tags, mark tags, signpost tags
- tag, label, status indicator, marker, annotation, comment tag, code tag, metadata tag, flag, badge
- TODO tag, FIXME tag, HACK tag, NOTE tag, XXX tag, WARNING tag, CAUTION tag, BUG tag, ISSUE tag, REFACTOR tag, OPTIMIZE tag, REVIEW tag, CHECK tag, VERIFY tag, TEST tag, DEBUG tag, DEPRECATED tag, OBSOLETE tag
- markup, annotation, notation, indicator, sign, symbol, marker, pointer, reference, flag, label, badge, stamp, seal, mark, signpost, milestone, checkpoint, waypoint, anchor, bookmark, reference point
- status indicator, completion marker, progress indicator, work marker, issue marker, problem marker, warning marker, error marker, note marker, reminder marker

**System/Metadata Tags:**
- File tags, folder tags, system tags, metadata tags, index tags, catalog tags, library tags, collection tags, category tags, classification tags, taxonomy tags, ontology tags (when used to mark incomplete work)

**API/Service Tags:**
- API tags, endpoint tags, route tags, service tags, microservice tags, container tags, deployment tags, environment tags, configuration tags, feature flags, toggle tags, switch tags (when used to mark incomplete work)

**Tracking/Monitoring Tags:**
- Tracking tags, analytics tags, monitoring tags, logging tags, event tags, metric tags, performance tags, diagnostic tags, debug tags, trace tags (when used to mark incomplete work)

**Social/Collaboration Tags:**
- Hashtags, mention tags, notification tags, alert tags, reminder tags, assignment tags, ownership tags, responsibility tags (when used to mark incomplete work)

**Content/Organizational Tags:**
- Content tags, topic tags, subject tags, keyword tags, search tags, filter tags, sort tags, group tags, category tags, tag clouds, tag lists, tag sets (when used to mark incomplete work)

**Examples of FORBIDDEN usage:**
- `#TODO`, `#FIXME`, `#PLACEHOLDER`, `#HACK`, `#NOTE`
- XML/HTML tags that aren't functional: `<placeholder>`, `<todo>`, `<incomplete>`
- Status indicators: `[IN PROGRESS]`, `[PENDING]`, `[TO BE DONE]`
- Any tag indicating incomplete work

#### 5. Status Words and Phrases (FORBIDDEN)

**Forbidden Status Words (Complete List - ALL Variations):**
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

**Forbidden Phrases (Complete List - ALL Variations):**
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

**Examples of FORBIDDEN usage:**
- `// This needs to be implemented`
- `// Coming soon`
- `// Will be done later`
- `// Temporary solution`
- `// For now, this works`
- `// Eventually we'll fix this`
- `// Not yet implemented`
- `// Missing implementation`
- `// Requires work`
- `// Pending review`
- `// In progress`
- `// Under development`
- `// Work in progress`
- `// WIP`

---

### 🚫 LOOPHOLE PREVENTION - NO WORKAROUNDS ALLOWED

**CRITICAL:** The following variations and workarounds are ALSO FORBIDDEN. AI agents MUST NOT use these to circumvent the rule.

#### Capitalization Variations (FORBIDDEN):
- ❌ `todo`, `Todo`, `TODO`, `ToDo`, `To-Do`, `to-do`, `TO-DO`
- ❌ `fixme`, `Fixme`, `FIXME`, `FixMe`, `Fix-Me`, `fix-me`, `FIX-ME`
- ❌ `wip`, `Wip`, `WIP`, `WiP`, `W-I-P`, `w-i-p`, `W-I-P`
- ❌ `tbd`, `Tbd`, `TBD`, `TbD`, `T-B-D`, `t-b-d`, `T-B-D`
- ❌ All forbidden terms in ANY capitalization variation

#### Spacing Variations (FORBIDDEN):
- ❌ `TO DO`, `TO-DO`, `TO_DO`, `TODO`, `TO DO`, `T O D O`
- ❌ `FIX ME`, `FIX-ME`, `FIX_ME`, `FIXME`, `FIX ME`, `F I X M E`
- ❌ `IN PROGRESS`, `IN-PROGRESS`, `IN_PROGRESS`, `INPROGRESS`, `IN PROGRESS`, `I N P R O G R E S S`
- ❌ All forbidden terms with ANY spacing variation (spaces, dashes, underscores, no spaces)

#### Punctuation Variations (FORBIDDEN):
- ❌ `TODO:`, `TODO.`, `TODO,`, `TODO;`, `TODO!`, `TODO?`, `TODO-`, `TODO_`, `TODO/`, `TODO\`, `TODO|`
- ❌ `[TODO]`, `(TODO)`, `{TODO}`, `<TODO>`, `"TODO"`, `'TODO'`, `` `TODO` ``, `*TODO*`, `_TODO_`, `~TODO~`
- ❌ `#TODO`, `@TODO`, `$TODO`, `%TODO`, `&TODO`, `*TODO`, `+TODO`, `=TODO`
- ❌ All forbidden terms with ANY punctuation variation

#### Abbreviation Variations (FORBIDDEN):
- ❌ `TBD`, `TBA`, `TBC`, `TBR`, `TBS`, `TBT`, `TBU` (all variations)
- ❌ `WIP`, `WIPD`, `WIPT`, `WIPR` (all variations)
- ❌ `N/A`, `NA`, `N/A`, `n/a`, `na` (when meaning "not applicable" or "not available" for incomplete work)
- ❌ `NIL`, `nil`, `NULL`, `null`, `NONE`, `none`, `VOID`, `void`, `ZERO`, `zero`, `NOTHING`, `nothing` (when meaning incomplete)
- ❌ `RC` (release candidate - when meaning incomplete)
- ❌ `ALPHA`, `alpha`, `BETA`, `beta`, `PREVIEW`, `preview` (when meaning incomplete)

#### Language Variations (FORBIDDEN):
- ❌ Translations of forbidden terms in other languages
- ❌ Foreign language equivalents of "TODO", "FIXME", "placeholder", "stub", "incomplete", "not yet", etc.
- ❌ Code comments in other languages that mean the same thing

#### Encoding Variations (FORBIDDEN):
- ❌ Unicode variations: `ＴＯＤＯ` (full-width), `TODO` (normal), `TODO` (with invisible characters)
- ❌ HTML entities: `&lt;TODO&gt;`, `&#84;&#79;&#68;&#79;`
- ❌ URL encoding: `TODO`, `%54%4F%44%4F`
- ❌ Base64 or other encodings of forbidden terms

#### Comment Style Variations (FORBIDDEN):
- ❌ `// TODO`, `/* TODO */`, `# TODO`, `<!-- TODO -->`, `; TODO`, `' TODO`, `` ` TODO ` ``, `REM TODO`
- ❌ `//TODO`, `/*TODO*/`, `#TODO`, `<!--TODO-->`, `;TODO`, `'TODO`, `` `TODO` ``, `REMTODO`
- ❌ `// TODO:`, `/* TODO: */`, `# TODO:`, `<!-- TODO: -->`, `; TODO:`, `' TODO:`
- ❌ All comment styles in ALL programming languages

#### String Concatenation Variations (FORBIDDEN):
- ❌ `"TO" + "DO"`, `"TODO".substring(0, 4)`, `"T" + "O" + "D" + "O"`
- ❌ `"FIX" + "ME"`, `"FIXME".substring(0, 5)`, `"F" + "I" + "X" + "M" + "E"`
- ❌ Any string concatenation that results in forbidden terms

#### Variable/Function Name Variations (FORBIDDEN):
- ❌ Variable names: `todo`, `TODO`, `todoItem`, `todoList`, `todoTask`, `fixme`, `FIXME`, `wip`, `WIP`, `placeholder`, `stub`, `dummy`, `mock`
- ❌ Function names: `todo()`, `TODO()`, `fixme()`, `FIXME()`, `wip()`, `WIP()`, `placeholder()`, `stub()`, `dummy()`, `mock()`
- ❌ Class names: `Todo`, `TODO`, `Fixme`, `FIXME`, `Wip`, `WIP`, `Placeholder`, `Stub`, `Dummy`, `Mock`
- ❌ File names: `todo.md`, `TODO.md`, `fixme.md`, `FIXME.md`, `wip.md`, `WIP.md`, `placeholder.md`, `stub.md`, `dummy.md`, `mock.md`

#### Emoji/Unicode Variations (FORBIDDEN):
- ❌ `📝 TODO`, `🔧 FIXME`, `⚠️ WARNING`, `🚧 WIP`, `⏳ PENDING`, `📌 NOTE`, `🔖 BOOKMARK`
- ❌ `TODO 📝`, `FIXME 🔧`, `WARNING ⚠️`, `WIP 🚧`, `PENDING ⏳`, `NOTE 📌`, `BOOKMARK 🔖`
- ❌ Any emoji combined with forbidden terms

#### Whitespace Variations (FORBIDDEN):
- ❌ ` TODO `, `TODO `, ` TODO`, `  TODO  `, `\tTODO\t`, `\nTODO\n`, `\rTODO\r`
- ❌ ` TODO: `, `TODO: `, ` TODO:`, `  TODO:  `, `\tTODO:\t`, `\nTODO:\n`, `\rTODO:\r`
- ❌ All forbidden terms with ANY whitespace variation

#### Regex/Pattern Variations (FORBIDDEN):
- ❌ Using regex patterns that match forbidden terms: `.*TODO.*`, `.*FIXME.*`, `.*WIP.*`
- ❌ Using wildcards: `T*D*O`, `F*I*X*M*E`, `W*I*P`
- ❌ Using character classes: `[Tt][Oo][Dd][Oo]`, `[Ff][Ii][Xx][Mm][Ee]`, `[Ww][Ii][Pp]`

#### Context Variations (FORBIDDEN):
- ❌ Using forbidden terms in strings: `"This is a TODO item"`, `"FIXME: needs work"`, `"WIP: in progress"`
- ❌ Using forbidden terms in documentation: `See TODO section`, `Check FIXME list`, `Review WIP items`
- ❌ Using forbidden terms in error messages: `TODO: Error occurred`, `FIXME: Fix this error`, `WIP: Error handling`
- ❌ Using forbidden terms in log messages: `TODO: Logging this`, `FIXME: Log this later`, `WIP: Logging in progress`
- ❌ Using forbidden terms in UI text: `TODO Button`, `FIXME Label`, `WIP Status`
- ❌ Using forbidden terms in file paths: `/todo/`, `/fixme/`, `/wip/`, `/placeholder/`, `/stub/`
- ❌ Using forbidden terms in URLs: `?todo=1`, `&fixme=1`, `#wip`, `#placeholder`, `#stub`

#### Negation Variations (FORBIDDEN):
- ❌ `NOT TODO`, `NOT FIXME`, `NOT WIP`, `NOT PLACEHOLDER`, `NOT STUB`
- ❌ `NO TODO`, `NO FIXME`, `NO WIP`, `NO PLACEHOLDER`, `NO STUB`
- ❌ `NOT A TODO`, `NOT A FIXME`, `NOT A WIP`, `NOT A PLACEHOLDER`, `NOT A STUB`
- ❌ Using negation to claim something is not a forbidden term when it actually is

#### Meta-References (FORBIDDEN):
- ❌ `"TODO" (as a string)`, `'TODO' (as a string)`, `` `TODO` (as a string) ``
- ❌ `The word TODO`, `The term FIXME`, `The phrase WIP`
- ❌ `TODO-like`, `FIXME-like`, `WIP-like`, `TODO-style`, `FIXME-style`, `WIP-style`
- ❌ `TODO-ish`, `FIXME-ish`, `WIP-ish`, `TODO-esque`, `FIXME-esque`, `WIP-esque`

#### Indirect References (FORBIDDEN):
- ❌ `Similar to TODO`, `Like FIXME`, `Same as WIP`
- ❌ `TODO equivalent`, `FIXME equivalent`, `WIP equivalent`
- ❌ `TODO alternative`, `FIXME alternative`, `WIP alternative`
- ❌ `TODO substitute`, `FIXME substitute`, `WIP substitute`

#### Time-Based Variations (FORBIDDEN):
- ❌ `TODO for now`, `FIXME for now`, `WIP for now`, `PLACEHOLDER for now`, `STUB for now`
- ❌ `TODO temporarily`, `FIXME temporarily`, `WIP temporarily`, `PLACEHOLDER temporarily`, `STUB temporarily`
- ❌ `TODO until later`, `FIXME until later`, `WIP until later`, `PLACEHOLDER until later`, `STUB until later`

#### Scope Variations (FORBIDDEN):
- ❌ `TODO in this function`, `FIXME in this method`, `WIP in this class`
- ❌ `TODO here`, `FIXME here`, `WIP here`, `PLACEHOLDER here`, `STUB here`
- ❌ `TODO in code`, `FIXME in code`, `WIP in code`, `PLACEHOLDER in code`, `STUB in code`

#### Priority Variations (FORBIDDEN):
- ❌ `High priority TODO`, `Low priority FIXME`, `Medium priority WIP`
- ❌ `TODO (high)`, `FIXME (low)`, `WIP (medium)`
- ❌ `TODO - high`, `FIXME - low`, `WIP - medium`

#### Status Variations (FORBIDDEN):
- ❌ `TODO (pending)`, `FIXME (incomplete)`, `WIP (unfinished)`
- ❌ `TODO - pending`, `FIXME - incomplete`, `WIP - unfinished`
- ❌ `TODO status: pending`, `FIXME status: incomplete`, `WIP status: unfinished`

**REMEMBER:** If it means the same thing as a forbidden term, it's FORBIDDEN regardless of how it's written, formatted, encoded, or referenced.

**NO EXCEPTIONS. NO WORKAROUNDS. NO LOOPHOLES.**

---

### ✅ WHAT IS REQUIRED

#### Code Requirements:
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

#### Documentation Requirements:
- ✅ Complete content, not outlines
- ✅ All examples work and are tested
- ✅ All procedures tested
- ✅ All links verified
- ✅ No empty sections
- ✅ No "TODO: Add content here"
- ✅ No placeholder text

#### UI Requirements:
- ✅ All controls functional
- ✅ All interactions work
- ✅ All states implemented
- ✅ All animations complete
- ✅ No "Placeholder" text in UI
- ✅ No disabled buttons that never work
- ✅ No "Coming soon" messages
- ✅ No empty states that say "TODO"

#### Exception for Testing:
- ✅ If mocking is required for testing, wrap it in a clear `if TEST_MODE:` conditional
- ✅ Log mock usage clearly
- ✅ Never use mocks in production code paths
- ✅ Test mocks must be clearly marked and isolated

---

### 🔍 VERIFICATION CHECKLIST

**Before Marking ANY Task Complete:**

1. **Search your code for ALL forbidden patterns:**
   - [ ] Bookmarks (TODO, FIXME, NOTE, HACK, REMINDER, XXX, WARNING, CAUTION, BUG, ISSUE, REFACTOR, OPTIMIZE, REVIEW, CHECK, VERIFY, TEST, DEBUG, DEPRECATED, OBSOLETE - all variations)
   - [ ] Placeholders (NotImplementedError, NotImplementedException, [PLACEHOLDER], {"mock": true}, dummy, mock, fake, sample, temporary - all variations)
   - [ ] Stubs (pass-only functions, empty methods, function signatures without implementation - all variations)
   - [ ] Tags (#TODO, #FIXME, [PLACEHOLDER], [WIP], [IN PROGRESS] - all variations)
   - [ ] Status Words ("pending", "incomplete", "unfinished", "coming soon", "not yet", "eventually", "later", "for now", "temporary", "needs", "requires", "missing", "WIP", "tbd", "tba", "tbc" - all variations)
   - [ ] Loophole Prevention Patterns (capitalization, spacing, punctuation, comment style, string concatenation, variable/function names, emoji, whitespace, regex, context, negation, meta-references, indirect references, time-based, scope, priority, status variations)

2. **Functional Testing:**
   - [ ] Does the code actually work?
   - [ ] Are all cases handled?
   - [ ] Are there any errors?
   - [ ] Is it production-ready?
   - [ ] Can it be tested?
   - [ ] Does it perform the actual intended function?

**If you find ANY of these patterns:**
- 🚨 **STOP IMMEDIATELY**
- 🚨 **COMPLETE THE IMPLEMENTATION**
- 🚨 **TEST IT**
- 🚨 **THEN** mark as complete

---

### 🚨 CONSEQUENCES OF VIOLATION

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

---

## 2. UI DESIGN RULES

### 🚨 THE UI DESIGN LAYOUT AND PLANS MUST STAY EXACTLY AS GIVEN FROM CHATGPT

**Source of Truth:**
- **`docs/design/ORIGINAL_UI_SCRIPT_CHATGPT.md`** - Original ChatGPT/User collaboration UI script
- **`docs/design/VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md`** - Complete original specification with full XAML code

**Framework:** WinUI 3 (.NET 8, C#/XAML) - **NOT** React/TypeScript, **NOT** Python GUI

---

### NON-NEGOTIABLE UI GUARDRAILS

#### Rule 1: Layout Complexity - DO NOT SIMPLIFY
```
❌ DO NOT reduce 3-column + nav + bottom deck layout
❌ DO NOT remove any PanelHost controls
❌ DO NOT collapse panels into single views
✅ MUST maintain MainWindow 3-Row Grid structure
✅ MUST have 4 PanelHosts: Left, Center, Right, Bottom
✅ MUST have 64px Nav Rail (8 toggle buttons)
✅ MUST have 48px Command Toolbar
✅ MUST have 26px Status Bar
```

#### Rule 2: MVVM Separation - DO NOT MERGE
```
❌ DO NOT merge View and ViewModel files
❌ DO NOT combine .xaml + .xaml.cs + ViewModel.cs
✅ MUST have separate files for every panel:
   - PanelNameView.xaml
   - PanelNameView.xaml.cs
   - PanelNameViewModel.cs (implements IPanelView)
```

#### Rule 3: PanelHost Control - DO NOT REPLACE
```
❌ DO NOT replace PanelHost with raw Grid
❌ DO NOT inline panel content in MainWindow
✅ MUST use PanelHost UserControl for all panels
✅ MUST maintain PanelHost structure (header 32px + content area)
```

#### Rule 4: Design Tokens - DO NOT HARDCODE
```
❌ DO NOT use hardcoded colors, fonts, or spacing
❌ DO NOT create new color schemes
✅ MUST use VSQ.* resources from DesignTokens.xaml
✅ MUST reference design tokens for ALL styling
```

#### Rule 5: Professional Complexity - REQUIRED
```
❌ DO NOT simplify "for clarity"
❌ DO NOT reduce panel count
❌ DO NOT remove placeholder areas
✅ MUST maintain Adobe/FL Studio level complexity
✅ MUST keep all 6 core panels
✅ MUST preserve all placeholder regions
```

---

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

---

### PANELHOST STRUCTURE (MANDATORY)

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

---

### DESIGN TOKENS (DesignTokens.xaml)

**Critical Resources - MUST USE:**

#### Colors (VSQ.*)
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

#### Brushes (VSQ.*Brush)
```
VSQ.Window.Background: LinearGradientBrush (Dark → Darker)
VSQ.Text.PrimaryBrush: SolidColorBrush
VSQ.Text.SecondaryBrush: SolidColorBrush
VSQ.Accent.CyanBrush: SolidColorBrush
VSQ.Panel.BackgroundBrush: SolidColorBrush
VSQ.Panel.BorderBrush: SolidColorBrush
```

#### Typography (VSQ.Font.*)
```
VSQ.Font.Caption: 10
VSQ.Font.Body: 12
VSQ.Font.Title: 16
VSQ.Font.Heading: 20
```

#### Styles (VSQ.Text.*)
```
VSQ.Text.Body: FontSize=12, Foreground=Primary
VSQ.Text.Caption: FontSize=10, Foreground=Secondary
VSQ.Text.Title: FontSize=16, Foreground=Primary, SemiBold
VSQ.Text.Heading: FontSize=20, Foreground=Primary, Bold
```

#### Constants (VSQ.*)
```
VSQ.CornerRadius.Panel: 8
VSQ.CornerRadius.Button: 4
VSQ.Animation.Duration.Fast: 100ms
VSQ.Animation.Duration.Medium: 150ms
VSQ.Animation.Duration.Slow: 300ms
```

---

### 6 CORE PANELS (REQUIRED)

1. **ProfilesView** - LeftPanelHost default
   - Tabs: Profiles / Library (32px header)
   - Left: Profiles grid (WrapGrid, 180×120 cards)
   - Right: Detail inspector (260px width)

2. **TimelineView** - CenterPanelHost default
   - Toolbar (32px): Add Track, Zoom, Grid settings
   - Tracks area (*): ItemsControl with track templates
   - Visualizer (160px): Spectrogram/visualizer placeholder

3. **EffectsMixerView** - RightPanelHost default
   - Mixer (60%): Horizontal ItemsControl with mixer strips
   - FX Chain (40%): Node view / FX chain placeholder

4. **AnalyzerView** - RightPanelHost alternative
   - Tabs (32px): Waveform, Spectral, Radar, Loudness, Phase
   - Chart area (*): Placeholder for chart rendering

5. **MacroView** - BottomPanelHost default
   - Tabs (32px): Macros / Automation
   - Node graph canvas (*): Placeholder for node-based macro system

6. **DiagnosticsView** - BottomPanelHost alternative
   - Logs (60%): ListView with log entries
   - Metrics charts (40%): CPU, GPU, RAM progress bars

---

### VIOLATION DETECTION & REMEDIATION

**If you detect ANY of these violations, issue immediate remediation:**

1. **Merged View/ViewModel files** → REVERT
2. **PanelHost replaced with Grid** → REVERT
3. **Reduced panel count** → REVERT
4. **Hardcoded colors** → REVERT
5. **Simplified layout** → REVERT

**REMEDIATION COMMAND:**
"Revert simplifications. This UI is intentionally complex. Restore PanelHost and separate panel Views/ViewModels according to ChatGPT specification. Do not merge or collapse."

---

## 4. INTEGRATION RULES

### INTEGRATION POLICY

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

**See:** `docs/governance/COMPREHENSIVE_INTEGRATION_LOG_2025-01-28.md` for complete integration priorities and guidelines

---

## 4. CODE QUALITY RULES

### 🚨 CORRECTNESS OVER SPEED RULE - HIGHEST PRIORITY

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
- **Quality cannot be rushed**
- **Correctness is the only metric that matters**

**This rule is MANDATORY and has NO EXCEPTIONS.**

---

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
- ✅ Test mode mocks (if any) clearly marked and logged

**Exception for Testing:**
- ✅ If mocking is required for testing, wrap it in a clear `if TEST_MODE:` conditional
- ✅ Log mock usage clearly
- ✅ Never use mocks in production code paths
- ✅ Test mocks must be clearly marked and isolated

### DEPENDENCY INSTALLATION RULE

**🚨 CRITICAL RULE - NO EXCEPTIONS:**

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
1. **Identify dependencies:** Check requirements files, documentation, code imports
2. **Check current installation:** Verify if dependencies are already installed
3. **Install missing dependencies:** Use appropriate package manager (pip, NuGet, etc.)
4. **Verify installation:** Test that dependencies work correctly
5. **Document installation:** Update requirements files if new dependencies added

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

---

## 5. ARCHITECTURE RULES

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

**Cursor MUST:**
1. **Set workspace to `E:\VoiceStudio`** when opening Cursor
2. **Treat `E:\VoiceStudio` as the ONLY place for changes:**
   - All new code goes here
   - All edits happen here
   - All file creation happens here
   - This is the authoritative source
3. **Treat `C:\VoiceStudio` and `C:\OldVoiceStudio` as read-only reference:**
   - ✅ **MAY** open and read files there
   - ✅ **MAY** reference code/patterns from there
   - ✅ **MAY** use as inspiration or reference
   - ❌ **MAY NOT** modify or create files there
   - ❌ **MAY NOT** bulk copy directories from there into `E:\VoiceStudio`
   - ❌ **MAY NOT** write to these directories

---

## 6. WORKER RULES

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
- ✅ Use periodic refresh system (see Section 9)

**Dependency Installation (MANDATORY):**
- ✅ **BEFORE starting any task:** Identify and install all required dependencies
- ✅ **BEFORE implementing code:** Verify all dependencies are installed
- ✅ **BEFORE marking task complete:** Verify all dependencies work correctly
- ✅ **NO EXCEPTIONS:** Install dependencies even if they seem optional
- ✅ **NO SKIPPING:** Do not skip dependency installation
- ✅ **NO ASSUMPTIONS:** Verify dependencies are installed, don't assume

---

## 7. OVERSEER RULES

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

---

## 8. ENFORCEMENT RULES

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

---

## 9. PERIODIC REFRESH SYSTEM

**PRIMARY REFERENCE:** `docs/governance/MASTER_RULES_COMPLETE.md` - **ALL INSTANCES MUST USE THIS AS PRIMARY REFERENCE**

**This document (`MASTER_RULES_COMPLETE.md`) contains ALL rules, ALL forbidden terms (including ALL synonyms and variations), and ALL loophole prevention patterns. This prevents instances from using similar-meaning words to bypass the rule.**

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

## 🎯 REMEMBER

**The UI design layout and plans MUST stay exactly as given from ChatGPT.**

**EVERY task must be 100% complete before moving to the next task.**

**NO exceptions. NO shortcuts. NO placeholders. NO bookmarks. NO tags. NO stubs.**

**Refresh yourself on these rules regularly. Don't forget. Don't deviate.**

**Quality over speed. Completeness over progress. Correctness over task count.**

**Do not prioritize speed or task count. Your only priority is to produce the correct solution, even if it takes longer or results in fewer changes. Never rush or cut corners.**

**This rule applies to ALL workers, ALL tasks, ALL the time.**

**NO EXCEPTIONS.**

---

## 📚 REFERENCE DOCUMENTS

**For complete details, see:**
- `docs/governance/COMPLETE_NO_STUBS_PLACEHOLDERS_BOOKMARKS_RULE.md` - Complete forbidden terms list
- `docs/design/ORIGINAL_UI_SCRIPT_CHATGPT.md` - Original ChatGPT UI specification
- `docs/design/VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md` - Complete original specification
- `docs/governance/OVERSEER_UI_RULES_COMPLETE.md` - Complete UI rules
- `docs/governance/COMPREHENSIVE_INTEGRATION_LOG_2025-01-28.md` - Integration priorities
- `docs/governance/PERIODIC_RULES_REFRESH_SYSTEM.md` - Periodic refresh system
- `docs/governance/RULE_ENFORCEMENT_RECOMMENDATIONS.md` - Enforcement strategies

---

**Last Updated:** 2025-01-28  
**Status:** COMPLETE - Master Rules Document  
**Version:** 1.0

