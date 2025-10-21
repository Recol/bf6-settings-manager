"""Main window for Battlefield 6 Settings Manager - Redesigned with card-based layout."""

import logging
from typing import Dict, Optional, List
from datetime import datetime

import flet as ft

from ..brightness_detector import BrightnessDetector
from ..config_manager import ConfigManager, SETTINGS
from ..process_checker import ProcessChecker
from .theme import configure_page_theme
from .theme_utils import (
    get_background_color,
    get_text_color,
    get_status_color,
    get_theme_colors,
    update_page_theme,
)
from .components import StatusChip, SettingCard, SettingRow, SearchBar

logger = logging.getLogger(__name__)


class MainWindow:
    """Main application window with modern card-based UI."""

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
        self.use_custom_brightness: bool = False

        # UI components
        self.status_text: Optional[ft.Text] = None
        self.apply_button: Optional[ft.ElevatedButton] = None
        self.progress_ring: Optional[ft.ProgressRing] = None
        self.brightness_status_text: Optional[ft.Text] = None
        self.config_status_text: Optional[ft.Text] = None
        self.search_bar: Optional[SearchBar] = None

        # Theme-aware containers
        self.brightness_container: Optional[ft.Container] = None
        self.performance_info_container: Optional[ft.Container] = None
        self.audio_info_container: Optional[ft.Container] = None
        self.header_container: Optional[ft.Container] = None

        # Cards
        self.hdr_card: Optional[SettingCard] = None
        self.visual_card: Optional[SettingCard] = None
        self.performance_card: Optional[SettingCard] = None
        self.audio_card: Optional[SettingCard] = None
        self.actions_card: Optional[SettingCard] = None

        # All cards list for filtering
        self.all_cards: List[SettingCard] = []

        # Status chips
        self.hdr_status_chip: Optional[StatusChip] = None
        self.visual_status_chip: Optional[StatusChip] = None
        self.performance_status_chip: Optional[StatusChip] = None
        self.audio_status_chip: Optional[StatusChip] = None

    async def initialize(self) -> None:
        """Initialize the application."""
        configure_page_theme(self.page, ft.ThemeMode.DARK)

        self.page.title = "Battlefield 6 Settings Manager"
        self.page.window.width = 900
        self.page.window.height = 950
        self.page.window.min_width = 750
        self.page.window.min_height = 800

        # Build UI
        await self.build_ui()

        # Initialize data
        await self.detect_brightness()
        await self.find_config_file()

    async def build_ui(self) -> None:
        """Build the user interface with card-based layout."""
        # Header with title and theme toggle
        self.header_container = self._build_header()

        # Search bar
        self.search_bar = SearchBar(
            self.page,
            hint_text="Search settings...",
            on_search=self._handle_search,
        )

        # Build cards
        self.hdr_card = await self._build_hdr_card()
        self.visual_card = self._build_visual_clarity_card()
        self.performance_card = self._build_performance_card()
        self.audio_card = self._build_audio_card()
        self.actions_card = self._build_actions_card()

        # Store all cards for filtering
        self.all_cards = [
            self.hdr_card,
            self.visual_card,
            self.performance_card,
            self.audio_card,
            self.actions_card,
        ]

        # Responsive grid layout
        grid = ft.ResponsiveRow(
            controls=[
                ft.Container(content=self.hdr_card, col={"sm": 12, "md": 6}, padding=8),
                ft.Container(content=self.visual_card, col={"sm": 12, "md": 6}, padding=8),
                ft.Container(content=self.performance_card, col={"sm": 12, "md": 6}, padding=8),
                ft.Container(content=self.audio_card, col={"sm": 12, "md": 6}, padding=8),
                ft.Container(content=self.actions_card, col={"sm": 12}, padding=8),
            ],
            spacing=0,
            run_spacing=0,
        )

        # Main content with scroll
        content = ft.Column(
            controls=[
                self.header_container,
                ft.Container(
                    content=self.search_bar,
                    padding=ft.padding.symmetric(horizontal=16, vertical=8),
                ),
                ft.Container(
                    content=grid,
                    expand=True,
                    padding=ft.padding.only(left=8, right=8, bottom=16),
                ),
            ],
            spacing=0,
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
        )

        # Add to page
        self.page.add(content)
        self.page.update()

    def _build_header(self) -> ft.Container:
        """Build application header with title and controls."""
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SPORTS_ESPORTS, size=32, color=get_status_color(self.page, "info")),
                    ft.Column(
                        controls=[
                            ft.Text(
                                "Battlefield 6 Settings Manager - Beta (By Deco)",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=get_text_color(self.page, "primary"),
                            ),
                            ft.Text(
                                "Optimize your game settings for competitive play",
                                size=13,
                                color=get_text_color(self.page, "secondary"),
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.BRIGHTNESS_6,
                        tooltip="Toggle theme",
                        on_click=self._toggle_theme,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=get_background_color(self.page, "surface"),
            padding=20,
            border=ft.border.only(bottom=ft.BorderSide(1, get_text_color(self.page, "hint"))),
        )

    async def _build_hdr_card(self) -> SettingCard:
        """Build HDR configuration card."""
        self.progress_ring = ft.ProgressRing(width=16, height=16, visible=True)
        self.brightness_status_text = ft.Text(
            "Detecting...",
            size=14,
            color=get_text_color(self.page, "secondary"),
        )

        # Status chip
        self.hdr_status_chip = StatusChip(
            self.page,
            text="Detecting",
            status="info",
        )

        # Brightness detection row
        detection_row = ft.Row(
            controls=[
                ft.Icon(ft.Icons.SEARCH, size=20, color=get_text_color(self.page, "secondary")),
                self.brightness_status_text,
                self.progress_ring,
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    icon_size=20,
                    tooltip="Refresh detection",
                    on_click=lambda _: self.page.run_task(self.detect_brightness),
                ),
            ],
            spacing=8,
        )

        # Custom brightness toggle
        self.custom_brightness_field = ft.TextField(
            label="Custom Brightness (nits)",
            hint_text="e.g., 1000",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
            visible=False,
        )

        use_custom_checkbox = ft.Checkbox(
            label="Use custom brightness value",
            value=False,
            on_change=lambda e: self._toggle_custom_brightness(e.control.value),
        )

        # Store brightness container reference for theme updates
        self.brightness_container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Brightness Detection",
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color=get_text_color(self.page, "primary"),
                ),
                detection_row,
            ], spacing=8),
            padding=12,
            bgcolor=get_background_color(self.page, "variant"),
            border_radius=8,
        )

        content = [
            self.brightness_container,
            use_custom_checkbox,
            self.custom_brightness_field,
        ]

        return SettingCard(
            self.page,
            title="HDR Configuration",
            icon=ft.Icons.BRIGHTNESS_7,
            icon_color="#ff9800",  # Amber
            subtitle="Configure display peak brightness for HDR",
            status_chip=self.hdr_status_chip,
            content=content,
            expanded=True,
            collapsible=True,
        )

    def _build_visual_clarity_card(self) -> SettingCard:
        """Build visual clarity settings card."""
        settings = [
            ("weapon_dof", "Weapon Depth of Field", ft.Icons.CENTER_FOCUS_WEAK),
            ("chromatic_aberration", "Chromatic Aberration", ft.Icons.GRADIENT),
            ("film_grain", "Film Grain", ft.Icons.GRAIN),
            ("vignette", "Vignette", ft.Icons.VIGNETTE),
            ("lens_distortion", "Lens Distortion", ft.Icons.PANORAMA_FISH_EYE),
            ("motion_blur_weapon", "Motion Blur (Weapon)", ft.Icons.SPORTS_SCORE),
            ("motion_blur_world", "Motion Blur (World)", ft.Icons.BLUR_ON),
        ]

        # Status chip
        self.visual_status_chip = StatusChip(
            self.page,
            text="7/7 Active",
            status="success",
        )

        # Setting rows
        setting_rows = []
        for setting_id, label, icon in settings:
            row = SettingRow(
                self.page,
                label=label,
                icon=icon,
                value=True,
                on_change=lambda e: self._update_visual_status(),
            )
            self.settings_checkboxes[setting_id] = row.checkbox
            setting_rows.append(row)

        # Action buttons
        button_row = ft.Row(
            controls=[
                ft.TextButton("Select All", on_click=lambda _: self._select_all_visual(True)),
                ft.TextButton("Deselect All", on_click=lambda _: self._select_all_visual(False)),
            ],
            spacing=8,
        )

        content = setting_rows + [button_row]

        return SettingCard(
            self.page,
            title="Visual Clarity (Competitive)",
            icon=ft.Icons.VISIBILITY,
            icon_color="#2196f3",  # Blue
            subtitle="Disable distracting visual effects for better visibility",
            status_chip=self.visual_status_chip,
            content=content,
            expanded=True,
            collapsible=True,
        )

    def _build_performance_card(self) -> SettingCard:
        """Build performance & latency settings card."""
        settings = [
            ("nvidia_low_latency", "NVIDIA Low Latency Mode", ft.Icons.MEMORY, "#4caf50"),  # Green
            ("amd_low_latency", "AMD Low Latency Mode", ft.Icons.MEMORY, "#f44336"),  # Red
            ("intel_low_latency", "Intel Low Latency Mode", ft.Icons.MEMORY, "#2196f3"),  # Blue
            ("future_frame_rendering", "Disable Future Frame Rendering", ft.Icons.BLOCK, None),
        ]

        # Status chip
        self.performance_status_chip = StatusChip(
            self.page,
            text="4/4 Active",
            status="success",
        )

        # Setting rows
        setting_rows = []
        for setting_id, label, icon, color in settings:
            row = SettingRow(
                self.page,
                label=label,
                icon=icon,
                value=True,
                on_change=lambda e: self._update_performance_status(),
                icon_color=color,
            )
            self.settings_checkboxes[setting_id] = row.checkbox
            setting_rows.append(row)

        # Store info banner reference for theme updates
        self.performance_info_container = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.INFO_OUTLINE,
                        size=16,
                        color=get_text_color(self.page, "secondary"),
                    ),
                    ft.Text(
                        "Vendor-specific settings auto-detect GPU",
                        size=12,
                        color=get_text_color(self.page, "secondary"),
                    ),
                ],
                spacing=8,
            ),
            padding=8,
            bgcolor=get_background_color(self.page, "variant"),
            border_radius=8,
        )

        content = setting_rows + [self.performance_info_container]

        return SettingCard(
            self.page,
            title="Performance & Latency",
            icon=ft.Icons.SPEED,
            icon_color="#00bcd4",  # Cyan
            subtitle="Reduce input lag and improve responsiveness",
            status_chip=self.performance_status_chip,
            content=content,
            expanded=True,
            collapsible=True,
        )

    def _build_audio_card(self) -> SettingCard:
        """Build audio settings card."""
        # Status chip
        self.audio_status_chip = StatusChip(
            self.page,
            text="Active",
            status="success",
        )

        # Setting row
        tinnitus_row = SettingRow(
            self.page,
            label="Disable Tinnitus Effect",
            icon=ft.Icons.VOLUME_OFF,
            value=True,
            on_change=lambda e: self._update_audio_status(),
        )
        self.settings_checkboxes["tinnitus"] = tinnitus_row.checkbox

        # Store info banner reference for theme updates
        self.audio_info_container = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.INFO_OUTLINE,
                        size=16,
                        color=get_text_color(self.page, "secondary"),
                    ),
                    ft.Text(
                        "Removes high-pitched ringing sound effect",
                        size=12,
                        color=get_text_color(self.page, "secondary"),
                    ),
                ],
                spacing=8,
            ),
            padding=8,
            bgcolor=get_background_color(self.page, "variant"),
            border_radius=8,
        )

        content = [tinnitus_row, self.audio_info_container]

        return SettingCard(
            self.page,
            title="Audio Settings",
            icon=ft.Icons.VOLUME_UP,
            icon_color="#9c27b0",  # Purple
            subtitle="Remove annoying audio effects",
            status_chip=self.audio_status_chip,
            content=content,
            expanded=False,
            collapsible=True,
        )

    def _build_actions_card(self) -> SettingCard:
        """Build quick actions card."""
        # Config status with stored reference
        self.config_status_text = ft.Text(
            "Detecting config file...",
            size=13,
            color=get_text_color(self.page, "secondary"),
        )

        config_status = ft.Column(
            controls=[
                ft.Text(
                    "Config Status",
                    size=16,
                    weight=ft.FontWeight.W_500,
                    color=get_text_color(self.page, "primary"),
                ),
                self.config_status_text,
            ],
            spacing=4,
        )

        # Apply button
        self.apply_button = ft.ElevatedButton(
            "Apply All Settings",
            icon=ft.Icons.CHECK_CIRCLE,
            on_click=lambda _: self.page.run_task(self.apply_settings),
            style=ft.ButtonStyle(
                bgcolor={"": "#2196f3"},  # Blue
                color={"": "#ffffff"},
                padding=20,
            ),
            height=50,
        )

        # Additional action buttons
        action_buttons = ft.Row(
            controls=[
                ft.OutlinedButton(
                    "Presets",
                    icon=ft.Icons.BOOKMARK,
                    on_click=self._show_presets_dialog,
                ),
                ft.OutlinedButton(
                    "Backups",
                    icon=ft.Icons.HISTORY,
                    on_click=self._show_backups_dialog,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )

        # Status text
        self.status_text = ft.Text(
            "Ready to apply settings",
            size=13,
            color=get_text_color(self.page, "secondary"),
            text_align=ft.TextAlign.CENTER,
        )

        content = [
            config_status,
            ft.Divider(),
            self.apply_button,
            action_buttons,
            self.status_text,
        ]

        return SettingCard(
            self.page,
            title="Quick Actions",
            icon=ft.Icons.SPORTS_ESPORTS,
            icon_color="#4caf50",  # Green
            subtitle="",
            content=content,
            expanded=True,
            collapsible=False,
        )

    def _toggle_theme(self, e):
        """Toggle between light and dark theme."""
        new_theme = (
            ft.ThemeMode.LIGHT
            if self.page.theme_mode == ft.ThemeMode.DARK
            else ft.ThemeMode.DARK
        )
        update_page_theme(self.page, new_theme)

        # Refresh all cards
        for card in self.all_cards:
            if card:
                card.refresh_theme()

        # Refresh search bar
        if self.search_bar:
            self.search_bar.refresh_theme()

        # Refresh theme-aware containers - update colors without calling update()
        if self.brightness_container:
            self.brightness_container.bgcolor = get_background_color(self.page, "variant")
            # Update text color in brightness detection
            if self.brightness_container.content and hasattr(self.brightness_container.content, 'controls'):
                for control in self.brightness_container.content.controls:
                    if isinstance(control, ft.Text):
                        control.color = get_text_color(self.page, "primary")

        if self.performance_info_container:
            self.performance_info_container.bgcolor = get_background_color(self.page, "variant")
            # Update icon and text colors
            if self.performance_info_container.content and hasattr(self.performance_info_container.content, 'controls'):
                for control in self.performance_info_container.content.controls:
                    if isinstance(control, ft.Icon):
                        control.color = get_text_color(self.page, "secondary")
                    elif isinstance(control, ft.Text):
                        control.color = get_text_color(self.page, "secondary")

        if self.audio_info_container:
            self.audio_info_container.bgcolor = get_background_color(self.page, "variant")
            # Update icon and text colors
            if self.audio_info_container.content and hasattr(self.audio_info_container.content, 'controls'):
                for control in self.audio_info_container.content.controls:
                    if isinstance(control, ft.Icon):
                        control.color = get_text_color(self.page, "secondary")
                    elif isinstance(control, ft.Text):
                        control.color = get_text_color(self.page, "secondary")

        # Update brightness status text and icons
        if self.brightness_status_text:
            self.brightness_status_text.color = get_text_color(self.page, "secondary")

        # Update other text elements
        if self.config_status_text:
            # Keep current color (success/error), don't override
            pass

        if self.status_text:
            self.status_text.color = get_text_color(self.page, "secondary")

        # Update header container colors
        if self.header_container:
            self.header_container.bgcolor = get_background_color(self.page, "surface")
            # Update header border
            self.header_container.border = ft.border.only(
                bottom=ft.BorderSide(1, get_text_color(self.page, "hint"))
            )
            # Update header text and icon colors
            if self.header_container.content and hasattr(self.header_container.content, 'controls'):
                for control in self.header_container.content.controls:
                    if isinstance(control, ft.Icon):
                        control.color = get_status_color(self.page, "info")
                    elif isinstance(control, ft.Column):
                        # Update title and subtitle
                        for text_control in control.controls:
                            if isinstance(text_control, ft.Text):
                                if text_control.weight == ft.FontWeight.BOLD:
                                    text_control.color = get_text_color(self.page, "primary")
                                else:
                                    text_control.color = get_text_color(self.page, "secondary")

        # Update page once to refresh all changes
        self.page.update()

    def _toggle_custom_brightness(self, use_custom: bool) -> None:
        """Toggle custom brightness input."""
        self.use_custom_brightness = use_custom
        if self.custom_brightness_field:
            self.custom_brightness_field.visible = use_custom
            self.page.update()

    def _select_all_visual(self, value: bool) -> None:
        """Select or deselect all visual clarity settings."""
        visual_settings = [
            "weapon_dof",
            "chromatic_aberration",
            "film_grain",
            "vignette",
            "lens_distortion",
            "motion_blur_weapon",
            "motion_blur_world",
        ]
        for setting_id in visual_settings:
            if setting_id in self.settings_checkboxes:
                self.settings_checkboxes[setting_id].value = value

        # Update visual card to reflect changes
        if self.visual_card and self.visual_card.content:
            self.visual_card.refresh_theme()

        self._update_visual_status()
        self.page.update()

    def _update_visual_status(self):
        """Update visual clarity status chip."""
        visual_settings = [
            "weapon_dof",
            "chromatic_aberration",
            "film_grain",
            "vignette",
            "lens_distortion",
            "motion_blur_weapon",
            "motion_blur_world",
        ]
        active_count = sum(
            1 for s in visual_settings
            if s in self.settings_checkboxes and self.settings_checkboxes[s].value
        )

        if self.visual_status_chip:
            if active_count == 7:
                self.visual_status_chip.update_status(f"{active_count}/7 Active", "success")
            elif active_count > 0:
                self.visual_status_chip.update_status(f"{active_count}/7 Active", "warning")
            else:
                self.visual_status_chip.update_status("0/7 Active", "info")

    def _update_performance_status(self):
        """Update performance status chip."""
        perf_settings = [
            "nvidia_low_latency",
            "amd_low_latency",
            "intel_low_latency",
            "future_frame_rendering",
        ]
        active_count = sum(
            1 for s in perf_settings
            if s in self.settings_checkboxes and self.settings_checkboxes[s].value
        )

        if self.performance_status_chip:
            if active_count == 4:
                self.performance_status_chip.update_status(f"{active_count}/4 Active", "success")
            elif active_count > 0:
                self.performance_status_chip.update_status(f"{active_count}/4 Active", "warning")
            else:
                self.performance_status_chip.update_status("0/4 Active", "info")

    def _update_audio_status(self):
        """Update audio status chip."""
        if "tinnitus" in self.settings_checkboxes:
            is_active = self.settings_checkboxes["tinnitus"].value
            if self.audio_status_chip:
                if is_active:
                    self.audio_status_chip.update_status("Active", "success")
                else:
                    self.audio_status_chip.update_status("Inactive", "info")

    def _handle_search(self, search_text: str):
        """Handle search filtering."""
        search_text = search_text.lower().strip()

        if not search_text:
            # Show all cards
            for card in self.all_cards:
                if card:
                    card.visible = True
                    card.update()
            return

        # Filter cards based on title and subtitle
        for card in self.all_cards:
            if card:
                title_match = search_text in card.title.lower()
                subtitle_match = card.subtitle and search_text in card.subtitle.lower()
                card.visible = title_match or subtitle_match
                card.update()

    def _show_presets_dialog(self, e):
        """Show presets management dialog (placeholder)."""
        # TODO: Implement preset dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Presets"),
            content=ft.Text("Preset management coming soon!\n\nThis will allow you to save and load custom setting configurations."),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self._close_dialog()),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _show_backups_dialog(self, e):
        """Show backups management dialog (placeholder)."""
        # TODO: Implement backup dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Backups"),
            content=ft.Text("Backup management coming soon!\n\nThis will allow you to view and restore previous config backups."),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self._close_dialog()),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _close_dialog(self):
        """Close active dialog."""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    async def detect_brightness(self) -> None:
        """Detect HDR peak brightness."""
        try:
            if self.progress_ring:
                self.progress_ring.visible = True
            if self.brightness_status_text:
                self.brightness_status_text.value = "Detecting..."
            if self.hdr_status_chip:
                self.hdr_status_chip.update_status("Detecting", "info")
            self.page.update()

            brightness = await self.brightness_detector.get_peak_brightness()

            if brightness:
                self.detected_brightness = brightness
                if self.brightness_status_text:
                    self.brightness_status_text.value = f"Detected: {brightness} nits"
                if self.hdr_status_chip:
                    self.hdr_status_chip.update_status(f"{brightness} nits", "success")
            else:
                if self.brightness_status_text:
                    self.brightness_status_text.value = "Could not detect - use custom value"
                if self.hdr_status_chip:
                    self.hdr_status_chip.update_status("Not Detected", "warning")

        except Exception as e:
            logger.error(f"Brightness detection failed: {e}")
            if self.brightness_status_text:
                self.brightness_status_text.value = "Detection failed"
            if self.hdr_status_chip:
                self.hdr_status_chip.update_status("Failed", "error")

        finally:
            if self.progress_ring:
                self.progress_ring.visible = False
            self.page.update()

    async def find_config_file(self) -> None:
        """Find the config file."""
        config_path = await self.config_manager.find_config_file()

        if config_path:
            self.config_file_path = str(config_path)
            # Update config status in actions card
            if self.config_status_text:
                config_text = f"✓ Found: {config_path.parent.name}/{config_path.name}"
                self.config_status_text.value = config_text
                self.config_status_text.color = get_status_color(self.page, "success")
                self.page.update()
        else:
            if self.config_status_text:
                self.config_status_text.value = "✗ Config file not found"
                self.config_status_text.color = get_status_color(self.page, "error")
                self.page.update()
            logger.warning("Config file not found")

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
            self.apply_button.icon = ft.Icons.HOURGLASS_EMPTY
            self.page.update()

        try:
            # Gather settings to apply
            settings_to_apply = {}

            # HDR Brightness
            if self.use_custom_brightness and self.custom_brightness_field:
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
                self._update_status("No settings selected", "warning")
                return

            # Apply settings
            result = await self.config_manager.apply_settings(settings_to_apply)

            if result["success"]:
                self._update_status(
                    f"✓ {result['message']}\nBackup: {result.get('backup_path', 'N/A')}",
                    "success",
                )
            else:
                self._update_status(f"✗ {result['message']}", "error")

        except Exception as e:
            logger.error(f"Failed to apply settings: {e}")
            self._update_status(f"Error: {str(e)}", "error")

        finally:
            if self.apply_button:
                self.apply_button.disabled = False
                self.apply_button.text = "Apply All Settings"
                self.apply_button.icon = ft.Icons.CHECK_CIRCLE
                self.page.update()

    async def _show_game_running_dialog(self, proc_info: dict) -> None:
        """Show dialog when game is running."""
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING_AMBER, color="#ff9800", size=32),
                ft.Text("Game is Running", size=20),
            ]),
            content=ft.Text(
                f"Battlefield 6 is currently running (PID: {proc_info['pid']}).\n\n"
                "Please close the game before applying settings."
            ),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self._close_dialog()),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _update_status(self, message: str, status_type: str) -> None:
        """Update status message."""
        if self.status_text:
            self.status_text.value = message
            if status_type == "success":
                self.status_text.color = get_status_color(self.page, "success")
            elif status_type == "error":
                self.status_text.color = get_status_color(self.page, "error")
            elif status_type == "warning":
                self.status_text.color = get_status_color(self.page, "warning")
            else:
                self.status_text.color = get_text_color(self.page, "secondary")
            self.page.update()


async def main(page: ft.Page) -> None:
    """Main entry point for Flet app."""
    window = MainWindow(page)
    await window.initialize()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ft.app(target=main)
