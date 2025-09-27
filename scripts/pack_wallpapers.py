#!/usr/bin/env python3
"""
HueSurf Wallpaper Packer

This script packages wallpaper packs from the assets folder into the website's
static folder for web distribution. It creates zip files, copies preview images,
and generates metadata for the web interface.

Usage:
    python scripts/pack_wallpapers.py [--force] [--verbose]

Author: HueSurf Team
License: MIT
"""

import os
import json
import zipfile
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import hashlib
import mimetypes
from PIL import Image
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WallpaperPacker:
    def __init__(self, source_dir=None, output_dir=None, force=False, verbose=False):
        """
        Initialize the wallpaper packer

        Args:
            source_dir: Source wallpapers directory (default: assets/Wallpapers)
            output_dir: Output static directory (default: website/static/wallpapers)
            force: Force overwrite existing files
            verbose: Enable verbose logging
        """
        # Set up paths relative to project root
        self.project_root = Path(__file__).parent.parent
        self.source_dir = (
            Path(source_dir)
            if source_dir
            else self.project_root / "assets" / "Wallpapers"
        )
        self.output_dir = (
            Path(output_dir)
            if output_dir
            else self.project_root / "website" / "static" / "wallpapers"
        )

        self.force = force
        self.verbose = verbose

        if verbose:
            logger.setLevel(logging.DEBUG)

        # Supported image formats
        self.supported_formats = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}

        # Statistics
        self.stats = {
            "packs_processed": 0,
            "wallpapers_processed": 0,
            "zips_created": 0,
            "previews_created": 0,
            "total_size": 0,
        }

    def ensure_directories(self):
        """Create necessary output directories"""
        directories = [
            self.output_dir,
            self.output_dir / "packs",
            self.output_dir / "previews",
            self.output_dir / "thumbs",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory: {directory}")

    def get_image_files(self, directory):
        """Get all image files from a directory"""
        image_files = []
        for file_path in directory.rglob("*"):
            if (
                file_path.is_file()
                and file_path.suffix.lower() in self.supported_formats
            ):
                image_files.append(file_path)
        return sorted(image_files)

    def create_thumbnail(self, image_path, thumb_path, size=(300, 200)):
        """Create a thumbnail for preview"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ("RGBA", "LA", "P"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(
                        img, mask=img.split()[-1] if img.mode == "RGBA" else None
                    )
                    img = background

                # Create thumbnail
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(thumb_path, "JPEG", quality=85, optimize=True)
                return True
        except Exception as e:
            logger.error(f"Failed to create thumbnail for {image_path}: {e}")
            return False

    def calculate_file_hash(self, file_path):
        """Calculate SHA256 hash of a file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def load_pack_info(self, pack_dir):
        """Load pack information from pack_info.json"""
        pack_info_path = pack_dir / "pack_info.json"
        default_info = {
            "pack_name": pack_dir.name,
            "version": "1.0.0",
            "author": "HueSurf Team",
            "description": f"{pack_dir.name} wallpaper pack for HueSurf browser",
            "category": "General",
            "created_date": datetime.now().isoformat().split("T")[0],
            "shuffle_enabled": True,
            "shuffle_on_new_tab": True,
            "wallpapers": [],
            "settings": {
                "shuffle_interval": "new_tab",
                "transition_effect": "fade",
                "transition_duration": 500,
                "allow_user_shuffle": True,
                "remember_last_wallpaper": False,
            },
        }

        if pack_info_path.exists():
            try:
                with open(pack_info_path, "r", encoding="utf-8") as f:
                    pack_info = json.load(f)
                    # Merge with defaults to ensure all fields exist
                    for key, value in default_info.items():
                        if key not in pack_info:
                            pack_info[key] = value
                    return pack_info
            except Exception as e:
                logger.warning(
                    f"Failed to load pack_info.json for {pack_dir.name}: {e}"
                )

        return default_info

    def create_pack_zip(self, pack_dir, pack_info, image_files):
        """Create a zip file for a wallpaper pack"""
        pack_name = pack_info["pack_name"]
        zip_path = (
            self.output_dir / "packs" / f"{pack_name.lower().replace(' ', '_')}.zip"
        )

        if zip_path.exists() and not self.force:
            logger.info(f"Zip already exists: {zip_path} (use --force to overwrite)")
            return zip_path

        try:
            with zipfile.ZipFile(
                zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6
            ) as zipf:
                # Add all wallpaper images
                for image_path in image_files:
                    arcname = f"{pack_name}/{image_path.relative_to(pack_dir)}"
                    zipf.write(image_path, arcname)

                # Create separate metadata for ZIP (don't modify original pack_info)
                zip_pack_info = pack_info.copy()
                zip_pack_info["count"] = len(image_files)
                zip_pack_info["packed_date"] = datetime.now().isoformat()

                # Add pack info to zip
                pack_info_json = json.dumps(zip_pack_info, indent=2, ensure_ascii=False)
                zipf.writestr(f"{pack_name}/pack_info.json", pack_info_json)

                # Add README
                readme_content = f"""# {pack_name} Wallpaper Pack

{pack_info["description"]}

## Contents
- {len(image_files)} wallpapers
- Shuffle enabled: {"Yes" if pack_info["shuffle_enabled"] else "No"}
- New tab shuffle: {"Yes" if pack_info["shuffle_on_new_tab"] else "No"}

## Installation
1. Extract this zip file to your HueSurf wallpapers directory
2. Restart HueSurf to see the new wallpapers
3. Enable shuffle in wallpaper settings if desired

## Created by HueSurf Team
Licensed under MIT License
"""
                zipf.writestr(f"{pack_name}/README.md", readme_content)

            self.stats["zips_created"] += 1
            self.stats["total_size"] += zip_path.stat().st_size
            logger.info(
                f"Created zip: {zip_path} ({zip_path.stat().st_size / 1024 / 1024:.1f} MB)"
            )
            return zip_path

        except Exception as e:
            logger.error(f"Failed to create zip for {pack_name}: {e}")
            return None

    def create_preview_image(self, pack_dir, image_files, pack_name):
        """Create a preview image for the pack"""
        preview_path = (
            self.output_dir / "previews" / f"{pack_name.lower().replace(' ', '_')}.jpg"
        )

        if preview_path.exists() and not self.force:
            logger.debug(f"Preview already exists: {preview_path}")
            return preview_path

        if not image_files:
            return None

        # Use the first image as preview
        first_image = image_files[0]
        thumb_path = (
            self.output_dir / "thumbs" / f"{pack_name.lower().replace(' ', '_')}.jpg"
        )

        if self.create_thumbnail(first_image, thumb_path):
            # Copy thumbnail as preview
            shutil.copy2(thumb_path, preview_path)
            self.stats["previews_created"] += 1
            logger.debug(f"Created preview: {preview_path}")
            return preview_path

        return None

    def process_pack(self, pack_dir):
        """Process a single wallpaper pack"""
        if not pack_dir.is_dir():
            return None

        logger.info(f"Processing pack: {pack_dir.name}")

        # Get all image files
        image_files = self.get_image_files(pack_dir)
        if not image_files:
            logger.warning(f"No image files found in {pack_dir.name}")
            return None

        # Load pack information
        pack_info = self.load_pack_info(pack_dir)

        # Create zip file (pack_info won't be modified)
        zip_path = self.create_pack_zip(pack_dir, pack_info, image_files)
        if not zip_path:
            return None

        # Create preview image
        preview_path = self.create_preview_image(
            pack_dir, image_files, pack_info["pack_name"]
        )

        # Generate pack manifest data directly from original pack_info.json
        pack_data = pack_info.copy()  # Start with all original pack_info data

        # Add manifest-specific fields
        pack_data.update(
            {
                "id": pack_info["pack_name"].lower().replace(" ", "_"),
                "name": pack_info["pack_name"],
                "count": len(image_files),
                "size_bytes": zip_path.stat().st_size,
                "size_mb": round(zip_path.stat().st_size / 1024 / 1024, 2),
                "download_url": f"/static/wallpapers/packs/{zip_path.name}",
                "preview_url": f"/static/wallpapers/previews/{preview_path.name}"
                if preview_path
                else None,
                "hash": self.calculate_file_hash(zip_path),
                "packed_date": datetime.now().isoformat(),
            }
        )

        # Ensure required defaults for missing fields
        pack_data.setdefault("category", "General")
        pack_data.setdefault("author", "Unknown")
        pack_data.setdefault("version", "1.0.0")
        pack_data.setdefault("shuffle_enabled", False)
        pack_data.setdefault("shuffle_on_new_tab", False)
        pack_data.setdefault("colors", {})
        pack_data.setdefault("recommended_for", [])
        pack_data.setdefault("min_resolution", "1920x1080")
        pack_data.setdefault("license", "MIT")
        pack_data.setdefault(
            "settings",
            {
                "shuffle_interval": "new_tab",
                "transition_effect": "fade",
                "transition_duration": 500,
                "allow_user_shuffle": True,
                "remember_last_wallpaper": False,
            },
        )

        self.stats["packs_processed"] += 1
        self.stats["wallpapers_processed"] += len(image_files)

        logger.info(
            f"✅ Processed {pack_info['pack_name']}: {len(image_files)} wallpapers"
        )
        return pack_data

    def generate_manifest(self, packs_data):
        """Generate manifest file for the website"""
        # Gather all unique values for global manifest metadata
        all_categories = list(set(pack["category"] for pack in packs_data))
        all_licenses = list(set(pack["license"] for pack in packs_data))
        all_resolutions = list(set(pack["min_resolution"] for pack in packs_data))

        manifest = {
            "version": "1.0.0",
            "generated": datetime.now().isoformat(),
            "total_packs": len(packs_data),
            "total_wallpapers": sum(pack["count"] for pack in packs_data),
            "total_size_mb": round(
                sum(pack["size_bytes"] for pack in packs_data) / 1024 / 1024, 2
            ),
            "packs": packs_data,
            "categories": all_categories,
            "licenses": all_licenses,
            "resolutions": all_resolutions,
            "api_version": "1.0",
            "base_url": "/static/wallpapers",
            "features": {
                "shuffle_supported": any(
                    pack["shuffle_enabled"] for pack in packs_data
                ),
                "new_tab_shuffle": any(
                    pack["shuffle_on_new_tab"] for pack in packs_data
                ),
                "color_themes": len([pack for pack in packs_data if pack.get("colors")])
                > 0,
                "multi_resolution": len(all_resolutions) > 1,
            },
            "statistics": {
                "packs_with_shuffle": len(
                    [pack for pack in packs_data if pack["shuffle_enabled"]]
                ),
                "average_pack_size_mb": round(
                    sum(pack["size_mb"] for pack in packs_data) / len(packs_data), 2
                )
                if packs_data
                else 0,
                "total_unique_tags": len(
                    set(
                        tag
                        for pack in packs_data
                        for wallpaper in pack["wallpapers"]
                        for tag in wallpaper.get("tags", [])
                    )
                ),
            },
        }

        manifest_path = self.output_dir / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        logger.info(f"Generated manifest: {manifest_path}")
        return manifest_path

    def pack_wallpapers(self):
        """Main method to pack all wallpapers"""
        logger.info("🎨 Starting HueSurf Wallpaper Packer")
        logger.info(f"Source: {self.source_dir}")
        logger.info(f"Output: {self.output_dir}")

        if not self.source_dir.exists():
            logger.error(f"Source directory does not exist: {self.source_dir}")
            return False

        # Ensure output directories exist
        self.ensure_directories()

        # Process all wallpaper packs
        packs_data = []
        for pack_dir in self.source_dir.iterdir():
            if pack_dir.is_dir():
                pack_data = self.process_pack(pack_dir)
                if pack_data:
                    packs_data.append(pack_data)

        if not packs_data:
            logger.warning("No wallpaper packs were processed")
            return False

        # Generate manifest file
        self.generate_manifest(packs_data)

        # Print statistics
        self.print_statistics()

        logger.info("✅ Wallpaper packing completed successfully!")
        return True

    def print_statistics(self):
        """Print packing statistics"""
        print("\n" + "=" * 50)
        print("📊 PACKING STATISTICS")
        print("=" * 50)
        print(f"Packs processed:      {self.stats['packs_processed']}")
        print(f"Wallpapers processed: {self.stats['wallpapers_processed']}")
        print(f"ZIP files created:    {self.stats['zips_created']}")
        print(f"Previews created:     {self.stats['previews_created']}")
        print(f"Total size:           {self.stats['total_size'] / 1024 / 1024:.1f} MB")
        print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="Pack HueSurf wallpapers for web distribution"
    )
    parser.add_argument("--source", help="Source wallpapers directory")
    parser.add_argument("--output", help="Output static directory")
    parser.add_argument(
        "--force", action="store_true", help="Force overwrite existing files"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        packer = WallpaperPacker(
            source_dir=args.source,
            output_dir=args.output,
            force=args.force,
            verbose=args.verbose,
        )

        success = packer.pack_wallpapers()
        exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n❌ Packing cancelled by user")
        exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
