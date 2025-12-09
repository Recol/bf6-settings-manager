"""Main window for Battlefield 6 Settings Manager - Redesigned with card-based layout."""

import logging
import webbrowser
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

import flet as ft

from ..brightness_detector import BrightnessDetector
from ..config_manager import ConfigManager, SETTINGS
from ..process_checker import ProcessChecker
from ..app_settings import get_app_settings
from ..updater import UpdateChecker, CURRENT_VERSION
from .theme import configure_page_theme
from .theme_utils import (
    get_background_color,
    get_text_color,
    get_status_color,
    get_theme_colors,
    update_page_theme,
)
from .components import (
    StatusChip,
    SettingCard,
    SettingRow,
    SearchBar,
    SliderSetting,
    DropdownSetting,
)

logger = logging.getLogger(__name__)

# Constants
DONATION_URL = "https://buymeacoffee.com/decouk"
GITHUB_ISSUES_URL = "https://github.com/Recol/bf6-settings-manager/issues"
DISCORD_URL = "https://discord.com/users/162568099839606784"
TWITTER_URL = "https://x.com/iDeco_UK"


class MainWindow:
    """Main application window with modern card-based UI."""

    def __init__(self, page: ft.Page):
        """Initialize main window."""
        self.page = page
        self.app_settings = get_app_settings()
        self.config_manager = ConfigManager(
            custom_path=self.app_settings.custom_config_path
        )
        self.brightness_detector = BrightnessDetector()
        self.update_checker = UpdateChecker()

        # State
        self.detected_brightness: Optional[int] = None
        self.config_file_path: Optional[str] = None
        self.settings_checkboxes: Dict[str, ft.Checkbox] = {}
        self.custom_brightness_field: Optional[ft.TextField] = None
        self.use_custom_brightness: bool = False

        # New settings state
        self.slider_settings: Dict[str, SliderSetting] = {}
        self.dropdown_settings: Dict[str, DropdownSetting] = {}

        # UI components
        self.status_text: Optional[ft.Text] = None
        self.apply_button: Optional[ft.ElevatedButton] = None
        self.progress_ring: Optional[ft.ProgressRing] = None
        self.brightness_status_text: Optional[ft.Text] = None
        self.config_status_text: Optional[ft.Text] = None
        self.config_path_text: Optional[ft.Text] = None
        self.search_bar: Optional[SearchBar] = None
        self.file_picker: Optional[ft.FilePicker] = None

        # Theme-aware containers
        self.brightness_container: Optional[ft.Container] = None
        self.performance_info_container: Optional[ft.Container] = None
        self.audio_info_container: Optional[ft.Container] = None
        self.header_container: Optional[ft.Container] = None
        self.display_info_container: Optional[ft.Container] = None

        # Cards
        self.hdr_card: Optional[SettingCard] = None
        self.visual_card: Optional[SettingCard] = None
        self.performance_card: Optional[SettingCard] = None
        self.audio_card: Optional[SettingCard] = None
        self.actions_card: Optional[SettingCard] = None
        self.display_card: Optional[SettingCard] = None
        self.frame_rate_card: Optional[SettingCard] = None

        # All cards list for filtering
        self.all_cards: List[SettingCard] = []

        # Status chips
        self.hdr_status_chip: Optional[StatusChip] = None
        self.visual_status_chip: Optional[StatusChip] = None
        self.performance_status_chip: Optional[StatusChip] = None
        self.audio_status_chip: Optional[StatusChip] = None
        self.display_status_chip: Optional[StatusChip] = None
        self.frame_rate_status_chip: Optional[StatusChip] = None

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
        # File picker for custom config path
        self.file_picker = ft.FilePicker(on_result=self._on_file_picker_result)
        self.page.overlay.append(self.file_picker)

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
        self.display_card = self._build_display_card()
        self.frame_rate_card = self._build_frame_rate_card()
        self.performance_card = self._build_performance_card()
        self.audio_card = self._build_audio_card()
        self.actions_card = self._build_actions_card()

        # Store all cards for filtering
        self.all_cards = [
            self.hdr_card,
            self.visual_card,
            self.display_card,
            self.frame_rate_card,
            self.performance_card,
            self.audio_card,
            self.actions_card,
        ]

        # Responsive grid layout
        grid = ft.ResponsiveRow(
            controls=[
                ft.Container(content=self.hdr_card, col={"sm": 12, "md": 6}, padding=8),
                ft.Container(content=self.visual_card, col={"sm": 12, "md": 6}, padding=8),
                ft.Container(content=self.display_card, col={"sm": 12, "md": 6}, padding=8),
                ft.Container(content=self.frame_rate_card, col={"sm": 12, "md": 6}, padding=8),
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
        """Build application header with title, version, and action buttons."""
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SPORTS_ESPORTS, size=32, color=get_status_color(self.page, "info")),
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        "Battlefield 6 Settings Manager",
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                        color=get_text_color(self.page, "primary"),
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            f"v{CURRENT_VERSION}",
                                            size=12,
                                            color=get_text_color(self.page, "secondary"),
                                        ),
                                        bgcolor=get_background_color(self.page, "variant"),
                                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                        border_radius=4,
                                    ),
                                ],
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Text(
                                "Optimize your game settings for competitive play (By Deco)",
                                size=13,
                                color=get_text_color(self.page, "secondary"),
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.OutlinedButton(
                        "Updates",
                        icon=ft.Icons.DOWNLOAD,
                        on_click=self._on_updates_click,
                        tooltip="Check for updates",
                    ),
                    ft.OutlinedButton(
                        "Notes",
                        icon=ft.Icons.DESCRIPTION,
                        on_click=self._on_notes_click,
                        tooltip="View release notes",
                    ),
                    ft.OutlinedButton(
                        "Donate",
                        icon=ft.Icons.FAVORITE,
                        on_click=lambda _: webbrowser.open(DONATION_URL),
                        tooltip="Support development",
                        style=ft.ButtonStyle(
                            color={"": "#e91e63"},
                        ),
                    ),
                    ft.OutlinedButton(
                        "Contact",
                        icon=ft.Icons.CHAT,
                        on_click=self._on_contact_click,
                        tooltip="Get in touch",
                    ),
                    ft.OutlinedButton(
                        "Report Issue",
                        icon=ft.Icons.BUG_REPORT,
                        on_click=lambda _: webbrowser.open(GITHUB_ISSUES_URL),
                        tooltip="Report a bug on GitHub",
                    ),
                    ft.IconButton(
                        icon=ft.Icons.BRIGHTNESS_6,
                        tooltip="Toggle theme",
                        on_click=self._toggle_theme,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
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

    def _build_display_card(self) -> SettingCard:
        """Build display settings card (HDR mode, UI scale, brightness, VSync)."""
        # Status chip
        self.display_status_chip = StatusChip(
            self.page,
            text="Active",
            status="success",
        )

        # HDR Mode toggle
        hdr_mode_row = SettingRow(
            self.page,
            label="Enable HDR Mode",
            icon=ft.Icons.HDR_ON,
            value=True,
            on_change=lambda e: self._update_display_status(),
            icon_color="#ff9800",  # Amber
        )
        self.settings_checkboxes["hdr_mode"] = hdr_mode_row.checkbox

        # UI Scale Factor slider
        ui_scale_slider = SliderSetting(
            self.page,
            label="UI Scale Factor",
            min_val=0.5,
            max_val=1.0,
            initial_value=0.5,
            step=0.05,
            decimals=2,
            icon=ft.Icons.ASPECT_RATIO,
            warning_text="Higher values improve sharpness but may impact performance",
            on_change_end=lambda v: self._on_slider_change("ui_scale_factor", v),
        )
        self.slider_settings["ui_scale_factor"] = ui_scale_slider

        # UI Brightness slider
        ui_brightness_slider = SliderSetting(
            self.page,
            label="UI Brightness",
            min_val=0.0,
            max_val=1.0,
            initial_value=0.5,
            step=0.05,
            decimals=2,
            icon=ft.Icons.BRIGHTNESS_MEDIUM,
            on_change_end=lambda v: self._on_slider_change("ui_brightness", v),
        )
        self.slider_settings["ui_brightness"] = ui_brightness_slider

        # VSync Mode dropdown
        vsync_dropdown = DropdownSetting(
            self.page,
            label="VSync Mode",
            options=[
                ("0", "Off (Recommended)"),
                ("1", "On"),
                ("2", "Adaptive"),
            ],
            initial_value="0",
            icon=ft.Icons.SYNC,
            descriptions={
                "0": "Lowest input lag - recommended for competitive",
                "1": "Standard VSync - eliminates tearing",
                "2": "VSync only when above refresh rate",
            },
            on_change=lambda v: self._on_dropdown_change("vsync_mode", v),
        )
        self.dropdown_settings["vsync_mode"] = vsync_dropdown

        content = [
            hdr_mode_row,
            ui_scale_slider,
            ui_brightness_slider,
            vsync_dropdown,
        ]

        return SettingCard(
            self.page,
            title="Display Settings",
            icon=ft.Icons.DISPLAY_SETTINGS,
            icon_color="#e91e63",  # Pink
            subtitle="Configure display and rendering options",
            status_chip=self.display_status_chip,
            content=content,
            expanded=True,
            collapsible=True,
        )

    def _build_frame_rate_card(self) -> SettingCard:
        """Build frame rate settings card."""
        # Status chip
        self.frame_rate_status_chip = StatusChip(
            self.page,
            text="Active",
            status="success",
        )

        # Frame limiter enable toggle
        limiter_row = SettingRow(
            self.page,
            label="Enable Frame Limiter",
            icon=ft.Icons.TIMER,
            value=True,
            on_change=lambda e: self._update_frame_rate_status(),
        )
        self.settings_checkboxes["frame_rate_limiter_enable"] = limiter_row.checkbox

        # Frame rate limit slider
        fps_slider = SliderSetting(
            self.page,
            label="Frame Rate Limit",
            min_val=30,
            max_val=500,
            initial_value=240,
            step=1,
            suffix=" FPS",
            decimals=0,
            icon=ft.Icons.SPEED,
            on_change_end=lambda v: self._on_slider_change("frame_rate_limit", v),
        )
        self.slider_settings["frame_rate_limit"] = fps_slider

        # Menu frame limiter enable toggle
        menu_limiter_row = SettingRow(
            self.page,
            label="Enable Menu Frame Limiter",
            icon=ft.Icons.TIMER,
            value=True,
            on_change=lambda e: self._update_frame_rate_status(),
        )
        self.settings_checkboxes["frame_rate_limiter_menu_enable"] = menu_limiter_row.checkbox

        # Menu frame rate limit slider
        menu_fps_slider = SliderSetting(
            self.page,
            label="Menu Frame Rate Limit",
            min_val=30,
            max_val=500,
            initial_value=151,
            step=1,
            suffix=" FPS",
            decimals=0,
            icon=ft.Icons.MENU,
            on_change_end=lambda v: self._on_slider_change("frame_rate_limit_menu", v),
        )
        self.slider_settings["frame_rate_limit_menu"] = menu_fps_slider

        content = [
            limiter_row,
            fps_slider,
            menu_limiter_row,
            menu_fps_slider,
        ]

        return SettingCard(
            self.page,
            title="Frame Rate Settings",
            icon=ft.Icons.SPEED,
            icon_color="#ff5722",  # Deep Orange
            subtitle="Configure frame rate limits",
            status_chip=self.frame_rate_status_chip,
            content=content,
            expanded=True,
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

        # Config path text for browse feature
        self.config_path_text = ft.Text(
            "Path: Auto-detect",
            size=12,
            color=get_text_color(self.page, "hint"),
            overflow=ft.TextOverflow.ELLIPSIS,
            expand=True,
        )

        # Config status section with browse button
        config_status = ft.Column(
            controls=[
                ft.Text(
                    "Config Status",
                    size=16,
                    weight=ft.FontWeight.W_500,
                    color=get_text_color(self.page, "primary"),
                ),
                self.config_status_text,
                ft.Row(
                    controls=[
                        self.config_path_text,
                        ft.OutlinedButton(
                            "Browse",
                            icon=ft.Icons.FOLDER_OPEN,
                            on_click=self._browse_config_file,
                            tooltip="Select custom config file location",
                        ),
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            icon_size=18,
                            tooltip="Reset to auto-detect",
                            on_click=self._reset_config_path,
                        ),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
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

        # Refresh slider settings
        for slider in self.slider_settings.values():
            if slider:
                slider.refresh_theme()

        # Refresh dropdown settings
        for dropdown in self.dropdown_settings.values():
            if dropdown:
                dropdown.refresh_theme()

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

    def _update_display_status(self):
        """Update display settings status chip."""
        if "hdr_mode" in self.settings_checkboxes:
            is_hdr_enabled = self.settings_checkboxes["hdr_mode"].value
            if self.display_status_chip:
                if is_hdr_enabled:
                    self.display_status_chip.update_status("HDR On", "success")
                else:
                    self.display_status_chip.update_status("HDR Off", "info")

    def _update_frame_rate_status(self):
        """Update frame rate settings status chip."""
        limiter_keys = ["frame_rate_limiter_enable", "frame_rate_limiter_menu_enable"]
        active_count = sum(
            1 for k in limiter_keys
            if k in self.settings_checkboxes and self.settings_checkboxes[k].value
        )

        if self.frame_rate_status_chip:
            if active_count == 2:
                self.frame_rate_status_chip.update_status("2/2 Active", "success")
            elif active_count > 0:
                self.frame_rate_status_chip.update_status(f"{active_count}/2 Active", "warning")
            else:
                self.frame_rate_status_chip.update_status("Disabled", "info")

    def _on_slider_change(self, setting_id: str, value: float):
        """Handle slider value change."""
        logger.debug(f"Slider changed: {setting_id} = {value}")
        # Value will be applied when Apply All Settings is clicked

    def _on_dropdown_change(self, setting_id: str, value: str):
        """Handle dropdown value change."""
        logger.debug(f"Dropdown changed: {setting_id} = {value}")
        # Value will be applied when Apply All Settings is clicked

    def _browse_config_file(self, e):
        """Open file picker to select custom config file."""
        if self.file_picker:
            self.file_picker.pick_files(
                dialog_title="Select PROFSAVE_profile",
                allowed_extensions=[""],
                allow_multiple=False,
            )

    def _on_file_picker_result(self, e: ft.FilePickerResultEvent):
        """Handle file picker result."""
        if e.files and len(e.files) > 0:
            selected_path = e.files[0].path
            logger.info(f"Selected config path: {selected_path}")

            # Save to app settings
            self.app_settings.custom_config_path = selected_path

            # Update config manager
            self.config_manager.set_custom_path(selected_path)

            # Re-detect config file
            self.page.run_task(self.find_config_file)

            # Update path display
            if self.config_path_text:
                self.config_path_text.value = f"Path: {selected_path}"
                self.config_path_text.update()

    def _reset_config_path(self, e):
        """Reset to auto-detect config path."""
        logger.info("Resetting to auto-detect config path")

        # Clear custom path
        self.app_settings.custom_config_path = None
        self.config_manager.set_custom_path(None)

        # Re-detect config file
        self.page.run_task(self.find_config_file)

        # Update path display
        if self.config_path_text:
            self.config_path_text.value = "Path: Auto-detect"
            self.config_path_text.update()

    async def _check_for_updates(self):
        """Check for application updates."""
        try:
            result = await self.update_checker.check_for_updates()

            def close_dlg(e):
                dlg.open = False
                self.page.update()

            def download_and_close(e):
                dlg.open = False
                self.page.update()
                self._download_update(result.get("download_url"))

            if result.get("error"):
                # Show error dialog
                dlg = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Update Check Failed"),
                    content=ft.Text(f"Could not check for updates:\n{result['error']}"),
                    actions=[
                        ft.TextButton("OK", on_click=close_dlg),
                    ],
                )
                self.page.overlay.append(dlg)
                dlg.open = True
                self.page.update()
                return

            if result.get("update_available"):
                # Show update available dialog
                dlg = ft.AlertDialog(
                    modal=True,
                    title=ft.Row([
                        ft.Icon(ft.Icons.SYSTEM_UPDATE, color="#4caf50", size=32),
                        ft.Text("Update Available", size=20),
                    ]),
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                f"A new version is available: v{result['latest_version']}\n"
                                f"You are currently on: v{CURRENT_VERSION}"
                            ),
                            ft.Text(
                                "Would you like to download the update?",
                                color=get_text_color(self.page, "secondary"),
                            ),
                        ],
                        tight=True,
                        spacing=12,
                    ),
                    actions=[
                        ft.TextButton("Download", on_click=download_and_close),
                        ft.TextButton("Later", on_click=close_dlg),
                    ],
                )
                self.page.overlay.append(dlg)
                dlg.open = True
                self.page.update()
            else:
                # Already up to date
                dlg = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Up to Date"),
                    content=ft.Text(f"You are running the latest version (v{CURRENT_VERSION})."),
                    actions=[
                        ft.TextButton("OK", on_click=close_dlg),
                    ],
                )
                self.page.overlay.append(dlg)
                dlg.open = True
                self.page.update()

        except Exception as e:
            logger.error(f"Update check failed: {e}")

    def _on_updates_click(self, e):
        """Handle Updates button click."""
        self.page.run_task(self._check_for_updates)

    def _on_notes_click(self, e):
        """Handle Notes button click."""
        self._show_release_notes_dialog()

    def _on_contact_click(self, e):
        """Handle Contact button click."""
        self._show_contact_dialog()

    def _show_contact_dialog(self):
        """Show contact options dialog."""
        def close_dialog(e):
            dialog.open = False
            self.page.update()

        def open_discord(e):
            webbrowser.open(DISCORD_URL)

        def open_twitter(e):
            webbrowser.open(TWITTER_URL)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.CHAT, color=get_status_color(self.page, "info"), size=24),
                ft.Text("Contact", size=18, weight=ft.FontWeight.BOLD),
            ]),
            content=ft.Column(
                controls=[
                    ft.Text("Get in touch via:", size=14),
                    ft.ElevatedButton(
                        "Discord",
                        icon=ft.Icons.DISCORD,
                        on_click=open_discord,
                        width=200,
                    ),
                    ft.ElevatedButton(
                        "Twitter / X",
                        icon=ft.Icons.ALTERNATE_EMAIL,
                        on_click=open_twitter,
                        width=200,
                    ),
                ],
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            actions=[
                ft.TextButton("Close", on_click=close_dialog),
            ],
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _download_update(self, download_url: str):
        """Open download URL in browser."""
        self._close_dialog()
        if download_url:
            webbrowser.open(download_url)
        else:
            # Fallback to releases page
            self.update_checker.open_releases_page()

    def _show_release_notes_dialog(self):
        """Show release notes dialog."""
        try:
            # Navigate from main_window.py to project root: ui -> src -> app -> project_root
            notes_path = Path(__file__).parent.parent.parent.parent / "RELEASE_NOTES.md"
            if notes_path.exists():
                content = notes_path.read_text(encoding='utf-8')
            else:
                content = "Release notes not available."
        except Exception as e:
            logger.error(f"Failed to load release notes: {e}")
            content = f"Error loading release notes: {e}"

        def close_dialog(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.DESCRIPTION, color=get_status_color(self.page, "info"), size=24),
                ft.Text("Release Notes", size=18, weight=ft.FontWeight.BOLD),
            ]),
            content=ft.Column(
                controls=[
                    ft.Markdown(
                        content,
                        selectable=True,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                    ),
                ],
                width=500,
                height=350,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton("Close", on_click=close_dialog),
            ],
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

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

            # Checkbox settings (toggle on/off)
            for setting_id, checkbox in self.settings_checkboxes.items():
                if checkbox.value:
                    setting = SETTINGS[setting_id]
                    settings_to_apply[setting_id] = setting.default_value
                elif setting_id in SETTINGS:
                    # For toggle settings, set to 0 when unchecked
                    if setting_id in ["hdr_mode", "frame_rate_limiter_enable", "frame_rate_limiter_menu_enable"]:
                        settings_to_apply[setting_id] = "0"

            # Slider settings (numeric values)
            for setting_id, slider in self.slider_settings.items():
                if setting_id in SETTINGS:
                    value = slider.get_value()
                    # Format based on setting type
                    if setting_id in ["frame_rate_limit", "frame_rate_limit_menu"]:
                        settings_to_apply[setting_id] = f"{value:.6f}"
                    else:
                        settings_to_apply[setting_id] = f"{value:.6f}"

            # Dropdown settings
            for setting_id, dropdown in self.dropdown_settings.items():
                if setting_id in SETTINGS:
                    settings_to_apply[setting_id] = dropdown.get_value()

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
