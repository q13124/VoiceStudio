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

from .state_machine import SupervisorState, SupervisorStateMachine
from .classifier import IntentClassifier, ClassificationResult, ComplexityLevel
from .router import SupervisorRouter
from .filler_generator import FillerPhraseGenerator
from .context_sync import ContextSync, ConversationTurn
from .barge_in import BargeInHandler
from .intent_buffer import IntentBuffer, BufferedUtterance
from .interruption_fsm import InterruptionFSM, InterruptionType, InterruptionAction

__all__ = [
    # Core components
    "SupervisorRouter",
    "SupervisorState",
    "SupervisorStateMachine",
    # Classification
    "IntentClassifier",
    "ClassificationResult",
    "ComplexityLevel",
    # Filler phrases
    "FillerPhraseGenerator",
    # Context preservation
    "ContextSync",
    "ConversationTurn",
    # Interruption handling
    "BargeInHandler",
    "IntentBuffer",
    "BufferedUtterance",
    "InterruptionFSM",
    "InterruptionType",
    "InterruptionAction",
]
