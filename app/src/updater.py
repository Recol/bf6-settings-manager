"""GitHub releases updater for checking and downloading updates."""

import asyncio
import logging
import os
import tempfile
import webbrowser
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import aiohttp

logger = logging.getLogger(__name__)

# Application constants
GITHUB_OWNER = "Recol"
GITHUB_REPO = "bf6-settings-manager"
MSI_FILE_PREFIX = "Battlefield.6.Settings.Manager"


def _get_version_from_pyproject() -> str:
    """
    Read version from pyproject.toml.

    Returns:
        Version string, or "1.0.0" if not found.
    """
    try:
        import tomllib  # Python 3.11+

        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                return data.get("project", {}).get("version", "1.0.0")
    except ImportError:
        # Python < 3.11, try toml package
        try:
            import toml

            pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "r") as f:
                    data = toml.load(f)
                    return data.get("project", {}).get("version", "1.0.0")
        except ImportError:
            pass
    except Exception as e:
        logger.warning(f"Failed to read version from pyproject.toml: {e}")

    return "1.0.0"


CURRENT_VERSION = _get_version_from_pyproject()


def compare_versions(current: str, latest: str) -> bool:
    """
    Compare semantic version strings.

    Args:
        current: Current version string (e.g., "1.0.0")
        latest: Latest version string (e.g., "1.0.1")

    Returns:
        True if latest is newer than current, False otherwise.
    """
    try:
        # Strip 'v' prefix if present
        current_clean = current.lstrip("v")
        latest_clean = latest.lstrip("v")

        # Parse version parts
        current_parts = [int(x) for x in current_clean.split(".")]
        latest_parts = [int(x) for x in latest_clean.split(".")]

        # Pad shorter version with zeros
        max_len = max(len(current_parts), len(latest_parts))
        current_parts.extend([0] * (max_len - len(current_parts)))
        latest_parts.extend([0] * (max_len - len(latest_parts)))

        return latest_parts > current_parts

    except (ValueError, AttributeError) as e:
        logger.error(f"Error comparing versions: {e}")
        return False


class UpdateChecker:
    """Check for application updates via GitHub releases."""

    def __init__(self, current_version: str = CURRENT_VERSION):
        """
        Initialize update checker.

        Args:
            current_version: Current application version
        """
        self.current_version = current_version
        self.api_url = (
            f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
        )
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def check_for_updates(self) -> Dict[str, Any]:
        """
        Check GitHub for latest release.

        Returns:
            Dictionary with:
                - update_available: bool
                - latest_version: str or None
                - download_url: str or None
                - release_notes: str or None
                - error: str or None
        """
        result = {
            "update_available": False,
            "latest_version": None,
            "download_url": None,
            "release_notes": None,
            "error": None,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.api_url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 404:
                        # No releases yet
                        logger.info("No releases found on GitHub")
                        return result

                    if response.status != 200:
                        result["error"] = f"GitHub API returned status {response.status}"
                        logger.error(result["error"])
                        return result

                    data = await response.json()

            # Extract release info
            tag_name = data.get("tag_name", "")
            result["latest_version"] = tag_name.lstrip("v")
            result["release_notes"] = data.get("body", "")[:500]  # Truncate long notes

            # Find MSI asset
            assets = data.get("assets", [])
            for asset in assets:
                asset_name = asset.get("name", "")
                if asset_name.endswith(".msi") and MSI_FILE_PREFIX in asset_name:
                    result["download_url"] = asset.get("browser_download_url")
                    break

            # Check if update is available
            if result["latest_version"]:
                result["update_available"] = compare_versions(
                    self.current_version, result["latest_version"]
                )

            logger.info(
                f"Update check: current={self.current_version}, "
                f"latest={result['latest_version']}, "
                f"available={result['update_available']}"
            )

        except aiohttp.ClientError as e:
            result["error"] = f"Network error: {str(e)}"
            logger.error(result["error"])
        except asyncio.TimeoutError:
            result["error"] = "Request timed out"
            logger.error(result["error"])
        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
            logger.error(result["error"])

        return result

    async def download_update(
        self,
        download_url: str,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> Optional[Path]:
        """
        Download the MSI installer.

        Args:
            download_url: URL to download from
            progress_callback: Optional callback with progress percentage (0-100)

        Returns:
            Path to downloaded file, or None if download failed.
        """
        try:
            # Create temp directory for download
            temp_dir = Path(tempfile.gettempdir()) / "BF6SettingsManager"
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Extract filename from URL
            filename = download_url.split("/")[-1]
            output_path = temp_dir / filename

            async with aiohttp.ClientSession() as session:
                async with session.get(download_url) as response:
                    if response.status != 200:
                        logger.error(f"Download failed with status {response.status}")
                        return None

                    # Get total size for progress
                    total_size = int(response.headers.get("content-length", 0))
                    downloaded = 0

                    # Download in chunks
                    with open(output_path, "wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                            downloaded += len(chunk)

                            if progress_callback and total_size > 0:
                                percent = int((downloaded / total_size) * 100)
                                progress_callback(percent)

            logger.info(f"Downloaded update to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None

    def launch_installer(self, msi_path: Path) -> bool:
        """
        Launch the MSI installer.

        Args:
            msi_path: Path to MSI file

        Returns:
            True if launch succeeded, False otherwise.
        """
        try:
            if not msi_path.exists():
                logger.error(f"MSI file not found: {msi_path}")
                return False

            # Use os.startfile on Windows for proper MSI handling
            os.startfile(str(msi_path))
            logger.info(f"Launched installer: {msi_path}")
            return True

        except AttributeError:
            # os.startfile not available (non-Windows)
            logger.error("MSI installation only supported on Windows")
            return False
        except Exception as e:
            logger.error(f"Failed to launch installer: {e}")
            return False

    def open_releases_page(self) -> None:
        """Open GitHub releases page in browser."""
        url = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases"
        webbrowser.open(url)
        logger.info(f"Opened releases page: {url}")

    def open_download_url(self, download_url: str) -> None:
        """Open download URL in browser."""
        webbrowser.open(download_url)
        logger.info(f"Opened download URL: {download_url}")


# Convenience function
async def check_for_updates() -> Dict[str, Any]:
    """Check for updates using default settings."""
    checker = UpdateChecker()
    return await checker.check_for_updates()
