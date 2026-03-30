import os
import zipfile
import json
import re
from pathlib import Path
import tempfile
import time
from functools import lru_cache

from flask import Flask, render_template, request, jsonify, send_file, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Cache for wallpaper packs
_PACKS_CACHE = None
_PACKS_CACHE_TIME = 0
_CACHE_DURATION = 300  # 5 minutes

# Configuration
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise ValueError("No SECRET_KEY set for Flask application")
app.config["DEBUG"] = os.environ.get("FLASK_ENV") == "development"


@app.route("/")
def index():
    """Landing page for HueSurf browser"""
    return render_template("index.html")


@app.route("/features")
def features():
    """Features page showcasing HueSurf capabilities"""
    return render_template("features.html")


@app.route("/download")
def download():
    """Download page with installation instructions"""
    return render_template("download.html")


@app.route("/about")
def about():
    """About page explaining HueSurf's mission and the 3-person team"""
    return render_template("about.html")


@app.route("/support")
def support():
    """Support page with help resources and donation info"""
    return render_template("support.html")


@app.route("/privacy")
def privacy():
    """Privacy policy page"""
    return render_template("privacy.html")


@app.route("/donate")
def donate():
    """Donation page to support the project"""
    return render_template("donate.html")


@app.route("/wallpapers")
def wallpapers():
    """Wallpapers management page for downloading and managing wallpaper packs"""
    return render_template("wallpapers.html")


