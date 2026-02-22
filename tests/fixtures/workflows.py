"""
VoiceStudio Workflow Fixtures.

Complete workflow definitions for end-to-end testing:
- User journey scenarios
- Feature workflow sequences
- Integration test flows
- Regression test cases
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class WorkflowCategory(Enum):
    """Categories for workflow scenarios."""

    SYNTHESIS = "synthesis"
    TRANSCRIPTION = "transcription"
    CLONING = "cloning"
    CONVERSION = "conversion"
    EFFECTS = "effects"
    BATCH = "batch"
    PROJECT = "project"
    TRAINING = "training"
    EXPORT = "export"
    SETTINGS = "settings"
    LIBRARY = "library"
    TIMELINE = "timeline"


class ActionType(Enum):
    """Types of workflow actions."""

    UI_NAVIGATION = "ui_navigation"
    UI_INTERACTION = "ui_interaction"
    UI_INPUT = "ui_input"
    UI_VERIFY = "ui_verify"
    API_REQUEST = "api_request"
    API_VERIFY = "api_verify"
    FILE_OPERATION = "file_operation"
    WAIT = "wait"
    CONDITION = "condition"
    SUBPROCESS = "subprocess"


@dataclass
class WorkflowAction:
    """Single action in a workflow."""

    id: str
    action_type: ActionType
    target: str  # Element ID, API endpoint, or file path
    params: dict[str, Any] = field(default_factory=dict)
    expected_result: str = ""
    timeout_seconds: int = 30
    optional: bool = False
    on_failure: str = "fail"  # fail, skip, retry

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.action_type.value,
            "target": self.target,
            "params": self.params,
            "expected": self.expected_result,
            "timeout": self.timeout_seconds,
            "optional": self.optional,
            "on_failure": self.on_failure,
        }


@dataclass
class WorkflowCheckpoint:
    """Checkpoint in a workflow for verification."""

    id: str
    name: str
    assertions: list[dict[str, Any]]
    screenshot: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "assertions": self.assertions,
            "screenshot": self.screenshot,
        }


@dataclass
class Workflow:
    """Complete workflow definition."""

    id: str
    name: str
    description: str
    category: WorkflowCategory
    actions: list[WorkflowAction]
    checkpoints: list[WorkflowCheckpoint] = field(default_factory=list)
    preconditions: list[str] = field(default_factory=list)
    postconditions: list[str] = field(default_factory=list)
    cleanup_actions: list[WorkflowAction] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    priority: int = 5  # 1-10, higher is more critical
    estimated_duration_seconds: int = 60

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "actions": [a.to_dict() for a in self.actions],
            "checkpoints": [c.to_dict() for c in self.checkpoints],
            "preconditions": self.preconditions,
            "postconditions": self.postconditions,
            "cleanup": [a.to_dict() for a in self.cleanup_actions],
            "tags": self.tags,
            "priority": self.priority,
            "estimated_duration": self.estimated_duration_seconds,
        }


# =============================================================================
# SYNTHESIS WORKFLOWS
# =============================================================================

SYNTHESIS_WORKFLOWS: list[Workflow] = [
    Workflow(
        id="wf_synth_basic",
        name="Basic Text-to-Speech",
        description="Simple TTS synthesis workflow",
        category=WorkflowCategory.SYNTHESIS,
        actions=[
            WorkflowAction(
                "nav_synth",
                ActionType.UI_NAVIGATION,
                "NavSynthesize",
                expected_result="VoiceSynthesisView loaded",
            ),
            WorkflowAction(
                "select_engine",
                ActionType.UI_INTERACTION,
                "VoiceSynthesisView_EngineComboBox",
                {"action": "select", "value": "piper"},
                "Engine selected",
            ),
            WorkflowAction(
                "enter_text",
                ActionType.UI_INPUT,
                "VoiceSynthesisView_TextInput",
                {"text": "Hello, this is a test of the text to speech system."},
                "Text entered",
            ),
            WorkflowAction(
                "click_synth",
                ActionType.UI_INTERACTION,
                "VoiceSynthesisView_SynthesizeButton",
                {"action": "click"},
                "Synthesis started",
            ),
            WorkflowAction(
                "wait_complete",
                ActionType.WAIT,
                "synthesis_progress",
                {"condition": "progress == 100", "max_wait": 30},
                "Synthesis complete",
            ),
            WorkflowAction(
                "verify_audio",
                ActionType.UI_VERIFY,
                "VoiceSynthesisView_PlayButton",
                {"enabled": True},
                "Play button enabled",
            ),
        ],
        checkpoints=[
            WorkflowCheckpoint(
                "cp_panel_loaded",
                "Panel Loaded",
                [{"element": "VoiceSynthesisView_Root", "visible": True}],
                screenshot=True,
            ),
            WorkflowCheckpoint(
                "cp_audio_ready",
                "Audio Ready",
                [{"element": "VoiceSynthesisView_PlayButton", "enabled": True}],
                screenshot=True,
            ),
        ],
        preconditions=["Backend running", "Piper engine available"],
        tags=["smoke", "synthesis", "basic"],
        priority=10,
        estimated_duration_seconds=30,
    ),
    Workflow(
        id="wf_synth_streaming",
        name="Streaming Synthesis",
        description="Real-time streaming TTS synthesis",
        category=WorkflowCategory.SYNTHESIS,
        actions=[
            WorkflowAction("nav_synth", ActionType.UI_NAVIGATION, "NavSynthesize"),
            WorkflowAction(
                "select_xtts",
                ActionType.UI_INTERACTION,
                "VoiceSynthesisView_EngineComboBox",
                {"action": "select", "value": "xtts"},
            ),
            WorkflowAction(
                "enter_text",
                ActionType.UI_INPUT,
                "VoiceSynthesisView_TextInput",
                {"text": "This is a longer text for streaming synthesis testing."},
            ),
            WorkflowAction(
                "click_stream",
                ActionType.UI_INTERACTION,
                "VoiceSynthesisView_StreamButton",
                {"action": "click"},
            ),
            WorkflowAction(
                "verify_streaming", ActionType.UI_VERIFY, "audio_waveform", {"updating": True}
            ),
            WorkflowAction(
                "wait_complete",
                ActionType.WAIT,
                "streaming_status",
                {"condition": "finished", "max_wait": 60},
            ),
        ],
        preconditions=["Backend running", "XTTS engine available"],
        tags=["streaming", "synthesis", "xtts"],
        priority=8,
        estimated_duration_seconds=60,
    ),
    Workflow(
        id="wf_synth_multi_engine",
        name="Multi-Engine Synthesis",
        description="Test synthesis across different engines",
        category=WorkflowCategory.SYNTHESIS,
        actions=[
            WorkflowAction("nav_synth", ActionType.UI_NAVIGATION, "NavSynthesize"),
            # Piper
            WorkflowAction(
                "select_piper",
                ActionType.UI_INTERACTION,
                "EngineComboBox",
                {"action": "select", "value": "piper"},
            ),
            WorkflowAction(
                "synth_piper", ActionType.UI_INTERACTION, "SynthesizeButton", {"action": "click"}
            ),
            WorkflowAction("wait_piper", ActionType.WAIT, "synthesis", {"max_wait": 30}),
            # XTTS
            WorkflowAction(
                "select_xtts",
                ActionType.UI_INTERACTION,
                "EngineComboBox",
                {"action": "select", "value": "xtts"},
            ),
            WorkflowAction(
                "synth_xtts", ActionType.UI_INTERACTION, "SynthesizeButton", {"action": "click"}
            ),
            WorkflowAction("wait_xtts", ActionType.WAIT, "synthesis", {"max_wait": 60}),
            # Bark
            WorkflowAction(
                "select_bark",
                ActionType.UI_INTERACTION,
                "EngineComboBox",
                {"action": "select", "value": "bark"},
                optional=True,
            ),
            WorkflowAction(
                "synth_bark",
                ActionType.UI_INTERACTION,
                "SynthesizeButton",
                {"action": "click"},
                optional=True,
            ),
            WorkflowAction(
                "wait_bark", ActionType.WAIT, "synthesis", {"max_wait": 120}, optional=True
            ),
        ],
        preconditions=["Backend running", "Multiple engines available"],
        tags=["multi-engine", "synthesis", "comprehensive"],
        priority=7,
        estimated_duration_seconds=180,
    ),
]


# =============================================================================
# TRANSCRIPTION WORKFLOWS
# =============================================================================

TRANSCRIPTION_WORKFLOWS: list[Workflow] = [
    Workflow(
        id="wf_transcribe_basic",
        name="Basic Transcription",
        description="Simple speech-to-text transcription",
        category=WorkflowCategory.TRANSCRIPTION,
        actions=[
            WorkflowAction("nav_transcribe", ActionType.UI_NAVIGATION, "NavTranscribe"),
            WorkflowAction(
                "import_audio",
                ActionType.UI_INTERACTION,
                "TranscribeView_ImportButton",
                {"action": "click"},
            ),
            WorkflowAction(
                "select_file",
                ActionType.FILE_OPERATION,
                "file_dialog",
                {"path": "fixtures/audio/sample_speech.wav"},
            ),
            WorkflowAction(
                "select_engine",
                ActionType.UI_INTERACTION,
                "TranscribeView_EngineComboBox",
                {"action": "select", "value": "whisper"},
            ),
            WorkflowAction(
                "start_transcribe",
                ActionType.UI_INTERACTION,
                "TranscribeView_TranscribeButton",
                {"action": "click"},
            ),
            WorkflowAction(
                "wait_complete",
                ActionType.WAIT,
                "transcription_progress",
                {"condition": "complete", "max_wait": 120},
            ),
            WorkflowAction(
                "verify_text", ActionType.UI_VERIFY, "TranscribeView_TextOutput", {"min_length": 10}
            ),
        ],
        checkpoints=[
            WorkflowCheckpoint(
                "cp_audio_loaded",
                "Audio Loaded",
                [{"element": "TranscribeView_AudioWaveform", "visible": True}],
            ),
            WorkflowCheckpoint(
                "cp_text_output",
                "Text Output",
                [{"element": "TranscribeView_TextOutput", "not_empty": True}],
            ),
        ],
        preconditions=["Backend running", "Whisper engine available", "Test audio exists"],
        tags=["transcription", "whisper", "basic"],
        priority=9,
        estimated_duration_seconds=90,
    ),
    Workflow(
        id="wf_transcribe_realtime",
        name="Real-time Transcription",
        description="Live microphone transcription",
        category=WorkflowCategory.TRANSCRIPTION,
        actions=[
            WorkflowAction("nav_transcribe", ActionType.UI_NAVIGATION, "NavTranscribe"),
            WorkflowAction(
                "select_realtime",
                ActionType.UI_INTERACTION,
                "TranscribeView_ModeToggle",
                {"value": "realtime"},
            ),
            WorkflowAction(
                "start_recording",
                ActionType.UI_INTERACTION,
                "TranscribeView_RecordButton",
                {"action": "click"},
            ),
            WorkflowAction("wait_recording", ActionType.WAIT, "recording", {"duration_seconds": 5}),
            WorkflowAction(
                "stop_recording",
                ActionType.UI_INTERACTION,
                "TranscribeView_StopButton",
                {"action": "click"},
            ),
            WorkflowAction(
                "verify_transcription",
                ActionType.UI_VERIFY,
                "TranscribeView_TextOutput",
                {"not_empty": True},
            ),
        ],
        preconditions=["Backend running", "Microphone available"],
        tags=["transcription", "realtime", "microphone"],
        priority=7,
        estimated_duration_seconds=30,
    ),
]


# =============================================================================
# VOICE CLONING WORKFLOWS
# =============================================================================

CLONING_WORKFLOWS: list[Workflow] = [
    Workflow(
        id="wf_clone_wizard",
        name="Voice Cloning Wizard",
        description="Complete voice cloning wizard workflow",
        category=WorkflowCategory.CLONING,
        actions=[
            # Step 1: Import samples
            WorkflowAction("nav_wizard", ActionType.UI_NAVIGATION, "NavVoiceCloning"),
            WorkflowAction(
                "start_wizard", ActionType.UI_INTERACTION, "NewCloningButton", {"action": "click"}
            ),
            WorkflowAction(
                "import_sample",
                ActionType.UI_INTERACTION,
                "ImportSampleButton",
                {"action": "click"},
            ),
            WorkflowAction(
                "select_files",
                ActionType.FILE_OPERATION,
                "file_dialog",
                {
                    "paths": [
                        "fixtures/audio/voice_sample_1.wav",
                        "fixtures/audio/voice_sample_2.wav",
                    ]
                },
            ),
            WorkflowAction("verify_samples", ActionType.UI_VERIFY, "SamplesList", {"count": 2}),
            WorkflowAction(
                "next_step1", ActionType.UI_INTERACTION, "WizardNextButton", {"action": "click"}
            ),
            # Step 2: Configure
            WorkflowAction(
                "select_model",
                ActionType.UI_INTERACTION,
                "ModelTypeComboBox",
                {"action": "select", "value": "xtts"},
            ),
            WorkflowAction(
                "enter_name", ActionType.UI_INPUT, "ProfileNameInput", {"text": "Test Voice Clone"}
            ),
            WorkflowAction(
                "next_step2", ActionType.UI_INTERACTION, "WizardNextButton", {"action": "click"}
            ),
            # Step 3: Process
            WorkflowAction(
                "start_processing",
                ActionType.UI_INTERACTION,
                "StartProcessingButton",
                {"action": "click"},
            ),
            WorkflowAction(
                "wait_processing",
                ActionType.WAIT,
                "cloning_progress",
                {"condition": "complete", "max_wait": 300},
            ),
            WorkflowAction(
                "next_step3", ActionType.UI_INTERACTION, "WizardNextButton", {"action": "click"}
            ),
            # Step 4: Test
            WorkflowAction(
                "test_voice",
                ActionType.UI_INPUT,
                "TestTextInput",
                {"text": "Testing the cloned voice."},
            ),
            WorkflowAction(
                "generate_test",
                ActionType.UI_INTERACTION,
                "GenerateTestButton",
                {"action": "click"},
            ),
            WorkflowAction("wait_test", ActionType.WAIT, "test_synthesis", {"max_wait": 60}),
            WorkflowAction(
                "finish_wizard",
                ActionType.UI_INTERACTION,
                "WizardFinishButton",
                {"action": "click"},
            ),
        ],
        checkpoints=[
            WorkflowCheckpoint(
                "cp_samples_imported",
                "Samples Imported",
                [{"element": "SamplesList", "min_items": 2}],
                screenshot=True,
            ),
            WorkflowCheckpoint(
                "cp_clone_complete",
                "Clone Complete",
                [{"element": "ProcessingStatus", "text": "Complete"}],
                screenshot=True,
            ),
            WorkflowCheckpoint(
                "cp_profile_created",
                "Profile Created",
                [{"api": "/api/profiles", "contains": "Test Voice Clone"}],
            ),
        ],
        preconditions=["Backend running", "XTTS engine available", "Sample audio exists"],
        cleanup_actions=[
            WorkflowAction(
                "cleanup_profile",
                ActionType.API_REQUEST,
                "/api/profiles/delete",
                {"method": "DELETE", "body": {"name": "Test Voice Clone"}},
            ),
        ],
        tags=["cloning", "wizard", "comprehensive"],
        priority=9,
        estimated_duration_seconds=300,
    ),
    Workflow(
        id="wf_clone_quick",
        name="Quick Voice Clone",
        description="Quick single-sample voice cloning",
        category=WorkflowCategory.CLONING,
        actions=[
            WorkflowAction("nav_quick", ActionType.UI_NAVIGATION, "NavQuickClone"),
            WorkflowAction(
                "drop_sample",
                ActionType.UI_INTERACTION,
                "QuickCloneDropZone",
                {"action": "drop", "file": "fixtures/audio/voice_sample.wav"},
            ),
            WorkflowAction(
                "enter_name", ActionType.UI_INPUT, "QuickCloneName", {"text": "Quick Test Clone"}
            ),
            WorkflowAction(
                "start_clone", ActionType.UI_INTERACTION, "QuickCloneButton", {"action": "click"}
            ),
            WorkflowAction("wait_clone", ActionType.WAIT, "cloning", {"max_wait": 180}),
            WorkflowAction(
                "verify_profile",
                ActionType.API_VERIFY,
                "/api/profiles",
                {"contains": "Quick Test Clone"},
            ),
        ],
        preconditions=["Backend running", "XTTS engine available"],
        tags=["cloning", "quick"],
        priority=8,
        estimated_duration_seconds=120,
    ),
]


# =============================================================================
# EFFECTS WORKFLOWS
# =============================================================================

EFFECTS_WORKFLOWS: list[Workflow] = [
    Workflow(
        id="wf_effects_chain",
        name="Effects Chain Processing",
        description="Build and apply audio effect chain",
        category=WorkflowCategory.EFFECTS,
        actions=[
            WorkflowAction("nav_effects", ActionType.UI_NAVIGATION, "NavEffects"),
            WorkflowAction(
                "import_audio",
                ActionType.UI_INTERACTION,
                "EffectsImportButton",
                {"action": "click"},
            ),
            WorkflowAction(
                "select_file",
                ActionType.FILE_OPERATION,
                "file_dialog",
                {"path": "fixtures/audio/sample.wav"},
            ),
            # Add effects
            WorkflowAction(
                "add_eq", ActionType.UI_INTERACTION, "AddEffectButton", {"effect": "equalizer"}
            ),
            WorkflowAction(
                "configure_eq",
                ActionType.UI_INTERACTION,
                "EqualizerControls",
                {"low": 2, "mid": 0, "high": 1},
            ),
            WorkflowAction(
                "add_comp", ActionType.UI_INTERACTION, "AddEffectButton", {"effect": "compressor"}
            ),
            WorkflowAction(
                "configure_comp",
                ActionType.UI_INTERACTION,
                "CompressorControls",
                {"threshold": -18, "ratio": 4},
            ),
            WorkflowAction(
                "add_limit", ActionType.UI_INTERACTION, "AddEffectButton", {"effect": "limiter"}
            ),
            WorkflowAction(
                "configure_limit", ActionType.UI_INTERACTION, "LimiterControls", {"threshold": -1}
            ),
            # Preview and apply
            WorkflowAction(
                "preview", ActionType.UI_INTERACTION, "PreviewButton", {"action": "click"}
            ),
            WorkflowAction(
                "wait_preview", ActionType.WAIT, "preview_playback", {"duration_seconds": 3}
            ),
            WorkflowAction(
                "apply_effects",
                ActionType.UI_INTERACTION,
                "ApplyEffectsButton",
                {"action": "click"},
            ),
            WorkflowAction("wait_apply", ActionType.WAIT, "processing", {"max_wait": 30}),
            WorkflowAction(
                "export", ActionType.UI_INTERACTION, "ExportButton", {"action": "click"}
            ),
        ],
        checkpoints=[
            WorkflowCheckpoint(
                "cp_chain_built",
                "Effects Chain Built",
                [{"element": "EffectsChainList", "min_items": 3}],
            ),
            WorkflowCheckpoint(
                "cp_processed",
                "Audio Processed",
                [{"element": "ProcessedWaveform", "visible": True}],
            ),
        ],
        tags=["effects", "audio-processing"],
        priority=7,
        estimated_duration_seconds=60,
    ),
]


# =============================================================================
# BATCH PROCESSING WORKFLOWS
# =============================================================================

BATCH_WORKFLOWS: list[Workflow] = [
    Workflow(
        id="wf_batch_synthesis",
        name="Batch Synthesis",
        description="Batch TTS synthesis workflow",
        category=WorkflowCategory.BATCH,
        actions=[
            WorkflowAction("nav_batch", ActionType.UI_NAVIGATION, "NavBatch"),
            WorkflowAction(
                "select_synth",
                ActionType.UI_INTERACTION,
                "BatchTypeComboBox",
                {"action": "select", "value": "synthesis"},
            ),
            # Add items
            WorkflowAction("add_item1", ActionType.UI_INTERACTION, "AddBatchItemButton"),
            WorkflowAction(
                "enter_text1",
                ActionType.UI_INPUT,
                "BatchItemText_0",
                {"text": "First item in batch."},
            ),
            WorkflowAction("add_item2", ActionType.UI_INTERACTION, "AddBatchItemButton"),
            WorkflowAction(
                "enter_text2",
                ActionType.UI_INPUT,
                "BatchItemText_1",
                {"text": "Second item in batch."},
            ),
            WorkflowAction("add_item3", ActionType.UI_INTERACTION, "AddBatchItemButton"),
            WorkflowAction(
                "enter_text3",
                ActionType.UI_INPUT,
                "BatchItemText_2",
                {"text": "Third item in batch."},
            ),
            # Configure and run
            WorkflowAction(
                "select_engine",
                ActionType.UI_INTERACTION,
                "BatchEngineComboBox",
                {"action": "select", "value": "piper"},
            ),
            WorkflowAction(
                "start_batch", ActionType.UI_INTERACTION, "StartBatchButton", {"action": "click"}
            ),
            WorkflowAction(
                "wait_batch",
                ActionType.WAIT,
                "batch_progress",
                {"condition": "all_complete", "max_wait": 120},
            ),
            WorkflowAction("verify_outputs", ActionType.UI_VERIFY, "BatchOutputList", {"count": 3}),
        ],
        checkpoints=[
            WorkflowCheckpoint(
                "cp_items_added", "Batch Items Added", [{"element": "BatchItemList", "count": 3}]
            ),
            WorkflowCheckpoint(
                "cp_batch_complete", "Batch Complete", [{"element": "BatchProgress", "value": 100}]
            ),
        ],
        tags=["batch", "synthesis"],
        priority=8,
        estimated_duration_seconds=90,
    ),
]


# =============================================================================
# PROJECT WORKFLOWS
# =============================================================================

PROJECT_WORKFLOWS: list[Workflow] = [
    Workflow(
        id="wf_project_lifecycle",
        name="Project Lifecycle",
        description="Complete project creation, editing, and saving",
        category=WorkflowCategory.PROJECT,
        actions=[
            # Create new project
            WorkflowAction("menu_file", ActionType.UI_INTERACTION, "FileMenu", {"action": "click"}),
            WorkflowAction(
                "new_project", ActionType.UI_INTERACTION, "NewProjectMenuItem", {"action": "click"}
            ),
            WorkflowAction(
                "enter_name", ActionType.UI_INPUT, "ProjectNameInput", {"text": "Test Project"}
            ),
            WorkflowAction(
                "create", ActionType.UI_INTERACTION, "CreateProjectButton", {"action": "click"}
            ),
            # Add content
            WorkflowAction("nav_synth", ActionType.UI_NAVIGATION, "NavSynthesize"),
            WorkflowAction(
                "enter_text", ActionType.UI_INPUT, "TextInput", {"text": "Project test synthesis."}
            ),
            WorkflowAction(
                "synthesize", ActionType.UI_INTERACTION, "SynthesizeButton", {"action": "click"}
            ),
            WorkflowAction("wait_synth", ActionType.WAIT, "synthesis", {"max_wait": 30}),
            WorkflowAction(
                "add_timeline",
                ActionType.UI_INTERACTION,
                "AddToTimelineButton",
                {"action": "click"},
            ),
            # Save project
            WorkflowAction(
                "save_project", ActionType.UI_INTERACTION, "SaveProjectButton", {"action": "click"}
            ),
            WorkflowAction("wait_save", ActionType.WAIT, "save", {"max_wait": 10}),
            # Close and reopen
            WorkflowAction(
                "close_project",
                ActionType.UI_INTERACTION,
                "CloseProjectButton",
                {"action": "click"},
            ),
            WorkflowAction(
                "open_recent",
                ActionType.UI_INTERACTION,
                "RecentProjectsList",
                {"action": "select", "value": "Test Project"},
            ),
            WorkflowAction(
                "verify_content", ActionType.UI_VERIFY, "TimelineClips", {"min_count": 1}
            ),
        ],
        checkpoints=[
            WorkflowCheckpoint(
                "cp_project_created",
                "Project Created",
                [{"element": "ProjectTitle", "text": "Test Project"}],
            ),
            WorkflowCheckpoint(
                "cp_content_added", "Content Added", [{"element": "TimelineClips", "min_count": 1}]
            ),
            WorkflowCheckpoint(
                "cp_project_saved", "Project Saved", [{"element": "SaveStatus", "text": "Saved"}]
            ),
        ],
        cleanup_actions=[
            WorkflowAction(
                "delete_project",
                ActionType.API_REQUEST,
                "/api/projects/delete",
                {"method": "DELETE", "body": {"name": "Test Project"}},
            ),
        ],
        tags=["project", "lifecycle", "comprehensive"],
        priority=9,
        estimated_duration_seconds=120,
    ),
]


# =============================================================================
# TRAINING WORKFLOWS
# =============================================================================

TRAINING_WORKFLOWS: list[Workflow] = [
    Workflow(
        id="wf_training_xtts",
        name="XTTS Model Training",
        description="Complete XTTS model fine-tuning workflow",
        category=WorkflowCategory.TRAINING,
        actions=[
            WorkflowAction("nav_training", ActionType.UI_NAVIGATION, "NavTraining"),
            # Dataset
            WorkflowAction(
                "select_dataset",
                ActionType.UI_INTERACTION,
                "DatasetComboBox",
                {"action": "select", "value": "test_dataset"},
            ),
            WorkflowAction(
                "validate_dataset",
                ActionType.UI_INTERACTION,
                "ValidateDatasetButton",
                {"action": "click"},
            ),
            WorkflowAction("wait_validation", ActionType.WAIT, "validation", {"max_wait": 30}),
            # Configuration
            WorkflowAction(
                "select_model",
                ActionType.UI_INTERACTION,
                "ModelTypeComboBox",
                {"action": "select", "value": "xtts"},
            ),
            WorkflowAction("set_epochs", ActionType.UI_INPUT, "EpochsInput", {"value": "5"}),
            WorkflowAction("set_batch", ActionType.UI_INPUT, "BatchSizeInput", {"value": "4"}),
            # Training
            WorkflowAction(
                "start_training",
                ActionType.UI_INTERACTION,
                "StartTrainingButton",
                {"action": "click"},
            ),
            WorkflowAction(
                "monitor_progress", ActionType.UI_VERIFY, "TrainingProgress", {"updating": True}
            ),
            WorkflowAction(
                "wait_training",
                ActionType.WAIT,
                "training",
                {"condition": "complete", "max_wait": 600},
            ),
            # Verify
            WorkflowAction(
                "verify_model", ActionType.API_VERIFY, "/api/models", {"contains": "trained_model"}
            ),
        ],
        checkpoints=[
            WorkflowCheckpoint(
                "cp_dataset_valid", "Dataset Valid", [{"element": "DatasetStatus", "text": "Valid"}]
            ),
            WorkflowCheckpoint(
                "cp_training_started",
                "Training Started",
                [{"element": "TrainingStatus", "text": "Training"}],
            ),
            WorkflowCheckpoint(
                "cp_training_complete",
                "Training Complete",
                [{"element": "TrainingStatus", "text": "Complete"}],
            ),
        ],
        preconditions=["Backend running", "GPU available", "Dataset exists"],
        tags=["training", "xtts", "comprehensive"],
        priority=6,
        estimated_duration_seconds=600,
    ),
]


# =============================================================================
# COMBINED WORKFLOW LIST
# =============================================================================

ALL_WORKFLOWS: list[Workflow] = (
    SYNTHESIS_WORKFLOWS
    + TRANSCRIPTION_WORKFLOWS
    + CLONING_WORKFLOWS
    + EFFECTS_WORKFLOWS
    + BATCH_WORKFLOWS
    + PROJECT_WORKFLOWS
    + TRAINING_WORKFLOWS
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_workflows_by_category(category: WorkflowCategory) -> list[Workflow]:
    """Get workflows by category."""
    return [w for w in ALL_WORKFLOWS if w.category == category]


def get_workflows_by_tag(tag: str) -> list[Workflow]:
    """Get workflows by tag."""
    return [w for w in ALL_WORKFLOWS if tag in w.tags]


def get_workflows_by_priority(min_priority: int) -> list[Workflow]:
    """Get workflows with priority >= min_priority."""
    return [w for w in ALL_WORKFLOWS if w.priority >= min_priority]


def get_workflow_by_id(workflow_id: str) -> Workflow | None:
    """Get workflow by ID."""
    for workflow in ALL_WORKFLOWS:
        if workflow.id == workflow_id:
            return workflow
    return None


def get_smoke_test_workflows() -> list[Workflow]:
    """Get workflows suitable for smoke testing."""
    return [w for w in ALL_WORKFLOWS if "smoke" in w.tags or w.priority >= 9]


def get_regression_test_workflows() -> list[Workflow]:
    """Get all workflows for regression testing."""
    return sorted(ALL_WORKFLOWS, key=lambda w: -w.priority)


# =============================================================================
# SUMMARY
# =============================================================================

WORKFLOW_SUMMARY = {
    "total_workflows": len(ALL_WORKFLOWS),
    "synthesis": len(SYNTHESIS_WORKFLOWS),
    "transcription": len(TRANSCRIPTION_WORKFLOWS),
    "cloning": len(CLONING_WORKFLOWS),
    "effects": len(EFFECTS_WORKFLOWS),
    "batch": len(BATCH_WORKFLOWS),
    "project": len(PROJECT_WORKFLOWS),
    "training": len(TRAINING_WORKFLOWS),
    "total_actions": sum(len(w.actions) for w in ALL_WORKFLOWS),
    "total_checkpoints": sum(len(w.checkpoints) for w in ALL_WORKFLOWS),
}


if __name__ == "__main__":
    print("VoiceStudio Workflow Fixtures")
    print("=" * 40)
    for key, value in WORKFLOW_SUMMARY.items():
        print(f"  {key}: {value}")
    print("=" * 40)
