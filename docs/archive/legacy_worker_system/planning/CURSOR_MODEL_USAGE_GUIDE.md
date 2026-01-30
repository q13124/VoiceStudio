# Cursor AI Model Usage Guide - Cost Efficiency

**Goal:** Maximize productivity while minimizing token usage/quota burn.

## 🎯 Model Selection Strategy (Cheapest → Most Expensive)

### Tier 1: Daily Work (Use 80% of the time)
**For:** Autocomplete, simple refactors, formatting, small fixes

**Recommended Models:**
- **Claude 3 Haiku** (if available) - Fastest, cheapest, good for simple tasks
- **GPT-4o-mini** - Very cost-effective, handles most coding tasks
- **GPT-3.5 Turbo** - Cheapest option, decent for straightforward code

**When to use:**
- Writing new functions/methods
- Simple refactoring
- Code formatting/style fixes
- Adding comments/documentation
- Small bug fixes
- File operations

---

### Tier 2: Medium Complexity (Use 15% of the time)
**For:** Multi-file refactors, architecture decisions, debugging

**Recommended Models:**
- **Claude 3 Sonnet** - Good balance of cost/quality
- **GPT-4o** - Strong reasoning, reasonable cost
- **GPT-4 Turbo** - Reliable for complex tasks

**When to use:**
- Refactoring across multiple files
- Understanding complex codebases
- Architecture decisions
- Debugging tricky issues
- Writing tests for complex logic

---

### Tier 3: Complex Reasoning (Use 5% of the time)
**For:** Major architecture changes, complex debugging, critical decisions

**Recommended Models:**
- **Claude 3.5 Sonnet** - Best reasoning, use sparingly
- **Claude 3 Opus** - Most capable, most expensive
- **GPT-4** - Strong but expensive

**When to use:**
- Major refactoring decisions
- Complex architectural changes
- Critical bug fixes
- Performance optimization analysis
- Security reviews

---

## ⚙️ Cursor Settings Configuration

### 1. Set Default Model (Settings → Models)
- **Primary:** GPT-4o-mini or Claude 3 Haiku
- **Fallback:** GPT-4o or Claude 3 Sonnet (only when needed)

### 2. Disable Auto-Suggestions for Large Context
- Settings → Features → **Limit autocomplete context**
- Reduces token usage from background indexing

### 3. Use Chat Selectively
- **Don't use chat for simple edits** - Use inline edits instead
- Chat burns tokens faster (full conversation context)
- Inline edits only send relevant code snippets

### 4. Configure Context Window
- Settings → **Limit context window** to 8K-16K tokens
- Only include relevant files in context
- Don't auto-include entire codebase

---

## 💡 Usage Optimization Tips

### Do This:
✅ **Use inline edits** for single-file changes  
✅ **Break large tasks** into smaller prompts  
✅ **Use smaller models** for autocomplete  
✅ **Clear chat history** when switching topics  
✅ **Be specific** in prompts (reduces back-and-forth)  
✅ **Use codebase search** before asking AI to find things  

### Don't Do This:
❌ **Don't use chat** for simple "add a function" tasks  
❌ **Don't include entire files** when only one function changed  
❌ **Don't use GPT-4/Opus** for formatting/typos  
❌ **Don't ask vague questions** that require multiple clarifications  
❌ **Don't keep old context** in chat (start fresh conversations)  
❌ **Don't use AI** for git operations (use terminal)  

---

## 📊 Cost Comparison (Approximate)

| Model | Relative Cost | Best For |
|-------|--------------|----------|
| GPT-3.5 Turbo | $ | Simple tasks, autocomplete |
| GPT-4o-mini | $$ | Most coding tasks |
| Claude 3 Haiku | $$ | Fast, simple to medium tasks |
| GPT-4o | $$$ | Complex reasoning |
| Claude 3 Sonnet | $$$ | Architecture, multi-file work |
| Claude 3.5 Sonnet | $$$$ | Critical decisions only |
| Claude 3 Opus | $$$$$ | Use rarely, major refactors |

---

## 🎯 Quick Decision Tree

```
Need to write/edit code?
├─ Simple function/method?
│  └─ Use: GPT-4o-mini or Claude Haiku
├─ Multiple files?
│  └─ Use: Claude Sonnet or GPT-4o
└─ Architecture decision?
   └─ Use: Claude 3.5 Sonnet (sparingly)

Need to understand code?
├─ Single file?
│  └─ Use: GPT-4o-mini
└─ Entire codebase?
   └─ Use: Claude Sonnet or GPT-4o

Need to debug?
├─ Simple error?
│  └─ Use: GPT-4o-mini
└─ Complex issue?
   └─ Use: Claude Sonnet or GPT-4o
```

---

## 🔧 Cursor-Specific Settings

### Recommended Settings:
1. **Default Model:** GPT-4o-mini (or Claude Haiku if available)
2. **Autocomplete Model:** GPT-3.5 Turbo (cheapest)
3. **Chat Model:** GPT-4o-mini (upgrade to GPT-4o only when needed)
4. **Context Window:** 8K-16K tokens (not unlimited)
5. **Auto-suggestions:** Enabled but limited context

### How to Change:
1. Open Cursor Settings (Ctrl+,)
2. Search for "model" or "AI"
3. Set default model to cheaper option
4. Configure autocomplete separately
5. Disable "include entire workspace" in context

---

## 📈 Monitoring Usage

### Check Usage:
- Cursor Settings → Account → Usage
- Monitor daily/hourly usage
- If burning through quota:
  - Switch to cheaper models
  - Reduce context window
  - Use inline edits instead of chat
  - Disable autocomplete temporarily

### Warning Signs:
- ⚠️ Using >50% quota in first hour → Switch to cheaper models
- ⚠️ Chat responses taking too long → Reduce context
- ⚠️ Autocomplete slow → Disable or use GPT-3.5 Turbo

---

## 🎓 Best Practices Summary

1. **80/15/5 Rule:**
   - 80% of work: GPT-4o-mini / Claude Haiku
   - 15% of work: Claude Sonnet / GPT-4o
   - 5% of work: Claude 3.5 Sonnet / Opus

2. **Use the Right Tool:**
   - Inline edits > Chat (for simple changes)
   - Smaller models > Larger models (for most tasks)
   - Specific prompts > Vague prompts (reduces iterations)

3. **Manage Context:**
   - Only include relevant files
   - Clear chat history regularly
   - Limit context window size

4. **Be Efficient:**
   - Break large tasks into smaller prompts
   - Use codebase search before asking AI
   - Don't use AI for things you can do faster manually

---

**Last Updated:** 2025-12-27  
**Status:** Active recommendations for cost-efficient Cursor usage
