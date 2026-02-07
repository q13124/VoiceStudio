/**
 * VoiceStudio JavaScript/TypeScript SDK
 * 
 * Phase 12.1: JavaScript SDK
 * Provides browser and Node.js compatible access to VoiceStudio API.
 * 
 * @example
 * ```typescript
 * import { VoiceStudioClient } from '@voicestudio/sdk';
 * 
 * const client = new VoiceStudioClient();
 * 
 * const voices = await client.listVoices();
 * const audio = await client.synthesize('Hello, world!', 'en-US-Neural');
 * ```
 */

export const VERSION = '1.0.0';

export interface Voice {
  voiceId: string;
  name: string;
  language: string;
  engine: string;
  description?: string;
  sampleRate: number;
  tags: string[];
  metadata: Record<string, unknown>;
}

export interface AudioResult {
  audioData: ArrayBuffer;
  sampleRate: number;
  format: OutputFormat;
  durationSeconds: number;
  voiceId: string;
  text: string;
  metadata: Record<string, unknown>;
}

export interface SynthesisOptions {
  voiceId: string;
  engine?: SynthesisEngine;
  format?: OutputFormat;
  sampleRate?: number;
  speed?: number;
  pitch?: number;
  energy?: number;
  emotion?: string;
  emotionIntensity?: number;
  language?: string;
  referenceAudio?: string;
}

export interface CloneResult {
  voiceId: string;
  name: string;
  qualityScore: number;
  sampleRate: number;
  metadata: Record<string, unknown>;
}

export enum OutputFormat {
  WAV = 'wav',
  MP3 = 'mp3',
  OGG = 'ogg',
  FLAC = 'flac',
}

export enum SynthesisEngine {
  XTTS = 'xtts',
  BARK = 'bark',
  TORTOISE = 'tortoise',
  CHATTERBOX = 'chatterbox',
  PIPER = 'piper',
  OPENAI_TTS = 'openai_tts',
  ELEVENLABS = 'elevenlabs',
}

export interface ClientOptions {
  baseUrl?: string;
  apiKey?: string;
  timeout?: number;
}

export class VoiceStudioError extends Error {
  constructor(message: string, public statusCode?: number) {
    super(message);
    this.name = 'VoiceStudioError';
  }
}

export class ConnectionError extends VoiceStudioError {
  constructor(message: string) {
    super(message);
    this.name = 'ConnectionError';
  }
}

export class SynthesisError extends VoiceStudioError {
  constructor(message: string) {
    super(message);
    this.name = 'SynthesisError';
  }
}

export class VoiceNotFoundError extends VoiceStudioError {
  constructor(voiceId: string) {
    super(`Voice not found: ${voiceId}`);
    this.name = 'VoiceNotFoundError';
  }
}

const DEFAULT_BASE_URL = 'http://localhost:8765';
const DEFAULT_TIMEOUT = 30000;

/**
 * VoiceStudio API Client
 * 
 * Provides access to VoiceStudio's voice synthesis capabilities from JavaScript/TypeScript.
 */
export class VoiceStudioClient {
  private baseUrl: string;
  private apiKey?: string;
  private timeout: number;

  /**
   * Create a new VoiceStudio client.
   * 
   * @param options - Client configuration options
   */
  constructor(options: ClientOptions = {}) {
    this.baseUrl = (options.baseUrl || DEFAULT_BASE_URL).replace(/\/$/, '');
    this.apiKey = options.apiKey || (typeof process !== 'undefined' ? process.env?.VOICESTUDIO_API_KEY : undefined);
    this.timeout = options.timeout || DEFAULT_TIMEOUT;
  }

