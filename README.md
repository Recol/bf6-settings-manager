![Downloads](https://img.shields.io/badge/Downloads-81-blue)
# Battlefield 6 Settings Manager

<img width="256" height="384" alt="bf6-settings-manager" src="https://github.com/user-attachments/assets/24f5d99d-308a-43f1-8cfa-64f82c5407a6" />

**Optimize your Battlefield 6 settings for competitive play**

A standalone Windows application that automatically detects your monitor's HDR peak brightness and applies optimal game settings for competitive gameplay. No more digging through config files or dealing with settings the game doesn't expose!

## Features

### Auto HDR Configuration
- **Automatic Brightness Detection**: Reads your monitor's actual peak brightness (nits) from Windows EDID data
- **Manual Override**: Option to set custom brightness values if auto-detection isn't available
- **Accurate HDR**: Sets `DisplayMappingHdr10PeakLuma` to match your display's capabilities

### Visual Clarity (Competitive)
Disable distracting visual effects for better enemy visibility:
- Weapon Depth of Field
- Chromatic Aberration
- Film Grain
- Vignette (edge darkening)
- Lens Distortion
- Motion Blur (Weapon & World)

### Performance & Latency
Reduce input lag and improve responsiveness:
- Enable Low Latency Mode (NVIDIA/AMD/Intel GPU-specific)
- Disable Future Frame Rendering

### Audio
- Disable Tinnitus Effect (annoying ringing sound)

### Safety Features
- **Process Detection**: Prevents modification while game is running
- **Automatic Backups**: Creates timestamped backups before any changes
- **Atomic Writes**: Safe file operations that won't corrupt your config
- **Read-Only Protection**: Locks settings after apply to prevent game from reverting changes

## Installation

### Download MSI Installer
1. Download the latest `BF6-Settings-Manager.msi` from [Releases](https://github.com/your-repo/bf6-settings-manager/releases)
2. Double-click to install
3. Launch from Start Menu: "Battlefield 6 Settings Manager"

### Requirements
- **OS**: Windows 10/11 (64-bit)
- **Battlefield 6**: Must be installed and run at least once (to create config file)
- **Python** (for development only): Python 3.12+ if building from source

## Usage

1. **Launch the application**
   - The app will automatically detect your monitor's HDR peak brightness
   - It will locate your Battlefield 6 config file (searches Steam/EA/Origin folders)

2. **Select desired settings**
   - Check the settings you want to apply
   - Use "Select All" for a full competitive preset
   - Optionally override HDR brightness with a custom value

3. **Apply Settings**
   - Click "Apply Settings"
   - The app will check if BF6 is running (prompts you to close it)
   - Creates a timestamped backup of your config
   - Applies all selected settings
   - Sets the file to read-only to prevent the game from reverting changes

4. **Done!**
   - Launch Battlefield 6 and enjoy optimized settings
   - You can re-run the tool anytime to modify settings

## Config File Location

The tool automatically searches for `PROFSAVE_profile` in:
```
C:\Users\{YourName}\Documents\Battlefield 6\settings\
  ├── steam\PROFSAVE_profile
  ├── ea\PROFSAVE_profile
  └── origin\PROFSAVE_profile
```

Only one file exists depending on your launcher, you can also specify your own location.

## Settings Reference

| Setting | Config Key | Competitive Value | Description |
|---------|-----------|-------------------|-------------|
| HDR Peak Brightness | `GstRender.DisplayMappingHdr10PeakLuma` | Auto-detected | Matches your monitor's nits value |
| Weapon DOF | `GstRender.WeaponDOF` | 0 | Disabled for clarity |
| Chromatic Aberration | `GstRender.ChromaticAberration` | 0 | Disabled |
| Film Grain | `GstRender.FilmGrain` | 0 | Disabled |
| Vignette | `GstRender.Vignette` | 0 | Disabled |
| Lens Distortion | `GstRender.LensDistortion` | 0 | Disabled |
| Motion Blur (Weapon) | `GstRender.MotionBlurWeapon` | 0.0 | Disabled |
| Motion Blur (World) | `GstRender.MotionBlurWorld` | 0.0 | Disabled |
| NVIDIA Low Latency | `GstRender.NvidiaLowLatency` | 1 | Enabled |
| AMD Low Latency | `GstRender.AMDLowLatency` | 1 | Enabled |
| Intel Low Latency | `GstRender.IntelLowLatency` | 1 | Enabled |
| Future Frame Rendering | `GstRender.FutureFrameRendering` | 0 | Disabled |
| Tinnitus Effect | `GstAudio.Volume_Tinnitus` | 0.0 | Disabled |

## Building from Source

### Prerequisites
```bash
# Install Python 3.12+
# Install dependencies
pip install -r requirements.txt

# Install Briefcase for MSI building
pip install briefcase

# Install WiX Toolset (for MSI)
# Download from: https://wixtoolset.org/
# Or via Chocolatey: choco install wixtoolset
```

### Development
```bash
# Run from source
python main.py

# Clean build artifacts
python clean_build.py

# Build MSI installer
python build_msi.py
```

## Troubleshooting

### Config file not found
- Make sure you've launched Battlefield 6 at least once
- Check that the game created your profile in `Documents\Battlefield 6\settings\`

### HDR brightness not detected
- Use the "Use custom brightness value" option
- Check your monitor's specifications for peak brightness (usually 400-1000 nits)
- Typical values: 400, 600, 1000 nits

### Game is running error
- Close Battlefield 6 completely before applying settings
- Check Task Manager for `bf6.exe` or `bf2042.exe` processes

### Settings reverted after game launch
- Make sure the "read-only" protection was applied successfully
- If needed, manually right-click the config file → Properties → Check "Read-only"

## FAQ

**Q: Will this get me banned?**
A: No. This tool only modifies your local config file, same as editing it manually. Many of these settings are used by competitive players.

**Q: Can I undo changes?**
A: Yes! The tool creates timestamped backups (`.backup_YYYYMMDD_HHMMSS`) before any modifications. You can restore from these backups.

**Q: Why is the file set to read-only?**
A: Battlefield 6 sometimes reverts settings when you change graphics options in-game. Read-only protection prevents this.

**Q: Do I need to re-apply after game updates?**
A: Usually no, but if the game resets your config, just run the tool again.

**Q: What if my launcher isn't Steam/EA/Origin?**
A: The tool searches recursively in `Documents\Battlefield 6\settings\` so it should find your config regardless of the launcher subfolder name.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Credits

Built with:
- [Flet](https://flet.dev/) - Modern UI framework
- [psutil](https://github.com/giampaolo/psutil) - Process detection
- [Briefcase](https://briefcase.readthedocs.io/) - MSI packaging

## Disclaimer

This tool is not affiliated with or endorsed by Electronic Arts (EA) or DICE. Battlefield and all related trademarks are property of Electronic Arts Inc.
