"""Battlefield 6 Settings Manager - Main entry point."""

import logging
import sys

import flet as ft

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bf6_settings_manager.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    try:
        logger.info("Starting Battlefield 6 Settings Manager")

        from src.ui.main_window import main as ui_main

        # Launch Flet app
        ft.app(target=ui_main)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
