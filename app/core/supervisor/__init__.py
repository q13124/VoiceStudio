"""
Hybrid Supervisor Package for VoiceStudio (Phase 11)

Implements intelligent routing between Speech-to-Speech (S2S),
Cascade (STT → LLM → TTS), and Half-Cascade pipelines based on
conversation complexity, intent, and cost constraints.

Components:
- SupervisorRouter: Main routing logic
- IntentClassifier: Classifies user input complexity
- SupervisorStateMachine: Manages supervisor state transitions
- FillerPhraseGenerator: Generates filler phrases during handoffs
- ContextSync: Preserves context across pipeline switches
- BargeInHandler: Handles user interruptions
- IntentBuffer: Buffers cooperative interruptions
- InterruptionFSM: Classifies interruption types
"""

from .barge_in import BargeInHandler
from .classifier import ClassificationResult, ComplexityLevel, IntentClassifier
from .context_sync import ContextSync, ConversationTurn
from .filler_generator import FillerPhraseGenerator
from .intent_buffer import BufferedUtterance, IntentBuffer
from .interruption_fsm import InterruptionAction, InterruptionFSM, InterruptionType
from .router import SupervisorRouter
from .state_machine import SupervisorState, SupervisorStateMachine

__all__ = [
    # Interruption handling
    "BargeInHandler",
    "BufferedUtterance",
    "ClassificationResult",
    "ComplexityLevel",
    # Context preservation
    "ContextSync",
    "ConversationTurn",
    # Filler phrases
    "FillerPhraseGenerator",
    "IntentBuffer",
    # Classification
    "IntentClassifier",
    "InterruptionAction",
    "InterruptionFSM",
    "InterruptionType",
    # Core components
    "SupervisorRouter",
    "SupervisorState",
    "SupervisorStateMachine",
]
