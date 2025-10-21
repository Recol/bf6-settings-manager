#!/usr/bin/env python3
"""
Build script for Battlefield 6 Settings Manager MSI installer using Briefcase.

This script automates the MSI build process and provides additional validation and setup.
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, description, cwd=None):
    """Run a command with error handling."""
    print(f"\n🔧 {description}...")
    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        if e.stdout:
            print(f"Standard output: {e.stdout}")
        return False


def check_prerequisites():
    """Check if all prerequisites are installed."""
    print("🔍 Checking prerequisites...")

    # Check Python version
    if sys.version_info < (3, 12):
        print("❌ Python 3.12+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

    # Check if briefcase is available
    try:
        result = subprocess.run(["briefcase", "--version"], capture_output=True, text=True)
        print(f"✅ Briefcase {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Briefcase not found. Installing...")
        if not run_command([sys.executable, "-m", "pip", "install", "briefcase>=0.3.24"], "Install Briefcase"):
            return False

    # Check WiX Toolset (required for MSI)
    wix_found = False

    # First check if wix.exe is in PATH (WiX v6.0+)
    try:
        result = subprocess.run(["wix", "--version"], capture_output=True, text=True)
        print(f"✅ WiX Toolset v6.0+ is available in PATH: {result.stdout.strip()}")
        wix_found = True
    except FileNotFoundError:
        # Fallback to older candle.exe check
        try:
            result = subprocess.run(["candle", "-?"], capture_output=True, text=True)
            print("✅ WiX Toolset (legacy) is available in PATH")
            wix_found = True
        except FileNotFoundError:
            pass

    # If not in PATH, check common installation locations
    if not wix_found:
        wix_locations = [
            # WiX v6.0+
            "C:\\Program Files\\WiX Toolset v6.0\\bin\\wix.exe",
            "C:\\Program Files (x86)\\WiX Toolset v6.0\\bin\\wix.exe",
            # WiX v4.0
            "C:\\Program Files (x86)\\WiX Toolset v4.0\\bin\\candle.exe",
            "C:\\Program Files\\WiX Toolset v4.0\\bin\\candle.exe",
            # WiX v3.11 (legacy)
            "C:\\Program Files (x86)\\WiX Toolset v3.11\\bin\\candle.exe",
            "C:\\Program Files\\WiX Toolset v3.11\\bin\\candle.exe"
        ]

        for wix_path in wix_locations:
            if Path(wix_path).exists():
                wix_version = "v6.0+" if "wix.exe" in wix_path else "legacy"
                print(f"✅ WiX Toolset {wix_version} found at {wix_path}")
                # Add to PATH for this session
                wix_bin_dir = str(Path(wix_path).parent)
                os.environ['PATH'] = wix_bin_dir + os.pathsep + os.environ.get('PATH', '')
                wix_found = True
                break

    if not wix_found:
        print("⚠️  WiX Toolset not found. You may need to install it for MSI generation.")
        print("   Download from: https://wixtoolset.org/")
        print("   Or install via chocolatey: choco install wixtoolset")
        print("   If installed, make sure it's in your PATH or in a standard location.")

    return True


def setup_resources():
    """Set up resource files needed for the build."""
    print("📦 Setting up resource files...")

    project_root = Path(__file__).parent
    resources_dir = project_root / "resources"

    # Create directories if they don't exist
    resources_dir.mkdir(parents=True, exist_ok=True)

    # Check for application icon
    icon_file = resources_dir / "icon.ico"
    if icon_file.exists():
        size_kb = icon_file.stat().st_size / 1024
        print(f"✅ Application icon found: {icon_file} ({size_kb:.1f} KB)")
    else:
        print(f"⚠️  Icon file not found at {icon_file}")
        print("   The application will use a default icon")

    return True


def build_msi():
    """Build the MSI installer using Briefcase."""
    print("\n🚀 Starting MSI build process...")

    project_root = Path(__file__).parent

    # Clean existing build first
    build_dir = project_root / "build"
    if build_dir.exists():
        print("🧹 Cleaning existing build directory...")
        import shutil
        shutil.rmtree(build_dir)

    # Step 1: Create the application
    if not run_command(
        ["briefcase", "create", "windows"],
        "Create Windows application structure",
        cwd=project_root
    ):
        return False

    # Step 2: Update the application with latest code
    if not run_command(
        ["briefcase", "update", "windows"],
        "Update application with latest code",
        cwd=project_root
    ):
        return False

    # Step 3: Build the application
    if not run_command(
        ["briefcase", "build", "windows"],
        "Build Windows application",
        cwd=project_root
    ):
        return False

    # Step 4: Package as MSI
    if not run_command(
        ["briefcase", "package", "windows", "--adhoc-sign"],
        "Package application as MSI installer",
        cwd=project_root
    ):
        return False

    return True


def find_msi_output():
    """Find and report the location of the generated MSI."""
    project_root = Path(__file__).parent

    # Briefcase outputs to multiple locations
    search_paths = [
        project_root / "windows",  # Primary Briefcase output
        project_root / "dist",     # Alternative output location
    ]

    msi_files = []
    for search_path in search_paths:
        if search_path.exists():
            msi_files.extend(list(search_path.glob("**/*.msi")))

    if msi_files:
        print("\n🎉 MSI installer generated successfully!")
        for msi_file in msi_files:
            size_mb = msi_file.stat().st_size / (1024 * 1024)
            print(f"   📦 {msi_file} ({size_mb:.1f} MB)")
        return True

    print("\n⚠️  MSI file not found in expected locations")
    print("   Searched: windows/, dist/")
    return False


def main():
    """Main build process."""
    print("=" * 60)
    print("🏗️  Battlefield 6 Settings Manager MSI Builder")
    print("=" * 60)

    start_time = time.time()

    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed")
        sys.exit(1)

    # Setup resources
    if not setup_resources():
        print("\n❌ Resource setup failed")
        sys.exit(1)

    # Build MSI
    if not build_msi():
        print("\n❌ MSI build failed")
        sys.exit(1)

    # Find output
    find_msi_output()

    elapsed_time = time.time() - start_time
    print(f"\n✅ Build completed in {elapsed_time:.1f} seconds")

    print("\n📋 Next Steps:")
    print("1. Test the MSI installer on a clean Windows machine")
    print("2. Verify settings are applied correctly")
    print("3. Test with different BF6 launcher configurations (Steam/EA/Origin)")
    print("4. Verify read-only protection works")

if __name__ == "__main__":
    main()
