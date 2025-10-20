"""File protection utilities for managing read-only attributes."""

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import win32api
import win32con

logger = logging.getLogger(__name__)


class FileProtector:
    """Manage Windows file attributes for protection."""

    @staticmethod
    def set_readonly(file_path: Path) -> bool:
        """
        Set file to read-only.

        Args:
            file_path: Path to the file

        Returns:
            True if successful, False otherwise
        """
        try:
            attrs = win32api.GetFileAttributes(str(file_path))
            new_attrs = attrs | win32con.FILE_ATTRIBUTE_READONLY
            win32api.SetFileAttributes(str(file_path), new_attrs)

            # Verify
            verify_attrs = win32api.GetFileAttributes(str(file_path))
            is_readonly = bool(verify_attrs & win32con.FILE_ATTRIBUTE_READONLY)

            if is_readonly:
                logger.info(f"Set read-only: {file_path}")
            return is_readonly

        except Exception as e:
            logger.error(f"Failed to set read-only on {file_path}: {e}")
            return False

    @staticmethod
    def remove_readonly(file_path: Path) -> bool:
        """
        Remove read-only attribute from file.

        Args:
            file_path: Path to the file

        Returns:
            True if successful, False otherwise
        """
        try:
            attrs = win32api.GetFileAttributes(str(file_path))
            new_attrs = attrs & ~win32con.FILE_ATTRIBUTE_READONLY
            win32api.SetFileAttributes(str(file_path), new_attrs)

            # Verify
            verify_attrs = win32api.GetFileAttributes(str(file_path))
            is_readonly = bool(verify_attrs & win32con.FILE_ATTRIBUTE_READONLY)

            if not is_readonly:
                logger.info(f"Removed read-only: {file_path}")
            return not is_readonly

        except Exception as e:
            logger.error(f"Failed to remove read-only from {file_path}: {e}")
            return False

    @staticmethod
    def is_readonly(file_path: Path) -> bool:
        """
        Check if file is read-only.

        Args:
            file_path: Path to the file

        Returns:
            True if read-only, False otherwise
        """
        try:
            attrs = win32api.GetFileAttributes(str(file_path))
            return bool(attrs & win32con.FILE_ATTRIBUTE_READONLY)
        except Exception as e:
            logger.error(f"Failed to check read-only status for {file_path}: {e}")
            return False

    @staticmethod
    @contextmanager
    def temporary_writable(file_path: Path) -> Generator[Path, None, None]:
        """
        Context manager to temporarily make file writable.

        Args:
            file_path: Path to the file

        Yields:
            Path object

        Example:
            with FileProtector.temporary_writable(config_path):
                # File is writable here
                with open(config_path, 'w') as f:
                    f.write(content)
            # File is read-only again here (if it was before)
        """
        file_path = Path(file_path)

        # Store original attributes
        try:
            original_attrs = win32api.GetFileAttributes(str(file_path))
            was_readonly = bool(original_attrs & win32con.FILE_ATTRIBUTE_READONLY)
        except Exception as e:
            logger.error(f"Failed to get file attributes: {e}")
            was_readonly = False
            original_attrs = None

        try:
            # Remove read-only if set
            if was_readonly:
                new_attrs = original_attrs & ~win32con.FILE_ATTRIBUTE_READONLY
                win32api.SetFileAttributes(str(file_path), new_attrs)
                logger.debug(f"Temporarily removed read-only: {file_path}")

            yield file_path

        finally:
            # Restore original attributes
            if was_readonly and original_attrs is not None:
                try:
                    win32api.SetFileAttributes(str(file_path), original_attrs)
                    logger.debug(f"Restored read-only: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to restore read-only attribute: {e}")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    test_file = Path("test.txt")

    # Create test file
    test_file.write_text("test content")

    # Set read-only
    FileProtector.set_readonly(test_file)
    print(f"Is read-only: {FileProtector.is_readonly(test_file)}")

    # Use context manager
    with FileProtector.temporary_writable(test_file):
        print(f"During context: {FileProtector.is_readonly(test_file)}")
        test_file.write_text("modified content")

    print(f"After context: {FileProtector.is_readonly(test_file)}")

    # Cleanup
    FileProtector.remove_readonly(test_file)
    test_file.unlink()
