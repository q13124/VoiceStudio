# 15-Minute Workflow

This workflow is designed to help you make consistent progress on VoiceStudio features in short, focused sprints.

## Goal
- **15 minutes per day**: Dedicated, uninterrupted time.
- **Clear outcome**: A small, testable change.
- **Iterative feedback**: Use AI for planning and review.

## Tools
- **ChatGPT / Claude**: For planning and critical review.
- **Cursor**: For code generation and execution.
- **Terminal / Makefile**: For quick tests and commits.

## Workflow Steps

### 0–2 min: 🧠 Plan with AI (ChatGPT/Claude)
1. **Open your AI assistant.**
2. **Use the `day-plan` Makefile target** to get the prompt template.
   ```bash
   make day-plan DAY=1 FEATURE="Implement X"
   ```
3. **Paste the prompt into your AI assistant.**
4. **Review the AI's output**: It should provide:
   - File path(s)
   - Complete code snippet(s)
   - A test command

### 2–5 min: 💻 Execute with Cursor
1. **Open Cursor.**
2. **Use `Ctrl+K` (or `Cmd+K`)** to open the AI chat.
3. **Paste the AI's plan (file path + code) into Cursor's chat.**
4. **Press `Ctrl+Enter` (or `Cmd+Enter`)** to accept the changes. Cursor will apply the code to the specified files.

### 5–10 min: 🧪 Quick Test
1. **Run the test command provided by the AI.**
   ```bash
   make day-test TEST="your_test_command_from_ai"
   ```
   (Or use `scripts/day.sh` / `scripts/day.ps1` directly)
2. **Verify the output.** Does it pass? Does it do what you expect?

### 10–12 min: 🧐 Review with AI (ChatGPT/Claude)
1. **If tests pass, generate a diff of your changes.**
   ```bash
   git diff
   ```
2. **Use the `day-review` Makefile target** to get the prompt.
   ```bash
   make day-review
   ```
3. **Paste the prompt and your `git diff` output into your AI assistant.**
4. **Ask for critical issues only.** Focus on major flaws, security, performance, or architectural problems.

### 12–15 min: 🛠️ Fix with Cursor
1. **If the AI review finds critical issues, use `Ctrl+L` (or `Cmd+L`) in Cursor.**
2. **Paste the critical issues into Cursor's chat.**
3. **Accept the fixes.**

### 🏁 Commit
1. **Once satisfied, commit your changes.**
   ```bash
   make day-commit DAY=1 FEATURE="Implement X"
   ```
   (Or use `scripts/day.sh` / `scripts/day.ps1` directly)
2. **Push to your repository.**

---

## Example Usage (Makefile)

```bash
# Set environment variables for the day
export DAY=1
export FEATURE="Implement basic health endpoint"
export TEST="curl http://localhost:8000/v1/health/metrics"

# Run the full workflow
make day-all
```

## Example Usage (PowerShell)

```powershell
.\scripts\day.ps1 -DayNum 1 -Feature "Implement basic health endpoint" -Test "curl http://localhost:8000/v1/health/metrics"
```
