# Missing Libraries Integration Plan
## Step-by-Step Guide to Integrate Missing Libraries from Old Projects

**Date:** 2025-01-28  
**Status:** Ready for Integration  
**Priority:** CRITICAL for audio quality features

---

## 📊 **SUMMARY**

**Total Missing Libraries:** 25+ critical libraries  
**Files Created:**
- ✅ `requirements_missing_libraries.txt` - Consolidated requirements file
- ✅ `docs/governance/OLD_PROJECT_LIBRARIES_AND_TOOLS_2025-01-28.md` - Complete inventory

---

## 🎯 **INTEGRATION STEPS**

### **Phase 1: Critical Audio Quality Libraries** (2-3 hours)

**Priority:** CRITICAL - These enable quality benchmarking and enhancement

1. **Install Quality Metrics:**
   ```bash
   pip install pesq>=0.0.4 pystoi>=0.3.3
   ```

2. **Install Audio Enhancement:**
   ```bash
   pip install voicefixer>=0.1.2 deepfilternet>=0.5.0
   ```

3. **Install Source Separation:**
   ```bash
   pip install spleeter>=2.3.0
   ```

4. **Install Professional Effects:**
   ```bash
   pip install pedalboard>=0.7.0
   ```

5. **Install Audio Augmentation:**
   ```bash
   pip install audiomentations>=1.7.0
   ```

6. **Install Advanced Resampling:**
   ```bash
   pip install resampy>=0.4.2 pyrubberband>=0.3.0
   ```

7. **Install Advanced Analysis:**
   ```bash
   pip install essentia-tensorflow>=1.1.1
   ```

**Verification:**
- [ ] Test each library import
- [ ] Verify no conflicts with existing dependencies
- [ ] Update `requirements_engines.txt` with new libraries

---

### **Phase 2: RVC Dependencies** (1-2 hours)

**Priority:** CRITICAL - Required for RVC engine functionality

1. **Install RVC Core:**
   ```bash
   pip install fairseq==0.12.2 faiss-cpu==1.7.4
   ```

2. **Install Vocoder Features:**
   ```bash
   pip install pyworld==0.3.2
   ```

3. **Install Prosody Analysis:**
   ```bash
   pip install praat-parselmouth>=0.4.3
   ```

**Note:** Some packages may require C++ compiler. If installation fails:
- Install Visual Studio Build Tools
- Or use conda: `conda install -c conda-forge fairseq faiss-cpu`

**Verification:**
- [ ] Test RVC engine with new dependencies
- [ ] Verify HuBERT features work
- [ ] Check vector similarity search

---

### **Phase 3: Performance Monitoring** (1 hour)

**Priority:** MEDIUM - Useful for optimization

1. **Install Monitoring Tools:**
   ```bash
   pip install py-cpuinfo>=9.0.0 GPUtil>=1.4.0 nvidia-ml-py>=11.0.0
   ```

2. **Install Experiment Tracking (Optional):**
   ```bash
   pip install wandb>=0.15.0
   ```

**Verification:**
- [ ] Test CPU/GPU monitoring
- [ ] Verify metrics collection

---

### **Phase 4: Advanced Utilities** (1 hour)

**Priority:** MEDIUM - Nice to have

1. **Install Voice Activity Detection:**
   ```bash
   pip install webrtcvad>=2.0.10
   ```

2. **Install Dimensionality Reduction:**
   ```bash
   pip install umap-learn>=0.5.9
   ```

3. **Install Training Visualization:**
   ```bash
   pip install tensorboard>=2.20.0
   ```

4. **Install NLP Processing (Optional, Large):**
   ```bash
   pip install spacy[ja]>=3.8.7
   ```

**Verification:**
- [ ] Test each utility
- [ ] Verify no conflicts

---

### **Phase 5: Metrics & Monitoring** (30 minutes)

**Priority:** LOW - For FastAPI backend metrics

