# common/errors.py
class VoiceStudioError(Exception): pass
class EngineNotAvailableError(VoiceStudioError): pass
class AudioProcessingError(VoiceStudioError): pass
class PolicyViolationError(VoiceStudioError): pass