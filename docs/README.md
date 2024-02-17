# Homepage

<div align="center">

<img src="https://cdn.discordapp.com/avatars/954930077815144499/25cb95c1f74c5205c55942554a1c4859.png?size=1024" alt="" width="100">

</div>

![Github Commit](https://img.shields.io/github/commit-activity/w/raianah/message-tracker) ![Maintenance](https://img.shields.io/maintenance/yes/2024) ![Last Commit](https://img.shields.io/github/last-commit/raianah/message-tracker) ![Language](https://img.shields.io/github/languages/count/raianah/message-tracker) [![Discord](https://img.shields.io/discord/1015509043130933278?logo=discord\&logoColor=%23FFF\&label=Message+Tracker\&labelColor=%235865F2\&color=%232B2D31)](https://discord.gg/HRvAb2cjBg) ![Disnake Version](https://img.shields.io/badge/Disnake%20Version-v2.8.0+-lightblue) ![Version](https://img.shields.io/badge/official%20version-v1.0.0-lightblue)

## Message Tracker

Message Tracker is a powerful yet user-friendly Discord Bot that focuses on storing and maintaining your message data from your server for moderation & transparency. It features powerful yet safe methods of storing message data across your server channels.

## Features of Message Tracker

* [x] **Safe Storage**: Uses secure methods to store message data, ensuring only authorized users can access it.
* [x] **Server-wide Tracking**: Capable of monitoring and logging messages across all channels in your server.
* [x] **User-friendly Interface**: Designed to be easy to use, allowing for quick setup and management divided by commands.
* [x] **Non-Instant Access**: Upon adding this bot into your server, it won't save messages instantly...until you enable it via command!
* [x] **Report Easily**: With its very own report command, you can report to your local server moderators with or without your user information!

## Getting Started

* Invite Message Tracker Bot on [Discord](https://discord.com/api/oauth2/authorize?client\_id=954930077815144499\&permissions=275146468368\&scope=bot).
* Begin storing messages by using `/begin`. For more information about commands, head to this [page](commands.md).

## Documentation

* [Official Documentation](./)

## Support

[![Discord Banner](https://discordapp.com/api/guilds/1015509043130933278/widget.png?style=banner2)](https://discord.gg/HRvAb2cjBg)

## Deploy your own Message Tracker

* You can also deploy your very own Message Tracker into your Discord Bot providing a bot token from [Discord Developer Portal](https://discord.com/developers/applications).
* Commit `git clone https://github.com/raianah/message-tracker.git`
* Create a `.env` file containing the following:
  * `MAIN_TOKEN = "YOUR_DISCORD_BOT_TOKEN"`
* Create a folder named `data`. Inside `data` folder create another folder named `db`. This is the default path for your SQLite database.
* Install python packages through `requirements.txt`.
* Run `main.py`.

## Prerequisites

* Python 3.8 or better.
* Disnake v2.8.0 or better.
* Discord Bot Token (provided via creating a bot on [Discord Developer Portal](https://discord.com/developers/applications))
* SQLite
* A device/server that can run the bot. If you are planning to run your bot 24/7, consider hosting your bot to a server.
