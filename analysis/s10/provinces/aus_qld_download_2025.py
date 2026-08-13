#!/usr/bin/env python3
"""Run the existing download.py over the 2025+ Queensland manifest.

download.py resolves manifest/raw/log from the prov tag, so the 2025 period is
driven through the tag "aus_qld_2025" (manifest + raw dir are symlinks to
aus_qld_manifest_2025.json and the existing aus_qld_raw/).  The tag is also
registered in PROV_UA so the desktop-Chrome UA is sent -- both Queensland hosts
sit behind an Azure WAF that 403s library user agents.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import download  # noqa: E402

download.PROV_UA["aus_qld_2025"] = download.BROWSER_UA
sys.argv = ["download.py", "aus_qld_2025"]
download.main()
