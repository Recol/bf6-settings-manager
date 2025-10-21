"""Setting card component with collapsible content."""

import flet as ft
from typing import Optional, List, Union
from ..theme_utils import get_background_color, get_text_color, get_outline_color, is_dark_theme
from .status_chip import StatusChip


class SettingCard(ft.Card):
    """
    A collapsible card for grouping related settings.

    Features:
    - Header with icon, title, subtitle, and status chip
    - Collapsible content with smooth animations
    - Border and shadow effects
    - Theme-aware styling
    - Hover effects
    """

    def __init__(
        self,
        page: ft.Page,
        title: str,
        icon: str,
        icon_color: str,
        subtitle: Optional[str] = None,
        status_chip: Optional[StatusChip] = None,
        content: Optional[Union[ft.Control, List[ft.Control]]] = None,
        expanded: bool = True,
        collapsible: bool = True,
        **kwargs
    ):
        """
        Initialize setting card.

        Args:
            page: Flet page for theme access
            title: Card title
            icon: Material Icon name for card header
            icon_color: Color for the icon
            subtitle: Optional subtitle text
            status_chip: Optional status chip to display in header
            content: Card content (single control or list of controls)
            expanded: Initial expansion state
            collapsible: If True, card can be collapsed
            **kwargs: Additional Card properties
        """
        self.page = page
        self.title = title
        self.icon_name = icon
        self.icon_color = icon_color
        self.subtitle = subtitle
        self.status_chip = status_chip
        self.card_content = content
        self.is_expanded = expanded
        self.is_collapsible = collapsible

        # Create expand button if collapsible
        self.expand_button = None
        if collapsible:
            self.expand_button = ft.IconButton(
                icon=ft.Icons.EXPAND_LESS if expanded else ft.Icons.EXPAND_MORE,
                icon_size=20,
                tooltip="Collapse" if expanded else "Expand",
                on_click=self._toggle_expand,
            )

        # Build card
        card_container = self._build_card()

        # Initialize Card
        super().__init__(
            elevation=2,
            content=card_container,
            **kwargs
        )

    def _build_card(self) -> ft.Container:
        """Build the complete card structure."""
        # Build header
        header = self._build_header()

        # Build content section
        content_section = self._build_content_section()

        # Combine
        return ft.Container(
            content=ft.Column(
                controls=[
                    header,
                    content_section,
                ],
                spacing=0,
                tight=True,
            ),
            bgcolor=get_background_color(self.page, "surface"),
            border=ft.border.all(1, get_outline_color(self.page)),
            border_radius=ft.border_radius.all(12),
            padding=20,
        )

    def _build_header(self) -> ft.Row:
        """Build card header with icon, title, and status chip."""
        header_controls = []

        # Icon
        header_controls.append(
            ft.Icon(
                name=self.icon_name,
                size=24,
                color=self.icon_color,
            )
        )

        # Title and subtitle column
        title_column = ft.Column(
            controls=[
                ft.Text(
                    self.title,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=get_text_color(self.page, "primary"),
                )
            ],
            spacing=2,
            expand=True,
        )

        if self.subtitle:
            title_column.controls.append(
                ft.Text(
                    self.subtitle,
                    size=13,
                    color=get_text_color(self.page, "secondary"),
                )
            )

        header_controls.append(title_column)

        # Status chip (if provided)
        if self.status_chip:
            header_controls.append(self.status_chip)

        # Expand button (if collapsible)
        if self.expand_button:
            header_controls.append(self.expand_button)

        return ft.Row(
            controls=header_controls,
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    def _build_content_section(self) -> ft.Container:
        """Build the collapsible content section."""
        if not self.card_content:
            return ft.Container(height=0, visible=False)

        # Wrap content in column if it's a list
        if isinstance(self.card_content, list):
            content_control = ft.Column(
                controls=self.card_content,
                spacing=8,
            )
        else:
            content_control = self.card_content

        return ft.Container(
            content=content_control,
            margin=ft.margin.only(top=16),
            visible=self.is_expanded,
            animate_opacity=ft.Animation(300, "easeOutCubic"),
            animate_size=ft.Animation(300, "easeOutCubic"),
        )

    def _toggle_expand(self, e):
        """Toggle card expansion state."""
        self.is_expanded = not self.is_expanded

        # Update expand button icon
        if self.expand_button:
            self.expand_button.icon = ft.Icons.EXPAND_LESS if self.is_expanded else ft.Icons.EXPAND_MORE
            self.expand_button.tooltip = "Collapse" if self.is_expanded else "Expand"

        # Toggle content visibility
        content_section = self.content.content.controls[1]  # Second element is content section
        content_section.visible = self.is_expanded

        # Update the card instead of individual controls
        if hasattr(self, 'page') and self.page:
            self.update()

    def set_expanded(self, expanded: bool):
        """
        Set expansion state programmatically.

        Args:
            expanded: New expansion state
        """
        if self.is_expanded != expanded:
            self._toggle_expand(None)

    def update_status_chip(self, text: str, status: Optional[str] = None):
        """
        Update the status chip.

        Args:
            text: New chip text
            status: Optional new status type
        """
        if self.status_chip:
            self.status_chip.update_status(text, status)

    def refresh_theme(self):
        """Refresh the card when theme changes."""
        # Refresh all setting rows in card content
        if self.card_content:
            if isinstance(self.card_content, list):
                for item in self.card_content:
                    if hasattr(item, 'refresh_theme'):
                        item.refresh_theme()
            elif hasattr(self.card_content, 'refresh_theme'):
                self.card_content.refresh_theme()

        # Rebuild the card
        self.content = self._build_card()

        # Refresh status chip
        if self.status_chip:
            self.status_chip.refresh_theme()

        if hasattr(self, 'page') and self.page:
            self.update()

    def add_content(self, new_content: Union[ft.Control, List[ft.Control]]):
        """
        Add additional content to the card.

        Args:
            new_content: Control or list of controls to add
        """
        if isinstance(self.card_content, list):
            if isinstance(new_content, list):
                self.card_content.extend(new_content)
            else:
                self.card_content.append(new_content)
        else:
            if isinstance(new_content, list):
                self.card_content = [self.card_content] + new_content
            else:
                self.card_content = [self.card_content, new_content]

        # Rebuild
        self.content = self._build_card()
        if hasattr(self, 'page') and self.page:
            self.update()
