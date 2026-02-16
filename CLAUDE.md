# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Reverse Gacha is a Discord bot where users "pull" randomized art prompts (a species + element combo with a rarity tier) and then complete them by uploading artwork. It uses discord.py slash commands.

## Commands

```bash
# Activate virtualenv
source venv/bin/activate

# Run the bot
python bot.py

# Run with auto-reload on file changes (watchfiles is installed)
watchfiles "python bot.py" *.py

# Test the gacha roll logic standalone
python gacha.py
```

## Environment

Requires a `.env` file with `DISCORD_TOKEN` set. Python 3.10+ (uses `X | Y` union syntax).

## Architecture

- **bot.py** — Discord client, slash command handlers (`/pull`, `/complete`, `/pulls`), and `GalleryView` (paginated embed viewer with prev/next buttons)
- **gacha.py** — `roll()` produces a prompt dict (`{id, prompt, rarity, time, created_at, image_path}`) by weighted-random picking a species + element + rarity from `prompts.json`
- **storage.py** — JSON-file persistence layer. Pulls stored in `data/pulls.json`, uploaded images saved to `data/images/`
- **prompts.json** — Data file with `species`, `elements`, and `rarities` arrays. Each entry has a `name` and optional `weight` (higher = more common; default base is 10 for species/elements). Rarities use explicit weights summing to 100.
