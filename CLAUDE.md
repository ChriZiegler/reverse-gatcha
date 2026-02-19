# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Reverse Gacha is a Discord bot where users "pull" randomized art prompts (1–2 aspects with a rarity tier) and then complete them by uploading artwork. It uses discord.py slash commands.

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
- **gacha.py** — `roll()` produces a prompt dict (`{id, prompt, rarity, time, created_at, image_path}`). Picks 1–2 random aspects (no two with the same `category`), sums their prices, and resolves rarity by matching against price thresholds.
- **storage.py** — JSON-file persistence layer. Pulls stored in `data/pulls.json`, uploaded images saved to `data/images/`
- **prompts.yaml** — Data file with `rarities` (each has `name`, `price` threshold, `time`) and `aspects` (each has `name`, `price`, optional `category` and `description`). Rarity is determined by the highest tier whose price threshold is met by the sum of chosen aspect prices.
