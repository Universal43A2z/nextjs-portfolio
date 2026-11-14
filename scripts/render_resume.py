from __future__ import annotations

import os
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "resume" / "resume.html"
OUTPUT = ROOT / "public" / "resume.pdf"


def main() -> None:
    browser_path = os.environ.get("CHROMIUM_PATH") or shutil.which("chromium")
    launch_options: dict[str, object] = {"headless": True}
    if browser_path:
        launch_options["executable_path"] = browser_path

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**launch_options)
        page = browser.new_page()
        page.goto(SOURCE.as_uri(), wait_until="load")
        page.pdf(
            path=str(OUTPUT),
            format="A4",
            print_background=True,
            prefer_css_page_size=True,
            display_header_footer=False,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        browser.close()

    print(f"Generated {OUTPUT.relative_to(ROOT)} from {SOURCE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
