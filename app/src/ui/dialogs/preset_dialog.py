"""Preset management dialog for saving and loading setting configurations."""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Callable

import flet as ft

from ..theme_utils import get_text_color, get_background_color, get_status_color

logger = logging.getLogger(__name__)


class PresetDialog:
    """
    Preset management dialog.

    Features:
    - Built-in presets (Competitive, Balanced, Cinematic)
    - Save custom presets
    - Load presets
    - Delete custom presets
    """

    # Built-in presets
    BUILTIN_PRESETS = {
        "Competitive": {
            "description": "All visual clarity and performance optimizations enabled",
            "settings": {
                "weapon_dof": True,
                "chromatic_aberration": True,
                "film_grain": True,
                "vignette": True,
                "lens_distortion": True,
                "motion_blur_weapon": True,
                "motion_blur_world": True,
                "nvidia_low_latency": True,
                "amd_low_latency": True,
                "intel_low_latency": True,
                "future_frame_rendering": True,
                "tinnitus": True,
            },
        },
        "Balanced": {
            "description": "Moderate settings balancing visual quality and performance",
            "settings": {
                "weapon_dof": True,
                "chromatic_aberration": False,
                "film_grain": True,
                "vignette": False,
                "lens_distortion": True,
                "motion_blur_weapon": True,
                "motion_blur_world": False,
                "nvidia_low_latency": True,
                "amd_low_latency": True,
                "intel_low_latency": True,
                "future_frame_rendering": True,
                "tinnitus": True,
            },
        },
        "Cinematic": {
            "description": "Visual effects enabled for screenshots and recordings",
            "settings": {
                "weapon_dof": False,
                "chromatic_aberration": False,
                "film_grain": False,
                "vignette": False,
                "lens_distortion": False,
                "motion_blur_weapon": False,
                "motion_blur_world": False,
                "nvidia_low_latency": False,
                "amd_low_latency": False,
                "intel_low_latency": False,
                "future_frame_rendering": False,
                "tinnitus": False,
            },
        },
    }

    def __init__(self, page: ft.Page, on_load_preset: Callable[[Dict], None]):
        """
        Initialize preset dialog.

        Args:
            page: Flet page
            on_load_preset: Callback when preset is loaded
        """
        self.page = page
        self.on_load_preset = on_load_preset
        self.presets_file = Path.home() / ".bf6-settings-manager" / "presets.json"
        self.custom_presets: Dict = {}
        self.dialog: Optional[ft.AlertDialog] = None

        # Ensure presets directory exists
        self.presets_file.parent.mkdir(parents=True, exist_ok=True)

        # Load custom presets
        self._load_custom_presets()

    def show(self):
        """Show the preset dialog."""
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.BOOKMARK, color=get_status_color(self.page, "info"), size=28),
                ft.Text("Preset Management", size=20),
            ]),
            content=self._build_content(),
            actions=[
                ft.TextButton("Close", on_click=lambda _: self._close()),
            ],
        )

        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    def _build_content(self) -> ft.Container:
        """Build dialog content."""
        # Built-in presets section
        builtin_section = ft.Column(
            controls=[
                ft.Text("Built-in Presets", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Quick presets for common use cases",
                    size=12,
                    color=get_text_color(self.page, "secondary"),
                ),
                ft.Divider(),
                *[self._create_preset_card(name, data, is_builtin=True)
                  for name, data in self.BUILTIN_PRESETS.items()],
            ],
            spacing=8,
        )

        # Custom presets section
        custom_controls = []
        if self.custom_presets:
            custom_controls.extend([
                *[self._create_preset_card(name, data, is_builtin=False)
                  for name, data in self.custom_presets.items()],
            ])
        else:
            custom_controls.append(
                ft.Text(
                    "No custom presets saved yet",
                    size=13,
                    color=get_text_color(self.page, "secondary"),
                    italic=True,
                )
            )

        custom_section = ft.Column(
            controls=[
                ft.Text("Custom Presets", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Your saved configurations",
                    size=12,
                    color=get_text_color(self.page, "secondary"),
                ),
                ft.Divider(),
                *custom_controls,
                ft.ElevatedButton(
                    "Save Current as Preset",
                    icon=ft.Icons.ADD,
                    on_click=lambda _: self._show_save_dialog(),
                ),
            ],
            spacing=8,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    builtin_section,
                    ft.Divider(height=20),
                    custom_section,
                ],
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=500,
            height=600,
        )

    def _create_preset_card(self, name: str, data: Dict, is_builtin: bool) -> ft.Card:
        """Create a preset card."""
        description = data.get("description", "")
        settings = data.get("settings", {})
        active_count = sum(1 for v in settings.values() if v)

        # Build action buttons
        actions = [
            ft.TextButton(
                "Load",
                icon=ft.Icons.DOWNLOAD,
                on_click=lambda _: self._load_preset(settings),
            ),
        ]

        if not is_builtin:
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color=get_status_color(self.page, "error"),
                    tooltip="Delete preset",
                    on_click=lambda _: self._delete_preset(name),
                )
            )

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(name, size=14, weight=ft.FontWeight.W_500, expand=True),
                                ft.Text(
                                    f"{active_count} settings",
                                    size=12,
                                    color=get_status_color(self.page, "info"),
                                ),
                            ],
                        ),
                        ft.Text(description, size=12, color=get_text_color(self.page, "secondary")),
                        ft.Row(
                            controls=actions,
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                    spacing=8,
                ),
                padding=12,
            ),
            elevation=1,
        )

    def _show_save_dialog(self):
        """Show dialog to save current settings as preset."""
        preset_name_field = ft.TextField(
            label="Preset Name",
            hint_text="e.g., My Custom Config",
            autofocus=True,
        )

        preset_description_field = ft.TextField(
            label="Description (optional)",
            hint_text="e.g., Custom settings for streaming",
            multiline=True,
            max_lines=3,
        )

        def save_preset(e):
            name = preset_name_field.value.strip()
            if not name:
                return

            # TODO: Get current settings from main window
            # For now, create a placeholder
            current_settings = {
                "description": preset_description_field.value.strip() or f"Custom preset: {name}",
                "settings": {},
            }

            self.custom_presets[name] = current_settings
            self._save_custom_presets()

            # Close save dialog
            self.page.dialog.open = False
            # Refresh main preset dialog
            self.show()

        save_dialog = ft.AlertDialog(
            title=ft.Text("Save Preset"),
            content=ft.Column(
                controls=[
                    preset_name_field,
                    preset_description_field,
                ],
                tight=True,
                spacing=12,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_save_dialog()),
                ft.ElevatedButton("Save", on_click=save_preset),
            ],
        )

        self.page.dialog = save_dialog
        save_dialog.open = True
        self.page.update()

    def _close_save_dialog(self):
        """Close save preset dialog and return to main dialog."""
        self.page.dialog.open = False
        self.show()

    def _load_preset(self, settings: Dict):
        """Load a preset."""
        if self.on_load_preset:
            self.on_load_preset(settings)
        self._close()

    def _delete_preset(self, name: str):
        """Delete a custom preset."""
        if name in self.custom_presets:
            del self.custom_presets[name]
            self._save_custom_presets()
            # Refresh dialog
            self.show()

    def _load_custom_presets(self):
        """Load custom presets from file."""
        try:
            if self.presets_file.exists():
                with open(self.presets_file, "r") as f:
                    self.custom_presets = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load custom presets: {e}")
            self.custom_presets = {}

    def _save_custom_presets(self):
        """Save custom presets to file."""
        try:
            with open(self.presets_file, "w") as f:
                json.dump(self.custom_presets, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save custom presets: {e}")

    def _close(self):
        """Close the dialog."""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
