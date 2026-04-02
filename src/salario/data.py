"""Data acquisition — downloads salary data if not already present."""

import urllib.request
from pathlib import Path

_DATA_URL = "https://www.kode24.no/files/2025/09/01/kode24s%20l%C3%B8nnstall%202025.json"
_DATA_PATH = Path.cwd() / "data" / "kode24_2025.json"
_USER_AGENT = "Mozilla/5.0 (compatible; salario/0.1; +https://github.com/ivarurdalen/salario)"


def ensure_data() -> Path:
    """Return path to the data file, downloading it first if not present."""
    if not _DATA_PATH.exists():
        print(f"Downloading salary data from kode24 → {_DATA_PATH}")
        _DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(_DATA_URL, headers={"User-Agent": _USER_AGENT})
        with urllib.request.urlopen(request) as response, _DATA_PATH.open("wb") as output:
            output.write(response.read())
        print("Download complete.")
    return _DATA_PATH
