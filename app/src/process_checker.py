"""Process detection utilities for checking if Battlefield 6 is running."""

import asyncio
import logging
from typing import Optional

import psutil

logger = logging.getLogger(__name__)


class ProcessChecker:
    """Check for running game processes."""

    GAME_PROCESSES = ["bf6.exe"]  # Alternative process names

    @staticmethod
    async def is_game_running() -> Optional[dict]:
        """
        Check if Battlefield 6 is running.

        Returns:
            Dict with process info if running, None otherwise
        """
        def _check():
            for proc in psutil.process_iter(attrs=['pid', 'name', 'exe']):
                try:
                    process_name = proc.info['name']
                    if process_name and process_name.lower() in [p.lower() for p in ProcessChecker.GAME_PROCESSES]:
                        return {
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'exe': proc.info['exe']
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            return None

        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _check)

    @staticmethod
    async def wait_for_game_to_close(
        check_interval: float = 2.0,
        max_wait_time: Optional[float] = None
    ) -> bool:
        """
        Wait for game process to close.

        Args:
            check_interval: Time in seconds between checks
            max_wait_time: Maximum time to wait in seconds (None = infinite)

        Returns:
            True if process closed, False if timeout reached
        """
        start_time = asyncio.get_event_loop().time()

        while True:
            proc_info = await ProcessChecker.is_game_running()

            if proc_info is None:
                logger.info("Game process closed")
                return True

            logger.debug(f"Game still running (PID: {proc_info['pid']})")

            # Check timeout
            if max_wait_time is not None:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= max_wait_time:
                    logger.warning("Timeout waiting for game to close")
                    return False

            await asyncio.sleep(check_interval)


# Example usage
async def main():
    """Test process detection."""
    checker = ProcessChecker()

    # Check if running
    proc_info = await checker.is_game_running()

    if proc_info:
        print(f"Battlefield 6 is running:")
        print(f"  Name: {proc_info['name']}")
        print(f"  PID: {proc_info['pid']}")
        print(f"  Path: {proc_info['exe']}")
    else:
        print("Battlefield 6 is not running")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
