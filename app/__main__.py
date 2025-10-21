#!/usr/bin/env python3
"""
Entry point for Battlefield 6 Settings Manager when run as a Briefcase app.
This imports and runs the main function from src.ui.main_window.
"""

def check_and_request_admin():
    """Check if running as admin and automatically request elevation if needed."""
    import sys

    if sys.platform != "win32":
        return True  # No UAC on non-Windows systems

    try:
        # Import admin functions from core module
        from app.src.admin import is_admin, run_as_admin

        if is_admin():
            print("Running with administrator privileges")
            return True
        else:
            print("Battlefield 6 Settings Manager requires administrator privileges for full functionality.")
            print("Requesting elevation...")

            try:
                run_as_admin()  # This will restart with admin privileges and exit current process
                return False  # This line should never be reached
            except Exception as elevation_error:
                print(f"Failed to elevate privileges: {elevation_error}")
                print("Please manually run Battlefield 6 Settings Manager as Administrator.")
                print("Right-click the app and select 'Run as administrator'")

                # Ask user if they want to continue without admin
                import time
                print("\nThe application will exit in 10 seconds unless you want to continue without admin privileges.")
                print("Press Enter to continue anyway (limited functionality) or wait to exit...")

                # Simple timeout mechanism for packaged apps
                try:
                    import select
                    import sys
                    if select.select([sys.stdin], [], [], 10):
                        sys.stdin.readline()  # User pressed Enter
                        print("Continuing without admin privileges - some features may be limited.")
                        return False
                    else:
                        print("Exiting...")
                        sys.exit(1)
                except:
                    # Fallback for Windows where select might not work with stdin
                    time.sleep(10)
                    print("Exiting...")
                    sys.exit(1)

    except ImportError as e:
        print(f"Could not import admin functions: {e}")
        print("Continuing without admin check - some features may be limited.")
        return False
    except Exception as e:
        print(f"Error checking admin status: {e}")
        return False

def main():
    """Main entry point for the Briefcase application."""
    import sys
    import traceback

    try:
        import flet as ft

        # Check admin status and enforce elevation (may exit if elevation fails)
        admin_status = check_and_request_admin()

        # If we reach here, either we have admin privileges or user chose to continue without them
        if not admin_status:
            print("Note: Running with limited privileges. Some features may not work correctly.")

        # Import the main function from the UI
        from app.src.ui.main_window import main as flet_main

        # Run the Flet application in desktop mode
        ft.app(target=flet_main)

    except Exception as e:
        print("\n" + "="*80)
        print("ERROR: Application failed to start")
        print("="*80)
        print(f"\nError: {str(e)}\n")
        print("Full traceback:")
        traceback.print_exc()
        print("="*80)
        print("\nPress Enter to exit...")
        try:
            input()
        except:
            import time
            time.sleep(30)  # Wait 30 seconds if input() fails
        sys.exit(1)


if __name__ == "__main__":
    import sys
    import traceback

    try:
        main()
    except Exception as e:
        print("\n" + "="*80)
        print("FATAL ERROR: Application crashed")
        print("="*80)
        print(f"\nError: {str(e)}\n")
        print("Full traceback:")
        traceback.print_exc()
        print("="*80)
        print("\nPress Enter to exit...")
        try:
            input()
        except:
            import time
            time.sleep(30)  # Wait 30 seconds if input() fails
        sys.exit(1)
