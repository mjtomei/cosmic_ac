#!/usr/bin/env python3
"""Run the existing aus_download.py over the 2025+ NSW manifest.

aus_download.py resolves its manifest/raw/log paths from the state tag, so the
2025 period is driven through the tag "nsw2025", whose manifest and raw dir are
symlinks to aus_nsw_manifest_2025.json and the existing aus_nsw_raw/.
Filenames carry the date, so there is no collision with 2006-2019.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import aus_download  # noqa: E402

sys.argv = ["aus_download.py", "nsw2025", "--delay", "1.05"]
aus_download.main()
