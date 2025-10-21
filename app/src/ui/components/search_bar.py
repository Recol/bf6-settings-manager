"""Search bar component for filtering settings."""

import flet as ft
from typing import Optional, Callable
from ..theme_utils import get_text_color, get_background_color, get_outline_color


class SearchBar(ft.Container):
    """
    Search bar for filtering settings and cards.

    Features:
    - Real-time search with debouncing
    - Clear button
    - Search icon
    - Theme-aware styling
    """

    def __init__(
        self,
        page: ft.Page,
        hint_text: str = "Search settings...",
        on_search: Optional[Callable[[str], None]] = None,
        debounce_ms: int = 300,
        **kwargs
    ):
        """
        Initialize search bar.

        Args:
            page: Flet page for theme access
            hint_text: Placeholder text
            on_search: Callback when search text changes (after debounce)
            debounce_ms: Debounce delay in milliseconds
            **kwargs: Additional Container properties
        """
        self.page = page
        self.hint_text = hint_text
        self.on_search_callback = on_search
        self.debounce_ms = debounce_ms
        self.debounce_timer = None

        # Create search field
        self.search_field = ft.TextField(
            hint_text=hint_text,
            prefix_icon=ft.Icons.SEARCH,
            suffix=self._create_clear_button(),
            border_color=get_outline_color(page),
            focused_border_color=get_text_color(page, "primary"),
            on_change=self._handle_search_change,
            text_size=14,
        )

        # Build container
        content = self._build_content()

        super().__init__(
            content=content,
            **kwargs
        )

    def _build_content(self) -> ft.Control:
        """Build search bar content."""
        return self.search_field

    def _create_clear_button(self) -> ft.IconButton:
        """Create clear button for search field."""
        return ft.IconButton(
            icon=ft.Icons.CLEAR,
            icon_size=18,
            tooltip="Clear search",
            on_click=self._clear_search,
            visible=False,  # Hidden when empty
        )

    def _handle_search_change(self, e):
        """Handle search text change with debouncing."""
        search_text = e.control.value

        # Show/hide clear button
        if self.search_field.suffix:
            self.search_field.suffix.visible = len(search_text) > 0
            self.search_field.update()

        # Cancel existing timer
        if self.debounce_timer:
            self.debounce_timer.cancel()

        # Set new timer for debounced search
        import threading
        self.debounce_timer = threading.Timer(
            self.debounce_ms / 1000.0,
            lambda: self._execute_search(search_text)
        )
        self.debounce_timer.start()

    def _execute_search(self, search_text: str):
        """Execute search callback."""
        if self.on_search_callback:
            self.on_search_callback(search_text)

    def _clear_search(self, e):
        """Clear search field."""
        self.search_field.value = ""
        if self.search_field.suffix:
            self.search_field.suffix.visible = False
        self.search_field.update()

        # Trigger search with empty string
        if self.on_search_callback:
            self.on_search_callback("")

    def get_search_text(self) -> str:
        """Get current search text."""
        return self.search_field.value or ""

    def set_search_text(self, text: str):
        """
        Set search text programmatically.

        Args:
            text: New search text
        """
        self.search_field.value = text
        if self.search_field.suffix:
            self.search_field.suffix.visible = len(text) > 0
        self.search_field.update()

        # Trigger search
        if self.on_search_callback:
            self.on_search_callback(text)

    def refresh_theme(self):
        """Refresh the search bar when theme changes."""
        self.search_field.border_color = get_outline_color(self.page)
        self.search_field.focused_border_color = get_text_color(self.page, "primary")
        if hasattr(self, 'page') and self.page:
            self.search_field.update()
