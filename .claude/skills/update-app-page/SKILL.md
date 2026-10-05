---
name: update-app-page
description: Use when the LudwigTech site (byronludwig.github.io) needs to catch up with a change to Dot Art or Kids Pretend Shop — a new release, a renamed app, new features, new store screenshots, or "the page needs updating for the latest app change".
---

# Updating the site for an app change

## Overview

The site describes what a user gets from Google Play, nothing else. A release contains only the commits up
to and including its `versionName` bump; anything after the bump belongs to the next release, even on
`main`/`master`.

## The apps

| Site key | Repo | Store copy | Phone screenshots |
|---|---|---|---|
| `dot-art` | `~/StudioProjects/matchthepicture` | `docs/store-listing.md` | `docs/play/listing-phone/` |
| `pretend-shop` | `~/StudioProjects/orderingapp` | `app-store-description.md` | `screenshots/marketing/phone/` |

`RELEASE_NOTES.md` holds the Play notes per release, but older cuts predate it; there, read
`git log <previous cut>..<cut>` instead.

## Steps

1. **Find what is live and what is cut.**
   `python3 .claude/skills/update-app-page/sync_app.py status`
   prints the Play version, title and ads flag, the bump commit for that version, the repo's latest bump,
   and the commits after it.
2. **Pick the target version.** The live Play version, or the cut the user says ships next. Never a version
   that is not cut yet. If unsure which, ask. When the change the user means sits after the latest cut, the
   answer is "nothing to do until it is cut" — say so and stop.
3. **Read the app's features at the target cut**, not HEAD:
   `git -C <repo> show <cut>:<store copy>` and the release notes, plus `git log <previous cut>..<cut>`.
4. **Read listing-only changes against Play.** Store title, description and screenshots publish without a
   build, so a listing commit after the cut may already be live. `status` gives the Play title and ads
   flag; for description wording, fetch the Play page and compare.
5. **Regenerate screenshots from the cut:**
   `python3 .claude/skills/update-app-page/sync_app.py shots <app> --version <x.y> --preview <scratch>/sheet.png`
   then look at the contact sheet. If it reports a path the cut does not track, the screenshot set
   predates that layout — leave the site's images alone and tell the user.
6. **Edit `index.html`** — check every place below.
7. **Commit one app per commit.** Push when the target version is live on Play, or when the user says to
   push ahead of a release they are about to publish. Otherwise commit and hold the push.

## What to check in index.html

- App name: `<meta name="description">`, the section `<h2>`, the Google Play badge `alt`.
- `.blurb` and `.features` against the store copy at the cut. A new feature can make old copy false
  (Dot Art's "no streaks" after the daily streak shipped).
- Keep `.features` at an even count; the grid leaves an orphan card on an odd one.
- Each screenshot `alt` describes the new image — look at it, don't trust the old text.
- A new screenshot needs a new `<img>`; one that dropped out of the listing needs removing, and the `shots`
  mapping in `sync_app.py` updated.
- Hero line "No pop-up ads" must stay true for both apps.

## Common mistakes

| Mistake | Fix |
|---|---|
| Copy or screenshots taken from HEAD | Read them at the target version's bump commit |
| Treating a merged feature as released | `status` shows it after the repo cut — wait for the next cut |
| Assuming a listing rename needs a release | Check the live Play title |
| Fixed counts in copy ("155 pictures", "eleven themes") | Vague wording; the counts change every release |
| Pushing an app whose version is not live yet, unasked | Commit it, hold the push |
| Site already pushed ahead of Play | Leave it if the user published ahead on purpose; ask before rolling back |

## Pushing

The remote is HTTPS and this shell has no GitHub credentials, so `git push` fails with
`could not read Username`. Ask the user to push (IDE or their terminal).
