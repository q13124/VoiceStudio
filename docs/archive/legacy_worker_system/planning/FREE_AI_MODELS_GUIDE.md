# Free AI Models for Cursor - Cost Savings Guide

**Problem:** Spending $60/day on Cursor Pro and burning through quota.

**Solution:** Use free/local models where possible.

---

## 🆓 Free Options in Cursor

### 1. Cursor Free Tier
- **What you get:** Limited requests per month
- **Models:** Usually GPT-3.5 Turbo or GPT-4o-mini
- **Strategy:** Use sparingly, only for critical tasks

### 2. Local Models (Best Option)
**Cursor supports local models via Ollama or LM Studio**

#### Setup Ollama (Recommended):
1. **Install Ollama:** https://ollama.ai/download
2. **Pull free models:**
   ```bash
   ollama pull codellama        # Code-focused, free
   ollama pull deepseek-coder   # Excellent for coding, free
   ollama pull llama3.2         # General purpose, free
   ollama pull mistral          # Fast, free
   ```
3. **Configure Cursor:**
   - Settings → Models → Add Local Model
   - Select Ollama provider
   - Choose your downloaded model

#### Best Free Coding Models:
- **DeepSeek Coder 6.7B** - Best free coding model
- **CodeLlama 13B** - Strong code understanding
- **Llama 3.2 3B** - Fast, lightweight
- **Mistral 7B** - Good balance

**Cost:** $0 (runs on your GPU/CPU)

---

## 🔄 Alternative Free Tools

### 1. Continue.dev (VS Code Extension)
- **Cost:** Free
- **Models:** Supports Ollama, OpenAI API (bring your own key), Anthropic API
- **Features:** Similar to Cursor chat
- **Setup:** Install extension, connect to Ollama

### 2. Codeium (Free Tier)
- **Cost:** Free for individuals
- **Models:** Their own models + GPT-4o-mini
- **Limits:** Generous free tier
- **Setup:** Install extension, sign up

### 3. GitHub Copilot (Free for Students/Open Source)
- **Cost:** Free if you qualify
- **Models:** GPT-4 based
- **Check:** https://education.github.com/pack

### 4. Tabnine (Free Tier)
- **Cost:** Free tier available
- **Models:** Local + cloud options
- **Limits:** Limited but usable

---

## 💰 Cost-Saving Strategy

### Option 1: Hybrid Approach (Recommended)
1. **Use local models** (Ollama) for 80% of work
   - Autocomplete
   - Simple refactors
   - Code generation
2. **Use Cursor free tier** for 20% of work
   - Complex reasoning
   - Architecture decisions
   - Critical debugging

**Savings:** ~$50-60/day → $0-10/day

### Option 2: Switch to Continue.dev + Ollama
- **Cost:** $0
- **Setup time:** 15 minutes
- **Trade-off:** Slightly less polished than Cursor

### Option 3: Use Cursor Free Tier Strategically
- **Disable autocomplete** (biggest token burner)
- **Use only for chat** when needed
- **Use local models** for autocomplete

---

## 🚀 Quick Setup: Ollama + Cursor

### Step 1: Install Ollama
```powershell
# Download from https://ollama.ai/download
# Or use winget:
winget install Ollama.Ollama
```

### Step 2: Pull Coding Models
```powershell
ollama pull deepseek-coder
ollama pull codellama
ollama pull llama3.2
```

### Step 3: Configure Cursor
1. Open Cursor Settings (Ctrl+,)
2. Search "model" or "local"
3. Add Ollama as provider
4. Select "deepseek-coder" as default
5. Set autocomplete to use local model

### Step 4: Test
- Try inline edit → Should use Ollama (free)
- Check Cursor usage → Should stay flat

---

## 📊 Model Comparison (Free vs Paid)

| Model | Cost | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **DeepSeek Coder** | Free | Fast | Excellent | Coding tasks |
| **CodeLlama** | Free | Medium | Very Good | Code understanding |
| **Llama 3.2** | Free | Fast | Good | General coding |
| **GPT-4o-mini** | $ | Fast | Excellent | When free tier allows |
| **Claude Haiku** | $ | Fast | Excellent | When free tier allows |
| **GPT-4o** | $$$ | Medium | Excellent | Complex reasoning |
| **Claude Opus** | $$$$ | Slow | Best | Critical decisions |

