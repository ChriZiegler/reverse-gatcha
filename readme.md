# Reverse Gacha

A Discord bot that generates randomized art prompts (species + element + rarity) for users to draw and submit.

## Setup

```bash
# Create and activate virtualenv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install discord.py python-dotenv watchfiles
```

Create a `.env` file with your Discord bot token:

```
DISCORD_TOKEN=your_token_here
```

## Commands

```bash
# Run the bot :)
python3 bot.py

# Test gacha roll logic standalone (prints 5 sample rolls) :^)
python3 gacha.py
```

## Watch Mode

To auto-restart the bot whenever you change a file, use `watchfiles`:

```bash
watchfiles "python3 bot.py" *.py
```

This watches the current directory for changes and re-runs `python3 bot.py` automatically on each save.
