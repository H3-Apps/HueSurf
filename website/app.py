from flask import Flask, render_template, request, jsonify, send_file, abort
import os
import zipfile
import json
from pathlib import Path
import tempfile
import shutil

app = Flask(__name__)

# Configuration
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your-secret-key-here")
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


@app.route("/api/wallpapers/repack")
def repack_wallpapers():
    """Trigger repacking of wallpapers to static folder"""
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
                    "output": result.stdout,
                }
            )
        else:
            return jsonify(
                {
                    "success": False,
                    "message": "Failed to repack wallpapers",
                    "error": result.stderr,
                }
            ), 500

    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "message": "Repacking timed out"}), 500
    except Exception as e:
        return jsonify(
            {"success": False, "message": f"Error repacking wallpapers: {str(e)}"}
        ), 500


@app.route("/api/contact", methods=["POST"])
def contact():
    """Handle contact form submissions"""
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        message = data.get("message")

        # Here you would typically send an email or save to database
        # For now, we'll just return a success response

        return jsonify(
            {
                "success": True,
                "message": "Thanks for reaching out! We'll get back to you soon (unless Javier's robot took over).",
            }
        )
    except Exception as e:
        return jsonify(
            {
                "success": False,
                "message": "Oops! Something went wrong. Please try again or hit us up on GitHub.",
            }
        ), 500


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
        packs = []

        if wallpapers_dir.exists():
            for pack_dir in wallpapers_dir.iterdir():
                if pack_dir.is_dir():
                    # Read pack metadata if available
                    pack_info = {}
                    pack_info_path = pack_dir / "pack_info.json"
                    if pack_info_path.exists():
                        with open(pack_info_path, "r") as f:
                            pack_info = json.load(f)

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

        return jsonify({"success": True, "packs": packs, "total_packs": len(packs)})
    except Exception as e:
        return jsonify(
            {"success": False, "message": f"Error fetching wallpaper packs: {str(e)}"}
        ), 500


@app.route("/api/wallpapers/pack/<pack_name>/download")
def download_wallpaper_pack(pack_name):
    """Download a wallpaper pack as a zip file from static files"""
    try:
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

        # Create temporary zip file
        temp_dir = tempfile.mkdtemp()
        zip_path = Path(temp_dir) / f"{pack_name}_wallpapers.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
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
            zipf.writestr(f"{pack_name}/pack_info.json", json.dumps(metadata, indent=2))

        @app.after_request
        def cleanup(response):
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
            return response

        return send_file(
            zip_path,
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


@app.route("/api/wallpapers/all")
def get_all_wallpapers():
    """Get list of all wallpapers with direct download links"""
    try:
        wallpapers_dir = Path(__file__).parent.parent / "assets" / "Wallpapers"
        wallpapers = []

        if wallpapers_dir.exists():
            for pack_dir in wallpapers_dir.iterdir():
                if pack_dir.is_dir():
                    # Read pack info for wallpaper metadata
                    pack_info = {}
                    wallpaper_metadata = {}
                    pack_info_path = pack_dir / "pack_info.json"
                    if pack_info_path.exists():
                        with open(pack_info_path, "r") as f:
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
                            wallpapers.append(
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

        return jsonify(
            {"success": True, "wallpapers": wallpapers, "total": len(wallpapers)}
        )
    except Exception as e:
        return jsonify(
            {"success": False, "message": f"Error fetching wallpapers: {str(e)}"}
        ), 500


@app.route("/api/wallpapers/single/<pack_name>/<filename>")
def get_single_wallpaper(pack_name, filename):
    """Download a single wallpaper file"""
    try:
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


@app.route("/api/wallpapers/shuffle/<pack_name>")
def get_random_wallpaper(pack_name):
    """Get a random wallpaper from the specified pack"""
    try:
        import random

        wallpapers_dir = Path(__file__).parent.parent / "assets" / "Wallpapers"
        pack_dir = wallpapers_dir / pack_name

        if not pack_dir.exists() or not pack_dir.is_dir():
            abort(404, description=f"Wallpaper pack '{pack_name}' not found")

        # Find all image files
        images = []
        for ext in [".png", ".jpg", ".jpeg", ".webp"]:
            images.extend(list(pack_dir.glob(f"*{ext}")))

        if not images:
            abort(404, description="No wallpapers found in pack")

        # Select random wallpaper
        random_image = random.choice(images)

        # Read pack info for metadata
        pack_info_path = pack_dir / "pack_info.json"
        wallpaper_meta = {}
        if pack_info_path.exists():
            with open(pack_info_path, "r") as f:
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
