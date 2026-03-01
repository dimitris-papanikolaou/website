#!/usr/bin/env python3
"""
Download all Dropbox-linked files from content/publications.yml into assets/papers/,
then update the YAML to use local paths. Uses only stdlib (no PyYAML).
Run from project root: python scripts/download_papers.py
"""
import re
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse, unquote

PROJECT_ROOT = Path(__file__).resolve().parent.parent
YAML_PATH = PROJECT_ROOT / "content" / "publications.yml"
PAPERS_DIR = PROJECT_ROOT / "assets" / "papers"
DROPBOX_PREFIX = "https://www.dropbox.com/"


def extract_dropbox_urls(yaml_text):
    """Find all lines containing url: https://www.dropbox.com/... and return (full_line, url)."""
    urls = []
    for line in yaml_text.splitlines():
        if "url:" in line and DROPBOX_PREFIX in line:
            # Get the URL part (after "url:")
            m = re.match(r'^(\s*url:\s*)(.+)$', line)
            if m:
                prefix, rest = m.groups()
                url = rest.strip()
                urls.append((line, url))
    return urls


def filename_from_url(url):
    """Last path segment of URL, URL-decoded."""
    parsed = urlparse(url)
    path = parsed.path
    name = path.rstrip("/").split("/")[-1]
    return unquote(name)


def download_file(url, dest_path):
    """Return True if download succeeded."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; download-papers/1.0)"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            if resp.status != 200:
                return False
            dest_path.write_bytes(resp.read())
        return True
    except Exception as e:
        print(f"  Failed: {e}")
        return False


def main():
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)

    yaml_text = YAML_PATH.read_text(encoding="utf-8")
    url_lines = extract_dropbox_urls(yaml_text)

    # Build unique filename for each URL (disambiguate duplicates)
    seen_filenames = {}
    url_to_local = {}

    for line, url in url_lines:
        base_name = filename_from_url(url)
        if not base_name:
            continue
        name = base_name
        counter = 0
        while name in seen_filenames and seen_filenames[name] != url:
            counter += 1
            stem, suffix = base_name.rsplit(".", 1) if "." in base_name else (base_name, "")
            if suffix:
                name = f"{stem}_{counter}.{suffix}"
            else:
                name = f"{base_name}_{counter}"
        seen_filenames[name] = url
        dest = PAPERS_DIR / name
        local_path = f"assets/papers/{name}"

        if dest.exists():
            print(f"Already exists: {name}")
            url_to_local[url] = local_path
            continue

        print(f"Downloading: {name} ...")
        if download_file(url, dest):
            url_to_local[url] = local_path
            print(f"  OK -> {local_path}")
        else:
            print(f"  Skip (leave URL unchanged)")
        time.sleep(0.5)

    # Replace URLs in YAML text with local paths
    new_text = yaml_text
    for url, local_path in url_to_local.items():
        # Replace the exact url value (avoid replacing in comments/abstracts)
        old_line = f"url: {url}"
        new_line = f"url: {local_path}"
        if old_line in new_text:
            new_text = new_text.replace(old_line, new_line, 1)

    YAML_PATH.write_text(new_text, encoding="utf-8")
    print(f"\nUpdated {YAML_PATH} with {len(url_to_local)} local paths.")


if __name__ == "__main__":
    main()