  private async request<T>(
    method: string,
    endpoint: string,
    body?: Record<string, unknown>,
    params?: Record<string, string>
  ): Promise<T> {
    const url = new URL(`${this.baseUrl}${endpoint}`);
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, value);
      });
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url.toString(), {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        throw new VoiceStudioError(`API error ${response.status}: ${errorText}`, response.status);
      }

      return response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof VoiceStudioError) {
        throw error;
      }
      
      if ((error as Error).name === 'AbortError') {
        throw new ConnectionError('Request timeout');
      }
      
      throw new ConnectionError(`Failed to connect: ${(error as Error).message}`);
    }
  }

  private async requestBinary(
    method: string,
    endpoint: string,
    body?: Record<string, unknown>
  ): Promise<ArrayBuffer> {
    const url = `${this.baseUrl}${endpoint}`;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        throw new VoiceStudioError(`API error ${response.status}: ${errorText}`, response.status);
      }

      return response.arrayBuffer();
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof VoiceStudioError) {
        throw error;
      }
      
      throw new ConnectionError(`Failed to connect: ${(error as Error).message}`);
    }
  }

  // Health & Status

  /**
   * Check API health status.
   */
  async health(): Promise<Record<string, unknown>> {
    return this.request('GET', '/health');
  }

  /**
   * Get API version.
   */
  async version(): Promise<string> {
    const result = await this.request<{ version: string }>('GET', '/version');
    return result.version || 'unknown';
  }

  // Voice Management

  /**
   * List available voices.
   * 
   * @param options - Filter options
   */
  async listVoices(options: {
    engine?: SynthesisEngine;
    language?: string;
  } = {}): Promise<Voice[]> {
    const params: Record<string, string> = {};
    if (options.engine) params.engine = options.engine;
    if (options.language) params.language = options.language;

    const result = await this.request<{ voices: Voice[] }>(
      'GET',
      '/api/v1/voices',
      undefined,
      params
    );

    return result.voices || [];
  }

  /**
   * Get voice details by ID.
   * 
   * @param voiceId - Voice identifier
   */
  async getVoice(voiceId: string): Promise<Voice> {
    const result = await this.request<Voice>('GET', `/api/v1/voices/${voiceId}`);
    if (!result) {
      throw new VoiceNotFoundError(voiceId);
    }
    return result;
  }

  // Speech Synthesis

  /**
   * Synthesize speech from text.
   * 
   * @param text - Text to synthesize
   * @param voiceId - Voice ID to use
   * @param options - Additional synthesis options
   */
  async synthesize(
    text: string,
    voiceId: string,
    options: Partial<SynthesisOptions> = {}
  ): Promise<AudioResult> {
    const requestData = {
      text,
      voiceId,
      format: options.format || OutputFormat.WAV,
      speed: options.speed || 1.0,
      pitch: options.pitch || 0.0,
      energy: options.energy || 1.0,
      ...options,
    };

    const audioData = await this.requestBinary('POST', '/api/v1/synthesize', requestData);

    return {
      audioData,
      sampleRate: options.sampleRate || 22050,
      format: options.format || OutputFormat.WAV,
      durationSeconds: audioData.byteLength / ((options.sampleRate || 22050) * 2),
      voiceId,
      text,
      metadata: {},
    };
  }

  /**
   * Stream synthesized speech.
   * 
   * @param text - Text to synthesize
   * @param voiceId - Voice ID to use
   * @param options - Synthesis options
   */
  async *synthesizeStream(
    text: string,
    voiceId: string,
    options: Partial<SynthesisOptions> = {}
  ): AsyncGenerator<Uint8Array> {
    const url = `${this.baseUrl}/api/v1/synthesize/stream`;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    const requestData = {
      text,
      voiceId,
      stream: true,
      ...options,
    };

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new SynthesisError(`Synthesis failed: ${errorText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new SynthesisError('Stream not available');
    }

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        yield value;
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * Batch synthesize multiple texts.
   * 
   * @param items - Array of synthesis requests
   */
  async synthesizeBatch(
    items: Array<{ text: string; voiceId: string; options?: Partial<SynthesisOptions> }>
  ): Promise<AudioResult[]> {
    const results: AudioResult[] = [];

    for (const item of items) {
      const result = await this.synthesize(item.text, item.voiceId, item.options);
      results.push(result);
    }

    return results;
  }

  // Voice Cloning

  /**
   * Clone a voice from audio samples.
   * 
   * @param name - Name for the cloned voice
   * @param audioFiles - Array of audio file Blobs
   * @param options - Cloning options
   */
  async cloneVoice(
    name: string,
    audioFiles: Blob[],
    options: {
      description?: string;
      engine?: SynthesisEngine;
    } = {}
  ): Promise<CloneResult> {
    const formData = new FormData();
    formData.append('name', name);
    formData.append('engine', options.engine || SynthesisEngine.XTTS);

    if (options.description) {
      formData.append('description', options.description);
    }

    audioFiles.forEach((file, index) => {
      formData.append('audio_files', file, `audio_${index}.wav`);
    });

    const url = `${this.baseUrl}/api/v1/voices/clone`;

    const headers: Record<string, string> = {};
    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new VoiceStudioError(`Cloning failed: ${errorText}`, response.status);
    }

    return response.json();
  }

  /**
   * Delete a cloned voice.
   * 
   * @param voiceId - Voice ID to delete
   */
  async deleteVoice(voiceId: string): Promise<boolean> {
    const result = await this.request<{ success: boolean }>(
      'DELETE',
      `/api/v1/voices/${voiceId}`
    );
    return result.success || false;
  }

  // Emotion Control

  /**
   * Synthesize speech with emotion.
   * 
   * @param text - Text to synthesize
   * @param voiceId - Voice ID to use
   * @param emotion - Emotion name
   * @param intensity - Emotion intensity (0.0-1.0)
   */
  async synthesizeWithEmotion(
    text: string,
    voiceId: string,
    emotion: string,
    intensity: number = 0.5
  ): Promise<AudioResult> {
    return this.synthesize(text, voiceId, {
      emotion,
      emotionIntensity: intensity,
    });
  }
}

// Browser helpers

/**
 * Play audio result in browser.
 * 
 * @param audio - Audio result to play
 */
export async function playAudio(audio: AudioResult): Promise<void> {
  const blob = new Blob([audio.audioData], { type: `audio/${audio.format}` });
  const url = URL.createObjectURL(blob);
  
  const audioElement = new Audio(url);
  
  return new Promise((resolve, reject) => {
    audioElement.onended = () => {
      URL.revokeObjectURL(url);
      resolve();
    };
    audioElement.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error('Audio playback failed'));
    };
    audioElement.play().catch(reject);
  });
}

/**
 * Download audio result as file.
 * 
 * @param audio - Audio result to download
 * @param filename - Filename for download
 */
export function downloadAudio(audio: AudioResult, filename: string = 'audio.wav'): void {
  const blob = new Blob([audio.audioData], { type: `audio/${audio.format}` });
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  
  URL.revokeObjectURL(url);
}

// Default export
export default VoiceStudioClient;
