"""Backup management dialog for viewing and restoring config backups."""

import logging
from pathlib import Path
from typing import Optional, Callable
from datetime import datetime

import flet as ft

from ..theme_utils import get_text_color, get_background_color, get_status_color

logger = logging.getLogger(__name__)


class BackupDialog:
    """
    Backup management dialog.

    Features:
    - List all backup files
    - Show backup metadata (date, time)
    - Restore from backup
    - Delete old backups
    """

    def __init__(self, page: ft.Page, backup_dir: Path, on_restore: Callable[[Path], None]):
        """
        Initialize backup dialog.

        Args:
            page: Flet page
            backup_dir: Directory containing backup files
            on_restore: Callback when backup is restored
        """
        self.page = page
        self.backup_dir = backup_dir
        self.on_restore = on_restore
        self.dialog: Optional[ft.AlertDialog] = None

    def show(self):
        """Show the backup dialog."""
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.HISTORY, color=get_status_color(self.page, "info"), size=28),
                ft.Text("Backup Management", size=20),
            ]),
            content=self._build_content(),
            actions=[
                ft.TextButton("Close", on_click=lambda _: self._close()),
            ],
        )

        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    def _build_content(self) -> ft.Container:
        """Build dialog content."""
        # Find backup files
        backup_files = self._find_backups()

        if not backup_files:
            content_controls = [
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.FOLDER_OFF, size=64, color=get_text_color(self.page, "disabled")),
                            ft.Text(
                                "No backups found",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                f"Backups will appear here after applying settings",
                                size=13,
                                color=get_text_color(self.page, "secondary"),
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                f"Backup location: {self.backup_dir}",
                                size=11,
                                color=get_text_color(self.page, "hint"),
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    padding=40,
                )
            ]
        else:
            content_controls = [
                ft.Text(
                    f"Found {len(backup_files)} backup{'s' if len(backup_files) != 1 else ''}",
                    size=14,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Text(
                    "Select a backup to restore",
                    size=12,
                    color=get_text_color(self.page, "secondary"),
                ),
                ft.Divider(),
                ft.Column(
                    controls=[self._create_backup_card(backup) for backup in backup_files],
                    spacing=8,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ]

        return ft.Container(
            content=ft.Column(
                controls=content_controls,
                spacing=12,
            ),
            width=550,
            height=500,
        )

    def _find_backups(self) -> list[Path]:
        """Find all backup files."""
        if not self.backup_dir.exists():
            return []

        # Look for backup files (assuming they follow the pattern from config_manager.py)
        backup_files = list(self.backup_dir.glob("PROFSAVE_profile*.backup"))

        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        return backup_files

    def _create_backup_card(self, backup_path: Path) -> ft.Card:
        """Create a backup card."""
        # Get file stats
        stats = backup_path.stat()
        modified_time = datetime.fromtimestamp(stats.st_mtime)
        file_size = stats.st_size / 1024  # KB

        # Extract timestamp from filename if available
        filename = backup_path.name
        # Example: PROFSAVE_profile_20250120_143022.backup

        # Format display
        time_display = modified_time.strftime("%Y-%m-%d %H:%M:%S")
        size_display = f"{file_size:.1f} KB"

        # Calculate age
        age = datetime.now() - modified_time
        if age.days > 0:
            age_display = f"{age.days} day{'s' if age.days != 1 else ''} ago"
        elif age.seconds > 3600:
            hours = age.seconds // 3600
            age_display = f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif age.seconds > 60:
            minutes = age.seconds // 60
            age_display = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            age_display = "Just now"

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.BACKUP, size=20, color=get_status_color(self.page, "info")),
                                ft.Column(
                                    controls=[
                                        ft.Text(filename, size=13, weight=ft.FontWeight.W_500),
                                        ft.Text(age_display, size=11, color=get_text_color(self.page, "secondary")),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                            ],
                            spacing=12,
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(f"📅 {time_display}", size=11),
                                ft.Text(f"💾 {size_display}", size=11),
                            ],
                            spacing=16,
                        ),
                        ft.Divider(height=1),
                        ft.Row(
                            controls=[
                                ft.ElevatedButton(
                                    "Restore",
                                    icon=ft.Icons.RESTORE,
                                    on_click=lambda _: self._restore_backup(backup_path),
                                ),
                                ft.TextButton(
                                    "Delete",
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    on_click=lambda _: self._delete_backup(backup_path),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=8,
                        ),
                    ],
                    spacing=8,
                ),
                padding=16,
            ),
            elevation=1,
        )

    def _restore_backup(self, backup_path: Path):
        """Restore from a backup."""
        # Show confirmation dialog
        def confirm_restore(e):
            self.page.dialog.open = False
            if self.on_restore:
                self.on_restore(backup_path)
            self._close()

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Restore"),
            content=ft.Text(
                f"Are you sure you want to restore from this backup?\n\n"
                f"File: {backup_path.name}\n\n"
                f"This will replace your current configuration."
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._cancel_restore()),
                ft.ElevatedButton(
                    "Restore",
                    icon=ft.Icons.RESTORE,
                    on_click=confirm_restore,
                ),
            ],
        )

        self.page.dialog = confirm_dialog
        confirm_dialog.open = True
        self.page.update()

    def _cancel_restore(self):
        """Cancel restore and return to backup list."""
        self.page.dialog.open = False
        self.show()

    def _delete_backup(self, backup_path: Path):
        """Delete a backup file."""
        # Show confirmation dialog
        def confirm_delete(e):
            try:
                backup_path.unlink()
                self.page.dialog.open = False
                # Refresh backup list
                self.show()
            except Exception as ex:
                logger.error(f"Failed to delete backup: {ex}")
                # Show error dialog
                error_dialog = ft.AlertDialog(
                    title=ft.Text("Error"),
                    content=ft.Text(f"Failed to delete backup:\n{str(ex)}"),
                    actions=[ft.TextButton("OK", on_click=lambda _: self._cancel_delete())],
                )
                self.page.dialog = error_dialog
                error_dialog.open = True
                self.page.update()

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Delete"),
            content=ft.Text(
                f"Are you sure you want to delete this backup?\n\n"
                f"File: {backup_path.name}\n\n"
                f"This action cannot be undone."
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._cancel_delete()),
                ft.ElevatedButton(
                    "Delete",
                    icon=ft.Icons.DELETE,
                    bgcolor=get_status_color(self.page, "error"),
                    color="#ffffff",
                    on_click=confirm_delete,
                ),
            ],
        )

        self.page.dialog = confirm_dialog
        confirm_dialog.open = True
        self.page.update()

    def _cancel_delete(self):
        """Cancel delete and return to backup list."""
        self.page.dialog.open = False
        self.show()

    def _close(self):
        """Close the dialog."""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
