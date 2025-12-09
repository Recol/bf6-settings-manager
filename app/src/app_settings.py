"""Persistent application settings storage."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class AppSettings:
    """
    Manage persistent application settings using JSON storage.

    Settings are stored in %APPDATA%/BF6SettingsManager/settings.json on Windows.
    """

    def __init__(self):
        """Initialize app settings manager."""
        # Determine settings directory based on platform
        appdata = os.environ.get("APPDATA")
        if appdata:
            self.settings_dir = Path(appdata) / "BF6SettingsManager"
        else:
            # Fallback for non-Windows or WSL
            self.settings_dir = Path.home() / ".bf6settingsmanager"

        self.settings_file = self.settings_dir / "settings.json"
        self._settings: dict = {}
        self._load()

    def _load(self) -> None:
        """Load settings from JSON file."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    self._settings = json.load(f)
                logger.info(f"Loaded settings from {self.settings_file}")
            else:
                self._settings = {}
                logger.info("No settings file found, using defaults")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse settings file: {e}")
            self._settings = {}
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            self._settings = {}

    def save(self) -> bool:
        """
        Save settings to JSON file.

        Returns:
            True if save was successful, False otherwise.
        """
        try:
            # Ensure directory exists
            self.settings_dir.mkdir(parents=True, exist_ok=True)

            # Write settings atomically
            temp_file = self.settings_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=2)

            # Replace original file
            temp_file.replace(self.settings_file)
            logger.info(f"Saved settings to {self.settings_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        return self._settings.get(key, default)

    def set(self, key: str, value: Any, auto_save: bool = True) -> None:
        """
        Set a setting value.

        Args:
            key: Setting key
            value: Value to set
            auto_save: Whether to save immediately (default True)
        """
        self._settings[key] = value
        if auto_save:
            self.save()

    def delete(self, key: str, auto_save: bool = True) -> bool:
        """
        Delete a setting.

        Args:
            key: Setting key to delete
            auto_save: Whether to save immediately (default True)

        Returns:
            True if key existed and was deleted, False otherwise
        """
        if key in self._settings:
            del self._settings[key]
            if auto_save:
                self.save()
            return True
        return False

    # Specific settings properties for type safety

    @property
    def custom_config_path(self) -> Optional[str]:
        """Get custom config file path."""
        return self.get("custom_config_path")

    @custom_config_path.setter
    def custom_config_path(self, path: Optional[str]) -> None:
        """Set custom config file path."""
        if path:
            self.set("custom_config_path", path)
        else:
            self.delete("custom_config_path")

    @property
    def last_check_for_updates(self) -> Optional[str]:
        """Get timestamp of last update check."""
        return self.get("last_check_for_updates")

    @last_check_for_updates.setter
    def last_check_for_updates(self, timestamp: str) -> None:
        """Set timestamp of last update check."""
        self.set("last_check_for_updates", timestamp)

    @property
    def skip_version(self) -> Optional[str]:
        """Get version to skip for updates."""
        return self.get("skip_version")

    @skip_version.setter
    def skip_version(self, version: Optional[str]) -> None:
        """Set version to skip for updates."""
        if version:
            self.set("skip_version", version)
        else:
            self.delete("skip_version")


# Singleton instance for easy access
_app_settings: Optional[AppSettings] = None


def get_app_settings() -> AppSettings:
    """Get the singleton AppSettings instance."""
    global _app_settings
    if _app_settings is None:
        _app_settings = AppSettings()
    return _app_settings
