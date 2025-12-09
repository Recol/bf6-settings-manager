# Release Notes

## v1.0.1 (2025-12-09)

### New Features
- **Check for Updates**: Button to check GitHub for new releases with automatic MSI download
- **Release Notes**: View changelog directly in the application
- **Donation Support**: Quick link to support development via Buy Me a Coffee
- **Contact**: Get in touch via Discord or Twitter/X
- **Report Issue**: Quick link to report bugs on GitHub Issues
- **Custom Config Path**: Browse and select custom PROFSAVE_profile location with persistent storage

### New Game Settings
- **HDR Mode**: Toggle HDR on/off directly
- **UI Scale Factor**: Slider control (0.5-1.0) for UI sharpness
- **UI Brightness**: Slider control (0.0-1.0) for interface brightness
- **VSync Mode**: Dropdown with Off/On/Adaptive options
- **Frame Rate Limit**: Slider control (30-500 FPS) for in-game cap
- **Menu Frame Rate Limit**: Slider control (30-500 FPS) for menu cap
- **Frame Rate Limiter Toggles**: Enable/disable limiters independently

### UI Improvements
- Version number displayed in application header
- New Display Settings card with HDR, UI scale, brightness, and VSync controls
- New Frame Rate Settings card with limiter toggles and FPS sliders
- Theme-aware slider and dropdown components with full dark/light mode support
- Improved header layout with action buttons
- New Icon for the application

### Technical Improvements
- GitHub releases API integration for update checking
- Persistent app settings stored in %APPDATA%
- Async HTTP requests using aiohttp for non-blocking updates
- Dynamic version reading from pyproject.toml

### Bug Fixes
- Fixed LICENSE file path in pyproject.toml for build compatibility

---

## v1.0.0 (2025-12-08)

### Initial Release
- **HDR Peak Brightness Detection**: Automatic detection of display capabilities
- **Visual Clarity Settings**: Disable Weapon DOF, Chromatic Aberration, Film Grain, Vignette, Lens Distortion, Motion Blur
- **Performance Settings**: Low latency modes for NVIDIA, AMD, and Intel GPUs
- **Audio Settings**: Disable tinnitus sound effect
- **Backup System**: Automatic timestamped backups before applying changes
- **Game Process Detection**: Prevents changes while game is running
- **File Protection**: Sets config as read-only to prevent game overwrites
- **Modern UI**: Card-based responsive layout with dark/light theme support
- **Search Functionality**: Filter settings by name
