"""
Training Page Object for VoiceStudio UI Tests.

Provides automation for the Training panel including:
- Dataset selection
- Model configuration
- Training execution and monitoring
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Optional

from .base_page import BasePage

if TYPE_CHECKING:
    from tests.ui.conftest import WinAppDriverElement


class TrainingPage(BasePage):
    """
    Page object for the Training panel.

    Handles voice model training workflow.
    """

    # Element automation IDs (from automation_ids.py)
    DATASET_SELECTOR = "TrainingView_DatasetSelector"
    MODEL_CONFIG = "TrainingView_ModelConfig"
    TRAIN_BUTTON = "TrainingView_TrainButton"

    @property
    def root_automation_id(self) -> str:
        return "TrainingView_Root"

    @property
    def nav_automation_id(self) -> str:
        return "NavTraining"

    # =========================================================================
    # Dataset Selection
    # =========================================================================

    def select_dataset(self, dataset_name: str) -> bool:
        """
        Select a training dataset.

        Args:
            dataset_name: Name of the dataset to select.

        Returns:
            True if dataset was selected.
        """
        return self.select_combobox_item(self.DATASET_SELECTOR, dataset_name)

    def get_available_datasets(self) -> list[str]:
        """Get list of available dataset names."""
        try:
            selector = self.find_element(self.DATASET_SELECTOR)
            selector.click()
            time.sleep(0.3)

            items = self.driver.find_elements("class name", "ComboBoxItem")
            names = [item.text for item in items if item.text]

            self.driver.press_escape()
            return names
        except RuntimeError:
            return []

    # =========================================================================
    # Training Configuration
    # =========================================================================

    def get_model_config_element(self) -> Optional[WinAppDriverElement]:
        """Get the model configuration element."""
        try:
            return self.find_element(self.MODEL_CONFIG)
        except RuntimeError:
            return None

    # =========================================================================
    # Training Actions
    # =========================================================================

    def start_training(self) -> bool:
        """Click the train button to start training."""
        return self.click_with_retry(self.TRAIN_BUTTON)

    def is_training_enabled(self) -> bool:
        """Check if the train button is enabled."""
        try:
            button = self.find_element(self.TRAIN_BUTTON)
            return button.is_enabled()
        except RuntimeError:
            return False

    # =========================================================================
    # Workflow Convenience
    # =========================================================================

    def configure_and_start_training(
        self,
        dataset_name: str,
        wait_for_start: bool = True
    ) -> bool:
        """
        Configure and start a training run.

        Args:
            dataset_name: Name of the dataset to use.
            wait_for_start: Whether to wait for training to start.

        Returns:
            True if training was started.
        """
        if not self.is_loaded():
            if not self.navigate():
                return False

        if not self.select_dataset(dataset_name):
            return False

        if not self.is_training_enabled():
            return False

        return self.start_training()
