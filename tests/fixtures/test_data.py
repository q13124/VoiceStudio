"""
VoiceStudio Test Data Fixtures.

Comprehensive test data for all test scenarios including:
- Text samples for synthesis
- SSML markup examples
- Multi-language content
- Voice profile configurations
- Effect presets
- Training configurations
- Workflow scenarios
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# =============================================================================
# TEXT SAMPLES
# =============================================================================


@dataclass
class TextSample:
    """Text sample for synthesis testing."""

    id: str
    text: str
    language: str
    category: str
    expected_duration_range: tuple = (0.5, 30.0)  # seconds
    description: str = ""


TEXT_SAMPLES: list[TextSample] = [
    # Short phrases (< 2 seconds)
    TextSample("short_greeting", "Hello there!", "en", "short", (0.5, 2.0), "Basic greeting"),
    TextSample("short_number", "One two three four five.", "en", "short", (1.0, 3.0), "Numbers"),
    TextSample("short_question", "How are you today?", "en", "short", (0.8, 2.5), "Question"),
    TextSample("short_exclaim", "Wow, that's amazing!", "en", "short", (0.8, 2.5), "Exclamation"),
    # Medium phrases (2-10 seconds)
    TextSample(
        "medium_sentence",
        "The quick brown fox jumps over the lazy dog near the riverbank.",
        "en",
        "medium",
        (2.0, 8.0),
        "Pangram",
    ),
    TextSample(
        "medium_paragraph",
        "Welcome to VoiceStudio, the comprehensive voice synthesis and cloning platform. "
        "We provide high-quality text-to-speech capabilities across multiple engines.",
        "en",
        "medium",
        (5.0, 15.0),
        "Product description",
    ),
    TextSample(
        "medium_technical",
        "The neural network architecture consists of multiple transformer layers with "
        "self-attention mechanisms for improved prosody and naturalness.",
        "en",
        "medium",
        (4.0, 12.0),
        "Technical content",
    ),
    # Long content (> 10 seconds)
    TextSample(
        "long_story",
        "Once upon a time, in a land far away, there lived a young inventor who dreamed of "
        "creating machines that could talk. Day after day, she worked in her small workshop, "
        "surrounded by gears, wires, and ancient books. Her neighbors thought she was eccentric, "
        "but she knew that someday her creation would change the world forever.",
        "en",
        "long",
        (15.0, 45.0),
        "Narrative story",
    ),
    TextSample(
        "long_article",
        "Artificial intelligence has made remarkable progress in recent years, particularly "
        "in the field of speech synthesis. Modern text-to-speech systems can now produce output "
        "that is nearly indistinguishable from human speech. These advances are powered by deep "
        "learning techniques, large datasets, and sophisticated neural architectures. Applications "
        "range from accessibility tools to entertainment and professional voice-over work.",
        "en",
        "long",
        (20.0, 60.0),
        "Article excerpt",
    ),
    # Edge cases
    TextSample("edge_empty", "", "en", "edge", (0.0, 0.1), "Empty string"),
    TextSample("edge_single", "A", "en", "edge", (0.1, 1.0), "Single character"),
    TextSample("edge_numbers", "123456789", "en", "edge", (1.0, 5.0), "Pure numbers"),
    TextSample(
        "edge_special",
        "Hello... world! How? Why? What?!",
        "en",
        "edge",
        (1.5, 5.0),
        "Special chars",
    ),
    TextSample(
        "edge_unicode", "Hello café résumé naïve", "en", "edge", (1.5, 5.0), "Unicode chars"
    ),
    TextSample(
        "edge_quotes", '"Hello," she said. "How are you?"', "en", "edge", (2.0, 6.0), "Quotes"
    ),
    TextSample(
        "edge_newlines",
        "First line.\nSecond line.\nThird line.",
        "en",
        "edge",
        (2.0, 8.0),
        "Newlines",
    ),
    TextSample("edge_tabs", "Column1\tColumn2\tColumn3", "en", "edge", (2.0, 6.0), "Tabs"),
]


# =============================================================================
# SSML TEST CASES
# =============================================================================


@dataclass
class SSMLSample:
    """SSML markup sample for testing."""

    id: str
    ssml: str
    category: str
    description: str
    expected_features: list[str] = field(default_factory=list)


SSML_SAMPLES: list[SSMLSample] = [
    # Basic SSML
    SSMLSample(
        "ssml_basic", "<speak>Hello, this is a test.</speak>", "basic", "Basic speak tag", ["speak"]
    ),
    # Prosody controls
    SSMLSample(
        "ssml_rate_slow",
        '<speak><prosody rate="slow">This is spoken slowly.</prosody></speak>',
        "prosody",
        "Slow speech rate",
        ["prosody", "rate"],
    ),
    SSMLSample(
        "ssml_rate_fast",
        '<speak><prosody rate="fast">This is spoken quickly.</prosody></speak>',
        "prosody",
        "Fast speech rate",
        ["prosody", "rate"],
    ),
    SSMLSample(
        "ssml_pitch_high",
        '<speak><prosody pitch="high">This has a higher pitch.</prosody></speak>',
        "prosody",
        "High pitch",
        ["prosody", "pitch"],
    ),
    SSMLSample(
        "ssml_pitch_low",
        '<speak><prosody pitch="low">This has a lower pitch.</prosody></speak>',
        "prosody",
        "Low pitch",
        ["prosody", "pitch"],
    ),
    SSMLSample(
        "ssml_volume",
        '<speak><prosody volume="loud">This is loud.</prosody> '
        '<prosody volume="soft">This is soft.</prosody></speak>',
        "prosody",
        "Volume variations",
        ["prosody", "volume"],
    ),
    # Breaks and pauses
    SSMLSample(
        "ssml_break_time",
        '<speak>First part.<break time="500ms"/>Second part.</speak>',
        "timing",
        "Timed break",
        ["break", "time"],
    ),
    SSMLSample(
        "ssml_break_strength",
        '<speak>Hello.<break strength="strong"/>Goodbye.</speak>',
        "timing",
        "Strength break",
        ["break", "strength"],
    ),
    # Emphasis
    SSMLSample(
        "ssml_emphasis_strong",
        '<speak>This is <emphasis level="strong">very important</emphasis>.</speak>',
        "emphasis",
        "Strong emphasis",
        ["emphasis"],
    ),
    SSMLSample(
        "ssml_emphasis_reduced",
        '<speak>The <emphasis level="reduced">small</emphasis> detail matters.</speak>',
        "emphasis",
        "Reduced emphasis",
        ["emphasis"],
    ),
    # Say-as interpretations
    SSMLSample(
        "ssml_sayas_date",
        '<speak>The date is <say-as interpret-as="date">2024-01-15</say-as>.</speak>',
        "interpretation",
        "Date interpretation",
        ["say-as", "date"],
    ),
    SSMLSample(
        "ssml_sayas_time",
        '<speak>The time is <say-as interpret-as="time">14:30</say-as>.</speak>',
        "interpretation",
        "Time interpretation",
        ["say-as", "time"],
    ),
    SSMLSample(
        "ssml_sayas_cardinal",
        '<speak>There are <say-as interpret-as="cardinal">42</say-as> items.</speak>',
        "interpretation",
        "Cardinal number",
        ["say-as", "cardinal"],
    ),
    SSMLSample(
        "ssml_sayas_ordinal",
        '<speak>This is the <say-as interpret-as="ordinal">3</say-as> time.</speak>',
        "interpretation",
        "Ordinal number",
        ["say-as", "ordinal"],
    ),
    SSMLSample(
        "ssml_sayas_spell",
        '<speak>Spell it: <say-as interpret-as="characters">AI</say-as>.</speak>',
        "interpretation",
        "Spell out",
        ["say-as", "characters"],
    ),
    SSMLSample(
        "ssml_sayas_telephone",
        '<speak>Call <say-as interpret-as="telephone">555-1234</say-as>.</speak>',
        "interpretation",
        "Telephone number",
        ["say-as", "telephone"],
    ),
    # Phoneme pronunciations
    SSMLSample(
        "ssml_phoneme_ipa",
        '<speak>I live in <phoneme alphabet="ipa" ph="ˈniːvɑdə">Nevada</phoneme>.</speak>',
        "pronunciation",
        "IPA phoneme",
        ["phoneme", "ipa"],
    ),
    # Sub (substitution)
    SSMLSample(
        "ssml_sub",
        '<speak><sub alias="World Wide Web Consortium">W3C</sub> standards.</speak>',
        "substitution",
        "Alias substitution",
        ["sub", "alias"],
    ),
    # Complex combinations
    SSMLSample(
        "ssml_complex",
        "<speak>"
        '<prosody rate="slow" pitch="+10%">'
        'Welcome to <emphasis level="strong">VoiceStudio</emphasis>.'
        "</prosody>"
        '<break time="1s"/>'
        '<prosody rate="medium">'
        'Today is <say-as interpret-as="date">2024-02-13</say-as>.'
        "</prosody>"
        "</speak>",
        "complex",
        "Multiple SSML features combined",
        ["prosody", "emphasis", "break", "say-as"],
    ),
    # Edge cases
    SSMLSample(
        "ssml_nested",
        '<speak><prosody rate="slow"><emphasis level="strong">Important</emphasis></prosody></speak>',
        "edge",
        "Nested tags",
        ["prosody", "emphasis"],
    ),
    SSMLSample("ssml_empty_speak", "<speak></speak>", "edge", "Empty speak tag", ["speak"]),
    SSMLSample(
        "ssml_whitespace",
        "<speak>  Text with   extra   spaces  </speak>",
        "edge",
        "Extra whitespace",
        ["speak"],
    ),
]


# =============================================================================
# MULTI-LANGUAGE CONTENT
# =============================================================================


@dataclass
class LanguageSample:
    """Multi-language text sample."""

    id: str
    language_code: str
    language_name: str
    native_name: str
    samples: list[dict[str, str]]  # {"category": ..., "text": ...}
    script: str = "Latin"


LANGUAGE_SAMPLES: list[LanguageSample] = [
    # English (US)
    LanguageSample(
        "lang_en_us",
        "en-US",
        "English (US)",
        "English",
        [
            {"category": "greeting", "text": "Hello, how are you today?"},
            {"category": "farewell", "text": "Goodbye, see you later!"},
            {"category": "question", "text": "What time is it?"},
            {"category": "numbers", "text": "One, two, three, four, five."},
            {"category": "paragraph", "text": "The quick brown fox jumps over the lazy dog."},
        ],
    ),
    # English (UK)
    LanguageSample(
        "lang_en_gb",
        "en-GB",
        "English (UK)",
        "English",
        [
            {"category": "greeting", "text": "Good morning, how are you?"},
            {"category": "farewell", "text": "Cheerio, take care!"},
            {"category": "question", "text": "What is the time?"},
            {"category": "paragraph", "text": "The colour of the centre is grey, not gray."},
        ],
    ),
    # Spanish
    LanguageSample(
        "lang_es",
        "es-ES",
        "Spanish",
        "Español",
        [
            {"category": "greeting", "text": "Hola, ¿cómo estás?"},
            {"category": "farewell", "text": "Adiós, hasta luego."},
            {"category": "question", "text": "¿Qué hora es?"},
            {"category": "numbers", "text": "Uno, dos, tres, cuatro, cinco."},
            {
                "category": "paragraph",
                "text": "El rápido zorro marrón salta sobre el perro perezoso.",
            },
        ],
    ),
    # French
    LanguageSample(
        "lang_fr",
        "fr-FR",
        "French",
        "Français",
        [
            {"category": "greeting", "text": "Bonjour, comment allez-vous?"},
            {"category": "farewell", "text": "Au revoir, à bientôt!"},
            {"category": "question", "text": "Quelle heure est-il?"},
            {"category": "numbers", "text": "Un, deux, trois, quatre, cinq."},
            {
                "category": "paragraph",
                "text": "Le renard brun rapide saute par-dessus le chien paresseux.",
            },
        ],
    ),
    # German
    LanguageSample(
        "lang_de",
        "de-DE",
        "German",
        "Deutsch",
        [
            {"category": "greeting", "text": "Guten Tag, wie geht es Ihnen?"},
            {"category": "farewell", "text": "Auf Wiedersehen!"},
            {"category": "question", "text": "Wie spät ist es?"},
            {"category": "numbers", "text": "Eins, zwei, drei, vier, fünf."},
            {
                "category": "paragraph",
                "text": "Der schnelle braune Fuchs springt über den faulen Hund.",
            },
        ],
    ),
    # Italian
    LanguageSample(
        "lang_it",
        "it-IT",
        "Italian",
        "Italiano",
        [
            {"category": "greeting", "text": "Ciao, come stai?"},
            {"category": "farewell", "text": "Arrivederci!"},
            {"category": "question", "text": "Che ore sono?"},
            {"category": "numbers", "text": "Uno, due, tre, quattro, cinque."},
        ],
    ),
    # Portuguese (Brazil)
    LanguageSample(
        "lang_pt_br",
        "pt-BR",
        "Portuguese (Brazil)",
        "Português",
        [
            {"category": "greeting", "text": "Olá, como você está?"},
            {"category": "farewell", "text": "Tchau, até logo!"},
            {"category": "question", "text": "Que horas são?"},
            {"category": "numbers", "text": "Um, dois, três, quatro, cinco."},
        ],
    ),
    # Dutch
    LanguageSample(
        "lang_nl",
        "nl-NL",
        "Dutch",
        "Nederlands",
        [
            {"category": "greeting", "text": "Hallo, hoe gaat het?"},
            {"category": "farewell", "text": "Tot ziens!"},
            {"category": "question", "text": "Hoe laat is het?"},
            {"category": "numbers", "text": "Een, twee, drie, vier, vijf."},
        ],
    ),
    # Polish
    LanguageSample(
        "lang_pl",
        "pl-PL",
        "Polish",
        "Polski",
        [
            {"category": "greeting", "text": "Cześć, jak się masz?"},
            {"category": "farewell", "text": "Do widzenia!"},
            {"category": "question", "text": "Która jest godzina?"},
            {"category": "numbers", "text": "Jeden, dwa, trzy, cztery, pięć."},
        ],
    ),
    # Russian
    LanguageSample(
        "lang_ru",
        "ru-RU",
        "Russian",
        "Русский",
        [
            {"category": "greeting", "text": "Привет, как дела?"},
            {"category": "farewell", "text": "До свидания!"},
            {"category": "question", "text": "Который час?"},
            {"category": "numbers", "text": "Один, два, три, четыре, пять."},
        ],
        script="Cyrillic",
    ),
    # Japanese
    LanguageSample(
        "lang_ja",
        "ja-JP",
        "Japanese",
        "日本語",
        [
            {"category": "greeting", "text": "こんにちは、お元気ですか?"},
            {"category": "farewell", "text": "さようなら!"},
            {"category": "question", "text": "今何時ですか?"},
            {"category": "numbers", "text": "一、二、三、四、五。"},
        ],
        script="Japanese",
    ),
    # Chinese (Mandarin)
    LanguageSample(
        "lang_zh",
        "zh-CN",
        "Chinese (Mandarin)",
        "中文",
        [
            {"category": "greeting", "text": "你好，你好吗?"},
            {"category": "farewell", "text": "再见!"},
            {"category": "question", "text": "现在几点?"},
            {"category": "numbers", "text": "一、二、三、四、五。"},
        ],
        script="Chinese",
    ),
    # Korean
    LanguageSample(
        "lang_ko",
        "ko-KR",
        "Korean",
        "한국어",
        [
            {"category": "greeting", "text": "안녕하세요, 어떻게 지내세요?"},
            {"category": "farewell", "text": "안녕히 가세요!"},
            {"category": "question", "text": "지금 몇 시예요?"},
            {"category": "numbers", "text": "하나, 둘, 셋, 넷, 다섯."},
        ],
        script="Korean",
    ),
    # Arabic
    LanguageSample(
        "lang_ar",
        "ar-SA",
        "Arabic",
        "العربية",
        [
            {"category": "greeting", "text": "مرحبا، كيف حالك؟"},
            {"category": "farewell", "text": "مع السلامة!"},
            {"category": "question", "text": "كم الساعة؟"},
            {"category": "numbers", "text": "واحد، اثنان، ثلاثة، أربعة، خمسة."},
        ],
        script="Arabic",
    ),
    # Hindi
    LanguageSample(
        "lang_hi",
        "hi-IN",
        "Hindi",
        "हिन्दी",
        [
            {"category": "greeting", "text": "नमस्ते, आप कैसे हैं?"},
            {"category": "farewell", "text": "अलविदा!"},
            {"category": "question", "text": "क्या समय हुआ है?"},
            {"category": "numbers", "text": "एक, दो, तीन, चार, पाँच।"},
        ],
        script="Devanagari",
    ),
    # Turkish
    LanguageSample(
        "lang_tr",
        "tr-TR",
        "Turkish",
        "Türkçe",
        [
            {"category": "greeting", "text": "Merhaba, nasılsınız?"},
            {"category": "farewell", "text": "Güle güle!"},
            {"category": "question", "text": "Saat kaç?"},
            {"category": "numbers", "text": "Bir, iki, üç, dört, beş."},
        ],
    ),
]


# =============================================================================
# VOICE PROFILE CONFIGURATIONS
# =============================================================================


@dataclass
class VoiceProfileConfig:
    """Voice profile configuration for testing."""

    id: str
    name: str
    engine: str
    voice_id: str
    language: str
    settings: dict[str, Any]
    description: str = ""


VOICE_PROFILES: list[VoiceProfileConfig] = [
    # Piper profiles
    VoiceProfileConfig(
        "profile_piper_default",
        "Piper Default",
        "piper",
        "en_US-amy-medium",
        "en-US",
        {"speed": 1.0, "pitch": 0},
        "Default Piper voice",
    ),
    VoiceProfileConfig(
        "profile_piper_slow",
        "Piper Slow",
        "piper",
        "en_US-amy-medium",
        "en-US",
        {"speed": 0.75, "pitch": 0},
        "Slow speaking rate",
    ),
    VoiceProfileConfig(
        "profile_piper_fast",
        "Piper Fast",
        "piper",
        "en_US-amy-medium",
        "en-US",
        {"speed": 1.5, "pitch": 0},
        "Fast speaking rate",
    ),
    # XTTS profiles
    VoiceProfileConfig(
        "profile_xtts_default",
        "XTTS Default",
        "xtts",
        "default",
        "en",
        {"temperature": 0.7, "top_k": 50},
        "Default XTTS settings",
    ),
    VoiceProfileConfig(
        "profile_xtts_creative",
        "XTTS Creative",
        "xtts",
        "default",
        "en",
        {"temperature": 0.9, "top_k": 75},
        "Higher variation",
    ),
    VoiceProfileConfig(
        "profile_xtts_precise",
        "XTTS Precise",
        "xtts",
        "default",
        "en",
        {"temperature": 0.3, "top_k": 25},
        "Lower variation",
    ),
    # Bark profiles
    VoiceProfileConfig(
        "profile_bark_default",
        "Bark Default",
        "bark",
        "v2/en_speaker_6",
        "en",
        {"semantic_temperature": 0.7, "coarse_temperature": 0.7},
        "Default Bark",
    ),
    # OpenVoice profiles
    VoiceProfileConfig(
        "profile_openvoice_default",
        "OpenVoice Default",
        "openvoice",
        "default",
        "en",
        {"accent": "en-default"},
        "Default OpenVoice",
    ),
    # Chatterbox profiles
    VoiceProfileConfig(
        "profile_chatterbox_default",
        "Chatterbox Default",
        "chatterbox",
        "default",
        "en",
        {},
        "Default Chatterbox",
    ),
]


# =============================================================================
# EFFECT PRESETS
# =============================================================================


@dataclass
class EffectPreset:
    """Audio effect preset configuration."""

    id: str
    name: str
    category: str
    effects: list[dict[str, Any]]
    description: str = ""


EFFECT_PRESETS: list[EffectPreset] = [
    # No effects
    EffectPreset("preset_bypass", "Bypass", "utility", [], "No effects applied"),
    # Basic presets
    EffectPreset(
        "preset_normalize",
        "Normalize",
        "mastering",
        [{"type": "normalize", "target_level": -3.0}],
        "Normalize audio levels",
    ),
    EffectPreset(
        "preset_compress",
        "Light Compression",
        "dynamics",
        [{"type": "compressor", "threshold": -20, "ratio": 3, "attack": 10, "release": 100}],
        "Light dynamic compression",
    ),
    # Voice enhancement
    EffectPreset(
        "preset_voice_enhance",
        "Voice Enhance",
        "voice",
        [
            {"type": "equalizer", "low_cut": 80, "presence_boost": 3},
            {"type": "compressor", "threshold": -18, "ratio": 4},
            {"type": "limiter", "threshold": -1},
        ],
        "Enhance voice clarity",
    ),
    EffectPreset(
        "preset_noise_reduction",
        "Noise Reduction",
        "voice",
        [
            {"type": "noise_gate", "threshold": -40, "attack": 5, "release": 50},
            {"type": "noise_reduction", "amount": 0.5},
        ],
        "Reduce background noise",
    ),
    # Creative presets
    EffectPreset(
        "preset_radio",
        "Radio Voice",
        "creative",
        [
            {"type": "equalizer", "low_cut": 300, "high_cut": 3000},
            {"type": "distortion", "amount": 0.1},
            {"type": "compressor", "threshold": -15, "ratio": 8},
        ],
        "Radio/telephone effect",
    ),
    EffectPreset(
        "preset_reverb_hall",
        "Hall Reverb",
        "creative",
        [
            {"type": "reverb", "room_size": 0.8, "damping": 0.5, "wet": 0.3},
        ],
        "Large hall reverb",
    ),
    EffectPreset(
        "preset_reverb_room",
        "Room Reverb",
        "creative",
        [
            {"type": "reverb", "room_size": 0.3, "damping": 0.7, "wet": 0.2},
        ],
        "Small room reverb",
    ),
    # Mastering chain
    EffectPreset(
        "preset_master",
        "Mastering Chain",
        "mastering",
        [
            {"type": "equalizer", "low_shelf": 2, "high_shelf": 1},
            {"type": "compressor", "threshold": -16, "ratio": 2.5, "attack": 20, "release": 200},
            {"type": "limiter", "threshold": -1, "release": 100},
            {"type": "normalize", "target_level": -1},
        ],
        "Full mastering chain",
    ),
]


# =============================================================================
# TRAINING CONFIGURATIONS
# =============================================================================


@dataclass
class TrainingConfig:
    """Voice model training configuration."""

    id: str
    name: str
    model_type: str
    epochs: int
    batch_size: int
    learning_rate: float
    settings: dict[str, Any]
    description: str = ""


TRAINING_CONFIGS: list[TrainingConfig] = [
    TrainingConfig(
        "train_xtts_quick",
        "XTTS Quick",
        "xtts",
        5,
        4,
        5e-5,
        {"warmup_steps": 50, "grad_accum": 2},
        "Quick XTTS fine-tuning",
    ),
    TrainingConfig(
        "train_xtts_standard",
        "XTTS Standard",
        "xtts",
        20,
        8,
        1e-5,
        {"warmup_steps": 200, "grad_accum": 4},
        "Standard XTTS training",
    ),
    TrainingConfig(
        "train_xtts_quality",
        "XTTS Quality",
        "xtts",
        50,
        4,
        5e-6,
        {"warmup_steps": 500, "grad_accum": 8},
        "High quality XTTS training",
    ),
    TrainingConfig(
        "train_rvc_quick",
        "RVC Quick",
        "rvc",
        100,
        8,
        1e-4,
        {"pitch_guidance": True, "crepe_hop": 160},
        "Quick RVC training",
    ),
    TrainingConfig(
        "train_rvc_standard",
        "RVC Standard",
        "rvc",
        500,
        16,
        1e-4,
        {"pitch_guidance": True, "crepe_hop": 128},
        "Standard RVC training",
    ),
]


# =============================================================================
# WORKFLOW SCENARIOS
# =============================================================================


@dataclass
class WorkflowStep:
    """Single step in a workflow."""

    action: str
    params: dict[str, Any]
    expected_result: str
    timeout_seconds: int = 30


@dataclass
class WorkflowScenario:
    """Complete workflow scenario for testing."""

    id: str
    name: str
    description: str
    category: str
    steps: list[WorkflowStep]
    preconditions: list[str] = field(default_factory=list)
    cleanup: list[str] = field(default_factory=list)


WORKFLOW_SCENARIOS: list[WorkflowScenario] = [
    # Basic synthesis workflow
    WorkflowScenario(
        "wf_basic_synthesis",
        "Basic Synthesis",
        "Simple TTS synthesis",
        "synthesis",
        [
            WorkflowStep("navigate", {"panel": "VoiceSynthesis"}, "Panel loaded"),
            WorkflowStep("select_engine", {"engine": "piper"}, "Engine selected"),
            WorkflowStep("enter_text", {"text": "Hello, this is a test."}, "Text entered"),
            WorkflowStep("click_synthesize", {}, "Synthesis started"),
            WorkflowStep("wait_completion", {"timeout": 30}, "Synthesis complete"),
            WorkflowStep("verify_audio", {"min_duration": 1.0}, "Audio generated"),
        ],
        preconditions=["Backend running", "Piper engine available"],
    ),
    # Voice cloning workflow
    WorkflowScenario(
        "wf_voice_cloning",
        "Voice Cloning",
        "Full voice cloning wizard",
        "cloning",
        [
            WorkflowStep("navigate", {"panel": "VoiceCloningWizard"}, "Wizard opened"),
            WorkflowStep("import_audio", {"path": "fixtures/sample.wav"}, "Audio imported"),
            WorkflowStep("configure_model", {"model": "xtts"}, "Model configured"),
            WorkflowStep("start_cloning", {}, "Cloning started"),
            WorkflowStep("wait_completion", {"timeout": 300}, "Cloning complete"),
            WorkflowStep("verify_profile", {}, "Profile created"),
            WorkflowStep("test_profile", {"text": "Testing cloned voice"}, "Profile works"),
        ],
        preconditions=["Backend running", "XTTS engine available", "Sample audio exists"],
        cleanup=["Delete test profile"],
    ),
    # Transcription workflow
    WorkflowScenario(
        "wf_transcription",
        "Transcription",
        "Speech to text",
        "transcription",
        [
            WorkflowStep("navigate", {"panel": "TranscribeView"}, "Panel loaded"),
            WorkflowStep("import_audio", {"path": "fixtures/sample.wav"}, "Audio imported"),
            WorkflowStep("select_engine", {"engine": "whisper"}, "Engine selected"),
            WorkflowStep("start_transcription", {}, "Transcription started"),
            WorkflowStep("wait_completion", {"timeout": 60}, "Transcription complete"),
            WorkflowStep("verify_text", {"min_length": 10}, "Text extracted"),
        ],
        preconditions=["Backend running", "Whisper engine available"],
    ),
    # Batch processing workflow
    WorkflowScenario(
        "wf_batch_synthesis",
        "Batch Synthesis",
        "Multiple item synthesis",
        "batch",
        [
            WorkflowStep("navigate", {"panel": "BatchProcessing"}, "Panel loaded"),
            WorkflowStep("add_items", {"count": 5}, "Items added"),
            WorkflowStep("configure_batch", {"engine": "piper"}, "Batch configured"),
            WorkflowStep("start_batch", {}, "Batch started"),
            WorkflowStep("monitor_progress", {"interval": 5}, "Progress tracked"),
            WorkflowStep("wait_completion", {"timeout": 120}, "Batch complete"),
            WorkflowStep("verify_outputs", {"count": 5}, "All outputs generated"),
        ],
        preconditions=["Backend running", "Piper engine available"],
    ),
    # Effects processing workflow
    WorkflowScenario(
        "wf_effects",
        "Effects Processing",
        "Apply audio effects",
        "effects",
        [
            WorkflowStep("navigate", {"panel": "EffectsPanel"}, "Panel loaded"),
            WorkflowStep("load_audio", {"path": "fixtures/sample.wav"}, "Audio loaded"),
            WorkflowStep("add_effect", {"type": "equalizer"}, "Effect added"),
            WorkflowStep("configure_effect", {"params": {"low": 2}}, "Effect configured"),
            WorkflowStep("preview_effect", {}, "Preview played"),
            WorkflowStep("apply_effect", {}, "Effect applied"),
            WorkflowStep("export_audio", {"format": "wav"}, "Audio exported"),
        ],
        preconditions=["Backend running"],
    ),
    # Project workflow
    WorkflowScenario(
        "wf_project",
        "Project Management",
        "Full project lifecycle",
        "project",
        [
            WorkflowStep("create_project", {"name": "Test Project"}, "Project created"),
            WorkflowStep("add_audio", {"path": "fixtures/sample.wav"}, "Audio added"),
            WorkflowStep("generate_voice", {"text": "Test"}, "Voice generated"),
            WorkflowStep("add_to_timeline", {}, "Added to timeline"),
            WorkflowStep("save_project", {}, "Project saved"),
            WorkflowStep("close_project", {}, "Project closed"),
            WorkflowStep("open_project", {"name": "Test Project"}, "Project reopened"),
            WorkflowStep("verify_contents", {}, "Contents verified"),
        ],
        preconditions=["Backend running"],
        cleanup=["Delete test project"],
    ),
    # Real-time conversion workflow
    WorkflowScenario(
        "wf_realtime",
        "Real-time Conversion",
        "Live voice conversion",
        "realtime",
        [
            WorkflowStep("navigate", {"panel": "RealTimeConverter"}, "Panel loaded"),
            WorkflowStep("select_profile", {"profile": "default"}, "Profile selected"),
            WorkflowStep("configure_latency", {"mode": "balanced"}, "Latency configured"),
            WorkflowStep("start_conversion", {}, "Conversion started"),
            WorkflowStep("verify_audio_flow", {"duration": 5}, "Audio flowing"),
            WorkflowStep("stop_conversion", {}, "Conversion stopped"),
        ],
        preconditions=["Backend running", "Audio devices available"],
    ),
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_text_samples_by_category(category: str) -> list[TextSample]:
    """Get text samples by category."""
    return [s for s in TEXT_SAMPLES if s.category == category]


def get_ssml_samples_by_category(category: str) -> list[SSMLSample]:
    """Get SSML samples by category."""
    return [s for s in SSML_SAMPLES if s.category == category]


def get_language_sample(language_code: str) -> LanguageSample | None:
    """Get language sample by code."""
    for sample in LANGUAGE_SAMPLES:
        if sample.language_code == language_code:
            return sample
    return None


def get_voice_profiles_by_engine(engine: str) -> list[VoiceProfileConfig]:
    """Get voice profiles by engine."""
    return [p for p in VOICE_PROFILES if p.engine == engine]


def get_effect_presets_by_category(category: str) -> list[EffectPreset]:
    """Get effect presets by category."""
    return [p for p in EFFECT_PRESETS if p.category == category]


def get_workflow_scenarios_by_category(category: str) -> list[WorkflowScenario]:
    """Get workflow scenarios by category."""
    return [w for w in WORKFLOW_SCENARIOS if w.category == category]


def get_all_supported_languages() -> list[str]:
    """Get all supported language codes."""
    return [s.language_code for s in LANGUAGE_SAMPLES]


# =============================================================================
# SUMMARY
# =============================================================================

FIXTURE_SUMMARY = {
    "text_samples": len(TEXT_SAMPLES),
    "ssml_samples": len(SSML_SAMPLES),
    "languages": len(LANGUAGE_SAMPLES),
    "voice_profiles": len(VOICE_PROFILES),
    "effect_presets": len(EFFECT_PRESETS),
    "training_configs": len(TRAINING_CONFIGS),
    "workflow_scenarios": len(WORKFLOW_SCENARIOS),
}


if __name__ == "__main__":
    print("VoiceStudio Test Data Fixtures")
    print("=" * 40)
    for key, count in FIXTURE_SUMMARY.items():
        print(f"  {key}: {count}")
    print("=" * 40)
