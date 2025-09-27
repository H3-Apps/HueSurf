#!/usr/bin/env python3
"""
HueSurf Manifest Validation Script
=================================

This script validates that the generated manifest.json file is properly aligned
with the original pack_info.json files from the assets directory.

It checks:
- Pack metadata alignment (names, descriptions, authors, etc.)
- Wallpaper data consistency (names, descriptions, tags)
- Extended metadata (colors, settings, recommended platforms)
- Completeness of all fields

Usage:
    python scripts/validate_manifest.py [--verbose] [--fix-issues]

Author: HueSurf Team
License: MIT
"""

import json
import sys
from pathlib import Path
import argparse
from typing import Dict, List, Any, Tuple
import difflib


class ManifestValidator:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.project_root = Path(__file__).parent.parent
        self.assets_dir = self.project_root / "assets" / "Wallpapers"
        self.manifest_path = (
            self.project_root / "website" / "static" / "wallpapers" / "manifest.json"
        )

        self.errors = []
        self.warnings = []
        self.info_messages = []

    def log_error(self, message: str):
        """Log an error message"""
        self.errors.append(f"❌ ERROR: {message}")
        print(f"❌ ERROR: {message}")

    def log_warning(self, message: str):
        """Log a warning message"""
        self.warnings.append(f"⚠️  WARNING: {message}")
        if self.verbose:
            print(f"⚠️  WARNING: {message}")

    def log_info(self, message: str):
        """Log an info message"""
        self.info_messages.append(f"ℹ️  INFO: {message}")
        if self.verbose:
            print(f"ℹ️  INFO: {message}")

    def log_success(self, message: str):
        """Log a success message"""
        print(f"✅ {message}")

    def load_manifest(self) -> Dict[str, Any]:
        """Load the manifest.json file"""
        if not self.manifest_path.exists():
            self.log_error(f"Manifest file not found: {self.manifest_path}")
            return {}

        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            self.log_info(
                f"Loaded manifest with {len(manifest.get('packs', []))} packs"
            )
            return manifest
        except Exception as e:
            self.log_error(f"Failed to load manifest: {e}")
            return {}

    def load_pack_info(self, pack_name: str) -> Dict[str, Any]:
        """Load pack_info.json for a specific pack"""
        pack_info_path = self.assets_dir / pack_name / "pack_info.json"

        if not pack_info_path.exists():
            self.log_error(f"Pack info not found: {pack_info_path}")
            return {}

        try:
            with open(pack_info_path, "r", encoding="utf-8") as f:
                pack_info = json.load(f)
            self.log_info(f"Loaded pack_info for {pack_name}")
            return pack_info
        except Exception as e:
            self.log_error(f"Failed to load pack_info for {pack_name}: {e}")
            return {}

    def compare_values(
        self, field_name: str, pack_name: str, manifest_value: Any, pack_info_value: Any
    ) -> bool:
        """Compare two values and log differences"""
        if manifest_value == pack_info_value:
            return True

        # Handle special cases
        if (
            field_name == "wallpapers"
            and isinstance(manifest_value, list)
            and isinstance(pack_info_value, list)
        ):
            return self.compare_wallpapers(pack_name, manifest_value, pack_info_value)

        self.log_error(f"Mismatch in pack '{pack_name}', field '{field_name}':")
        self.log_error(f"  Manifest: {repr(manifest_value)}")
        self.log_error(f"  Pack Info: {repr(pack_info_value)}")
        return False

    def compare_wallpapers(
        self,
        pack_name: str,
        manifest_wallpapers: List[Dict],
        pack_info_wallpapers: List[Dict],
    ) -> bool:
        """Compare wallpaper arrays in detail"""
        if len(manifest_wallpapers) != len(pack_info_wallpapers):
            self.log_error(
                f"Pack '{pack_name}': Wallpaper count mismatch - Manifest: {len(manifest_wallpapers)}, Pack Info: {len(pack_info_wallpapers)}"
            )
            return False

        all_match = True

        # Create lookup dictionaries by filename
        manifest_by_filename = {wp.get("filename"): wp for wp in manifest_wallpapers}
        pack_info_by_filename = {wp.get("filename"): wp for wp in pack_info_wallpapers}

        # Check each wallpaper
        for filename in pack_info_by_filename.keys():
            if filename not in manifest_by_filename:
                self.log_error(
                    f"Pack '{pack_name}': Wallpaper '{filename}' missing from manifest"
                )
                all_match = False
                continue

            manifest_wp = manifest_by_filename[filename]
            pack_info_wp = pack_info_by_filename[filename]

            # Check each field
            for field in ["name", "description", "tags"]:
                if field in pack_info_wp:
                    if not self.compare_values(
                        f"wallpapers[{filename}].{field}",
                        pack_name,
                        manifest_wp.get(field),
                        pack_info_wp.get(field),
                    ):
                        all_match = False

        # Check for extra wallpapers in manifest
        for filename in manifest_by_filename.keys():
            if filename not in pack_info_by_filename:
                self.log_warning(
                    f"Pack '{pack_name}': Extra wallpaper '{filename}' in manifest"
                )

        return all_match

    def validate_pack(self, manifest_pack: Dict[str, Any]) -> bool:
        """Validate a single pack against its pack_info.json"""
        pack_name = manifest_pack.get("pack_name", manifest_pack.get("name", "Unknown"))
        self.log_info(f"Validating pack: {pack_name}")

        # Load corresponding pack_info.json
        pack_info = self.load_pack_info(pack_name)
        if not pack_info:
            return False

        all_good = True

        # Fields that should match exactly
        direct_fields = [
            "pack_name",
            "version",
            "author",
            "description",
            "category",
            "created_date",
            "shuffle_enabled",
            "shuffle_on_new_tab",
            "colors",
            "recommended_for",
            "min_resolution",
            "license",
            "settings",
        ]

        for field in direct_fields:
            if field in pack_info:
                # Handle pack_name vs name inconsistency
                manifest_field = "name" if field == "pack_name" else field
                manifest_value = manifest_pack.get(manifest_field)
                pack_info_value = pack_info.get(field)

                if not self.compare_values(
                    field, pack_name, manifest_value, pack_info_value
                ):
                    all_good = False

        # Validate wallpapers array
        if "wallpapers" in pack_info:
            manifest_wallpapers = manifest_pack.get("wallpapers", [])
            pack_info_wallpapers = pack_info.get("wallpapers", [])

            if not self.compare_wallpapers(
                pack_name, manifest_wallpapers, pack_info_wallpapers
            ):
                all_good = False

        # Check for manifest-only fields (these are expected)
        manifest_only_fields = [
            "id",
            "count",
            "size_bytes",
            "size_mb",
            "download_url",
            "preview_url",
            "hash",
            "packed_date",
        ]
        for field in manifest_only_fields:
            if field not in manifest_pack:
                self.log_warning(
                    f"Pack '{pack_name}': Missing manifest field '{field}'"
                )

        return all_good

    def validate_manifest_structure(self, manifest: Dict[str, Any]) -> bool:
        """Validate the overall manifest structure"""
        required_fields = [
            "version",
            "generated",
            "total_packs",
            "total_wallpapers",
            "total_size_mb",
            "packs",
        ]
        all_good = True

        for field in required_fields:
            if field not in manifest:
                self.log_error(f"Missing required manifest field: {field}")
                all_good = False

        # Check packs array
        packs = manifest.get("packs", [])
        if not isinstance(packs, list):
            self.log_error("Manifest 'packs' field must be an array")
            all_good = False

        # Validate enhanced metadata
        if "features" in manifest:
            features = manifest["features"]
            if not isinstance(features, dict):
                self.log_warning("Manifest 'features' should be a dictionary")
            else:
                expected_features = [
                    "shuffle_supported",
                    "new_tab_shuffle",
                    "color_themes",
                    "multi_resolution",
                ]
                for feature in expected_features:
                    if feature not in features:
                        self.log_warning(f"Missing feature flag: {feature}")

        if "statistics" in manifest:
            stats = manifest["statistics"]
            if not isinstance(stats, dict):
                self.log_warning("Manifest 'statistics' should be a dictionary")

        return all_good

    def check_completeness(self, manifest: Dict[str, Any]) -> bool:
        """Check that all pack_info.json files are represented in manifest"""
        if not self.assets_dir.exists():
            self.log_error(f"Assets directory not found: {self.assets_dir}")
            return False

        # Get all pack directories
        asset_packs = set()
        for pack_dir in self.assets_dir.iterdir():
            if pack_dir.is_dir() and (pack_dir / "pack_info.json").exists():
                asset_packs.add(pack_dir.name)

        # Get all manifest packs
        manifest_packs = set()
        for pack in manifest.get("packs", []):
            pack_name = pack.get("pack_name", pack.get("name"))
            if pack_name:
                manifest_packs.add(pack_name)

        # Check for missing packs
        missing_from_manifest = asset_packs - manifest_packs
        missing_from_assets = manifest_packs - asset_packs

        all_good = True

        if missing_from_manifest:
            for pack_name in missing_from_manifest:
                self.log_error(
                    f"Pack '{pack_name}' exists in assets but missing from manifest"
                )
                all_good = False

        if missing_from_assets:
            for pack_name in missing_from_assets:
                self.log_error(
                    f"Pack '{pack_name}' exists in manifest but missing from assets"
                )
                all_good = False

        if all_good:
            self.log_success(
                f"All {len(asset_packs)} asset packs are represented in manifest"
            )

        return all_good

    def validate(self) -> bool:
        """Run complete validation"""
        print("🔍 Starting HueSurf Manifest Validation")
        print("=" * 50)

        # Load manifest
        manifest = self.load_manifest()
        if not manifest:
            return False

        # Validate manifest structure
        print("\n📋 Validating manifest structure...")
        structure_valid = self.validate_manifest_structure(manifest)

        # Check completeness
        print("\n🔍 Checking pack completeness...")
        completeness_valid = self.check_completeness(manifest)

        # Validate each pack
        print("\n📦 Validating individual packs...")
        packs_valid = True
        for pack in manifest.get("packs", []):
            if not self.validate_pack(pack):
                packs_valid = False

        # Print summary
        self.print_summary()

        return structure_valid and completeness_valid and packs_valid

    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 50)
        print("📊 VALIDATION SUMMARY")
        print("=" * 50)

        if not self.errors and not self.warnings:
            print(
                "🎉 PERFECT ALIGNMENT! Manifest is perfectly synchronized with pack_info.json files."
            )
            print(f"✅ {len(self.info_messages)} operations completed successfully")
        else:
            print(f"❌ Errors: {len(self.errors)}")
            print(f"⚠️  Warnings: {len(self.warnings)}")
            print(f"ℹ️  Info: {len(self.info_messages)}")

            if self.errors:
                print("\n🚨 ERRORS FOUND:")
                for error in self.errors:
                    print(f"  {error}")

            if self.warnings and self.verbose:
                print("\n⚠️  WARNINGS:")
                for warning in self.warnings:
                    print(f"  {warning}")

        print("\n📝 RECOMMENDATIONS:")
        if self.errors:
            print(
                "  • Fix errors by running: python scripts/pack_wallpapers.py --force"
            )
            print("  • Check pack_info.json files for missing or incorrect data")
        else:
            print("  • Manifest is properly aligned with pack_info.json files")
            print("  • System is ready for production use")

    def generate_diff_report(
        self, pack_name: str, manifest_pack: Dict, pack_info: Dict
    ) -> str:
        """Generate a detailed diff report for debugging"""
        manifest_json = json.dumps(manifest_pack, indent=2, sort_keys=True)
        pack_info_json = json.dumps(pack_info, indent=2, sort_keys=True)

        diff = difflib.unified_diff(
            pack_info_json.splitlines(keepends=True),
            manifest_json.splitlines(keepends=True),
            fromfile=f"pack_info.json ({pack_name})",
            tofile=f"manifest.json ({pack_name})",
            lineterm="",
        )

        return "".join(diff)


def main():
    parser = argparse.ArgumentParser(
        description="Validate HueSurf wallpaper manifest alignment"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--diff", action="store_true", help="Generate diff reports for mismatches"
    )

    args = parser.parse_args()

    validator = ManifestValidator(verbose=args.verbose)
    success = validator.validate()

    if args.diff and validator.errors:
        print("\n📄 GENERATING DIFF REPORTS...")
        # This would generate detailed diffs for each mismatch
        # Implementation could be added here if needed

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
