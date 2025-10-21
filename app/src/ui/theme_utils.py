"""
Theme utilities for consistent theming across the application.
Provides theme detection, color constants, and helper functions for light/dark mode support.

Adapted from Project Matrix design patterns for BF6 Settings Manager.
"""

import flet as ft
from typing import Optional


class ThemeColors:
    """Color constants for light and dark themes with accessibility-compliant contrast ratios."""

    # Light Theme Colors
    class Light:
        # Backgrounds
        MAIN_BACKGROUND = "#f5f5f5"          # Light gray background
        SURFACE = "#ffffff"                   # Pure white for cards/panels
        SURFACE_CONTAINER = "#fafafa"        # Off-white container
        SURFACE_VARIANT = "#f0f0f0"          # Light gray surfaces

        # Text Colors
        PRIMARY_TEXT = "#212121"             # High contrast text
        SECONDARY_TEXT = "#757575"           # Secondary info
        DISABLED_TEXT = "#9e9e9e"            # Disabled elements
        HINT_TEXT = "#bdbdbd"                # Placeholder text

        # Borders & Outlines
        OUTLINE = "#e0e0e0"                  # Card borders
        OUTLINE_VARIANT = "#eeeeee"          # Subtle divisions

        # Status Colors
        SUCCESS = "#388e3c"                  # Green (enabled/success)
        WARNING = "#f57c00"                  # Orange (warning/partial)
        ERROR = "#d32f2f"                    # Red (error/disabled)
        INFO = "#0288d1"                     # Blue (informational)

        # Interactive Colors
        PRIMARY = "#1976d2"                  # Primary blue
        SECONDARY = "#7b1fa2"                # Secondary purple
        PRIMARY_CONTAINER = "#e3f2fd"        # Light blue background
        SECONDARY_CONTAINER = "#f3e5f5"      # Light purple background

        # Chip Colors
        CHIP_BACKGROUND = "#e3f2fd"          # Light blue chip background
        CHIP_TEXT = "#1565c0"                # Dark blue chip text

    # Dark Theme Colors
    class Dark:
        # Backgrounds
        MAIN_BACKGROUND = "#1a1a1a"          # Main dark background
        SURFACE = "#2d2d2d"                  # Card/panel backgrounds
        SURFACE_CONTAINER = "#353535"        # Container surfaces
        SURFACE_VARIANT = "#404040"          # Variant surfaces

        # Text Colors
        PRIMARY_TEXT = "#ffffff"             # White text
        SECONDARY_TEXT = "#b0b0b0"           # Light gray
        DISABLED_TEXT = "#666666"            # Darker gray
        HINT_TEXT = "#888888"                # Hint text

        # Borders & Outlines
        OUTLINE = "#404040"                  # Card borders
        OUTLINE_VARIANT = "#353535"          # Subtle divisions

        # Status Colors
        SUCCESS = "#4caf50"                  # Green (enabled/success)
        WARNING = "#ff9800"                  # Orange (warning/partial)
        ERROR = "#f44336"                    # Red (error/disabled)
        INFO = "#29b6f6"                     # Blue (informational)

        # Interactive Colors
        PRIMARY = "#4a9eff"                  # Primary blue
        SECONDARY = "#ab47bc"                # Secondary purple
        PRIMARY_CONTAINER = "#1565c0"        # Dark blue background
        SECONDARY_CONTAINER = "#6a1b9a"      # Dark purple background

        # Chip Colors
        CHIP_BACKGROUND = "#1e3a5f"          # Dark blue chip background
        CHIP_TEXT = "#64b5f6"                # Light blue chip text


def is_dark_theme(page: ft.Page) -> bool:
    """
    Check if the current theme is dark mode.

    Args:
        page: The Flet page object

    Returns:
        True if dark theme, False if light theme
    """
    return getattr(page, 'theme_mode', ft.ThemeMode.DARK) == ft.ThemeMode.DARK


