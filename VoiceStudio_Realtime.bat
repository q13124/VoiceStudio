@echo off
REM VoiceStudio Ultimate - Real-time Optimized Launcher
REM Optimized for low-latency professional voice cloning

echo VoiceStudio Ultimate - Real-time Mode
echo =====================================

REM Set performance environment variables
set PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
set CUDA_VISIBLE_DEVICES=0
set TORCH_CUDNN_V8_API_ENABLED=1
set OMP_NUM_THREADS=4
set MKL_NUM_THREADS=4

REM Set audio processing optimization
set AUDIO_BUFFER_SIZE=512
set AUDIO_SAMPLE_RATE=22050
set AUDIO_MAX_LATENCY_MS=50

REM Set voice cloning optimization
set VOICE_CLONING_BATCH_SIZE=1
set VOICE_CLONING_MAX_WORKERS=2
set VOICE_CLONING_CUDA_MEMORY_FRACTION=0.7

echo Starting VoiceStudio Ultimate in real-time mode...
echo Audio latency target: %AUDIO_MAX_LATENCY_MS%ms
echo Buffer size: %AUDIO_BUFFER_SIZE% samples
echo Sample rate: %AUDIO_SAMPLE_RATE% Hz

REM Start performance monitor
start "Performance Monitor" python "C:\ProgramData\VoiceStudio\workers\ops\performance_monitor.py"

REM Start real-time DSP chain
start "DSP Chain" python "C:\ProgramData\VoiceStudio\workers\ops\realtime_dsp_chain.py"

REM Start VoiceStudio Ultimate
python "C:\Users\Tyler\VoiceStudio\voice_studio_ultimate.py" --realtime-mode

pause