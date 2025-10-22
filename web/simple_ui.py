#!/usr/bin/env python3
"""
VoiceStudio Ultimate - Simple Web UI for Voice Cloning
FastAPI-based web interface with drag-and-drop audio upload
"""

import os
import json
import tempfile
from pathlib import Path
from typing import List, Optional
import logging

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Voice cloning integration
from workers.ops.voice_fusion import VoiceFusion, VoiceCloningIntegration
from workers.ops.quality_scorer import VoiceCloningQualityGate

# Initialize FastAPI app
app = FastAPI(
    title="VoiceStudio Ultimate",
    description="Professional Voice Cloning System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize voice cloning systems
voice_fusion = VoiceFusion()
voice_integration = VoiceCloningIntegration()
quality_gate = VoiceCloningQualityGate()

# Create uploads directory
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

# Create outputs directory
OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def get_voice_cloning_interface():
    """
    Serve the main voice cloning interface.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>VoiceStudio Ultimate - Voice Cloning</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5rem;
                margin-bottom: 10px;
            }
            
            .header p {
                font-size: 1.2rem;
                opacity: 0.9;
            }
            
            .main-content {
                padding: 40px;
            }
            
            .upload-section {
                margin-bottom: 40px;
            }
            
            .upload-area {
                border: 3px dashed #6366f1;
                border-radius: 15px;
                padding: 40px;
                text-align: center;
                background: #f8fafc;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            
            .upload-area:hover {
                border-color: #4f46e5;
                background: #f1f5f9;
            }
            
            .upload-area.dragover {
                border-color: #4f46e5;
                background: #e0e7ff;
                transform: scale(1.02);
            }
            
            .upload-icon {
                font-size: 3rem;
                color: #6366f1;
                margin-bottom: 20px;
            }
            
            .upload-text {
                font-size: 1.2rem;
                color: #374151;
                margin-bottom: 10px;
            }
            
            .upload-subtext {
                color: #6b7280;
                font-size: 0.9rem;
            }
            
            .file-input {
                display: none;
            }
            
            .file-list {
                margin-top: 20px;
                display: none;
            }
            
            .file-item {
                display: flex;
                align-items: center;
                padding: 15px;
                background: #f9fafb;
                border-radius: 10px;
                margin-bottom: 10px;
            }
            
            .file-icon {
                font-size: 1.5rem;
                color: #6366f1;
                margin-right: 15px;
            }
            
            .file-info {
                flex: 1;
            }
            
            .file-name {
                font-weight: 600;
                color: #374151;
            }
            
            .file-size {
                color: #6b7280;
                font-size: 0.9rem;
            }
            
            .remove-file {
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                cursor: pointer;
                font-size: 0.8rem;
            }
            
            .text-section {
                margin-bottom: 30px;
            }
            
            .section-title {
                font-size: 1.3rem;
                font-weight: 600;
                color: #374151;
                margin-bottom: 15px;
            }
            
            .text-input {
                width: 100%;
                padding: 15px;
                border: 2px solid #e5e7eb;
                border-radius: 10px;
                font-size: 1rem;
                resize: vertical;
                min-height: 100px;
            }
            
            .text-input:focus {
                outline: none;
                border-color: #6366f1;
            }
            
            .settings-section {
                margin-bottom: 30px;
            }
            
            .settings-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
            }
            
            .setting-group {
                background: #f9fafb;
                padding: 20px;
                border-radius: 10px;
            }
            
            .setting-label {
                display: block;
                font-weight: 600;
                color: #374151;
                margin-bottom: 10px;
            }
            
            .setting-input {
                width: 100%;
                padding: 10px;
                border: 2px solid #e5e7eb;
                border-radius: 5px;
            }
            
            .generate-button {
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                color: white;
                border: none;
                padding: 20px 40px;
                border-radius: 15px;
                font-size: 1.2rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                width: 100%;
            }
            
            .generate-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3);
            }
            
            .generate-button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            
            .progress-section {
                margin-top: 30px;
                display: none;
            }
            
            .progress-bar {
                width: 100%;
                height: 20px;
                background: #e5e7eb;
                border-radius: 10px;
                overflow: hidden;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                width: 0%;
                transition: width 0.3s ease;
            }
            
            .progress-text {
                text-align: center;
                margin-top: 10px;
                color: #6b7280;
            }
            
            .result-section {
                margin-top: 30px;
                display: none;
            }
            
            .result-audio {
                width: 100%;
                margin-top: 20px;
            }
            
            .error-message {
                background: #fef2f2;
                color: #dc2626;
                padding: 15px;
                border-radius: 10px;
                margin-top: 20px;
                display: none;
            }
            
            .success-message {
                background: #f0fdf4;
                color: #16a34a;
                padding: 15px;
                border-radius: 10px;
                margin-top: 20px;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎵 VoiceStudio Ultimate</h1>
                <p>Professional Voice Cloning System</p>
            </div>
            
            <div class="main-content">
                <form id="voiceCloneForm">
                    <!-- Audio Upload Section -->
                    <div class="upload-section">
                        <h2 class="section-title">📁 Upload Reference Audio</h2>
                        <div class="upload-area" id="uploadArea">
                            <div class="upload-icon">🎤</div>
                            <div class="upload-text">Drag & Drop Audio Files Here</div>
                            <div class="upload-subtext">or click to browse (WAV, MP3, FLAC supported)</div>
                            <input type="file" id="fileInput" class="file-input" multiple accept="audio/*">
                        </div>
                        <div class="file-list" id="fileList"></div>
                    </div>
                    
                    <!-- Text Input Section -->
                    <div class="text-section">
                        <h2 class="section-title">📝 Text to Synthesize</h2>
                        <textarea 
                            id="textInput" 
                            class="text-input" 
                            placeholder="Enter the text you want to synthesize with the uploaded voice..."
                            required
                        ></textarea>
                    </div>
                    
                    <!-- Settings Section -->
                    <div class="settings-section">
                        <h2 class="section-title">⚙️ Voice Settings</h2>
                        <div class="settings-grid">
                            <div class="setting-group">
                                <label class="setting-label">Engine</label>
                                <select id="engineSelect" class="setting-input">
                                    <option value="xtts">XTTS-2 (Recommended)</option>
                                    <option value="openvoice">OpenVoice</option>
                                    <option value="rvc">RVC</option>
                                    <option value="auto">Auto-Select</option>
                                </select>
                            </div>
                            <div class="setting-group">
                                <label class="setting-label">Quality Mode</label>
                                <select id="qualitySelect" class="setting-input">
                                    <option value="balanced">Balanced</option>
                                    <option value="quality">High Quality</option>
                                    <option value="fast">Fast</option>
                                </select>
                            </div>
                            <div class="setting-group">
                                <label class="setting-label">Min Quality Score</label>
                                <input type="range" id="qualityThreshold" class="setting-input" 
                                       min="0.6" max="0.95" step="0.05" value="0.8">
                                <span id="qualityValue">0.8</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Generate Button -->
                    <button type="submit" class="generate-button" id="generateButton">
                        🎵 Generate Voice Clone
                    </button>
                    
                    <!-- Progress Section -->
                    <div class="progress-section" id="progressSection">
                        <div class="progress-bar">
                            <div class="progress-fill" id="progressFill"></div>
                        </div>
                        <div class="progress-text" id="progressText">Processing...</div>
                    </div>
                    
                    <!-- Result Section -->
                    <div class="result-section" id="resultSection">
                        <h2 class="section-title">🎧 Generated Audio</h2>
                        <audio controls class="result-audio" id="resultAudio"></audio>
                        <div style="margin-top: 20px;">
                            <button type="button" class="generate-button" onclick="downloadAudio()">
                                💾 Download Audio
                            </button>
                        </div>
                    </div>
                    
                    <!-- Messages -->
                    <div class="error-message" id="errorMessage"></div>
                    <div class="success-message" id="successMessage"></div>
                </form>
            </div>
        </div>
        
        <script>
            // File upload handling
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            const fileList = document.getElementById('fileList');
            const uploadedFiles = [];
            
            // Drag and drop functionality
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                handleFiles(e.dataTransfer.files);
            });
            
            uploadArea.addEventListener('click', () => {
                fileInput.click();
            });
            
            fileInput.addEventListener('change', (e) => {
                handleFiles(e.target.files);
            });
            
            function handleFiles(files) {
                for (let file of files) {
                    if (file.type.startsWith('audio/')) {
                        uploadedFiles.push(file);
                    }
                }
                updateFileList();
            }
            
            function updateFileList() {
                if (uploadedFiles.length === 0) {
                    fileList.style.display = 'none';
                    return;
                }
                
                fileList.style.display = 'block';
                fileList.innerHTML = uploadedFiles.map((file, index) => `
                    <div class="file-item">
                        <div class="file-icon">🎵</div>
                        <div class="file-info">
                            <div class="file-name">${file.name}</div>
                            <div class="file-size">${(file.size / 1024 / 1024).toFixed(2)} MB</div>
                        </div>
                        <button type="button" class="remove-file" onclick="removeFile(${index})">
                            Remove
                        </button>
                    </div>
                `).join('');
            }
            
            function removeFile(index) {
                uploadedFiles.splice(index, 1);
                updateFileList();
            }
            
            // Quality threshold display
            const qualityThreshold = document.getElementById('qualityThreshold');
            const qualityValue = document.getElementById('qualityValue');
            
            qualityThreshold.addEventListener('input', (e) => {
                qualityValue.textContent = e.target.value;
            });
            
            // Form submission
            document.getElementById('voiceCloneForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                if (uploadedFiles.length === 0) {
                    showError('Please upload at least one audio file');
                    return;
                }
                
                const text = document.getElementById('textInput').value.trim();
                if (!text) {
                    showError('Please enter text to synthesize');
                    return;
                }
                
                await generateVoice(text);
            });
            
            async function generateVoice(text) {
                const generateButton = document.getElementById('generateButton');
                const progressSection = document.getElementById('progressSection');
                const resultSection = document.getElementById('resultSection');
                
                // Show progress
                generateButton.disabled = true;
                progressSection.style.display = 'block';
                resultSection.style.display = 'none';
                hideMessages();
                
                try {
                    // Create form data
                    const formData = new FormData();
                    formData.append('text', text);
                    formData.append('engine', document.getElementById('engineSelect').value);
                    formData.append('quality_mode', document.getElementById('qualitySelect').value);
                    formData.append('min_quality', document.getElementById('qualityThreshold').value);
                    
                    // Add audio files
                    uploadedFiles.forEach(file => {
                        formData.append('audio_files', file);
                    });
                    
                    // Update progress
                    updateProgress(20, 'Uploading files...');
                    
                    // Send request
                    const response = await fetch('/clone', {
                        method: 'POST',
                        body: formData
                    });
                    
                    updateProgress(50, 'Processing audio...');
                    
                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || 'Generation failed');
                    }
                    
                    updateProgress(80, 'Generating voice...');
                    
                    // Get result
                    const result = await response.json();
                    
                    updateProgress(100, 'Complete!');
                    
                    // Show result
                    setTimeout(() => {
                        showResult(result);
                        generateButton.disabled = false;
                        progressSection.style.display = 'none';
                    }, 1000);
                    
                } catch (error) {
                    console.error('Generation error:', error);
                    showError(error.message);
                    generateButton.disabled = false;
                    progressSection.style.display = 'none';
                }
            }
            
            function updateProgress(percent, text) {
                document.getElementById('progressFill').style.width = percent + '%';
                document.getElementById('progressText').textContent = text;
            }
            
            function showResult(result) {
                const resultSection = document.getElementById('resultSection');
                const resultAudio = document.getElementById('resultAudio');
                
                resultAudio.src = result.audio_url;
                resultSection.style.display = 'block';
                
                showSuccess(`Voice generated successfully! Quality score: ${result.quality_score.toFixed(3)}`);
            }
            
            function downloadAudio() {
                const audio = document.getElementById('resultAudio');
                const link = document.createElement('a');
                link.href = audio.src;
                link.download = 'voice_clone.wav';
                link.click();
            }
            
            function showError(message) {
                const errorDiv = document.getElementById('errorMessage');
                errorDiv.textContent = message;
                errorDiv.style.display = 'block';
            }
            
            function showSuccess(message) {
                const successDiv = document.getElementById('successMessage');
                successDiv.textContent = message;
                successDiv.style.display = 'block';
            }
            
            function hideMessages() {
                document.getElementById('errorMessage').style.display = 'none';
                document.getElementById('successMessage').style.display = 'none';
            }
        </script>
    </body>
    </html>
    """


@app.post("/clone")
async def clone_voice(
    text: str = Form(...),
    audio_files: List[UploadFile] = File(...),
    engine: str = Form("xtts"),
    quality_mode: str = Form("balanced"),
    min_quality: float = Form(0.8)
):
    """
    Clone voice using uploaded audio files.
    """
    try:
        logging.info(f"Voice cloning request: {len(audio_files)} files, engine: {engine}")
        
        # Save uploaded files
        audio_paths = []
        for audio_file in audio_files:
            # Save to temporary file
            temp_path = UPLOADS_DIR / f"temp_{audio_file.filename}"
            with open(temp_path, "wb") as f:
                content = await audio_file.read()
                f.write(content)
            audio_paths.append(temp_path)
        
        # Create voice profile using fusion
        voice_profile = voice_fusion.create_voice_profile(audio_paths, f"profile_{len(audio_paths)}_files")
        
        # Load reference audio for quality comparison
        reference_audio = voice_fusion.load_audio(audio_paths[0])
        
        # Generate voice with quality gate
        generated_audio, quality_info = quality_gate.generate_with_quality_gate(
            text, reference_audio, voice_profile, engine, min_quality
        )
        
        # Save generated audio
        output_filename = f"voice_clone_{len(audio_paths)}_files.wav"
        output_path = OUTPUTS_DIR / output_filename
        
        sf.write(output_path, generated_audio, voice_fusion.sample_rate)
        
        # Clean up temporary files
        for temp_path in audio_paths:
            if temp_path.exists():
                temp_path.unlink()
        
        # Return result
        return {
            "success": True,
            "audio_url": f"/outputs/{output_filename}",
            "quality_score": quality_info["overall_score"],
            "quality_level": quality_info["quality_level"],
            "recommendation": quality_info["recommendation"],
            "engine_used": engine,
            "files_processed": len(audio_files)
        }
        
    except Exception as e:
        logging.error(f"Voice cloning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/outputs/{filename}")
async def get_output_file(filename: str):
    """
    Serve generated audio files.
    """
    file_path = OUTPUTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, media_type="audio/wav")


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "VoiceStudio Ultimate",
        "version": "1.0.0",
        "voice_fusion": "active",
        "quality_scoring": "active"
    }


def run_voice_cloning_server(host: str = "0.0.0.0", port: int = 5188):
    """
    Run the voice cloning web server.
    """
    print("🎵 Starting VoiceStudio Ultimate Voice Cloning Server")
    print("=" * 60)
    print(f"🌐 Server: http://{host}:{port}")
    print(f"🎤 Voice Fusion: Active")
    print(f"📊 Quality Scoring: Active")
    print(f"🎯 Multi-reference: Enabled")
    print("=" * 60)
    
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    # Run the voice cloning server
    run_voice_cloning_server()