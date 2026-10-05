#!/usr/bin/env python3
import argparse
import re
import subprocess
import sys
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image

SITE = Path(__file__).resolve().parents[3]
HOME = Path.home()
GRADLE = "app/build.gradle.kts"
SHOT_SIZE = (720, 1280)
WEBP_QUALITY = 80

APPS = {
    "dot-art": {
        "repo": HOME / "StudioProjects/matchthepicture",
        "package": "com.byronludwig.matchthepicture",
        "listing": "docs/store-listing.md",
        "release_notes": "RELEASE_NOTES.md",
        "shots": {
            "01": "docs/play/listing-phone/01-picture-shelf.png",
            "02": "docs/play/listing-phone/02-perfect-solve.png",
            "03": "docs/play/listing-phone/03-free-draw-mirror.png",
            "04": "docs/play/listing-phone/05-board-mid-solve.png",
            "05": "docs/play/listing-phone/06-hint.png",
            "06": "docs/play/listing-phone/07-dark-mode-ocean.png",
            "07": "docs/play/listing-phone/04-daily-mid-solve.png",
        },
    },
    "pretend-shop": {
        "repo": HOME / "StudioProjects/orderingapp",
        "package": "com.byronludwig.pretendplay",
        "listing": "app-store-description.md",
        "release_notes": "RELEASE_NOTES.md",
        "shots": {
            "01": "screenshots/marketing/phone/01_hero.png",
            "02": "screenshots/marketing/phone/02_orders.png",
            "03": "screenshots/marketing/phone/03_total.png",
            "04": "screenshots/marketing/phone/04_tap_to_pay.png",
            "05": "screenshots/marketing/phone/05_more_shops.png",
            "06": "screenshots/marketing/phone/06_allergy.png",
            "07": "screenshots/marketing/phone/07_customise.png",
            "08": "screenshots/marketing/phone/08_parents.png",
        },
    },
}


def git(repo, *args, binary=False):
    out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True)
    return out.stdout if binary else out.stdout.decode().strip()


def repo_version(repo, ref="HEAD"):
    match = re.search(r'versionName\s*=\s*"([^"]+)"', git(repo, "show", f"{ref}:{GRADLE}"))
    return match.group(1)


def bump_commit(repo, version):
    commits = git(repo, "log", "--reverse", "--format=%h", "-S", f'versionName = "{version}"', "--", GRADLE)
    if not commits:
        sys.exit(f"no commit sets versionName {version} in {repo}")
    return commits.splitlines()[0]


def play_listing(package):
    url = f"https://play.google.com/store/apps/details?id={package}&hl=en_GB&gl=GB"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    page = urllib.request.urlopen(request, timeout=30).read().decode("utf-8", "replace")
    version = re.search(r'\[\[\["(\d+(?:\.\d+)+)"\]\]', page)
    title = re.search(r'<title id="main-title">(.*?) – Apps on Google Play', page)
    return {
        "version": version.group(1) if version else "unknown",
        "title": title.group(1) if title else "unknown",
        "contains_ads": "Contains ads" in page,
    }


def status(name):
    app = APPS[name]
    repo = app["repo"]
    live = play_listing(app["package"])
    head_version = repo_version(repo)
    head_bump = bump_commit(repo, head_version)
    after_bump = git(repo, "log", "--format=%h %ad %s", "--date=short", f"{head_bump}..HEAD")

    print(f"== {name} ({app['package']})")
    print(f"Play live      : {live['version']}  title={live['title']!r}  contains_ads={live['contains_ads']}")
    if live["version"] != "unknown":
        print(f"Live cut       : {bump_commit(repo, live['version'])}  (versionName {live['version']})")
    print(f"Repo cut       : {head_bump}  (versionName {head_version}, branch {git(repo, 'branch', '--show-current')})")
    print(f"After repo cut : {'(none)' if not after_bump else ''}")
    for line in after_bump.splitlines():
        print(f"  {line}")
    print()


def shots(name, version, preview):
    app = APPS[name]
    repo = app["repo"]
    ref = bump_commit(repo, version)
    out_dir = SITE / "assets/shots" / name
    missing = [source for source in app["shots"].values()
               if subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{ref}:{source}"],
                                 capture_output=True).returncode]
    if missing:
        sys.exit(f"{version} ({ref}) does not track: {', '.join(missing)} - nothing written")
    sheet = []
    for site_name, source in app["shots"].items():
        image = Image.open(BytesIO(git(repo, "show", f"{ref}:{source}", binary=True))).convert("RGB")
        image = image.resize(SHOT_SIZE, Image.LANCZOS)
        image.save(out_dir / f"{site_name}.webp", "WEBP", quality=WEBP_QUALITY, method=6)
        sheet.append(image.resize((240, 427)))
        print(f"{site_name}.webp  <-  {ref}:{source}")
    if preview:
        contact = Image.new("RGB", (240 * len(sheet), 427), "white")
        for index, thumb in enumerate(sheet):
            contact.paste(thumb, (240 * index, 0))
        contact.save(preview)
        print(f"contact sheet: {preview}")


def main():
    parser = argparse.ArgumentParser(description="Compare LudwigTech apps with Google Play and refresh site screenshots.")
    commands = parser.add_subparsers(dest="command", required=True)
    status_cmd = commands.add_parser("status", help="live Play version against the repo's release cuts")
    status_cmd.add_argument("app", nargs="?", choices=APPS)
    shots_cmd = commands.add_parser("shots", help="regenerate site screenshots from a release cut")
    shots_cmd.add_argument("app", choices=APPS)
    shots_cmd.add_argument("--version", required=True, help="versionName whose bump commit to read screenshots from")
    shots_cmd.add_argument("--preview", help="write a contact sheet PNG here")
    args = parser.parse_args()

    if args.command == "status":
        for name in [args.app] if args.app else APPS:
            status(name)
    else:
        shots(args.app, args.version, args.preview)


if __name__ == "__main__":
    main()