---

## ⚙️ Cursor Settings for Maximum Savings

### 1. Disable Expensive Features
- **Autocomplete:** Disable or set to local model only
- **Background indexing:** Disable (burns tokens)
- **Auto-suggestions:** Disable

### 2. Use Local Models First
- **Default model:** Ollama (DeepSeek Coder)
- **Chat model:** Ollama (DeepSeek Coder)
- **Fallback:** Cursor free tier only when needed

### 3. Limit Context
- **Context window:** 4K tokens max
- **Don't include workspace:** Unchecked
- **Only relevant files:** Checked

---

## 🎯 Recommended Daily Workflow

### Morning Setup:
1. Start Ollama: `ollama serve` (runs in background)
2. Set Cursor to use Ollama models
3. Disable autocomplete (or set to Ollama)

### During Work:
- **80% of tasks:** Use Ollama (free)
- **15% of tasks:** Use Cursor free tier (if available)
- **5% of tasks:** Use paid models (only if critical)

### End of Day:
- Check usage → Should be minimal
- Switch back to paid models only if needed for tomorrow

---

## 💡 Pro Tips

1. **GPU vs CPU:**
   - GPU: Much faster for local models
   - CPU: Works but slower (still free)
   - Check: `nvidia-smi` to see if GPU available

2. **Model Size:**
   - 7B models: Fast, good quality, runs on most hardware
   - 13B models: Better quality, needs more RAM
   - 34B+ models: Best quality, needs powerful GPU

3. **When to Use Paid:**
   - Only for complex architecture decisions
   - Only when local model fails
   - Only for critical production code

4. **Monitor Usage:**
   - Check Cursor usage dashboard daily
   - If burning quota → Switch to Ollama immediately
   - Set daily budget alerts if possible

---

## 🔧 Troubleshooting

### Ollama Not Working?
```powershell
# Check if running
ollama list

# Restart service
ollama serve

# Test model
ollama run deepseek-coder "Write a Python function"
```

### Cursor Not Finding Ollama?
- Make sure Ollama is running (`ollama serve`)
- Check Cursor settings → Models → Local providers
- Restart Cursor after installing Ollama

### Model Too Slow?
- Use smaller model (3B instead of 7B)
- Use GPU if available
- Reduce context window

---

## 📈 Expected Savings

### Current Situation:
- **Daily cost:** $60
- **Monthly cost:** ~$1,800
- **Usage:** Burning through quota

### With Ollama + Strategic Paid Use:
- **Daily cost:** $0-5
- **Monthly cost:** ~$0-150
- **Savings:** ~$1,650/month

### With Continue.dev + Ollama:
- **Daily cost:** $0
- **Monthly cost:** $0
- **Savings:** ~$1,800/month

---

## 🎓 Action Plan (Do This Now)

1. **Install Ollama** (5 minutes)
   ```powershell
   winget install Ollama.Ollama
   ```

2. **Pull DeepSeek Coder** (10 minutes, depends on internet)
   ```powershell
   ollama pull deepseek-coder
   ```

3. **Configure Cursor** (2 minutes)
   - Settings → Models → Add Ollama
   - Set DeepSeek Coder as default

4. **Disable Autocomplete** (1 minute)
   - Settings → Features → Disable autocomplete
   - Or set to Ollama only

5. **Test** (2 minutes)
   - Try inline edit → Should work free
   - Check usage → Should not increase

**Total time:** ~20 minutes  
**Savings:** ~$1,650/month

---

## 🔗 Resources

- **Ollama:** https://ollama.ai
- **DeepSeek Models:** https://huggingface.co/deepseek-ai
- **Continue.dev:** https://continue.dev
- **Codeium:** https://codeium.com

---

**Last Updated:** 2025-12-27  
**Status:** Active guide for reducing Cursor costs to near-zero
