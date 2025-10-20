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

        # Check and request admin privileges
        from src.admin import is_admin, run_as_admin

        if not is_admin():
            logger.warning("Not running as administrator")
            logger.info("Requesting admin privileges...")
            try:
                run_as_admin()
                # If we get here, elevation failed or was cancelled
                logger.warning("Continuing without admin privileges (some features may not work)")
            except Exception as e:
                logger.warning(f"Admin elevation failed: {e}")
                logger.warning("Continuing without admin privileges")

        from src.ui.main_window import main as ui_main

        # Launch Flet app
        ft.app(target=ui_main)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
