"""Battlefield 6 configuration file manager."""

import asyncio
import logging
import os
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import aiofiles

from .file_protector import FileProtector

logger = logging.getLogger(__name__)


class ConfigSetting:
    """Represents a single config setting."""

    def __init__(self, key: str, default_value: str, description: str):
        """
        Initialize a config setting.

        Args:
            key: Setting key (e.g., "GstRender.WeaponDOF")
            default_value: Default value to set
            description: Human-readable description
        """
        self.key = key
        self.default_value = default_value
        self.description = description
        self.pattern = self._create_pattern(key)

    @staticmethod
    def _create_pattern(key: str) -> str:
        """Create regex pattern for the setting."""
        # Escape dots in key and capture the value
        escaped_key = key.replace(".", r"\.")
        return rf"({escaped_key}\s+)([-+]?\d+\.?\d*)"

    def create_replacement(self, new_value: str) -> str:
        """Create replacement string preserving formatting."""
        return rf"\g<1>{new_value}"


# Define all available settings
SETTINGS = {
    # HDR
    "hdr_peak_brightness": ConfigSetting(
        "GstRender.DisplayMappingHdr10PeakLuma",
        "400.000000",
        "HDR Peak Brightness (nits)"
    ),

    # Visual Clarity
    "weapon_dof": ConfigSetting(
        "GstRender.WeaponDOF",
        "0",
        "Weapon Depth of Field"
    ),
    "chromatic_aberration": ConfigSetting(
        "GstRender.ChromaticAberration",
        "0",
        "Chromatic Aberration"
    ),
    "film_grain": ConfigSetting(
        "GstRender.FilmGrain",
        "0",
        "Film Grain"
    ),
    "vignette": ConfigSetting(
        "GstRender.Vignette",
        "0",
        "Vignette"
    ),
    "lens_distortion": ConfigSetting(
        "GstRender.LensDistortion",
        "0",
        "Lens Distortion"
    ),
    "motion_blur_weapon": ConfigSetting(
        "GstRender.MotionBlurWeapon",
        "0.000000",
        "Motion Blur - Weapon"
    ),
    "motion_blur_world": ConfigSetting(
        "GstRender.MotionBlurWorld",
        "0.000000",
        "Motion Blur - World"
    ),

    # Performance/Latency
    "nvidia_low_latency": ConfigSetting(
        "GstRender.NvidiaLowLatency",
        "1",
        "NVIDIA Low Latency Mode"
    ),
    "amd_low_latency": ConfigSetting(
        "GstRender.AMDLowLatency",
        "1",
        "AMD Low Latency Mode"
    ),
    "intel_low_latency": ConfigSetting(
        "GstRender.IntelLowLatency",
        "1",
        "Intel Low Latency Mode"
    ),
    "future_frame_rendering": ConfigSetting(
        "GstRender.FutureFrameRendering",
        "0",
        "Future Frame Rendering"
    ),

    # Audio
    "tinnitus": ConfigSetting(
        "GstAudio.Volume_Tinnitus",
        "0.000000",
        "Tinnitus Effect Volume"
    ),
}


