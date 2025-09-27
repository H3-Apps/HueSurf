#!/usr/bin/env python3
"""
HueSurf Wallpaper System Demo
============================

This script demonstrates the complete wallpaper pack system functionality:
- Wallpaper packing from assets to static folder
- API endpoints for downloading and managing packs
- Shuffle functionality for random wallpapers
- Web interface integration

Author: HueSurf Team
License: MIT
"""

import os
import json
import time
import requests
from pathlib import Path
import zipfile
import tempfile
import shutil
import subprocess
import sys


class WallpaperDemo:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.assets_dir = self.project_root / "assets" / "Wallpapers"
        self.static_dir = self.project_root / "website" / "static" / "wallpapers"
        self.server_url = (
            "http://localhost:5001"  # Using different port to avoid conflicts
        )

    def print_header(self, title):
        print("\n" + "=" * 60)
        print(f"🎨 {title}")
        print("=" * 60)

    def print_step(self, step):
        print(f"\n📍 {step}")
        print("-" * 40)

    def print_success(self, message):
        print(f"✅ {message}")

    def print_info(self, message):
        print(f"ℹ️  {message}")

    def print_error(self, message):
        print(f"❌ {message}")

    def demo_1_check_assets(self):
        """Demo 1: Check what wallpapers are available in assets"""
        self.print_step("Checking available wallpaper assets")

        if not self.assets_dir.exists():
            self.print_error(f"Assets directory not found: {self.assets_dir}")
            return False

        total_wallpapers = 0
        total_packs = 0

        for pack_dir in self.assets_dir.iterdir():
            if pack_dir.is_dir():
                total_packs += 1
                image_files = [
                    f
                    for f in pack_dir.iterdir()
                    if f.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]
                ]
                pack_count = len(image_files)
                total_wallpapers += pack_count

                # Check for metadata
                metadata_file = pack_dir / "pack_info.json"
                has_metadata = metadata_file.exists()

                print(
                    f"  📦 {pack_dir.name}: {pack_count} wallpapers {'(with metadata)' if has_metadata else '(no metadata)'}"
                )

                # Show a few wallpaper names
                for i, img in enumerate(image_files[:3]):
                    print(f"     • {img.name}")
                if len(image_files) > 3:
                    print(f"     • ... and {len(image_files) - 3} more")

        self.print_success(
            f"Found {total_packs} wallpaper packs with {total_wallpapers} total wallpapers"
        )
        return total_packs > 0

    def demo_2_run_packer(self):
        """Demo 2: Run the wallpaper packer to create static files"""
        self.print_step("Running wallpaper packer to create static files")

        packer_script = self.project_root / "scripts" / "pack_wallpapers.py"
        if not packer_script.exists():
            self.print_error(f"Packer script not found: {packer_script}")
            return False

        try:
            # Run the packer with force flag
            result = subprocess.run(
                [sys.executable, str(packer_script), "--force", "--verbose"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                self.print_success("Wallpaper packer completed successfully!")
                # Show some output
                lines = result.stdout.strip().split("\n")
                for line in lines[-10:]:  # Show last 10 lines
                    if "✅" in line or "📊" in line or "=" in line:
                        print(f"  {line}")
            else:
                self.print_error("Packer failed:")
                print(result.stderr)
                return False
        except subprocess.TimeoutExpired:
            self.print_error("Packer timed out")
            return False
        except Exception as e:
            self.print_error(f"Error running packer: {e}")
            return False

        return True

    def demo_3_check_static_files(self):
        """Demo 3: Check what was created in static folder"""
        self.print_step("Checking generated static files")

        if not self.static_dir.exists():
            self.print_error(f"Static directory not found: {self.static_dir}")
            return False

        # Check manifest
        manifest_path = self.static_dir / "manifest.json"
        if manifest_path.exists():
            with open(manifest_path, "r") as f:
                manifest = json.load(f)

            self.print_success("Found manifest.json:")
            print(f"  📊 Total packs: {manifest['total_packs']}")
            print(f"  📊 Total wallpapers: {manifest['total_wallpapers']}")
            print(f"  📊 Total size: {manifest['total_size_mb']} MB")
            print(f"  📊 Generated: {manifest['generated']}")

        # Check packs folder
        packs_dir = self.static_dir / "packs"
        if packs_dir.exists():
            zip_files = list(packs_dir.glob("*.zip"))
            self.print_success(f"Found {len(zip_files)} ZIP files:")
            for zip_file in zip_files:
                size_mb = zip_file.stat().st_size / 1024 / 1024
                print(f"  📦 {zip_file.name}: {size_mb:.1f} MB")

        # Check previews folder
        previews_dir = self.static_dir / "previews"
        if previews_dir.exists():
            preview_files = list(previews_dir.glob("*.jpg"))
            self.print_success(f"Found {len(preview_files)} preview images:")
            for preview in preview_files:
                print(f"  🖼️  {preview.name}")

        return True

    def demo_4_start_server(self):
        """Demo 4: Start Flask server for API testing"""
        self.print_step("Starting Flask server for API testing")

        app_file = self.project_root / "website" / "app.py"
        if not app_file.exists():
            self.print_error(f"Flask app not found: {app_file}")
            return False

        try:
            # Start server in background with custom port
            env = os.environ.copy()
            env["FLASK_RUN_PORT"] = "5001"
            env["FLASK_APP"] = "app.py"

            self.server_process = subprocess.Popen(
                [sys.executable, str(app_file)],
                cwd=str(self.project_root / "website"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )

            # Wait for server to start
            self.print_info("Waiting for server to start...")
            time.sleep(3)

            # Test if server is running
            try:
                response = requests.get(f"{self.server_url}/", timeout=5)
                if response.status_code == 200:
                    self.print_success(f"Server running at {self.server_url}")
                    return True
            except requests.exceptions.ConnectionError:
                pass

            self.print_error("Server failed to start properly")
            return False

        except Exception as e:
            self.print_error(f"Error starting server: {e}")
            return False

    def demo_5_test_api(self):
        """Demo 5: Test wallpaper API endpoints"""
        self.print_step("Testing wallpaper API endpoints")

        # Test packs endpoint
        try:
            response = requests.get(
                f"{self.server_url}/api/wallpapers/packs", timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.print_success("✅ Packs API working:")
                    print(f"  📦 Found {data['total_packs']} packs:")
                    for pack in data["packs"]:
                        print(
                            f"     • {pack['name']}: {pack['count']} wallpapers ({pack['size_mb']} MB)"
                        )
                        print(
                            f"       Shuffle: {'✅' if pack['shuffle_enabled'] else '❌'} | "
                            f"New tab: {'✅' if pack['shuffle_on_new_tab'] else '❌'}"
                        )
                else:
                    self.print_error("Packs API returned error")
                    return False
            else:
                self.print_error(f"Packs API failed: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Error testing packs API: {e}")
            return False

        return True

    def demo_6_test_shuffle(self):
        """Demo 6: Test shuffle functionality"""
        self.print_step("Testing wallpaper shuffle functionality")

        # Get available packs first
        try:
            response = requests.get(
                f"{self.server_url}/api/wallpapers/packs", timeout=10
            )
            data = response.json()
            if not data.get("success") or not data.get("packs"):
                self.print_error("No packs available for shuffle test")
                return False

            # Test shuffle for each pack
            for pack in data["packs"]:
                pack_name = pack["name"]
                if pack["shuffle_enabled"]:
                    try:
                        shuffle_response = requests.get(
                            f"{self.server_url}/api/wallpapers/shuffle/{pack_name}",
                            timeout=10,
                        )
                        if shuffle_response.status_code == 200:
                            shuffle_data = shuffle_response.json()
                            if shuffle_data.get("success"):
                                wallpaper = shuffle_data["wallpaper"]
                                self.print_success(
                                    f"🎲 Random from {pack_name}: {wallpaper['name']}"
                                )
                                print(f"   File: {wallpaper['filename']}")
                                if wallpaper.get("description"):
                                    print(f"   Description: {wallpaper['description']}")
                                if wallpaper.get("tags"):
                                    print(f"   Tags: {', '.join(wallpaper['tags'])}")
                            else:
                                self.print_error(f"Shuffle failed for {pack_name}")
                        else:
                            self.print_error(
                                f"Shuffle API failed for {pack_name}: {shuffle_response.status_code}"
                            )
                    except Exception as e:
                        self.print_error(f"Error testing shuffle for {pack_name}: {e}")
                else:
                    self.print_info(f"Shuffle disabled for {pack_name}")

        except Exception as e:
            self.print_error(f"Error in shuffle test: {e}")
            return False

        return True

    def demo_7_test_download(self):
        """Demo 7: Test wallpaper pack download"""
        self.print_step("Testing wallpaper pack download")

        # Get first available pack
        try:
            response = requests.get(
                f"{self.server_url}/api/wallpapers/packs", timeout=10
            )
            data = response.json()
            if not data.get("success") or not data.get("packs"):
                self.print_error("No packs available for download test")
                return False

            first_pack = data["packs"][0]
            pack_name = first_pack["name"]

            # Test download
            download_response = requests.get(
                f"{self.server_url}/api/wallpapers/pack/{pack_name}/download",
                timeout=30,
            )

            if download_response.status_code == 200:
                # Save to temp file and check
                with tempfile.NamedTemporaryFile(
                    suffix=".zip", delete=False
                ) as temp_file:
                    temp_file.write(download_response.content)
                    temp_path = temp_file.name

                try:
                    # Verify it's a valid zip
                    with zipfile.ZipFile(temp_path, "r") as zf:
                        file_list = zf.namelist()
                        self.print_success(
                            f"✅ Downloaded {pack_name} pack successfully!"
                        )
                        print(
                            f"   Size: {len(download_response.content) / 1024 / 1024:.1f} MB"
                        )
                        print(f"   Files in ZIP: {len(file_list)}")

                        # Show some contents
                        for f in file_list[:5]:
                            print(f"     • {f}")
                        if len(file_list) > 5:
                            print(f"     • ... and {len(file_list) - 5} more")

                    # Clean up temp file
                    os.unlink(temp_path)
                    return True

                except zipfile.BadZipFile:
                    self.print_error("Downloaded file is not a valid ZIP")
                    os.unlink(temp_path)
                    return False
            else:
                self.print_error(f"Download failed: {download_response.status_code}")
                return False

        except Exception as e:
            self.print_error(f"Error testing download: {e}")
            return False

    def demo_8_web_interface(self):
        """Demo 8: Show web interface info"""
        self.print_step("Web Interface Information")

        self.print_success("🌐 Web interface available at:")
        print(f"   Main site: {self.server_url}/")
        print(f"   Wallpapers: {self.server_url}/wallpapers")
        print(f"   API docs: {self.server_url}/api/wallpapers/packs")

        self.print_info("Features available in web interface:")
        print("   • Browse wallpaper packs with previews")
        print("   • Download packs as ZIP files")
        print("   • Enable/disable shuffle settings")
        print("   • Test shuffle functionality")
        print("   • Repack wallpapers from assets")
        print("   • View pack statistics and metadata")

        return True

    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, "server_process"):
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                self.server_process.kill()

    def run_demo(self):
        """Run the complete wallpaper system demo"""
        self.print_header("HueSurf Wallpaper System Demo")
        print("This demo showcases the complete wallpaper pack system:")
        print("• Asset scanning and metadata reading")
        print("• Wallpaper packing to static files")
        print("• Web API for downloads and shuffle")
        print("• Integration testing")

        demos = [
            ("Check Assets", self.demo_1_check_assets),
            ("Run Packer", self.demo_2_run_packer),
            ("Check Static Files", self.demo_3_check_static_files),
            ("Start Server", self.demo_4_start_server),
            ("Test API", self.demo_5_test_api),
            ("Test Shuffle", self.demo_6_test_shuffle),
            ("Test Download", self.demo_7_test_download),
            ("Web Interface Info", self.demo_8_web_interface),
        ]

        results = []

        try:
            for demo_name, demo_func in demos:
                try:
                    success = demo_func()
                    results.append((demo_name, success))

                    if not success:
                        self.print_error(
                            f"Demo '{demo_name}' failed, continuing with next demo..."
                        )

                    time.sleep(1)  # Brief pause between demos

                except KeyboardInterrupt:
                    self.print_error("\nDemo interrupted by user")
                    break
                except Exception as e:
                    self.print_error(f"Demo '{demo_name}' crashed: {e}")
                    results.append((demo_name, False))

        finally:
            self.cleanup()

        # Show final results
        self.print_header("Demo Results Summary")

        passed = sum(1 for _, success in results if success)
        total = len(results)

        print(f"Completed {total} demos, {passed} passed, {total - passed} failed\n")

        for demo_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} - {demo_name}")

        if passed == total:
            self.print_success(
                "\n🎉 All demos passed! The wallpaper system is working perfectly!"
            )
        else:
            self.print_error(
                f"\n⚠️  {total - passed} demos failed. Check the output above for details."
            )

        print(f"\n📝 Next steps:")
        print("   • Visit the web interface to test manually")
        print("   • Integrate with HueSurf browser build")
        print("   • Add more wallpaper packs to assets folder")
        print("   • Customize pack_info.json files for better metadata")

        return passed == total


if __name__ == "__main__":
    demo = WallpaperDemo()
    success = demo.run_demo()
    sys.exit(0 if success else 1)
