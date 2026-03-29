
import os
import shutil
import tempfile
import pytest
from pathlib import Path
import sys

# Ensure we can import website
sys.path.append(os.getcwd())

from website.app import _scan_wallpaper_packs
import website.app

@pytest.fixture
def temp_wallpapers_dir():
    # Create a temp directory structure
    temp_dir = tempfile.mkdtemp()
    base_dir = Path(temp_dir)

    # Create pack1
    pack1 = base_dir / "Pack1"
    pack1.mkdir()
    (pack1 / "image1.png").write_text("a" * 1024) # 1KB
    (pack1 / "image2.jpg").write_text("b" * 2048) # 2KB
    (pack1 / "other.txt").write_text("c" * 512)   # 0.5KB

    # Create sub directory in pack1
    sub = pack1 / "sub"
    sub.mkdir()
    (sub / "deep.png").write_text("d" * 1024)     # 1KB

    yield base_dir

    # Cleanup
    shutil.rmtree(temp_dir)

def test_scan_wallpaper_packs_logic(temp_wallpapers_dir):
    # Clear cache
    website.app._PACKS_CACHE = None

    packs = _scan_wallpaper_packs(temp_wallpapers_dir)

    assert len(packs) == 1
    pack = packs[0]

    assert pack["name"] == "Pack1"

    # Check count: only top level png and jpg.
    # image1.png, image2.jpg -> 2.
    # deep.png is in sub, so ignored. other.txt is ignored.
    assert pack["count"] == 2

    # Check size: all files.
    # 1024 + 2048 + 512 + 1024 = 4608 bytes.
    # The function converts to MB: round(size / (1024 * 1024), 2)
    expected_size_mb = round(4608 / (1024 * 1024), 2)
    assert pack["size_mb"] == expected_size_mb
