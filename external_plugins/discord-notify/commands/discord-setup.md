---
description: Set up Discord bot credentials for the discord-notify plugin — walks through token and guild ID configuration
allowed-tools: [Read, Write, Bash]
---

# Discord Setup

Configure Discord bot credentials so the discord-notify plugin can send messages.

## Step 1 — Check existing config

```bash
cat ~/.claude/discord.env 2>/dev/null
```

If the file exists and has both `DISCORD_TOKEN` and `DISCORD_GUILD_ID` set (non-empty), tell the user:
> "Discord credentials already configured. Want to reconfigure? (yes / no)"

If they say no, stop.

## Step 2 — Guide the user through bot setup

Present this to the user:

> **To use this plugin, you need a Discord bot token and your server's Guild ID.**
>
> ### Get your Bot Token
> 1. Go to https://discord.com/developers/applications
> 2. Click **New Application** (or select an existing one)
> 3. Go to the **Bot** section in the sidebar
> 4. Click **Reset Token** and copy it
> 5. Enable **Message Content Intent** under Privileged Gateway Intents
> 6. Go to **OAuth2 > URL Generator**, select `bot` scope + `Send Messages` permission
> 7. Copy the generated URL and open it to invite the bot to your server
>
> ### Get your Guild (Server) ID
> 1. In Discord, go to **Settings > Advanced > Developer Mode** (toggle on)
> 2. Right-click your server name in the sidebar
> 3. Click **Copy Server ID**
>
> Paste your **Bot Token** when ready.

Wait for the user to provide the bot token.

Then ask:
> "Now paste your **Guild (Server) ID**."

Wait for the guild ID.

## Step 3 — Validate inputs

- Bot token should be a long string (50+ chars), typically contains dots
- Guild ID should be a numeric string (17-20 digits)

If either looks wrong, warn the user but let them proceed if they confirm.

## Step 4 — Write credentials

Create the directory if needed, then write the file:

```bash
mkdir -p ~/.claude
```

Write `~/.claude/discord.env`:
```
DISCORD_TOKEN={token}
DISCORD_GUILD_ID={guild_id}
```

Do NOT include the values in any output shown to the user after writing. Just confirm:
> "Credentials saved to `~/.claude/discord.env`."

## Step 5 — Test the connection

Run a quick test to verify the bot can connect:

```bash
~/.claude/bin/discord "general" "discord-notify plugin connected successfully"
```

If it succeeds, tell the user setup is complete.

If it fails, show the error and suggest:
- Check that the bot was invited to the server
- Check that the bot has Send Messages permission
- Check that the token and guild ID are correct
- Re-run `/discord-setup` to reconfigure
