#!/usr/bin/env python3
"""
Main entry point for Battlefield 6 Settings Manager that works with PyInstaller.
This avoids complex import issues by setting up the path correctly.
"""

import os
import sys
from pathlib import Path


def setup_path():
    """Set up the Python path for both development and compiled execution."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = Path(sys.executable).parent
    else:
        # Running in development
        base_path = Path(__file__).parent

    src_path = base_path / "app/src"

    # Add paths if they exist and aren't already in sys.path
    for path in [str(base_path), str(src_path)]:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)

def main():
    """Main entry point."""
    setup_path()

    # Check and enforce admin privileges before proceeding
    try:
        from app.src.admin import is_admin, run_as_admin

        if not is_admin():
            print("Battlefield 6 Settings Manager requires administrator privileges for full functionality.")
            print("Requesting elevation...")
            run_as_admin()  # This will restart the app with admin privileges and exit current process
            return  # This line should never be reached
        else:
            print("Running with administrator privileges ✓")
    except Exception as e:
        print(f"Error checking/requesting admin privileges: {e}")
        print("Continuing without admin privileges - some features may be limited.")

    # Now start the actual Flet application
    try:
        print("Starting Battlefield 6 Settings Manager UI...")
        import flet as ft
        from app.src.ui.main_window import main as flet_main

        # Run the Flet application
        ft.app(target=flet_main)
    except Exception as e:
        import traceback
        print("\n" + "="*80)
        print("ERROR: Failed to start UI")
        print("="*80)
        print(f"\nError: {str(e)}\n")
        print("Full traceback:")
        traceback.print_exc()
        print("="*80)
        raise  # Re-raise to be caught by outer exception handler

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutdown requested by user (Ctrl+C)")
        input("\nPress Enter to exit...")
        sys.exit(0)
    except ImportError as e:
        import traceback
        print(f"Import Error - Missing dependency or module: {e}")
        print("This usually indicates a missing package or incorrect installation.")
        print("Try running: uv sync  or  pip install -e .")
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
    except PermissionError as e:
        import traceback
        print(f"Permission Error: {e}")
        print("This usually means the application needs to be run as Administrator.")
        print("Try running the batch file: 'project_matrix_admin.bat'")
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
    except FileNotFoundError as e:
        import traceback
        print(f"File Not Found Error: {e}")
        print("This indicates a missing file or incorrect installation.")
        print("Ensure all project files are properly installed.")
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
    except Exception as e:
        import traceback
        print(f"Error starting Battlefield 6 Settings Manager: {e}")
        print("\nFull error details:")
        traceback.print_exc()
        print("\nTroubleshooting tips:")
        print("1. Ensure you're running as Administrator")
        print("2. Check that all dependencies are installed: uv sync")
        print("3. Verify Python version is 3.12+")
        print("4. Check if any antivirus software is blocking the application")
        input("\nPress Enter to exit...")
        sys.exit(1)
