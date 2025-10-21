"""Theme configuration for the UI."""

import flet as ft
from .theme_utils import (
    ThemeColors,
    get_theme_colors,
    get_background_color,
    get_text_color,
    get_status_color,
    update_page_theme,
    is_dark_theme,
)


def configure_page_theme(page: ft.Page, theme_mode: ft.ThemeMode = ft.ThemeMode.DARK) -> None:
    """
    Configure page theme settings with Material Design 3.

    Args:
        page: Flet page to configure
        theme_mode: Initial theme mode (default: DARK)
    """
    # Set initial theme mode
    page.theme_mode = theme_mode

    # Get theme colors
    colors = get_theme_colors(page)

    # Configure light theme
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ThemeColors.Light.PRIMARY,
            secondary=ThemeColors.Light.SECONDARY,
            surface=ThemeColors.Light.SURFACE,
            background=ThemeColors.Light.MAIN_BACKGROUND,
            on_surface=ThemeColors.Light.PRIMARY_TEXT,
            on_background=ThemeColors.Light.PRIMARY_TEXT,
            surface_variant=ThemeColors.Light.SURFACE_VARIANT,
            outline=ThemeColors.Light.OUTLINE,
            outline_variant=ThemeColors.Light.OUTLINE_VARIANT,
        ),
        use_material3=True,
    )

    # Configure dark theme
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ThemeColors.Dark.PRIMARY,
            secondary=ThemeColors.Dark.SECONDARY,
            surface=ThemeColors.Dark.SURFACE,
            background=ThemeColors.Dark.MAIN_BACKGROUND,
            on_surface=ThemeColors.Dark.PRIMARY_TEXT,
            on_background=ThemeColors.Dark.PRIMARY_TEXT,
            surface_variant=ThemeColors.Dark.SURFACE_VARIANT,
            outline=ThemeColors.Dark.OUTLINE,
            outline_variant=ThemeColors.Dark.OUTLINE_VARIANT,
        ),
        use_material3=True,
    )

    # Set page background
    page.bgcolor = get_background_color(page, "main")

    # Remove default padding/spacing
    page.padding = 0
    page.spacing = 0
