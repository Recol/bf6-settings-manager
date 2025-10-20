"""Admin privileges handling for Battlefield 6 Settings Manager."""

import ctypes
import logging
import subprocess
import sys

logger = logging.getLogger(__name__)


def is_admin() -> bool:
    """Check if the current process has admin privileges."""
    if sys.platform != "win32":
        return False

    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    """Restart the current program with admin privileges."""
    if sys.platform != "win32":
        raise OSError("Admin elevation only supported on Windows")

    if is_admin():
        logger.info("Already running with admin privileges")
        return

    # Get the executable path
    if getattr(sys, 'frozen', False):
        # Running as compiled executable (Briefcase, PyInstaller, etc.)
        executable = sys.executable
        args = sys.argv[1:]
        logger.info(f"Detected compiled executable: {executable}")
    else:
        # Running as Python script
        executable = sys.executable
        args = [sys.argv[0]] + sys.argv[1:]
        logger.info(f"Detected Python script execution: {executable} {args[0]}")

    # Prepare the command
    cmd = [executable] + args
    cmd_line = subprocess.list2cmdline(cmd)

    logger.info(f"Requesting admin privileges for: {cmd_line}")

    try:
        # Use ShellExecute to run with elevated privileges
        result = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",           # Verb to request elevation
            executable,        # Program to run
            subprocess.list2cmdline(args) if args else None,  # Arguments
            None,              # Working directory (use current)
            1                  # SW_SHOWNORMAL - show window normally
        )

        # ShellExecute returns a handle; values > 32 indicate success
        if result > 32:
            logger.info("Successfully requested elevation, exiting current process")
            # Exit the current process - the elevated process will take over
            sys.exit(0)
        else:
            error_msg = f"ShellExecute failed with return code: {result}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    except Exception as e:
        error_msg = f"Failed to elevate privileges: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def check_admin_required() -> bool:
    """
    Check if admin privileges are required.

    Returns:
        True if admin is needed but not present, False otherwise
    """
    if not is_admin():
        logger.warning("Running without admin privileges")
        logger.warning("Admin privileges are recommended for:")
        logger.warning("  - Modifying read-only config files")
        logger.warning("  - Setting file attributes")
        return True

    return False
