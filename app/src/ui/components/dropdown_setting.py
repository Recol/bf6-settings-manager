"""Dropdown setting component for option selection."""

import flet as ft
from typing import Callable, List, Optional, Tuple

from ..theme_utils import (
    get_background_color,
    get_text_color,
    get_outline_color,
    get_theme_colors,
)


class DropdownSetting(ft.Container):
    """
    A dropdown setting component with label and themed styling.

    Features:
    - Material-styled dropdown with theme support
    - Label text above dropdown
    - Optional description for selected option
    - Theme-aware colors
    """

    def __init__(
        self,
        page: ft.Page,
        label: str,
        options: List[Tuple[str, str]],
        initial_value: str,
        on_change: Optional[Callable[[str], None]] = None,
        descriptions: Optional[dict] = None,
        icon: Optional[str] = None,
        width: Optional[int] = None,
        **kwargs,
    ):
        """
        Initialize dropdown setting.

        Args:
            page: Flet page for theme access
            label: Setting label text
            options: List of (key, display_text) tuples
            initial_value: Initial selected key
            on_change: Callback when selection changes
            descriptions: Optional dict mapping keys to description text
            icon: Optional Material Icon name
            width: Optional fixed width for dropdown
            **kwargs: Additional Container properties
        """
        self.page = page
        self.label = label
        self.options = options
        self.current_value = initial_value
        self.on_change_callback = on_change
        self.descriptions = descriptions or {}
        self.icon_name = icon
        self.dropdown_width = width

        # Create components
        self.dropdown = self._create_dropdown(initial_value)
        self.description_text = self._create_description_text()

        # Build content
        content = self._build_content()

        super().__init__(
            content=content,
            padding=ft.padding.symmetric(horizontal=4, vertical=4),
            **kwargs,
        )

    def _create_dropdown(self, initial_value: str) -> ft.Dropdown:
        """Create the dropdown control."""
        colors = get_theme_colors(self.page)

        dropdown_options = [
            ft.dropdown.Option(key=key, text=text) for key, text in self.options
        ]

        return ft.Dropdown(
            value=initial_value,
            options=dropdown_options,
            filled=True,
            fill_color=get_background_color(self.page, "variant"),
            bgcolor=get_background_color(self.page, "surface"),
            color=get_text_color(self.page, "primary"),
            border_color=get_outline_color(self.page),
            focused_border_color=colors.PRIMARY,
            border_radius=8,
            text_size=14,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
            on_change=self._handle_change,
            width=self.dropdown_width,
        )

    def _create_description_text(self) -> ft.Text:
        """Create description text for selected option."""
        description = self.descriptions.get(self.current_value, "")
        return ft.Text(
            description,
            size=11,
            color=get_text_color(self.page, "secondary"),
            italic=True,
            visible=bool(description),
        )

    def _build_content(self) -> ft.Column:
        """Build the complete dropdown content."""
        # Label row with optional icon
        label_controls = []

        if self.icon_name:
            label_controls.append(
                ft.Icon(
                    name=self.icon_name,
                    size=18,
                    color=get_text_color(self.page, "secondary"),
                )
            )

        label_controls.append(
            ft.Text(
                self.label,
                size=14,
                color=get_text_color(self.page, "primary"),
            )
        )

        label_row = ft.Row(
            controls=label_controls,
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Build column
        controls = [label_row, self.dropdown]

        if self.descriptions:
            controls.append(self.description_text)

        return ft.Column(
            controls=controls,
            spacing=4,
            tight=True,
        )

    def _handle_change(self, e):
        """Handle dropdown selection change."""
        self.current_value = e.control.value

        # Update description if available
        if self.descriptions:
            description = self.descriptions.get(self.current_value, "")
            self.description_text.value = description
            self.description_text.visible = bool(description)
            self.description_text.update()

        if self.on_change_callback:
            self.on_change_callback(self.current_value)

    def get_value(self) -> str:
        """Get current selected value."""
        return self.current_value

    def set_value(self, value: str) -> None:
        """
        Set dropdown value programmatically.

        Args:
            value: Key to select
        """
        # Verify value is valid
        valid_keys = [key for key, _ in self.options]
        if value not in valid_keys:
            return

        self.current_value = value
        self.dropdown.value = value

        # Update description
        if self.descriptions:
            description = self.descriptions.get(value, "")
            self.description_text.value = description
            self.description_text.visible = bool(description)

        if hasattr(self, "page") and self.page:
            self.update()

    def refresh_theme(self) -> None:
        """Refresh component colors when theme changes."""
        colors = get_theme_colors(self.page)

        # Update dropdown colors
        self.dropdown.fill_color = get_background_color(self.page, "variant")
        self.dropdown.bgcolor = get_background_color(self.page, "surface")
        self.dropdown.color = get_text_color(self.page, "primary")
        self.dropdown.border_color = get_outline_color(self.page)
        self.dropdown.focused_border_color = colors.PRIMARY

        # Update description text
        self.description_text.color = get_text_color(self.page, "secondary")

        # Rebuild content to refresh all text colors
        self.content = self._build_content()

        if hasattr(self, "page") and self.page:
            self.update()
