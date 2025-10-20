"""Main window for Battlefield 6 Settings Manager."""

import asyncio
import logging
from typing import Dict, Optional

import flet as ft

from ..brightness_detector import BrightnessDetector
from ..config_manager import ConfigManager, SETTINGS
from ..process_checker import ProcessChecker
from .theme import configure_page_theme

logger = logging.getLogger(__name__)


class MainWindow:
    """Main application window."""

    def __init__(self, page: ft.Page):
        """Initialize main window."""
        self.page = page
        self.config_manager = ConfigManager()
        self.brightness_detector = BrightnessDetector()

        # State
        self.detected_brightness: Optional[int] = None
        self.config_file_path: Optional[str] = None
        self.settings_checkboxes: Dict[str, ft.Checkbox] = {}
        self.custom_brightness_field: Optional[ft.TextField] = None

        # UI components
        self.status_text: Optional[ft.Text] = None
        self.apply_button: Optional[ft.ElevatedButton] = None
        self.progress_ring: Optional[ft.ProgressRing] = None

    async def initialize(self) -> None:
        """Initialize the application."""
        configure_page_theme(self.page)

        self.page.title = "Battlefield 6 Settings Manager"
        self.page.window.width = 700
        self.page.window.height = 850
        self.page.window.min_width = 600
        self.page.window.min_height = 700

        # Build UI
        await self.build_ui()

        # Initialize data
        await self.detect_brightness()
        await self.find_config_file()

    async def build_ui(self) -> None:
        """Build the user interface."""
        # Header
        header = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Battlefield 6 Settings Manager",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Optimize your game settings for competitive play",
                    size=14,
                    color=ft.Colors.GREY_400,
                ),
            ], spacing=5),
            padding=20,
            bgcolor=ft.Colors.SURFACE_VARIANT,
        )

        # HDR Section
        hdr_section = await self._build_hdr_section()

        # Visual Clarity Section
        visual_section = self._build_visual_clarity_section()

        # Performance Section
        performance_section = self._build_performance_section()

        # Audio Section
        audio_section = self._build_audio_section()

        # Status and Action Section
        action_section = self._build_action_section()

        # Main content
        content = ft.Column(
            [
                header,
                ft.Container(
                    content=ft.Column([
                        hdr_section,
                        ft.Divider(),
                        visual_section,
                        ft.Divider(),
                        performance_section,
                        ft.Divider(),
                        audio_section,
                        ft.Divider(),
                        action_section,
                    ], spacing=10),
                    padding=20,
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
        )

        # Add to page
        self.page.add(ft.Container(content=content, expand=True))
        self.page.update()

    async def _build_hdr_section(self) -> ft.Container:
        """Build HDR configuration section."""
        self.progress_ring = ft.ProgressRing(width=16, height=16, visible=False)

        brightness_status = ft.Row([
            ft.Icon(ft.Icons.BRIGHTNESS_7, color=ft.Colors.AMBER),
            ft.Text("Detecting HDR brightness...", id="brightness_status"),
            self.progress_ring,
        ], spacing=10)

        self.custom_brightness_field = ft.TextField(
            label="Custom Brightness (nits)",
            hint_text="e.g., 1000",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
            visible=False,
        )

        use_custom = ft.Checkbox(
            label="Use custom brightness value",
            on_change=lambda e: self._toggle_custom_brightness(e.control.value),
        )

        return ft.Container(
            content=ft.Column([
                ft.Text("HDR Configuration", size=18, weight=ft.FontWeight.BOLD),
                brightness_status,
                use_custom,
                self.custom_brightness_field,
            ], spacing=10),
        )

    def _build_visual_clarity_section(self) -> ft.Container:
        """Build visual clarity settings section."""
        settings = [
            ("weapon_dof", "Disable Weapon Depth of Field"),
            ("chromatic_aberration", "Disable Chromatic Aberration"),
            ("film_grain", "Disable Film Grain"),
            ("vignette", "Disable Vignette"),
            ("lens_distortion", "Disable Lens Distortion"),
            ("motion_blur_weapon", "Disable Motion Blur (Weapon)"),
            ("motion_blur_world", "Disable Motion Blur (World)"),
        ]

        checkboxes = []
        for setting_id, label in settings:
            cb = ft.Checkbox(label=label, value=True)
            self.settings_checkboxes[setting_id] = cb
            checkboxes.append(cb)

        return ft.Container(
            content=ft.Column([
                ft.Text("Visual Clarity (Competitive)", size=18, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Disable distracting visual effects for better visibility",
                    size=12,
                    color=ft.Colors.GREY_400,
                ),
                *checkboxes,
            ], spacing=8),
        )

    def _build_performance_section(self) -> ft.Container:
        """Build performance/latency settings section."""
        settings = [
            ("nvidia_low_latency", "Enable NVIDIA Low Latency Mode"),
            ("amd_low_latency", "Enable AMD Low Latency Mode"),
            ("intel_low_latency", "Enable Intel Low Latency Mode"),
            ("future_frame_rendering", "Disable Future Frame Rendering"),
        ]

        checkboxes = []
        for setting_id, label in settings:
            cb = ft.Checkbox(label=label, value=True)
            self.settings_checkboxes[setting_id] = cb
            checkboxes.append(cb)

        return ft.Container(
            content=ft.Column([
                ft.Text("Performance & Latency", size=18, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Reduce input lag and improve responsiveness",
                    size=12,
                    color=ft.Colors.GREY_400,
                ),
                *checkboxes,
            ], spacing=8),
        )

    def _build_audio_section(self) -> ft.Container:
        """Build audio settings section."""
        tinnitus_cb = ft.Checkbox(label="Disable Tinnitus Effect", value=True)
        self.settings_checkboxes["tinnitus"] = tinnitus_cb

        return ft.Container(
            content=ft.Column([
                ft.Text("Audio", size=18, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Remove annoying audio effects",
                    size=12,
                    color=ft.Colors.GREY_400,
                ),
                tinnitus_cb,
            ], spacing=8),
        )

    def _build_action_section(self) -> ft.Container:
        """Build action buttons and status section."""
        self.status_text = ft.Text(
            "",
            size=14,
            color=ft.Colors.GREY_400,
            text_align=ft.TextAlign.CENTER,
        )

        self.apply_button = ft.ElevatedButton(
            "Apply Settings",
            icon=ft.Icons.CHECK_CIRCLE,
            on_click=lambda _: asyncio.create_task(self.apply_settings()),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE,
            ),
        )

        select_all_button = ft.TextButton(
            "Select All",
            on_click=lambda _: self._select_all(True),
        )

        deselect_all_button = ft.TextButton(
            "Deselect All",
            on_click=lambda _: self._select_all(False),
        )

        return ft.Container(
            content=ft.Column([
                self.status_text,
                ft.Row([
                    self.apply_button,
                    select_all_button,
                    deselect_all_button,
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ], spacing=15),
        )

    async def detect_brightness(self) -> None:
        """Detect HDR peak brightness."""
        try:
            brightness = await self.brightness_detector.get_peak_brightness()

            if brightness:
                self.detected_brightness = brightness
                brightness_text = f"Detected: {brightness} nits"
                status_control = self.page.get_control("brightness_status")
                if status_control:
                    status_control.value = brightness_text
                    status_control.color = ft.Colors.GREEN
                    self.page.update()
            else:
                status_control = self.page.get_control("brightness_status")
                if status_control:
                    status_control.value = "Could not detect - use custom value"
                    status_control.color = ft.Colors.ORANGE
                    self.page.update()

        except Exception as e:
            logger.error(f"Brightness detection failed: {e}")

        finally:
            if self.progress_ring:
                self.progress_ring.visible = False
                self.page.update()

    async def find_config_file(self) -> None:
        """Find the config file."""
        config_path = await self.config_manager.find_config_file()

        if config_path:
            self.config_file_path = str(config_path)
            self._update_status(f"Config found: {config_path.parent.name}/{config_path.name}", ft.Colors.GREEN)
        else:
            self._update_status("Config file not found. Please run BF6 at least once.", ft.Colors.ORANGE)

    def _toggle_custom_brightness(self, use_custom: bool) -> None:
        """Toggle custom brightness input."""
        if self.custom_brightness_field:
            self.custom_brightness_field.visible = use_custom
            self.page.update()

    def _select_all(self, value: bool) -> None:
        """Select or deselect all checkboxes."""
        for cb in self.settings_checkboxes.values():
            cb.value = value
        self.page.update()

    async def apply_settings(self) -> None:
        """Apply selected settings."""
        # Check if game is running
        proc_info = await ProcessChecker.is_game_running()

        if proc_info:
            await self._show_game_running_dialog(proc_info)
            return

        # Disable button and show progress
        if self.apply_button:
            self.apply_button.disabled = True
            self.apply_button.text = "Applying..."
            self.page.update()

        try:
            # Gather settings to apply
            settings_to_apply = {}

            # HDR Brightness
            if self.custom_brightness_field and self.custom_brightness_field.visible:
                try:
                    custom_value = float(self.custom_brightness_field.value)
                    settings_to_apply["hdr_peak_brightness"] = f"{custom_value:.6f}"
                except (ValueError, TypeError):
                    pass
            elif self.detected_brightness:
                settings_to_apply["hdr_peak_brightness"] = f"{self.detected_brightness:.6f}"

            # Other settings
            for setting_id, checkbox in self.settings_checkboxes.items():
                if checkbox.value:
                    setting = SETTINGS[setting_id]
                    settings_to_apply[setting_id] = setting.default_value

            if not settings_to_apply:
                self._update_status("No settings selected", ft.Colors.ORANGE)
                return

            # Apply settings
            result = await self.config_manager.apply_settings(settings_to_apply)

            if result["success"]:
                self._update_status(
                    f"✓ {result['message']}\nBackup: {result['backup_path']}",
                    ft.Colors.GREEN
                )
            else:
                self._update_status(f"✗ {result['message']}", ft.Colors.RED)

        except Exception as e:
            logger.error(f"Failed to apply settings: {e}")
            self._update_status(f"Error: {str(e)}", ft.Colors.RED)

        finally:
            if self.apply_button:
                self.apply_button.disabled = False
                self.apply_button.text = "Apply Settings"
                self.page.update()

    async def _show_game_running_dialog(self, proc_info: dict) -> None:
        """Show dialog when game is running."""
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING_AMBER, color=ft.Colors.ORANGE, size=32),
                ft.Text("Game is Running", size=20),
            ]),
            content=ft.Text(
                f"Battlefield 6 is currently running (PID: {proc_info['pid']}).\n\n"
                "Please close the game before applying settings."
            ),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self._close_dialog(dialog)),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _close_dialog(self, dialog: ft.AlertDialog) -> None:
        """Close a dialog."""
        dialog.open = False
        self.page.update()

    def _update_status(self, message: str, color: str) -> None:
        """Update status message."""
        if self.status_text:
            self.status_text.value = message
            self.status_text.color = color
            self.page.update()


async def main(page: ft.Page) -> None:
    """Main entry point for Flet app."""
    window = MainWindow(page)
    await window.initialize()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ft.app(target=main)