def get_theme_colors(page: ft.Page) -> type:
    """
    Get the appropriate color scheme based on current theme.

    Args:
        page: The Flet page object

    Returns:
        ThemeColors.Light or ThemeColors.Dark class
    """
    return ThemeColors.Dark if is_dark_theme(page) else ThemeColors.Light


def get_background_color(page: ft.Page, surface_type: str = "main") -> str:
    """
    Get background color for different surface types.

    Args:
        page: The Flet page object
        surface_type: Type of surface ("main", "surface", "container", "variant")

    Returns:
        Hex color string
    """
    colors = get_theme_colors(page)

    surface_map = {
        "main": colors.MAIN_BACKGROUND,
        "surface": colors.SURFACE,
        "container": colors.SURFACE_CONTAINER,
        "variant": colors.SURFACE_VARIANT
    }

    return surface_map.get(surface_type, colors.SURFACE)


def get_text_color(page: ft.Page, text_type: str = "primary") -> str:
    """
    Get text color for different text types.

    Args:
        page: The Flet page object
        text_type: Type of text ("primary", "secondary", "disabled", "hint")

    Returns:
        Hex color string
    """
    colors = get_theme_colors(page)

    text_map = {
        "primary": colors.PRIMARY_TEXT,
        "secondary": colors.SECONDARY_TEXT,
        "disabled": colors.DISABLED_TEXT,
        "hint": colors.HINT_TEXT
    }

    return text_map.get(text_type, colors.PRIMARY_TEXT)


def get_status_color(page: ft.Page, status: str) -> str:
    """
    Get status color (success, warning, error, info).

    Args:
        page: The Flet page object
        status: Status type ("success", "warning", "error", "info")

    Returns:
        Hex color string
    """
    colors = get_theme_colors(page)

    status_map = {
        "success": colors.SUCCESS,
        "warning": colors.WARNING,
        "error": colors.ERROR,
        "info": colors.INFO
    }

    return status_map.get(status, colors.INFO)


def get_outline_color(page: ft.Page, variant: bool = False) -> str:
    """
    Get outline/border color.

    Args:
        page: The Flet page object
        variant: If True, returns secondary outline color

    Returns:
        Hex color string
    """
    colors = get_theme_colors(page)
    return colors.OUTLINE_VARIANT if variant else colors.OUTLINE


def get_chip_colors(page: ft.Page) -> tuple[str, str]:
    """
    Get chip background and text colors.

    Args:
        page: The Flet page object

    Returns:
        Tuple of (background_color, text_color)
    """
    colors = get_theme_colors(page)
    return colors.CHIP_BACKGROUND, colors.CHIP_TEXT


def update_page_theme(page: ft.Page, theme_mode: ft.ThemeMode) -> None:
    """
    Update the page theme and apply appropriate colors.

    Args:
        page: The Flet page object
        theme_mode: The theme mode to apply
    """
    page.theme_mode = theme_mode

    # Update page background
    page.bgcolor = get_background_color(page, "main")

    # Update the theme configuration with Material Design 3
    colors = get_theme_colors(page)

    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=colors.PRIMARY,
            secondary=colors.SECONDARY,
            surface=colors.SURFACE,
            background=colors.MAIN_BACKGROUND,
            on_surface=colors.PRIMARY_TEXT,
            on_background=colors.PRIMARY_TEXT,
            surface_variant=colors.SURFACE_VARIANT,
            outline=colors.OUTLINE,
            outline_variant=colors.OUTLINE_VARIANT,
        ),
        use_material3=True,
    )

    page.update()


def apply_theme_to_container(
    page: ft.Page,
    container: ft.Container,
    surface_type: str = "surface",
    text_type: str = "primary"
) -> ft.Container:
    """
    Apply theme-appropriate colors to a container.

    Args:
        page: The Flet page object
        container: The container to apply theme to
        surface_type: Type of surface for background
        text_type: Type of text for content

    Returns:
        The modified container
    """
    container.bgcolor = get_background_color(page, surface_type)

    # Apply text color if container has content with color property
    if hasattr(container.content, 'color'):
        container.content.color = get_text_color(page, text_type)

    return container
