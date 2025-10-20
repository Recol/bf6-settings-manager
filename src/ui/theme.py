"""Theme configuration for the UI."""

import flet as ft


def get_theme_colors(is_dark: bool) -> dict:
    """Get theme colors based on mode."""
    if is_dark:
        return {
            "bg": "#1a1a1a",
            "surface": "#2d2d2d",
            "primary": "#4a9eff",
            "success": "#4caf50",
            "warning": "#ff9800",
            "error": "#f44336",
            "text": "#ffffff",
            "text_secondary": "#b0b0b0",
        }
    else:
        return {
            "bg": "#f5f5f5",
            "surface": "#ffffff",
            "primary": "#1976d2",
            "success": "#388e3c",
            "warning": "#f57c00",
            "error": "#d32f2f",
            "text": "#212121",
            "text_secondary": "#757575",
        }


def configure_page_theme(page: ft.Page) -> None:
    """Configure page theme settings."""
    page.theme_mode = ft.ThemeMode.DARK  # Default to dark
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        use_material3=True,
    )
    page.padding = 0
    page.spacing = 0
