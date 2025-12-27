/**
 * Real-Time Quality Preview Example (IDEA 69)
 * 
 * This example demonstrates how to use WebSocket to receive
 * real-time quality preview updates during synthesis and processing.
 */

// WebSocket connection for quality preview
class QualityPreviewClient {
  constructor(baseUrl = 'ws://localhost:8000') {
    this.baseUrl = baseUrl;
    this.ws = null;
    this.reconnectDelay = 1000;
    this.maxReconnectDelay = 30000;
  }

  /**
   * Connect to WebSocket and subscribe to quality topic
   */
  connect() {
    const url = `${this.baseUrl}/ws/realtime?topics=quality`;
    
    this.ws = new WebSocket(url);
    
    this.ws.onopen = () => {
      console.log('✅ Connected to quality preview WebSocket');
      this.reconnectDelay = 1000;
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleQualityUpdate(data);
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    this.ws.onclose = () => {
      console.log('WebSocket closed, reconnecting...');
      this.reconnect();
    };
  }

  /**
   * Handle quality update messages
   */
  handleQualityUpdate(data) {
    if (data.topic === 'quality') {
      const payload = data.payload;
      
      switch (payload.process_type) {
        case 'multipass_synthesis':
          this.handleMultiPassUpdate(payload);
          break;
        case 'artifact_removal':
          this.handleArtifactRemovalUpdate(payload);
          break;
        case 'post_processing':
          this.handlePostProcessingUpdate(payload);
          break;
        case 'characteristic_analysis':
          this.handleCharacteristicAnalysisUpdate(payload);
          break;
        default:
          console.log('Quality update:', payload);
      }
    }
  }

  /**
   * Handle multi-pass synthesis quality updates
   */
  handleMultiPassUpdate(payload) {
    console.log(`\n📊 Multi-Pass Synthesis Update:`);
    console.log(`  Pass: ${payload.pass_number}/${payload.total_passes}`);
    console.log(`  Quality Score: ${(payload.quality_score * 100).toFixed(1)}%`);
    console.log(`  MOS Score: ${payload.quality_metrics?.mos_score?.toFixed(2) || 'N/A'}`);
    console.log(`  Similarity: ${(payload.quality_metrics?.similarity * 100).toFixed(1)}% || 'N/A'}`);
    
    if (payload.improvement !== undefined) {
      const improvementSign = payload.improvement >= 0 ? '+' : '';
      console.log(`  Improvement: ${improvementSign}${(payload.improvement * 100).toFixed(2)}%`);
    }
    
    // Update UI (example)
    this.updateQualityDisplay(payload);
  }

  /**
   * Handle artifact removal quality updates
   */
  handleArtifactRemovalUpdate(payload) {
    console.log(`\n🔧 Artifact Removal Update:`);
    console.log(`  Progress: ${(payload.progress * 100).toFixed(1)}%`);
    console.log(`  Artifacts Detected: ${payload.artifacts_detected?.join(', ') || 'None'}`);
    console.log(`  Artifacts Removed: ${payload.artifacts_removed?.join(', ') || 'None'}`);
    
    if (payload.quality_improvement !== undefined) {
      console.log(`  Quality Improvement: ${(payload.quality_improvement * 100).toFixed(2)}%`);
    }
  }

  /**
   * Handle post-processing stage updates
   */
  handlePostProcessingUpdate(payload) {
    console.log(`\n⚙️ Post-Processing Update:`);
    console.log(`  Stage: ${payload.stage}`);
    console.log(`  Stage Progress: ${(payload.stage_progress * 100).toFixed(1)}%`);
    console.log(`  Completed Stages: ${payload.completed_stages}/${payload.total_stages}`);
    console.log(`  Quality: ${(payload.quality_before * 100).toFixed(1)}% → ${(payload.quality_after * 100).toFixed(1)}%`);
    
    if (payload.improvement !== undefined) {
      console.log(`  Improvement: +${(payload.improvement * 100).toFixed(2)}%`);
    }
  }

  /**
   * Handle voice characteristic analysis updates
   */
  handleCharacteristicAnalysisUpdate(payload) {
    console.log(`\n🎤 Voice Characteristic Analysis:`);
    console.log(`  Similarity Score: ${(payload.similarity_score * 100).toFixed(1)}%`);
    console.log(`  Preservation Score: ${(payload.preservation_score * 100).toFixed(1)}%`);
    
    if (payload.recommendations && payload.recommendations.length > 0) {
      console.log(`  Recommendations:`);
      payload.recommendations.forEach(rec => {
        console.log(`    - ${rec}`);
      });
    }
  }

  /**
   * Update quality display in UI (example implementation)
   */
  updateQualityDisplay(payload) {
    // Example: Update progress bar
    if (payload.process_type === 'multipass_synthesis') {
      const progress = (payload.pass_number / payload.total_passes) * 100;
      console.log(`Progress: ${progress.toFixed(0)}%`);
    }
    
    // Example: Update quality metrics chart
    if (payload.quality_metrics) {
      // Update chart with new metrics
      console.log('Update quality metrics chart:', payload.quality_metrics);
    }
  }

  /**
   * Reconnect with exponential backoff
   */
  reconnect() {
    setTimeout(() => {
      console.log(`Reconnecting in ${this.reconnectDelay}ms...`);
      this.connect();
      this.reconnectDelay = Math.min(
        this.reconnectDelay * 2,
        this.maxReconnectDelay
      );
    }, this.reconnectDelay);
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Usage example
const qualityClient = new QualityPreviewClient();

// Connect and start receiving quality updates
qualityClient.connect();

// Example: Start a synthesis operation and receive real-time quality updates
async function synthesizeWithQualityPreview(profileId, text) {
  // Connect to quality preview
  qualityClient.connect();
  
  // Start synthesis (this would trigger quality updates via WebSocket)
  const response = await fetch('http://localhost:8000/api/voice/synthesize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      engine: 'chatterbox',
      profile_id: profileId,
      text: text
    })
  });
  
  const result = await response.json();
  console.log('Synthesis complete:', result.audio_id);
  
  // Quality updates will be received via WebSocket automatically
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  qualityClient.disconnect();
});

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = QualityPreviewClient;
}

