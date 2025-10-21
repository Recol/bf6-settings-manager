"""Setting row component with icon, checkbox, and label."""

import flet as ft
from typing import Optional, Callable
from ..theme_utils import get_text_color, get_status_color


class SettingRow(ft.Container):
    """
    A setting row with icon, checkbox, and label.

    Features:
    - Material icon prefix
    - Checkbox for enable/disable
    - Descriptive label
    - Hover effects
    - Visual feedback for state
    """

    def __init__(
        self,
        page: ft.Page,
        label: str,
        icon: str,
        value: bool = True,
        on_change: Optional[Callable] = None,
        tooltip: Optional[str] = None,
        icon_color: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize setting row.

        Args:
            page: Flet page for theme access
            label: Setting label text
            icon: Material Icon name
            value: Initial checkbox value
            on_change: Callback when checkbox changes
            tooltip: Optional tooltip text
            icon_color: Optional custom icon color
            **kwargs: Additional Container properties
        """
        self.page = page
        self.label = label
        self.icon_name = icon
        self.checkbox_value = value
        self.on_change_callback = on_change
        self.tooltip_text = tooltip
        self.icon_color = icon_color

        # Create checkbox
        self.checkbox = ft.Checkbox(
            label="",
            value=value,
            on_change=self._handle_change,
        )

        # Build row content
        content = self._build_content()

        # Initialize container with hover support
        super().__init__(
            content=content,
            padding=ft.padding.symmetric(horizontal=4, vertical=2),
            border_radius=ft.border_radius.all(4),
            on_hover=self._on_hover,
            **kwargs
        )

    def _build_content(self) -> ft.Row:
        """Build the row content."""
        # Determine icon color
        if self.icon_color:
            icon_color = self.icon_color
        elif self.checkbox_value:
            icon_color = get_status_color(self.page, "success")
        else:
            icon_color = get_text_color(self.page, "disabled")

        # Create icon
        icon = ft.Icon(
            name=self.icon_name,
            size=20,
            color=icon_color,
        )

        # Create label text
        label_text = ft.Text(
            self.label,
            size=14,
            color=get_text_color(self.page, "primary") if self.checkbox_value else get_text_color(self.page, "disabled"),
        )

        # Wrap in row
        row = ft.Row(
            controls=[
                self.checkbox,
                icon,
                label_text,
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Add tooltip if provided
        if self.tooltip_text:
            return ft.Tooltip(
                message=self.tooltip_text,
                content=row,
            )

        return row

    def _handle_change(self, e):
        """Handle checkbox change."""
        self.checkbox_value = e.control.value

        # Rebuild content to update colors
        self.content = self._build_content()

        # Only update if attached to page
        if hasattr(self, 'page') and self.page:
            self.update()

        # Call user callback
        if self.on_change_callback:
            self.on_change_callback(e)

    def _on_hover(self, e):
        """Handle hover state."""
        if e.data == "true":
            # Mouse entered
            self.bgcolor = ft.Colors.with_opacity(0.05, get_text_color(self.page, "primary"))
        else:
            # Mouse left
            self.bgcolor = None

        # Only update if attached to page
        if hasattr(self, 'page') and self.page:
            self.update()

    def get_value(self) -> bool:
        """Get current checkbox value."""
        return self.checkbox_value

    def set_value(self, value: bool):
        """
        Set checkbox value.

        Args:
            value: New checkbox value
        """
        self.checkbox_value = value
        self.checkbox.value = value

        # Rebuild content
        self.content = self._build_content()

        if hasattr(self, 'page') and self.page:
            self.update()

    def refresh_theme(self):
        """Refresh the row when theme changes."""
        self.content = self._build_content()
        if hasattr(self, 'page') and self.page:
            self.update()
