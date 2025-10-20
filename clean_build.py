#!/usr/bin/env python3
"""
Clean build artifacts for Battlefield 6 Settings Manager.

This script removes all build artifacts from Briefcase builds.
"""

import shutil
from pathlib import Path


def clean_build_artifacts():
    """Remove build artifacts."""
    project_root = Path(__file__).parent

    # Directories to clean
    clean_dirs = [
        "build",
        "dist",
        "windows",
        ".briefcase",
        "bf6_settings_manager.egg-info",
        "__pycache__"
    ]

    files_removed = 0
    dirs_removed = 0

    for dir_name in clean_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"🗑️  Removing {dir_path}")
            try:
                if dir_path.is_dir():
                    shutil.rmtree(dir_path)
                    dirs_removed += 1
                else:
                    dir_path.unlink()
                    files_removed += 1
            except OSError as e:
                print(f"❌ Error removing {dir_path}: {e}")

    # Clean __pycache__ directories recursively
    for pycache_dir in project_root.rglob("__pycache__"):
        print(f"🗑️  Removing {pycache_dir}")
        try:
            shutil.rmtree(pycache_dir)
            dirs_removed += 1
        except OSError as e:
            print(f"❌ Error removing {pycache_dir}: {e}")

    # Clean .pyc files
    for pyc_file in project_root.rglob("*.pyc"):
        print(f"🗑️  Removing {pyc_file}")
        try:
            pyc_file.unlink()
            files_removed += 1
        except OSError as e:
            print(f"❌ Error removing {pyc_file}: {e}")

    return dirs_removed, files_removed


def main():
    """Main cleanup process."""
    print("=" * 60)
    print("🧹 Battlefield 6 Settings Manager Build Cleaner")
    print("=" * 60)

    # Clean build artifacts
    print("\n📦 Cleaning build artifacts...")
    dirs_removed, files_removed = clean_build_artifacts()

    print("\n✅ Cleanup completed:")
    print(f"   📁 Directories removed: {dirs_removed}")
    print(f"   📄 Files removed: {files_removed}")

    if dirs_removed + files_removed == 0:
        print("   🎉 No build artifacts found - already clean!")


if __name__ == "__main__":
    main()