class ConfigManager:
    """Manage Battlefield 6 configuration file."""

    CONFIG_FILENAME = "PROFSAVE_profile"

    def __init__(self):
        """Initialize config manager."""
        self.documents = Path.home() / "Documents"
        self.bf6_settings_path = self.documents / "Battlefield 6" / "settings"
        self.config_path: Optional[Path] = None

    async def find_config_file(self) -> Optional[Path]:
        """
        Find the PROFSAVE_profile file.

        Returns:
            Path to config file, or None if not found
        """
        def _search():
            if not self.bf6_settings_path.exists():
                logger.warning(f"BF6 settings path not found: {self.bf6_settings_path}")
                return None

            # Search recursively
            for file_path in self.bf6_settings_path.rglob(self.CONFIG_FILENAME):
                logger.info(f"Found config file: {file_path}")
                return file_path

            return None

        loop = asyncio.get_event_loop()
        self.config_path = await loop.run_in_executor(None, _search)
        return self.config_path

    async def create_backup(self, file_path: Path) -> Path:
        """
        Create timestamped backup of config file.

        Args:
            file_path: Path to config file

        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.with_name(f"{file_path.name}.backup_{timestamp}")

        def _backup():
            shutil.copy2(file_path, backup_path)

        await asyncio.to_thread(_backup)
        logger.info(f"Backup created: {backup_path}")
        return backup_path

    async def apply_settings(
        self,
        settings_to_apply: Dict[str, str],
        set_readonly: bool = True
    ) -> Dict[str, any]:
        """
        Apply settings to config file.

        Args:
            settings_to_apply: Dict of setting_id -> value
            set_readonly: Whether to set file read-only after modification

        Returns:
            Dict with results
        """
        if not self.config_path or not await asyncio.to_thread(self.config_path.exists):
            return {
                "success": False,
                "message": "Config file not found. Please locate it first."
            }

        try:
            # Create backup
            backup_path = await self.create_backup(self.config_path)

            # Read current content
            async with aiofiles.open(self.config_path, mode='r', encoding='utf-8-sig') as f:
                content = await f.read()

            original_content = content
            changes_made = []

            # Apply each setting
            for setting_id, new_value in settings_to_apply.items():
                if setting_id not in SETTINGS:
                    logger.warning(f"Unknown setting: {setting_id}")
                    continue

                setting = SETTINGS[setting_id]

                # Apply regex replacement
                new_content = re.sub(
                    setting.pattern,
                    setting.create_replacement(new_value),
                    content,
                    flags=re.MULTILINE
                )

                if new_content != content:
                    changes_made.append(f"{setting.description}: {new_value}")
                    content = new_content
                    logger.info(f"Applied: {setting.key} = {new_value}")
                else:
                    logger.warning(f"Pattern not found for: {setting.key}")

            # Check if any changes were made
            if content == original_content:
                return {
                    "success": False,
                    "message": "No changes applied (patterns may not match)",
                    "backup_path": str(backup_path)
                }

            # Atomic write using temp file
            await self._atomic_write(self.config_path, content)

            # Set read-only if requested
            if set_readonly:
                FileProtector.set_readonly(self.config_path)

            return {
                "success": True,
                "message": f"Successfully applied {len(changes_made)} setting(s)",
                "changes": changes_made,
                "backup_path": str(backup_path),
                "config_path": str(self.config_path)
            }

        except Exception as e:
            logger.error(f"Failed to apply settings: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

    async def _atomic_write(self, file_path: Path, content: str) -> None:
        """
        Atomically write content to file.

        Args:
            file_path: Target file path
            content: Content to write
        """
        # Remove read-only if set
        was_readonly = FileProtector.is_readonly(file_path)
        if was_readonly:
            FileProtector.remove_readonly(file_path)

        # Create temp file in same directory
        temp_fd, temp_path = await asyncio.to_thread(
            tempfile.mkstemp,
            dir=file_path.parent,
            prefix='.tmp_',
            text=True
        )

        try:
            # Write to temp file
            async with aiofiles.open(temp_path, mode='w', encoding='utf-8') as f:
                await f.write(content)

            # Atomic replace
            await asyncio.to_thread(os.replace, temp_path, file_path)
            logger.debug(f"Atomically wrote to {file_path}")

        except Exception:
            # Clean up temp file on failure
            if os.path.exists(temp_path):
                await asyncio.to_thread(os.unlink, temp_path)
            raise
        finally:
            os.close(temp_fd)

    async def get_current_values(self) -> Dict[str, Optional[str]]:
        """
        Read current values of all settings from config file.

        Returns:
            Dict of setting_id -> current value
        """
        if not self.config_path or not await asyncio.to_thread(self.config_path.exists):
            return {}

        try:
            async with aiofiles.open(self.config_path, mode='r', encoding='utf-8-sig') as f:
                content = await f.read()

            current_values = {}

            for setting_id, setting in SETTINGS.items():
                match = re.search(setting.pattern, content, re.MULTILINE)
                if match:
                    current_values[setting_id] = match.group(2)
                else:
                    current_values[setting_id] = None

            return current_values

        except Exception as e:
            logger.error(f"Failed to read current values: {e}")
            return {}


# Example usage
async def main():
    """Test config manager."""
    logging.basicConfig(level=logging.INFO)

    manager = ConfigManager()

    # Find config file
    config_path = await manager.find_config_file()

    if config_path:
        print(f"Found config: {config_path}")

        # Read current values
        current = await manager.get_current_values()
        print("\nCurrent values:")
        for setting_id, value in current.items():
            if value:
                setting = SETTINGS[setting_id]
                print(f"  {setting.description}: {value}")
    else:
        print("Config file not found")


if __name__ == "__main__":
    asyncio.run(main())
