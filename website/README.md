# HueSurf Website

The official website for HueSurf - a lightweight Chromium-based browser without ads, AI, sponsors, or bloat.

## Overview

This is a Flask-based website built for onboarding users to the HueSurf browser project. It provides information about the browser's features, development status, team information, and allows users to follow the project's progress.

## Features

- **Responsive Design**: Mobile-first design with Bootstrap 5
- **Modern UI**: Clean, professional interface with custom styling
- **Dynamic Content**: Flask-powered with Jinja2 templates
- **SEO Friendly**: Proper meta tags and structured content
- **Performance Optimized**: Lightweight and fast-loading
- **Shared Hosting Ready**: Configured for Namecheap shared hosting

## Project Structure

```
website/
├── app.py                 # Main Flask application
├── passenger_wsgi.py      # WSGI entry point for shared hosting
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # Jinja2 templates
│   ├── base.html         # Base template with navigation and footer
│   ├── index.html        # Landing page
│   ├── features.html     # Features showcase
│   ├── download.html     # Download page (development status)
│   └── about.html        # About page with team info
└── static/               # Static assets
    ├── css/              # Custom stylesheets (currently using CDN)
    └── js/               # Custom JavaScript (currently using CDN)
```

## Local Development

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/H3-Apps/HueSurf.git
   cd HueSurf/website
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the development server:**
   ```bash
   python app.py
   ```

5. **Open your browser:**
   Navigate to `http://localhost:5000`

## Deployment to Namecheap Shared Hosting

### Prerequisites

- Namecheap shared hosting account with Python support
- cPanel or file manager access
- SSH access (optional but recommended)

### Deployment Steps

1. **Upload Files:**
   - Upload all files to your domain's public folder (usually `public_html` or similar)
   - Ensure `passenger_wsgi.py` is in the root directory of your domain

2. **Install Dependencies:**
   - If you have SSH access:
     ```bash
     cd /path/to/your/domain
     python -m pip install --user -r requirements.txt
     ```
   - If no SSH access, contact Namecheap support to install the required packages

3. **Configure Python App:**
   - In cPanel, go to "Python App" or "Setup Python App"
   - Create a new application:
     - Python version: 3.7+ (latest available)
     - App directory: Your domain folder
     - App URL: Your domain
     - Startup file: `passenger_wsgi.py`

4. **Environment Variables:**
   - Set `FLASK_ENV=production` in your hosting control panel
   - Optionally set `SECRET_KEY` for enhanced security

5. **Restart the Application:**
   - Use the "Restart" button in cPanel's Python App section

### Important Files for Shared Hosting

- **`passenger_wsgi.py`**: WSGI entry point required by shared hosting
- **`requirements.txt`**: Lists all Python dependencies
- **`.htaccess`** (auto-generated): URL rewriting rules

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment mode | `development` |
| `SECRET_KEY` | Flask secret key | `your-secret-key-here` |

## Dependencies

- **Flask 2.3.3**: Web framework
- **Werkzeug 2.3.7**: WSGI toolkit
- **Jinja2 3.1.2**: Template engine
- **Bootstrap 5.3.2** (CDN): CSS framework
- **Font Awesome 6.4.0** (CDN): Icons
- **Google Fonts** (CDN): Typography

## Pages

- **Home (`/`)**: Landing page with project overview
- **Features (`/features`)**: Detailed feature showcase
- **Download (`/download`)**: Download page with development status
- **About (`/about`)**: Team information and project story
- **Support (`/support`)**: Help and support resources
- **Privacy (`/privacy`)**: Privacy policy
- **Donate (`/donate`)**: Donation information

## Customization

### Adding New Pages

1. Create a new route in `app.py`:
   ```python
   @app.route('/newpage')
   def newpage():
       return render_template('newpage.html')
   ```

2. Create the template in `templates/newpage.html`
3. Add navigation link in `templates/base.html`

### Styling

The website uses Bootstrap 5 with custom CSS variables defined in `base.html`. Key color variables:

- `--primary-color`: #00d4aa (HueSurf green)
- `--secondary-color`: #0066cc (HueSurf blue)
- `--accent-color`: #ff6b6b (Accent red)

### Content Updates

Most content is managed through the Flask context processor in `app.py`. Update the `inject_globals()` function to modify:

- App information (name, version, tagline)
- Team members
- Feature lists
- Social links

## Troubleshooting

### Common Issues

1. **500 Internal Server Error:**
   - Check that `passenger_wsgi.py` is in the correct location
   - Verify all dependencies are installed
   - Check error logs in cPanel

2. **Static Files Not Loading:**
   - Ensure static files are uploaded to the correct directory
   - Check file permissions (should be 644 for files, 755 for directories)

3. **Templates Not Found:**
   - Verify template files are in the `templates/` directory
   - Check that template names match exactly in routes

### Logs

- **Development**: Flask will output errors to the console
- **Production**: Check cPanel error logs or `/var/log/` if you have SSH access

## Contributing

This website is part of the HueSurf project. To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

MIT License - Do what you want, just don't add ads. Or sell it with little to no difference.

## Support

- **GitHub**: [HueSurf Repository](https://github.com/H3-Apps/HueSurf)
- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join conversations in GitHub Discussions

---

Made with 💚 by 3 dudes (H3, vexalous, and i love pand ass) and potentially a robot if Javier goes insane! 😜