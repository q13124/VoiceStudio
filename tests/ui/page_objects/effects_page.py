"""
Effects Mixer Page Object.

Provides methods for interacting with the audio effects panel.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from .base_page import BasePage

if TYPE_CHECKING:
    pass


class EffectsPage(BasePage):
    """Page object for the Effects Mixer panel."""

    # =========================================================================
    # Automation IDs
    # =========================================================================

    @property
    def root_automation_id(self) -> str:
        return "EffectsMixerView_Root"

    @property
    def nav_automation_id(self) -> str:
        return "NavEffects"

    # Main controls
    MIXER_PRESETS_COMBO = "EffectsMixerView_MixerPresetsComboBox"
    APPLY_BUTTON = "EffectsMixerView_ApplyButton"
    EXPORT_BUTTON = "EffectsMixerView_ExportButton"
    RESET_BUTTON = "EffectsMixerView_ResetMixerButton"

    # Master controls
    MASTER_VOLUME_SLIDER = "EffectsMixerView_MasterVolumeSlider"
    MASTER_MUTE_BUTTON = "EffectsMixerView_MasterMuteButton"

    # Effect channels
    CHANNEL_1_SLIDER = "EffectsMixerView_Channel1Slider"
    CHANNEL_2_SLIDER = "EffectsMixerView_Channel2Slider"
    CHANNEL_3_SLIDER = "EffectsMixerView_Channel3Slider"
    CHANNEL_4_SLIDER = "EffectsMixerView_Channel4Slider"

    # Effect toggles
    REVERB_TOGGLE = "EffectsMixerView_ReverbToggle"
    ECHO_TOGGLE = "EffectsMixerView_EchoToggle"
    EQ_TOGGLE = "EffectsMixerView_EQToggle"
    COMPRESSOR_TOGGLE = "EffectsMixerView_CompressorToggle"

    # Preview controls
    PREVIEW_BUTTON = "EffectsMixerView_PreviewButton"
    STOP_PREVIEW_BUTTON = "EffectsMixerView_StopPreviewButton"

    # Status
    STATUS_TEXT = "EffectsMixerView_StatusText"
    PROGRESS_BAR = "EffectsMixerView_ProgressBar"

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def status_text(self) -> str | None:
        """Get the current status text."""
        return self.get_text(self.STATUS_TEXT)

    @property
    def is_apply_enabled(self) -> bool:
        """Check if the apply button is enabled."""
        try:
            element = self.find_element(self.APPLY_BUTTON, timeout=2)
            return element.is_enabled()
        except RuntimeError:
            return False

    @property
    def is_processing(self) -> bool:
        """Check if effects are being applied."""
        return self.element_exists(self.PROGRESS_BAR)

    # =========================================================================
    # Actions
    # =========================================================================

    def select_preset(self, preset_name: str) -> bool:
        """
        Select an effects preset.

        Args:
            preset_name: Name of the preset to select.

        Returns:
            True if successful.
        """
        return self.select_combobox_item(self.MIXER_PRESETS_COMBO, preset_name)

    def click_apply(self) -> bool:
        """
        Click the apply button.

        Returns:
            True if successful.
        """
        return self.click_with_retry(self.APPLY_BUTTON)

    def click_export(self) -> bool:
        """
        Click the export button.

        Returns:
            True if successful.
        """
        return self.click_with_retry(self.EXPORT_BUTTON)

    def click_reset(self) -> bool:
        """
        Click the reset button.

        Returns:
            True if successful.
        """
        return self.click_with_retry(self.RESET_BUTTON)

    def click_preview(self) -> bool:
        """
        Click the preview button.

        Returns:
            True if successful.
        """
        return self.click_with_retry(self.PREVIEW_BUTTON)

    def click_stop_preview(self) -> bool:
        """
        Click the stop preview button.

        Returns:
            True if successful.
        """
        return self.click_with_retry(self.STOP_PREVIEW_BUTTON)

    def toggle_master_mute(self) -> bool:
        """
        Toggle the master mute button.

        Returns:
            True if successful.
        """
        return self.click_with_retry(self.MASTER_MUTE_BUTTON)

    def toggle_effect(self, effect_name: str) -> bool:
        """
        Toggle an effect on/off.

        Args:
            effect_name: Effect name (reverb, echo, eq, compressor).

        Returns:
            True if successful.
        """
        toggle_ids = {
            "reverb": self.REVERB_TOGGLE,
            "echo": self.ECHO_TOGGLE,
            "eq": self.EQ_TOGGLE,
            "compressor": self.COMPRESSOR_TOGGLE,
        }

        toggle_id = toggle_ids.get(effect_name.lower())
        if not toggle_id:
            return False

        return self.click_with_retry(toggle_id)

    # =========================================================================
    # Workflows
    # =========================================================================

    def apply_preset(
        self, preset_name: str, wait_for_completion: bool = True, timeout: float = 30.0
    ) -> bool:
        """
        Complete workflow to apply a preset.

        Args:
            preset_name: Name of the preset to apply.
            wait_for_completion: Whether to wait for application to complete.
            timeout: Maximum time to wait for completion.

        Returns:
            True if preset applied (and completed if wait_for_completion).
        """
        # Select preset
        if not self.select_preset(preset_name):
            return False

        time.sleep(0.3)

        # Click apply
        if not self.click_apply():
            return False

        if wait_for_completion:
            return self.wait_for_processing_complete(timeout)

        return True

    def wait_for_processing_complete(self, timeout: float = 30.0) -> bool:
        """
        Wait for effects processing to complete.

        Args:
            timeout: Maximum time to wait.

        Returns:
            True if processing completed within timeout.
        """
        start = time.time()
        while time.time() - start < timeout:
            if not self.is_processing:
                return True
            time.sleep(0.5)
        return False

    def verify_elements_present(self) -> dict:
        """
        Verify all critical elements are present.

        Returns:
            Dictionary with element names and their presence status.
        """
        elements = {
            "root": self.root_automation_id,
            "presets_combo": self.MIXER_PRESETS_COMBO,
            "apply_button": self.APPLY_BUTTON,
            "reset_button": self.RESET_BUTTON,
            "master_volume": self.MASTER_VOLUME_SLIDER,
        }

        return {name: self.element_exists(auto_id) for name, auto_id in elements.items()}

    def get_enabled_effects(self) -> list[str]:
        """
        Get list of currently enabled effects.

        Returns:
            List of effect names that are enabled.
        """
        effects = []
        effect_checks = [
            ("reverb", self.REVERB_TOGGLE),
            ("echo", self.ECHO_TOGGLE),
            ("eq", self.EQ_TOGGLE),
            ("compressor", self.COMPRESSOR_TOGGLE),
        ]

        for effect_name, toggle_id in effect_checks:
            try:
                element = self.find_element(toggle_id, timeout=1)
                # Check toggle state (implementation depends on UI)
                if element.get_attribute("Toggle.ToggleState") == "1":
                    effects.append(effect_name)
            except (RuntimeError, AttributeError):
                continue

        return effects
