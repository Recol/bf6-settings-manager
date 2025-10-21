"""Status chip component for displaying status indicators."""

import flet as ft
from typing import Optional
from ..theme_utils import get_chip_colors, get_status_color, get_text_color


class StatusChip(ft.Container):
    """
    A compact status indicator chip with color coding.

    Features:
    - Color-coded status (success=green, warning=orange, error=red, info=blue)
    - Optional icon
    - Compact design
    - Theme-aware colors
    """

    def __init__(
        self,
        page: ft.Page,
        text: str,
        status: str = "info",  # "success", "warning", "error", "info"
        icon: Optional[str] = None,
        compact: bool = True,
        **kwargs
    ):
        """
        Initialize status chip.

        Args:
            page: Flet page for theme access
            text: Chip text content
            status: Status type (success, warning, error, info)
            icon: Optional Material Icon name
            compact: If True, use compact padding
            **kwargs: Additional Container properties
        """
        self.page = page
        self.chip_text = text
        self.status = status
        self.icon_name = icon
        self.compact = compact

        # Build chip content
        content = self._build_content()

        # Get status color
        status_color = get_status_color(page, status)

        # Initialize container
        super().__init__(
            content=content,
            bgcolor=self._get_background_color(status_color),
            border_radius=ft.border_radius.all(12),
            padding=ft.padding.symmetric(horizontal=8, vertical=4) if compact else ft.padding.all(8),
            **kwargs
        )

    def _build_content(self) -> ft.Row:
        """Build the chip content with optional icon."""
        controls = []

        # Add icon if provided
        if self.icon_name:
            controls.append(
                ft.Icon(
                    name=self.icon_name,
                    size=14,
                    color=self._get_text_color(),
                )
            )

        # Add text
        controls.append(
            ft.Text(
                self.chip_text,
                size=12,
                weight=ft.FontWeight.W_500,
                color=self._get_text_color(),
            )
        )

        return ft.Row(
            controls=controls,
            spacing=4,
            tight=True,
        )

    def _get_background_color(self, status_color: str) -> str:
        """Get background color with opacity based on status."""
        # For dark theme, use semi-transparent status color
        # For light theme, use lighter tint
        if self.status == "success":
            return status_color + "40" if hasattr(self.page, 'theme_mode') and self.page.theme_mode == ft.ThemeMode.DARK else "#e8f5e9"
        elif self.status == "warning":
            return status_color + "40" if hasattr(self.page, 'theme_mode') and self.page.theme_mode == ft.ThemeMode.DARK else "#fff3e0"
        elif self.status == "error":
            return status_color + "40" if hasattr(self.page, 'theme_mode') and self.page.theme_mode == ft.ThemeMode.DARK else "#ffebee"
        else:  # info
            return status_color + "40" if hasattr(self.page, 'theme_mode') and self.page.theme_mode == ft.ThemeMode.DARK else "#e3f2fd"

    def _get_text_color(self) -> str:
        """Get text color based on status."""
        # Use the status color directly for text
        return get_status_color(self.page, self.status)

    def update_status(self, new_text: str, new_status: Optional[str] = None):
        """
        Update chip text and optionally status.

        Args:
            new_text: New text to display
            new_status: Optional new status type
        """
        self.chip_text = new_text
        if new_status:
            self.status = new_status

        # Rebuild content
        self.content = self._build_content()
        self.bgcolor = self._get_background_color(get_status_color(self.page, self.status))

        # Update if attached to page
        if hasattr(self, 'page') and self.page:
            self.update()

    def refresh_theme(self):
        """Refresh the chip when theme changes."""
        self.content = self._build_content()
        self.bgcolor = self._get_background_color(get_status_color(self.page, self.status))
        if hasattr(self, 'page') and self.page:
            self.update()
