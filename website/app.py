from flask import Flask, render_template, request, jsonify
import os

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