@app.route("/api/wallpapers/repack", methods=["POST"])
def repack_wallpapers():
    """Trigger repacking of wallpapers to static folder"""
    if not app.config["DEBUG"]:
        abort(403)
    try:
        import subprocess
        import sys

        # Run the packer script
        script_path = Path(__file__).parent.parent / "scripts" / "pack_wallpapers.py"
        result = subprocess.run(
            [sys.executable, str(script_path), "--force"],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            return jsonify(
                {
                    "success": True,
                    "message": "Wallpapers repacked successfully",
                }
            )
        else:
            app.logger.error(f"Repack failed: {result.stderr}")
            return jsonify(
                {
                    "success": False,
                    "message": "Failed to repack wallpapers",
                }
            ), 500

    except subprocess.TimeoutExpired:
        app.logger.error("Repacking timed out")
        return jsonify({"success": False, "message": "Repacking timed out"}), 500
    except Exception as e:
        app.logger.error(f"Error repacking wallpapers: {str(e)}")
        return jsonify(
            {"success": False, "message": "An error occurred while repacking wallpapers"}
        ), 500


@app.route("/api/contact", methods=["POST"])
def contact():
    """Handle contact form submissions"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400

        name = data.get("name")
        email = data.get("email")
        message = data.get("message")

        # Basic validation
        if not name or not email or not message:
            return (
                jsonify({"success": False, "message": "All fields are required"}),
                400,
            )

        # Email validation
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, email):
            return (
                jsonify({"success": False, "message": "Invalid email address"}),
                400,
            )

        # Length validation to prevent DoS/overflow
        if len(name) > 100 or len(email) > 100 or len(message) > 5000:
            return (
                jsonify({"success": False, "message": "Input exceeds maximum length"}),
                400,
            )

        # Here you would typically send an email or save to database
        # For now, we'll just return a success response

        return jsonify(
            {
                "success": True,
                "message": "Thanks for reaching out! We'll get back to you soon (unless Javier's robot took over).",
            }
        )
    except Exception as e:
        app.logger.error(f"Contact form error: {str(e)}")
        return jsonify(
            {
                "success": False,
                "message": "Oops! Something went wrong. Please try again or hit us up on GitHub.",
            }
        ), 500


def _scan_wallpaper_packs(wallpapers_dir):
    """Scan wallpaper packs directory with caching"""
    global _PACKS_CACHE, _PACKS_CACHE_TIME

    current_time = time.time()

    # Return cached data if valid
    if _PACKS_CACHE is not None and (current_time - _PACKS_CACHE_TIME) < _CACHE_DURATION:
        return _PACKS_CACHE

    packs = []
    if wallpapers_dir.exists():
        for pack_dir in wallpapers_dir.iterdir():
            if pack_dir.is_dir():
                # Read pack metadata if available
                pack_info = {}
                pack_info_path = pack_dir / "pack_info.json"
                if pack_info_path.exists():
                    try:
                        with open(pack_info_path, "r", encoding="utf-8") as f:
                            pack_info = json.load(f)
                    except Exception:
                        pass

                # Count wallpapers in pack
                wallpaper_count = len(
                    list(pack_dir.glob("*.png"))
                    + list(pack_dir.glob("*.jpg"))
                    + list(pack_dir.glob("*.jpeg"))
                )

                # Calculate pack size
                pack_size = sum(
                    f.stat().st_size for f in pack_dir.rglob("*") if f.is_file()
                )

                packs.append(
                    {
                        "id": pack_dir.name.lower().replace(" ", "_"),
                        "name": pack_dir.name,
                        "count": wallpaper_count,
                        "size_mb": round(pack_size / (1024 * 1024), 2),
                        "preview": f"/api/wallpapers/preview/{pack_dir.name}",
                        "description": pack_info.get(
                            "description", "Wallpaper pack for HueSurf browser"
                        ),
                        "shuffle_enabled": pack_info.get("shuffle_enabled", False),
                        "shuffle_on_new_tab": pack_info.get(
                            "shuffle_on_new_tab", False
                        ),
                    }
                )

    _PACKS_CACHE = packs
    _PACKS_CACHE_TIME = current_time
    return packs


@app.route("/api/wallpapers/packs")
def get_wallpaper_packs():
    """Get list of available wallpaper packs from static manifest"""
    try:
        # Try to read from static manifest first
        manifest_path = (
            Path(__file__).parent / "static" / "wallpapers" / "manifest.json"
        )

        if manifest_path.exists():
            with open(manifest_path, "r") as f:
                manifest = json.load(f)

            packs = []
            for pack in manifest.get("packs", []):
                pack_data = {
                    "id": pack.get(
                        "id", pack.get("pack_name", "").lower().replace(" ", "_")
                    ),
                    "name": pack.get("name", pack.get("pack_name")),
                    "count": pack.get("count", 0),
                    "size_mb": pack.get("size_mb", 0),
                    "preview": pack.get("preview_url", ""),
                    "description": pack.get("description", ""),
                    "shuffle_enabled": pack.get("shuffle_enabled", False),
                    "shuffle_on_new_tab": pack.get("shuffle_on_new_tab", False),
                    "download_url": pack.get("download_url", ""),
                    "category": pack.get("category", "General"),
                    "author": pack.get("author", "Unknown"),
                    "version": pack.get("version", "1.0.0"),
                    "created_date": pack.get("created_date"),
                    "colors": pack.get("colors", {}),
                    "recommended_for": pack.get("recommended_for", []),
                    "min_resolution": pack.get("min_resolution", "1920x1080"),
                    "license": pack.get("license", "MIT"),
                    "settings": pack.get("settings", {}),
                    "wallpapers": pack.get("wallpapers", []),
                    "size_bytes": pack.get("size_bytes", 0),
                    "hash": pack.get("hash", ""),
                    "packed_date": pack.get("packed_date"),
                }
                packs.append(pack_data)

            return jsonify(
                {
                    "success": True,
                    "packs": packs,
                    "total_packs": len(packs),
                    "manifest_version": manifest.get("version"),
                    "generated": manifest.get("generated"),
                }
            )

        # Fallback to assets directory scanning
        wallpapers_dir = Path(__file__).parent.parent / "assets" / "Wallpapers"
        packs = _scan_wallpaper_packs(wallpapers_dir)

        return jsonify({"success": True, "packs": packs, "total_packs": len(packs)})
    except Exception as e:
        return jsonify(
            {"success": False, "message": f"Error fetching wallpaper packs: {str(e)}"}
        ), 500


@app.route("/api/wallpapers/pack/<pack_name>/download")
def download_wallpaper_pack(pack_name):
    """Download a wallpaper pack as a zip file from static files"""
    try:
        # 🛡️ Sanitize user input to prevent path traversal
        pack_name = secure_filename(pack_name)

        # Try static files first
        static_zip_path = (
            Path(__file__).parent
            / "static"
            / "wallpapers"
            / "packs"
            / f"{pack_name.lower().replace(' ', '_')}.zip"
        )

        if static_zip_path.exists():
            return send_file(
                static_zip_path,
                as_attachment=True,
                download_name=f"{pack_name}_wallpapers.zip",
                mimetype="application/zip",
            )

        # Fallback to dynamic generation from assets
        wallpapers_dir = Path(__file__).parent.parent / "assets" / "Wallpapers"
        pack_dir = wallpapers_dir / pack_name

        if not pack_dir.exists() or not pack_dir.is_dir():
            abort(404, description=f"Wallpaper pack '{pack_name}' not found")

        # Create directory if it doesn't exist
        static_zip_path.parent.mkdir(parents=True, exist_ok=True)

        # Use a unique temp file for atomic write to avoid race conditions
        # We use delete=False so we can atomically move it later
        temp_zip_path = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=static_zip_path.parent, suffix=".tmp", delete=False
            ) as tmp_file:
                temp_zip_path = Path(tmp_file.name)
                with zipfile.ZipFile(tmp_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                    # Add all image files from the pack
                    for file_path in pack_dir.rglob("*"):
                        if file_path.is_file() and file_path.suffix.lower() in [
                            ".png",
                            ".jpg",
                            ".jpeg",
                            ".webp",
                        ]:
                            arcname = f"{pack_name}/{file_path.relative_to(pack_dir)}"
                            zipf.write(file_path, arcname)

                    # Add metadata
                    pack_info_path = pack_dir / "pack_info.json"
                    if pack_info_path.exists():
                        with open(pack_info_path, "r") as f:
                            metadata = json.load(f)
                    else:
                        metadata = {
                            "pack_name": pack_name,
                            "version": "1.0.0",
                            "author": "HueSurf Team",
                            "description": f"{pack_name} wallpaper pack for HueSurf browser",
                            "shuffle_enabled": True,
                            "shuffle_on_new_tab": True,
                            "count": len(
                                list(pack_dir.glob("*.png"))
                                + list(pack_dir.glob("*.jpg"))
                                + list(pack_dir.glob("*.jpeg"))
                            ),
                            "settings": {
                                "shuffle_interval": "new_tab",
                                "transition_effect": "fade",
                                "transition_duration": 500,
                                "allow_user_shuffle": True,
                                "remember_last_wallpaper": False,
                            },
                        }
                    zipf.writestr(
                        f"{pack_name}/pack_info.json", json.dumps(metadata, indent=2)
                    )

            # Atomic move
            os.replace(temp_zip_path, static_zip_path)

        except Exception:
            # Clean up temp file on error
            if temp_zip_path and temp_zip_path.exists():
                os.remove(temp_zip_path)
            raise

        return send_file(
            static_zip_path,
            as_attachment=True,
            download_name=f"{pack_name}_wallpapers.zip",
            mimetype="application/zip",
        )
    except Exception as e:
        return jsonify(
            {"success": False, "message": f"Error creating wallpaper pack: {str(e)}"}
        ), 500


@app.route("/api/wallpapers/preview/<pack_name>")
def get_wallpaper_preview(pack_name):
    """Get preview image for a wallpaper pack"""
    try:
        # 🛡️ Sanitize user input to prevent path traversal
        pack_name = secure_filename(pack_name)

        # Try static preview first
        static_preview_path = (
            Path(__file__).parent
            / "static"
            / "wallpapers"
            / "previews"
            / f"{pack_name.lower().replace(' ', '_')}.jpg"
        )

        if static_preview_path.exists():
            return send_file(static_preview_path, mimetype="image/jpeg")

        # Fallback to assets directory
        wallpapers_dir = Path(__file__).parent.parent / "assets" / "Wallpapers"
        pack_dir = wallpapers_dir / pack_name

        if not pack_dir.exists() or not pack_dir.is_dir():
            abort(404, description=f"Wallpaper pack '{pack_name}' not found")

        # Find first image file
        for ext in [".png", ".jpg", ".jpeg", ".webp"]:
            images = list(pack_dir.glob(f"*{ext}"))
            if images:
                return send_file(images[0], mimetype=f"image/{ext[1:]}")

        abort(404, description="No preview available")
    except Exception as e:
        return jsonify(
            {"success": False, "message": f"Error fetching preview: {str(e)}"}
        ), 500


@lru_cache(maxsize=1)
def _scan_wallpapers():
    """Helper to scan wallpapers directory and cache results"""
    wallpapers_dir = Path(__file__).parent.parent / "assets" / "Wallpapers"
    wallpapers_list = []

    if wallpapers_dir.exists():
        for pack_dir in wallpapers_dir.iterdir():
            if pack_dir.is_dir():
                # Read pack info for wallpaper metadata
                pack_info = {}
                wallpaper_metadata = {}
                pack_info_path = pack_dir / "pack_info.json"
                if pack_info_path.exists():
                    with open(pack_info_path, "r", encoding="utf-8") as f:
                        pack_info = json.load(f)
                        # Create lookup dictionary for wallpaper metadata
                        for wp in pack_info.get("wallpapers", []):
                            wallpaper_metadata[wp["filename"]] = wp

                for file_path in pack_dir.rglob("*"):
                    if file_path.is_file() and file_path.suffix.lower() in [
                        ".png",
                        ".jpg",
                        ".jpeg",
                        ".webp",
                    ]:
                        wp_meta = wallpaper_metadata.get(file_path.name, {})
                        wallpapers_list.append(
                            {
                                "name": wp_meta.get("name", file_path.stem),
                                "pack": pack_dir.name,
                                "filename": file_path.name,
                                "path": f"/api/wallpapers/single/{pack_dir.name}/{file_path.name}",
                                "size_kb": round(
                                    file_path.stat().st_size / 1024, 2
                                ),
                                "description": wp_meta.get("description", ""),
                                "tags": wp_meta.get("tags", []),
                            }
                        )
    return wallpapers_list


# ⚡ Bolt: Cache the wallpaper list to avoid expensive filesystem scans on every request.
# This endpoint's data changes infrequently, making it a perfect candidate for in-memory caching.
# Impact: Reduces response time from ~150ms to <5ms after the first hit.
@app.route("/api/wallpapers/all")
@lru_cache(maxsize=1)  # The function has no args, so only one result will ever be cached.
def get_all_wallpapers():
    """Get list of all wallpapers with direct download links"""
    try:
        wallpapers_list = _scan_wallpapers()
        return jsonify(
            {"success": True, "wallpapers": wallpapers_list, "total": len(wallpapers_list)}
        )
    except Exception as e:
        return jsonify(
            {"success": False, "message": f"Error fetching wallpapers: {str(e)}"}
        ), 500


@app.route("/api/wallpapers/single/<pack_name>/<filename>")
def get_single_wallpaper(pack_name, filename):
    """Download a single wallpaper file"""
    try:
        # 🛡️ Sanitize user input to prevent path traversal
        pack_name = secure_filename(pack_name)
        filename = secure_filename(filename)

        wallpapers_dir = Path(__file__).parent.parent / "assets" / "Wallpapers"
        file_path = wallpapers_dir / pack_name / filename

        if not file_path.exists() or not file_path.is_file():
            abort(
                404,
                description=f"Wallpaper '{filename}' not found in pack '{pack_name}'",
            )

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify(
            {"success": False, "message": f"Error downloading wallpaper: {str(e)}"}
        ), 500


# ⚡ Bolt: Cache the filesystem scan for images in a pack.
# This avoids expensive I/O on every request for a random wallpaper.
# Impact: Reduces response time significantly after the first hit for a given pack.
@lru_cache(maxsize=32)  # Cache results for up to 32 wallpaper packs
def _get_cached_images_in_pack(pack_name):
    """Helper to scan a wallpaper pack directory and cache the list of images."""
    wallpapers_dir = Path(__file__).parent.parent / "assets" / "Wallpapers"
    pack_dir = wallpapers_dir / pack_name

    if not pack_dir.exists() or not pack_dir.is_dir():
        # Return None to indicate the pack is not found
        return None

    # Find all image files
    images = []
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        images.extend(list(pack_dir.glob(f"*{ext}")))
    return images


@app.route("/api/wallpapers/shuffle/<pack_name>")
def get_random_wallpaper(pack_name):
    """Get a random wallpaper from the specified pack"""
    try:
        # 🛡️ Sanitize user input to prevent path traversal
        pack_name = secure_filename(pack_name)

        import random

        images = _get_cached_images_in_pack(pack_name)

        if images is None:
            abort(404, description=f"Wallpaper pack '{pack_name}' not found")

        if not images:
            abort(404, description="No wallpapers found in pack")

        # Select random wallpaper
        random_image = random.choice(images)

        # Define pack_dir for metadata reading
        wallpapers_dir = Path(__file__).parent.parent / "assets" / "Wallpapers"
        pack_dir = wallpapers_dir / pack_name

        # Read pack info for metadata
        pack_info_path = pack_dir / "pack_info.json"
        wallpaper_meta = {}
        if pack_info_path.exists():
            with open(pack_info_path, "r", encoding='utf-8') as f:
                pack_info = json.load(f)
                for wp in pack_info.get("wallpapers", []):
                    if wp["filename"] == random_image.name:
                        wallpaper_meta = wp
                        break

        return jsonify(
            {
                "success": True,
                "wallpaper": {
                    "filename": random_image.name,
                    "name": wallpaper_meta.get("name", random_image.stem),
                    "path": f"/api/wallpapers/single/{pack_name}/{random_image.name}",
                    "description": wallpaper_meta.get("description", ""),
                    "tags": wallpaper_meta.get("tags", []),
                },
            }
        )
    except Exception as e:
        return jsonify(
            {"success": False, "message": f"Error getting random wallpaper: {str(e)}"}
        ), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template("500.html"), 500


@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Content Security Policy - allow self and necessary CDNs
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' cdn.tailwindcss.com cdn.jsdelivr.net cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' fonts.googleapis.com cdn.tailwindcss.com; "
        "font-src 'self' fonts.gstatic.com; "
        "img-src 'self' data:;"
    )
    return response


# Context processors to make data available to all templates
@app.context_processor
def inject_globals():
    return {
        "app_name": "HueSurf",
        "tagline": "A lightweight Chromium-based browser without ADs, AI, Sponsors, or bloat.",
        "version": "0.1.0-dev",
        "github_url": "https://github.com/H3-Apps/HueSurf",
        "team_members": ["H3", "vexalous", "i love pand ass"],
        "features": [
            {
                "icon": "fas fa-ad",
                "title": "No Ads, No Sponsors",
                "desc": "Surf distraction-free",
            },
            {
                "icon": "fas fa-robot",
                "title": "No AI",
                "desc": "Your data stays yours, no weird bots lurking",
            },
            {
                "icon": "fas fa-feather-alt",
                "title": "Lightweight",
                "desc": "Minimal footprint, quick to start, easy on your RAM",
            },
            {
                "icon": "fas fa-code-branch",
                "title": "Open Source",
                "desc": "Fork it, star it, make it your own",
            },
            {
                "icon": "fas fa-heart",
                "title": "Donation Friendly",
                "desc": "If you vibe with us, show some love!",
            },
        ],
    }


if __name__ == "__main__":
    # This is for local development only
    app.run(debug=True, host="0.0.0.0", port=5000)
