---
description: Send a message to a Discord channel
argument-hint: <channel> <message>
allowed-tools: [Read, Bash]
---

# Discord

Send a message to a Discord channel via the bot API.

## Arguments

The user invoked this command with: $ARGUMENTS

## Step 1 — Check credentials

```bash
test -f ~/.claude/discord.env && grep -q "DISCORD_TOKEN=." ~/.claude/discord.env && echo "OK" || echo "MISSING"
```

If MISSING, tell the user:
> "Discord credentials not configured. Run `/discord-setup` first."

Stop here.

## Step 2 — Parse arguments

The first argument is the channel name (strip leading `#` if present).
Everything after is the message.

If no arguments provided, ask the user:
> "Which channel and what message? Usage: `/discord <channel> <message>`"

## Step 3 — Send

```bash
~/.claude/bin/discord "<channel>" "<message>"
```

Report success or surface any errors to the user.