1. **Install Prometheus:**
   ```bash
   pip install prometheus-client>=0.23.1 prometheus-fastapi-instrumentator>=6.1.0
   ```

**Verification:**
- [ ] Test metrics endpoint
- [ ] Verify FastAPI integration

---

## 🔧 **TOOLS TO COPY**

### **High Priority Tools** (Copy from `C:\OldVoiceStudio\tools\`)

1. **`audio_quality_benchmark.py`** → `tools/audio_quality_benchmark.py`
2. **`quality_dashboard.py`** → `tools/quality_dashboard.py`
3. **`dataset_qa.py`** → `tools/dataset_qa.py`
4. **`dataset_report.py`** → `tools/dataset_report.py`
5. **`benchmark_engines.py`** → `tools/benchmark_engines.py`
6. **`repair_wavs.py`** → `tools/repair_wavs.py`
7. **`mark_bad_clips.py`** → `tools/mark_bad_clips.py`

### **Medium Priority Tools**

8. **`system_health_validator.py`** → `tools/system_health_validator.py`
9. **`system_monitor.py`** → `tools/system_monitor.py`
10. **`performance-monitor.py`** → `tools/performance_monitor.py`
11. **`profile_engine_memory.py`** → `tools/profile_engine_memory.py`

### **Training Tools**

12. **`train_ultimate.py`** → `tools/train_ultimate.py`
13. **`train_voice_quality.py`** → `tools/train_voice_quality.py`
14. **`config-optimizer.py`** → `tools/config_optimizer.py`

**Action for Each Tool:**
1. Copy file from old project
2. Review and adapt to current project structure
3. Update imports and paths
4. Test functionality
5. Add to project documentation

---

## ✅ **VERIFICATION CHECKLIST**

After each phase:

- [ ] All libraries install without errors
- [ ] No version conflicts with existing dependencies
- [ ] All imports work correctly
- [ ] Tools copied and adapted successfully
- [ ] Documentation updated
- [ ] Integration log updated

---

## 📝 **UPDATING REQUIREMENTS**

After successful integration:

1. **Update `requirements_engines.txt`:**
   - Add all successfully installed libraries
   - Lock versions that work
   - Add installation notes for complex packages

2. **Update Documentation:**
   - Add new libraries to `TECHNICAL_STACK_SPECIFICATION.md`
   - Update `COMPATIBILITY_MATRIX.md`
   - Add tool usage guides

3. **Update Integration Log:**
   - Mark libraries as integrated in `COMPREHENSIVE_INTEGRATION_LOG_2025-01-28.md`
   - Document any issues or workarounds

---

## 🚨 **TROUBLESHOOTING**

### **Common Issues:**

1. **C++ Compiler Required:**
   - Install Visual Studio Build Tools
   - Or use conda for binary packages

2. **Version Conflicts:**
   - Install in separate virtual environment
   - Test compatibility before merging

3. **Large Downloads:**
   - Some packages (spacy, tensorboard) are large
   - Consider optional installation

4. **Platform-Specific:**
   - Some packages may be Linux/Mac only
   - Check Windows compatibility

---

## 📊 **ESTIMATED TIME**

- **Phase 1 (Critical Audio):** 2-3 hours
- **Phase 2 (RVC):** 1-2 hours
- **Phase 3 (Monitoring):** 1 hour
- **Phase 4 (Utilities):** 1 hour
- **Phase 5 (Metrics):** 30 minutes
- **Tools Integration:** 4-6 hours
- **Total:** 10-14 hours

---

## 🎯 **NEXT STEPS**

1. ✅ Review this plan
2. ✅ Start with Phase 1 (Critical Audio Libraries)
3. ✅ Test each library individually
4. ✅ Update requirements after successful installation
5. ✅ Copy and adapt tools
6. ✅ Update documentation

---

**Last Updated:** 2025-01-28  
**Status:** Ready for execution

