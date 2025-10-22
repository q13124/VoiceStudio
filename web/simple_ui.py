#!/usr/bin/env python3
"""
VoiceStudio Simple Web UI
Clean web interface for voice cloning with drag-drop upload
Based on ChatGPT strategic plan for Day 6-7 implementation
"""

import os
import tempfile
import uuid
from pathlib import Path
from typing import List, Optional
import logging
import asyncio
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import our voice fusion and quality systems
try:
    from workers.ops.voice_fusion import VoiceFusion, FusionConfig
    from workers.ops.quality_scorer import VoiceQualityScorer, QualityConfig
    VOICE_SYSTEMS_AVAILABLE = True
except ImportError as e:
    VOICE_SYSTEMS_AVAILABLE = False
    logging.warning(f"Voice systems not available: {e}")

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="VoiceStudio Voice Cloner",
    description="Professional voice cloning with multi-reference fusion",
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

# Configuration
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize voice systems
voice_fusion = None
quality_scorer = None

if VOICE_SYSTEMS_AVAILABLE:
    try:
        voice_fusion = VoiceFusion(FusionConfig())
        quality_scorer = VoiceQualityScorer(QualityConfig())
        logger.info("Voice systems initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize voice systems: {e}")
        VOICE_SYSTEMS_AVAILABLE = False

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>VoiceStudio - Voice Cloner</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                padding: 40px;
                max-width: 600px;
                width: 100%;
            }
            
            h1 {
                text-align: center;
                color: #333;
                margin-bottom: 30px;
                font-size: 2.5em;
                font-weight: 300;
            }
            
            .upload-area {
                border: 3px dashed #ddd;
                border-radius: 15px;
                padding: 40px;
                text-align: center;
                margin-bottom: 30px;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            
            .upload-area:hover {
                border-color: #667eea;
                background-color: #f8f9ff;
            }
            
            .upload-area.dragover {
                border-color: #667eea;
                background-color: #f0f4ff;
                transform: scale(1.02);
            }
            
            .upload-icon {
                font-size: 3em;
                color: #ddd;
                margin-bottom: 15px;
            }
            
            .upload-text {
                color: #666;
                font-size: 1.1em;
                margin-bottom: 10px;
            }
            
            .upload-hint {
                color: #999;
                font-size: 0.9em;
            }
            
            #fileInput {
                display: none;
            }
            
            .file-list {
                margin: 20px 0;
                max-height: 200px;
                overflow-y: auto;
            }
            
            .file-item {
                display: flex;
                align-items: center;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 8px;
                margin-bottom: 8px;
            }
            
            .file-name {
                flex: 1;
                color: #333;
                font-weight: 500;
            }
            
            .file-size {
                color: #666;
                font-size: 0.9em;
                margin-left: 10px;
            }
            
            .remove-file {
                background: #ff4757;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                cursor: pointer;
                font-size: 0.8em;
            }
            
            .text-input {
                width: 100%;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 1em;
                margin-bottom: 20px;
                resize: vertical;
                min-height: 100px;
            }
            
            .text-input:focus {
                outline: none;
                border-color: #667eea;
            }
            
            .char-count {
                text-align: right;
                color: #666;
                font-size: 0.9em;
                margin-bottom: 20px;
            }
            
            .generate-btn {
                width: 100%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px;
                border-radius: 10px;
                font-size: 1.2em;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-bottom: 20px;
            }
            
            .generate-btn:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }
            
            .generate-btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            
            .progress {
                width: 100%;
                height: 6px;
                background: #f0f0f0;
                border-radius: 3px;
                overflow: hidden;
                margin-bottom: 20px;
                display: none;
            }
            
            .progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #667eea, #764ba2);
                width: 0%;
                transition: width 0.3s ease;
            }
            
            .result-area {
                text-align: center;
                margin-top: 20px;
            }
            
            .audio-player {
                width: 100%;
                margin: 20px 0;
            }
            
            .download-btn {
                background: #2ed573;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
                margin-top: 10px;
            }
            
            .error {
                color: #ff4757;
                background: #ffe6e6;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                display: none;
            }
            
            .success {
                color: #2ed573;
                background: #e6ffe6;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎤 VoiceStudio</h1>
            
            <div class="upload-area" id="uploadArea">
                <div class="upload-icon">📁</div>
                <div class="upload-text">Drop audio files here or click to browse</div>
                <div class="upload-hint">Upload 3-10 audio files of the same speaker (WAV, MP3, M4A)</div>
                <input type="file" id="fileInput" multiple accept="audio/*">
            </div>
            
            <div class="file-list" id="fileList"></div>
            
            <textarea 
                class="text-input" 
                id="textInput" 
                placeholder="Enter the text you want to clone the voice to say..."
                maxlength="1000"
            ></textarea>
            
            <div class="char-count" id="charCount">0 / 1000 characters</div>
            
            <button class="generate-btn" id="generateBtn" onclick="generateVoice()">
                🎵 Generate Voice Clone
            </button>
            
            <div class="progress" id="progress">
                <div class="progress-bar" id="progressBar"></div>
            </div>
            
            <div class="error" id="errorMsg"></div>
            <div class="success" id="successMsg"></div>
            
            <div class="result-area" id="resultArea" style="display: none;">
                <h3>🎉 Generated Voice Clone</h3>
                <audio class="audio-player" id="audioPlayer" controls></audio>
                <br>
                <button class="download-btn" onclick="downloadAudio()">📥 Download Audio</button>
            </div>
        </div>

        <script>
            let selectedFiles = [];
            let generatedAudioBlob = null;

            // File upload handling
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            const fileList = document.getElementById('fileList');
            const textInput = document.getElementById('textInput');
            const charCount = document.getElementById('charCount');
            const generateBtn = document.getElementById('generateBtn');
            const progress = document.getElementById('progress');
            const progressBar = document.getElementById('progressBar');
            const errorMsg = document.getElementById('errorMsg');
            const successMsg = document.getElementById('successMsg');
            const resultArea = document.getElementById('resultArea');
            const audioPlayer = document.getElementById('audioPlayer');

            // Drag and drop
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

            // Character count
            textInput.addEventListener('input', () => {
                const count = textInput.value.length;
                charCount.textContent = `${count} / 1000 characters`;
                
                if (count > 1000) {
                    charCount.style.color = '#ff4757';
                } else {
                    charCount.style.color = '#666';
                }
            });

            function handleFiles(files) {
                Array.from(files).forEach(file => {
                    if (file.type.startsWith('audio/')) {
                        selectedFiles.push(file);
                        updateFileList();
                    }
                });
            }

            function updateFileList() {
                fileList.innerHTML = '';
                selectedFiles.forEach((file, index) => {
                    const fileItem = document.createElement('div');
                    fileItem.className = 'file-item';
                    fileItem.innerHTML = `
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${formatFileSize(file.size)}</div>
                        <button class="remove-file" onclick="removeFile(${index})">Remove</button>
                    `;
                    fileList.appendChild(fileItem);
                });
                
                updateGenerateButton();
            }

            function removeFile(index) {
                selectedFiles.splice(index, 1);
                updateFileList();
            }

            function formatFileSize(bytes) {
                if (bytes === 0) return '0 Bytes';
                const k = 1024;
                const sizes = ['Bytes', 'KB', 'MB', 'GB'];
                const i = Math.floor(Math.log(bytes) / Math.log(k));
                return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
            }

            function updateGenerateButton() {
                const hasFiles = selectedFiles.length >= 1;
                const hasText = textInput.value.trim().length > 0;
                generateBtn.disabled = !hasFiles || !hasText;
            }

            textInput.addEventListener('input', updateGenerateButton);

            async function generateVoice() {
                if (selectedFiles.length === 0) {
                    showError('Please select at least one audio file');
                    return;
                }

                if (textInput.value.trim().length === 0) {
                    showError('Please enter text to generate');
                    return;
                }

                generateBtn.disabled = true;
                progress.style.display = 'block';
                hideMessages();

                try {
                    const formData = new FormData();
                    selectedFiles.forEach(file => {
                        formData.append('files', file);
                    });
                    formData.append('text', textInput.value.trim());

                    const response = await fetch('/clone', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        const error = await response.text();
                        throw new Error(error);
                    }

                    const audioBlob = await response.blob();
                    generatedAudioBlob = audioBlob;
                    
                    const audioUrl = URL.createObjectURL(audioBlob);
                    audioPlayer.src = audioUrl;
                    resultArea.style.display = 'block';
                    
                    showSuccess('Voice clone generated successfully!');
                    
                } catch (error) {
                    showError('Generation failed: ' + error.message);
                } finally {
                    generateBtn.disabled = false;
                    progress.style.display = 'none';
                }
            }

            function downloadAudio() {
                if (generatedAudioBlob) {
                    const url = URL.createObjectURL(generatedAudioBlob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `voice_clone_${new Date().getTime()}.wav`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                }
            }

            function showError(message) {
                errorMsg.textContent = message;
                errorMsg.style.display = 'block';
                successMsg.style.display = 'none';
            }

            function showSuccess(message) {
                successMsg.textContent = message;
                successMsg.style.display = 'block';
                errorMsg.style.display = 'none';
            }

            function hideMessages() {
                errorMsg.style.display = 'none';
                successMsg.style.display = 'none';
            }

            // Initialize
            updateGenerateButton();
        </script>
    </body>
    </html>
    """

@app.post("/clone")
async def clone_voice(
    files: List[UploadFile] = File(...),
    text: str = Form(...)
):
    """
    Clone voice using multiple reference files
    """
    if not VOICE_SYSTEMS_AVAILABLE:
        raise HTTPException(status_code=500, detail="Voice systems not available")
    
    if len(files) < 1:
        raise HTTPException(status_code=400, detail="At least one audio file required")
    
    if len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        # Save uploaded files
        temp_files = []
        for file in files:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}")
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            temp_files.append(temp_file.name)
        
        logger.info(f"Processing {len(temp_files)} files for text: {text[:50]}...")
        
        # For now, return a placeholder response
        # In a real implementation, this would:
        # 1. Use voice_fusion to create fused embedding
        # 2. Generate audio using TTS engine
        # 3. Apply quality scoring
        # 4. Return the generated audio
        
        # Create a simple placeholder audio file
        output_file = OUTPUT_DIR / f"generated_{uuid.uuid4().hex}.wav"
        
        # For demo purposes, copy the first uploaded file as "generated" audio
        # In real implementation, this would be the actual generated audio
        import shutil
        shutil.copy2(temp_files[0], output_file)
        
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        
        return FileResponse(
            path=str(output_file),
            media_type="audio/wav",
            filename=f"voice_clone_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        )
        
    except Exception as e:
        logger.error(f"Voice cloning failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "voice_systems_available": VOICE_SYSTEMS_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "service": "VoiceStudio Voice Cloner",
        "version": "1.0.0",
        "features": {
            "multi_reference_fusion": VOICE_SYSTEMS_AVAILABLE,
            "quality_scoring": VOICE_SYSTEMS_AVAILABLE,
            "web_interface": True
        },
        "endpoints": {
            "clone": "/clone",
            "health": "/health",
            "status": "/api/status"
        }
    }

if __name__ == "__main__":
    # Run the development server
    uvicorn.run(
        "web.simple_ui:app",
        host="127.0.0.1",
        port=5188,
        reload=True,
        log_level="info"
    )
