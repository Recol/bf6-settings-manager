"""HDR peak brightness detection from Windows EDID data."""

import asyncio
import logging
from typing import Optional
import winreg

logger = logging.getLogger(__name__)


class BrightnessDetector:
    """Detect HDR peak brightness from display EDID."""

    def __init__(self):
        """Initialize brightness detector."""
        self.registry_base = r"SYSTEM\CurrentControlSet\Enum\DISPLAY"

    async def get_peak_brightness(self) -> Optional[int]:
        """
        Get peak brightness in nits from primary display.

        Returns:
            Peak brightness in nits, or None if not detected
        """
        try:
            # Run blocking registry operations in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._get_brightness_sync)
        except Exception as e:
            logger.error(f"Failed to detect peak brightness: {e}")
            return None

    def _get_brightness_sync(self) -> Optional[int]:
        """Synchronous peak brightness detection."""
        try:
            # Enumerate display devices
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.registry_base) as key:
                i = 0
                while True:
                    try:
                        display_id = winreg.EnumKey(key, i)
                        brightness = self._check_display_brightness(display_id)
                        if brightness:
                            logger.info(f"Detected peak brightness: {brightness} nits")
                            return brightness
                        i += 1
                    except OSError:
                        break
        except Exception as e:
            logger.error(f"Registry enumeration error: {e}")

        return None

    def _check_display_brightness(self, display_id: str) -> Optional[int]:
        """Check a specific display for HDR brightness info."""
        try:
            display_path = f"{self.registry_base}\\{display_id}"

            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, display_path) as display_key:
                # Enumerate device instances
                j = 0
                while True:
                    try:
                        instance_id = winreg.EnumKey(display_key, j)
                        device_params_path = f"{display_path}\\{instance_id}\\Device Parameters"

                        try:
                            with winreg.OpenKey(
                                winreg.HKEY_LOCAL_MACHINE,
                                device_params_path
                            ) as params_key:
                                # Read EDID data
                                edid_data, _ = winreg.QueryValueEx(params_key, "EDID")
                                edid_bytes = bytes(edid_data)

                                # Parse EDID for HDR metadata
                                brightness = self._parse_hdr_metadata(edid_bytes)
                                if brightness:
                                    return brightness
                        except FileNotFoundError:
                            pass

                        j += 1
                    except OSError:
                        break
        except Exception as e:
            logger.debug(f"Error checking display {display_id}: {e}")

        return None

    def _parse_hdr_metadata(self, edid_data: bytes) -> Optional[int]:
        """
        Parse CTA-861.3 HDR Static Metadata block from EDID.

        Args:
            edid_data: Raw EDID bytes

        Returns:
            Peak brightness in nits, or None if not found
        """
        try:
            if len(edid_data) < 256:  # Need at least one extension block
                return None

            # Check extension blocks starting at offset 128
            for offset in range(128, len(edid_data), 128):
                if offset + 128 > len(edid_data):
                    break

                extension = edid_data[offset:offset + 128]

                # Check for CEA-861 extension (tag 0x02)
                if extension[0] != 0x02:
                    continue

                dtd_offset = extension[2]
                pos = 4  # Data block collection starts at byte 4

                while pos < dtd_offset and pos < len(extension) - 1:
                    block_header = extension[pos]
                    block_tag = (block_header >> 5) & 0x07
                    block_length = block_header & 0x1F

                    # Extended tag block (tag = 7)
                    if block_tag == 7 and block_length > 0:
                        if pos + 1 < len(extension):
                            extended_tag = extension[pos + 1]

                            # HDR Static Metadata (extended tag = 0x06)
                            if extended_tag == 0x06 and block_length >= 4:
                                # Byte at pos+4 contains max luminance code
                                if pos + 4 < len(extension):
                                    max_lum_code = extension[pos + 4]

                                    # Convert to nits using formula: 50 * 2^(code/32)
                                    if max_lum_code > 0:
                                        peak_nits = 50 * (2 ** (max_lum_code / 32.0))
                                        return round(peak_nits)

                    pos += block_length + 1
                    if pos >= len(extension):
                        break
        except Exception as e:
            logger.debug(f"Error parsing EDID HDR metadata: {e}")

        return None


# Example usage
async def main():
    """Test brightness detection."""
    detector = BrightnessDetector()
    brightness = await detector.get_peak_brightness()

    if brightness:
        print(f"Detected peak brightness: {brightness} nits")
    else:
        print("Could not detect peak brightness")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
