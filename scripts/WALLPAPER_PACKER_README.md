# HueSurf Wallpaper Packer

A Python script that packages wallpaper packs from the assets folder into the website's static folder for web distribution.

## 🎯 Purpose

This script automates the process of:
- Creating ZIP files from wallpaper folders in `assets/Wallpapers/`
- Generating preview thumbnails for each pack
- Creating a manifest file for the web API
- Organizing everything in the website's static folder structure

## 📋 Requirements

Install the required dependencies:

```bash
pip install -r scripts/requirements_packer.txt
```

Required packages:
- **Pillow**: For image processing and thumbnail creation
- **tqdm**: For progress bars (optional)
- **pathvalidate**: For file validation (optional)
- **colorlog**: For enhanced logging (optional)

## 🚀 Usage

### Basic Usage
```bash
# Pack all wallpapers to static folder
python scripts/pack_wallpapers.py
```

### Advanced Options
```bash
# Force overwrite existing files
python scripts/pack_wallpapers.py --force

# Verbose output for debugging
python scripts/pack_wallpapers.py --verbose

# Custom source and output directories
python scripts/pack_wallpapers.py --source /path/to/wallpapers --output /path/to/static

# Combine options
python scripts/pack_wallpapers.py --force --verbose
```

### Via Web API
You can also trigger repacking through the website (requires `POST` method):
```bash
curl -X POST http://localhost:5000/api/wallpapers/repack
```

## 📁 Directory Structure

### Input Structure
```
assets/Wallpapers/
├── Indiana/
│   ├── pack_info.json
│   ├── mount tree.png
│   ├── roads.png
│   ├── rush.png
│   └── tracks.png
└── Star/
    ├── pack_info.json
    ├── black.png
    ├── blue.png
    └── ...
```

### Output Structure
```
website/static/wallpapers/
├── manifest.json              # Global manifest for API
├── packs/                     # ZIP files for download
│   ├── indiana.zip
│   └── star.zip
├── previews/                  # Pack preview images
│   ├── indiana.jpg
│   └── star.jpg
└── thumbs/                    # Thumbnail cache
    ├── indiana.jpg
    └── star.jpg
```

## 📄 Pack Info Format

Each wallpaper pack should have a `pack_info.json` file:

```json
{
  "pack_name": "Indiana",
  "version": "1.0.0",
  "author": "HueSurf Team",
  "description": "Indiana-themed wallpapers featuring scenic landscapes",
  "category": "Landscape",
  "created_date": "2025-01-01",
  "shuffle_enabled": true,
  "shuffle_on_new_tab": true,
  "wallpapers": [
    {
      "filename": "mount tree.png",
      "name": "Mount Tree",
      "description": "Scenic mountain view with tree silhouette",
      "tags": ["mountain", "tree", "nature", "landscape"]
    }
  ],
  "colors": {
    "primary": "#E86F51",
    "secondary": "#4A90E2",
    "accent": "#50C878"
  },
  "recommended_for": ["desktop", "tablet"],
  "min_resolution": "1920x1080",
  "license": "MIT",
  "settings": {
    "shuffle_interval": "new_tab",
    "transition_effect": "fade",
    "transition_duration": 500,
    "allow_user_shuffle": true,
    "remember_last_wallpaper": false
  }
}
```

## 🎨 Supported Image Formats

- PNG (*.png)
- JPEG (*.jpg, *.jpeg)
- WebP (*.webp)
- BMP (*.bmp)
- TIFF (*.tiff)

## ⚙️ What the Script Does

1. **Scans** the `assets/Wallpapers/` directory for pack folders
2. **Reads** pack_info.json files for metadata (creates defaults if missing)
3. **Creates** ZIP files containing all wallpapers + metadata
4. **Generates** preview thumbnails (300x200px JPEG)
5. **Calculates** file sizes and hashes for integrity
6. **Creates** a global manifest.json for the web API
7. **Organizes** everything in the website's static folder

## 📊 Statistics Output

The script provides detailed statistics:

```
==================================================
📊 PACKING STATISTICS
==================================================
Packs processed:      2
Wallpapers processed: 15
ZIP files created:    2
Previews created:     2
Total size:           12.3 MB
==================================================
```

## 🔧 Integration with Website

The Flask app automatically uses packed wallpapers when available:

1. **API Priority**: Static manifest → Assets fallback
2. **Download URLs**: `/static/wallpapers/packs/{pack}.zip`
3. **Preview URLs**: `/static/wallpapers/previews/{pack}.jpg`
4. **Auto-repacking**: Via `/api/wallpapers/repack` endpoint

## 🐛 Troubleshooting

### Common Issues

**"No image files found"**
- Ensure wallpaper files have supported extensions
- Check file permissions

**"Failed to create thumbnail"**
- Install Pillow correctly: `pip install Pillow`
- Check if images are corrupted

**"Permission denied"**
- Run with appropriate file permissions
- Check output directory write access

**"Module not found"**
- Install requirements: `pip install -r requirements_packer.txt`

### Debug Mode
Run with `--verbose` flag for detailed logging:
```bash
python scripts/pack_wallpapers.py --verbose
```

## 🔄 Workflow Integration

### Development Workflow
1. Add new wallpapers to `assets/Wallpapers/{PackName}/`
2. Create or update `pack_info.json`
3. Run packer script: `python scripts/pack_wallpapers.py --force`
4. Test website: `python website/app.py`
5. Visit `/wallpapers` to verify packs

### Production Deployment
1. Run packer before deployment
2. Include `website/static/wallpapers/` in deployment
3. No need to include `assets/Wallpapers/` in production

## 📝 Notes

- **Force flag** (`--force`): Overwrites existing ZIP files and previews
- **Caching**: Thumbnails are cached to avoid regeneration
- **Manifest**: Always regenerated to ensure consistency
- **Hashing**: SHA256 hashes ensure file integrity
- **Compression**: ZIP files use DEFLATE compression level 6

## 🤝 Contributing

When adding new wallpaper packs:
1. Create folder in `assets/Wallpapers/`
2. Add high-quality images (1920x1080+ recommended)
3. Create detailed `pack_info.json`
4. Run packer script to test
5. Commit both assets and generated static files

## 📜 License

MIT License - Part of the HueSurf project