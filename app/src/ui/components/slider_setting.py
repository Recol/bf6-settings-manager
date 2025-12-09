"""Slider setting component for numeric value selection."""

import flet as ft
from typing import Callable, Optional

from ..theme_utils import (
    get_background_color,
    get_text_color,
    get_outline_color,
    get_theme_colors,
)


class SliderSetting(ft.Container):
    """
    A slider setting component with label, value display, and optional warning.

    Features:
    - Material-styled slider with theme support
    - Live value display during drag
    - Optional suffix (e.g., " FPS", "%")
    - Optional warning text for performance notes
    - Theme-aware colors
    """

    def __init__(
        self,
        page: ft.Page,
        label: str,
        min_val: float,
        max_val: float,
        initial_value: float,
        step: float = 1.0,
        suffix: str = "",
        decimals: int = 0,
        on_change: Optional[Callable[[float], None]] = None,
        on_change_end: Optional[Callable[[float], None]] = None,
        warning_text: Optional[str] = None,
        icon: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize slider setting.

        Args:
            page: Flet page for theme access
            label: Setting label text
            min_val: Minimum slider value
            max_val: Maximum slider value
            initial_value: Initial slider value
            step: Step increment (default 1.0)
            suffix: Suffix for value display (e.g., " FPS")
            decimals: Number of decimal places to display
            on_change: Callback during slider drag (for live preview)
            on_change_end: Callback when slider released (for saving)
            warning_text: Optional warning text to display
            icon: Optional Material Icon name
            **kwargs: Additional Container properties
        """
        self.page = page
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.current_value = initial_value
        self.step = step
        self.suffix = suffix
        self.decimals = decimals
        self.on_change_callback = on_change
        self.on_change_end_callback = on_change_end
        self.warning_text = warning_text
        self.icon_name = icon

        # Calculate divisions for step
        self.divisions = int((max_val - min_val) / step) if step > 0 else None

        # Create components
        self.value_text = self._create_value_text()
        self.slider = self._create_slider(initial_value)
        self.warning_container = self._create_warning() if warning_text else None

        # Build content
        content = self._build_content()

        super().__init__(
            content=content,
            padding=ft.padding.symmetric(horizontal=4, vertical=4),
            **kwargs,
        )

    def _format_value(self, value: float) -> str:
        """Format value for display."""
        if self.decimals == 0:
            return f"{int(value)}{self.suffix}"
        else:
            return f"{value:.{self.decimals}f}{self.suffix}"

    def _create_value_text(self) -> ft.Text:
        """Create the value display text."""
        colors = get_theme_colors(self.page)
        return ft.Text(
            self._format_value(self.current_value),
            size=14,
            weight=ft.FontWeight.W_500,
            color=colors.PRIMARY,
        )

    def _create_slider(self, initial_value: float) -> ft.Slider:
        """Create the slider control."""
        colors = get_theme_colors(self.page)
        return ft.Slider(
            min=self.min_val,
            max=self.max_val,
            divisions=self.divisions,
            value=initial_value,
            label="{value}",
            active_color=colors.PRIMARY,
            inactive_color=get_outline_color(self.page),
            thumb_color=colors.PRIMARY,
            on_change=self._handle_change,
            on_change_end=self._handle_change_end,
            expand=True,
        )

    def _create_warning(self) -> ft.Container:
        """Create warning info container."""
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.INFO_OUTLINE,
                        size=14,
                        color=get_text_color(self.page, "secondary"),
                    ),
                    ft.Text(
                        self.warning_text,
                        size=11,
                        color=get_text_color(self.page, "secondary"),
                        italic=True,
                    ),
                ],
                spacing=4,
            ),
            padding=ft.padding.only(top=4),
        )

    def _build_content(self) -> ft.Column:
        """Build the complete slider content."""
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
                expand=True,
            )
        )
        label_controls.append(self.value_text)

        label_row = ft.Row(
            controls=label_controls,
            spacing=8,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Slider row with min/max labels
        slider_row = ft.Row(
            controls=[
                ft.Text(
                    self._format_value(self.min_val),
                    size=11,
                    color=get_text_color(self.page, "hint"),
                ),
                self.slider,
                ft.Text(
                    self._format_value(self.max_val),
                    size=11,
                    color=get_text_color(self.page, "hint"),
                ),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Build column
        controls = [label_row, slider_row]
        if self.warning_container:
            controls.append(self.warning_container)

        return ft.Column(
            controls=controls,
            spacing=0,
            tight=True,
        )

    def _handle_change(self, e):
        """Handle slider value change during drag."""
        self.current_value = e.control.value
        self.value_text.value = self._format_value(self.current_value)
        self.value_text.update()

        if self.on_change_callback:
            self.on_change_callback(self.current_value)

    def _handle_change_end(self, e):
        """Handle slider release (final value)."""
        self.current_value = e.control.value

        if self.on_change_end_callback:
            self.on_change_end_callback(self.current_value)

    def get_value(self) -> float:
        """Get current slider value."""
        return self.current_value

    def set_value(self, value: float) -> None:
        """
        Set slider value programmatically.

        Args:
            value: New value to set
        """
        # Clamp value to valid range
        value = max(self.min_val, min(self.max_val, value))
        self.current_value = value
        self.slider.value = value
        self.value_text.value = self._format_value(value)

        if hasattr(self, "page") and self.page:
            self.update()

    def refresh_theme(self) -> None:
        """Refresh component colors when theme changes."""
        colors = get_theme_colors(self.page)

        # Update slider colors
        self.slider.active_color = colors.PRIMARY
        self.slider.inactive_color = get_outline_color(self.page)
        self.slider.thumb_color = colors.PRIMARY

        # Update value text
        self.value_text.color = colors.PRIMARY

        # Rebuild content to refresh all text colors
        self.content = self._build_content()

        if hasattr(self, "page") and self.page:
            self.update()
