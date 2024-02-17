"""
    MIT License

    Copyright (c) 2024 rai

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

import ast
from disnake import Embed, Member, ApplicationCommandInteraction, Color, Option, OptionType, TextChannel, Role
from disnake.ext import commands
from message_tracker.db import db

class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Settings is loaded.")

    @commands.slash_command(description="Activate Message Tracker in your server!")
    async def begin(self, ctx: ApplicationCommandInteraction):
        await ctx.response.defer()
        toggle_checker = db.field(f"SELECT Toggle FROM \"{ctx.guild.id}\" WHERE UserID = 123")
        if toggle_checker == 0:
            db.execute(f"UPDATE \"{ctx.guild.id}\" SET Toggle = 1")
            embed=Embed(color=Color.green(), title="Successfully Activated!", description=f"{ctx.guild.me.mention} has been activated in this server. All messages will now be stored and can be used accordingly. Use `/help` for more information and guides.\n\nNot sure about what the bot stores? Check our [Privacy Policy](), [Terms of Service]() here.\n\nGitHub link: https://github.com/raianah/MessageTracker")
            embed.set_footer(text="To disable Message Tracker, type /stop.", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            embed=Embed(color=Color.red(), title="Already Activated!", description=f"{ctx.guild.me.mention} has already been activated in this server. Use `/help` for more information and guides.\n\nNot sure about what the bot stores? Check our [Privacy Policy](), [Terms of Service]() here.\n\nGitHub link: https://github.com/raianah/MessageTracker")
            embed.set_footer(text="To disable Message Tracker, type /stop.", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)

    @commands.slash_command(description="Disable Message Tracker in your server!")
    async def stop(self, ctx: ApplicationCommandInteraction):
        await ctx.response.defer()
        toggle_checker = db.field(f"SELECT Toggle FROM \"{ctx.guild.id}\" WHERE UserID = 123")
        if toggle_checker == 1:
            db.execute(f"UPDATE \"{ctx.guild.id}\" SET Toggle = 0")
            embed=Embed(color=Color.green(), title="Successfully Disabled!", description=f"{ctx.guild.me.mention} has been disabled in this server. All messages will now be ignored. Use `/help` for more information and guides.\n\nNot sure about what the bot stores? Check our [Privacy Policy](), [Terms of Service]() here.\n\nGitHub link: https://github.com/raianah/MessageTracker")
            embed.set_footer(text="To activate Message Tracker, type /begin.", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            embed=Embed(color=Color.red(), title="Already Disabled!", description=f"{ctx.guild.me.mention} has already been disabled in this server. Use `/help` for more information and guides.\n\nNot sure about what the bot stores? Check our [Privacy Policy](), [Terms of Service]() here.\n\nGitHub link: https://github.com/raianah/MessageTracker")
            embed.set_footer(text="To activate Message Tracker, type /begin.", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)

    # ENABLE #
    @commands.slash_command()
    async def enable(self, ctx: ApplicationCommandInteraction):
        pass

    @enable.sub_command(description="Enable logs for message inputs.", option=[
        Option("channel", "The channel to log the messages.", OptionType.channel, required=True)
    ])
    async def logs(self, ctx: ApplicationCommandInteraction, channel: TextChannel):
        await ctx.response.defer()
        if ctx.author.guild_permissions.manage_channels:
            if isinstance(channel, TextChannel):
                db.execute(f"UPDATE \"{ctx.guild.id}\" SET LoggingChannel = ? WHERE UserID = 123", channel.id)
                embed=Embed(color=Color.green(), title="Successfully Enabled!", description=f"{ctx.author.mention} enabled messages edited/deleted in {channel.mention}. Messages sent will not be logged here.")
                embed.set_footer(text="To disable logs, type /disable logs.", icon_url=ctx.author.avatar.url)
            else:
                embed=Embed(color=Color.red(), title="Invalid Channel!", description=f"{ctx.author.mention}, the channel you provided is not a text channel. Please include only text channels.")
                embed.set_footer(text="Please make sure that the channel you select is an instance of TEXT CHANNEL.", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            embed=Embed(color=Color.red(), title="Permission Denied!", description=f"{ctx.author.mention}, you do not have the permission to commit this command in this server. Make sure you have the **MANAGE CHANNELS** permission or higher.")
            await ctx.send(embed=embed)

    @enable.sub_command(description="Enable mod-logs for user reports.", option=[
        Option("channel", "The channel to log the messages.", OptionType.channel, required=False),
        Option("mod_role", "The role to notify.", OptionType.channel, required=False),
        Option("required_role", "The required role to use this command.", OptionType.role, required=False)
    ])
    async def modlogs(self, ctx: ApplicationCommandInteraction, channel: TextChannel = None, mod_role: Role = None, required_role: Role = None):
        await ctx.response.defer()
        if ctx.author.guild_permissions.manage_channels:
            if channel is None and mod_role is None and required_role is None:
                embed=Embed(color=Color.red(), title="Invalid Arguments!", description=f"{ctx.author.mention}, you need to include either a channel or a role to enable mod-logs.")
                return await ctx.send(embed=embed)
            if channel:
                if isinstance(channel, TextChannel):
                    db.execute(f"UPDATE \"{ctx.guild.id}\" SET ModlogChannel = ? WHERE UserID = 123", channel.id)
                    channel_option = channel.mention if channel else 'N/A'
                else:
                    embed=Embed(color=Color.red(), title="Invalid Channel!", description=f"{ctx.author.mention}, the channel you provided is not a text channel. Please include only text channels.")
                    embed.set_footer(text="Please make sure that the channel you select is an instance of TEXT CHANNEL.", icon_url=ctx.author.avatar.url)
                    return await ctx.send(embed=embed)
            if mod_role:
                db.execute(f"UPDATE \"{ctx.guild.id}\" SET ReportModRole = ? WHERE UserID = 123", mod_role.id)
                mod_role_option = mod_role.mention if mod_role else 'N/A'
            if required_role:
                db.execute(f"UPDATE \"{ctx.guild.id}\" SET ModlogRequired = ? WHERE UserID = 123", required_role.id)
                required_role_option = required_role.mention if required_role else 'N/A'
                required_role_message = f"users with {required_role.mention}" if required_role else "**everyone**"
            db.execute(f"UPDATE \"{ctx.guild.id}\" SET ModlogToggle = 1 WHERE UserID = 123")
            embed=Embed(color=Color.green(), title="Successfully Enabled!", description=f"{ctx.author.mention} enabled the following options:\n- Channel Logs: {channel_option}\n- Mod-Logs: {mod_role_option}\n- Required Role: {required_role_option}\n\nThe commands `/report` and `/areport` will now be enabled to {required_role_message}.")
            await ctx.send(embed=embed)
        else:
            embed=Embed(color=Color.red(), title="Permission Denied!", description=f"{ctx.author.mention}, you do not have the permission to commit this command in this server. Make sure you have the **MANAGE CHANNELS** permission or higher.")
            await ctx.send(embed=embed)

    @enable.sub_command(description="Removes channel to the ignored list.", option=[
        Option("channel", "The channel to remove.", OptionType.channel, required=True)
    ])
    async def channel(self, ctx: ApplicationCommandInteraction, channel: TextChannel):
        await ctx.response.defer()
        if ctx.author.guild_permissions.manage_channels:
            if isinstance(channel, TextChannel):
                _disabled_channels = db.field(f"SELECT ChannelDisable FROM \"{ctx.guild.id}\" WHERE UserID = 123")
                disabled_channels = ast.literal_eval(_disabled_channels)
                if channel.id in disabled_channels:
                    disabled_channels.remove(channel.id)
                    db.execute(f"UPDATE \"{ctx.guild.id}\" SET ChannelDisable = ? WHERE UserID = 123", f"{_disabled_channels}")
                    embed=Embed(color=Color.green(), title="Successfully Enabled!", description=f"{ctx.author.mention} enabled messages in {channel.mention}. Messages sent will now be tracked here.")
                    embed.set_footer(text="To disable a channel, type /disable channel.", icon_url=ctx.author.avatar.url)
                else:
                    embed=Embed(color=Color.red(), title="Already Enabled!", description=f"{ctx.author.mention}, the channel you provided is not in the disabled list. Use `/disable channel` to disable the channel.")
                    embed.set_footer(text="To disable a channel, type /disable channel.", icon_url=ctx.author.avatar.url)
            else:
                embed=Embed(color=Color.red(), title="Invalid Channel!", description=f"{ctx.author.mention}, the channel you provided is not a text channel. Please include only text channels.")
                embed.set_footer(text="Please make sure that the channel you select is an instance of TEXT CHANNEL.", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            embed=Embed(color=Color.red(), title="Permission Denied!", description=f"{ctx.author.mention}, you do not have the permission to commit this command in this server. Make sure you have the **MANAGE CHANNELS** permission or higher.")
            await ctx.send(embed=embed)

    @enable.sub_command(description="Removes role to the ignored list.", option=[
        Option("role", "The role to remove.", OptionType.channel, required=True)
    ])
    async def role(self, ctx: ApplicationCommandInteraction, role: Role):
        await ctx.response.defer()
        if ctx.author.guild_permissions.manage_roles:
            _disabled_roles = db.field(f"SELECT RoleDisable FROM \"{ctx.guild.id}\" WHERE UserID = 123")
            disabled_roles = ast.literal_eval(_disabled_roles)
            if role.id in disabled_roles:
                _disabled_roles.remove(role.id)
                db.execute(f"UPDATE \"{ctx.guild.id}\" SET RoleDisable = ? WHERE UserID = 123", f"{_disabled_roles}")
                embed=Embed(color=Color.green(), title="Successfully Enabled!", description=f"{ctx.author.mention} enabled roles in {role.mention}. Users' messages with {role.mention} roles sent will not be tracked here.")
                embed.set_footer(text="To enable disabled role, type /enable role.", icon_url=ctx.author.avatar.url)
            else:
                embed=Embed(color=Color.red(), title="Already Enabled!", description=f"{ctx.author.mention}, the role you provided is not in the disabled list. Use `/disable role` to disable the role.")
                embed.set_footer(text="To enable disabled role, type /enable role.", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            embed=Embed(color=Color.red(), title="Permission Denied!", description=f"{ctx.author.mention}, you do not have the permission to commit this command in this server. Make sure you have the **MANAGE CHANNELS** permission or higher.")
            await ctx.send(embed=embed)

    @enable.sub_command(description="Enables user to be tracked.", option=[
        Option("user", "The user to allow.", OptionType.channel, required=True)
    ])
    async def user(self, ctx: ApplicationCommandInteraction, user: Member):
        await ctx.response.defer()
        if ctx.author.guild_permissions.administrator:
            toggle = db.field(f"SELECT Toggle FROM \"{ctx.guild.id}\" WHERE UserID = ?", ctx.author.id)
            if toggle == 0:
                db.execute(f"UPDATE \"{ctx.guild.id}\" SET Toggle = 1 WHERE UserID = 123", ctx.author.id)
                embed=Embed(color=Color.green(), title="Successfully Enabled!", description=f"{ctx.author.mention} enabled {user.mention} to be tracked with messages.")
                embed.set_footer(text="To disable user's message tracking, type /disable user.", icon_url=ctx.author.avatar.url)
            else:
                embed=Embed(color=Color.red(), title="Already Enabled!", description=f"{ctx.author.mention}, the user you provided is already enabled to be tracked with messages. Use `/disable user` to disable the user.")
                embed.set_footer(text="To disable user's message tracking, type /disable user.", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            embed=Embed(color=Color.red(), title="Permission Denied!", description=f"{ctx.author.mention}, you do not have the permission to commit this command in this server. Make sure you have the **MANAGE CHANNELS** permission or higher.")
            await ctx.send(embed=embed)

    # DISABLE #
    @commands.slash_command()
    async def disable(self, ctx: ApplicationCommandInteraction):
        pass

    @disable.sub_command(description="Disable logs for message inputs.")
    async def logs(self, ctx: ApplicationCommandInteraction):
        await ctx.response.defer()
        if ctx.author.guild_permissions.manage_channels:
            channel_logs = db.field(f"SELECT LoggingChannel FROM \"{ctx.guild.id}\" WHERE UserID = 123")
            if channel_logs > 0:
                db.execute(f"UPDATE \"{ctx.guild.id}\" SET LoggingChannel = 0 WHERE UserID = 123")
                embed=Embed(color=Color.green(), title="Successfully Disabled!", description=f"{ctx.author.mention} disabled messages edited/deleted logs. Edited/deleted messages will be suppressed.")
                embed.set_footer(text="To enable logs, type /enable logs.", icon_url=ctx.author.avatar.url)
            else:
                embed=Embed(color=Color.red(), title="Already Disabled!", description=f"{ctx.guild.me.mention} has already been disabled in this server. Use `/help` for more information and guides.")
                embed.set_footer(text="To enable logs, type /enable logs.", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            embed=Embed(color=Color.red(), title="Permission Denied!", description=f"{ctx.author.mention}, you do not have the permission to commit this command in this server. Make sure you have the **MANAGE CHANNELS** permission or higher.")
            await ctx.send(embed=embed)

    @disable.sub_command(description="Disable mod-logs for user reports.")
    async def modlogs(self, ctx: ApplicationCommandInteraction):
        await ctx.response.defer()
        if ctx.author.guild_permissions.manage_channels:
            channel_logs = db.field(f"SELECT LoggingChannel FROM \"{ctx.guild.id}\" WHERE UserID = 123")
            if channel_logs > 0:
                db.execute(f"UPDATE \"{ctx.guild.id}\" SET ModlogToggle = 0, ModlogChannel = 0, ReportModRole = 0, ModlogRequired = 0 WHERE UserID = 123")
                embed=Embed(color=Color.green(), title="Successfully Disabled!", description=f"{ctx.author.mention} disabled mod-logs in this server. The command `/report` and `/areport` will be disabled.")
                embed.set_footer(text="To enable mod-logs, type /enable modlogs.", icon_url=ctx.author.avatar.url)
                await ctx.send(embed=embed)
            else:
                embed=Embed(color=Color.red(), title="Already Disabled!", description=f"{ctx.guild.me.mention} has already been disabled in this server. Use `/help` for more information and guides.")
                embed.set_footer(text="To enable mod-logs, type /enable modlogs.", icon_url=ctx.author.avatar.url)
                await ctx.send(embed=embed)
        else:
            embed=Embed(color=Color.red(), title="Permission Denied!", description=f"{ctx.author.mention}, you do not have the permission to commit this command in this server. Make sure you have the **MANAGE CHANNELS** permission or higher.")
            await ctx.send(embed=embed)

    @disable.sub_command(description="Ignores channel to track message.", option=[
        Option("channel", "The channel to ignore.", OptionType.channel, required=True)
    ])
    async def channel(self, ctx: ApplicationCommandInteraction, channel: TextChannel):
        await ctx.response.defer()
        if ctx.author.guild_permissions.manage_channels:
            if isinstance(channel, TextChannel):
                _disabled_channels = db.field(f"SELECT ChannelDisable FROM \"{ctx.guild.id}\" WHERE UserID = 123")
                disabled_channels = ast.literal_eval(_disabled_channels)
                if channel.id not in disabled_channels:
                    _disabled_channels.append(channel.id)
                    db.execute(f"UPDATE \"{ctx.guild.id}\" SET ChannelDisable = ? WHERE UserID = 123", f"{_disabled_channels}")
                    embed=Embed(color=Color.green(), title="Successfully Disabled!", description=f"{ctx.author.mention} disabled messages in {channel.mention}. Messages sent will not be tracked here.")
                    embed.set_footer(text="To enable disabled channel, type /enable channel.", icon_url=ctx.author.avatar.url)
                else:
                    embed=Embed(color=Color.red(), title="Already Disabled!", description=f"{ctx.author.mention}, the channel you provided is already in the disabled list. Use `/enable channel` to enable the channel.")
                    embed.set_footer(text="To enable disabled channel, type /enable channel.", icon_url=ctx.author.avatar.url)
            else:
                embed=Embed(color=Color.red(), title="Invalid Channel!", description=f"{ctx.author.mention}, the channel you provided is not a text channel. Please include only text channels.")
                embed.set_footer(text="Please make sure that the channel you select is an instance of TEXT CHANNEL.", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            embed=Embed(color=Color.red(), title="Permission Denied!", description=f"{ctx.author.mention}, you do not have the permission to commit this command in this server. Make sure you have the **MANAGE CHANNELS** permission or higher.")
            await ctx.send(embed=embed)
    
    @disable.sub_command(description="Ignores users with certain role to track message.", option=[
        Option("role", "The role to ignore.", OptionType.channel, required=True)
    ])
    async def role(self, ctx: ApplicationCommandInteraction, role: Role):
        await ctx.response.defer()
        if ctx.author.guild_permissions.manage_roles:
            _disabled_roles = db.field(f"SELECT RoleDisable FROM \"{ctx.guild.id}\" WHERE UserID = 123")
            disabled_roles = ast.literal_eval(_disabled_roles)
            if role.id not in disabled_roles:
                _disabled_roles.append(role.id)
                db.execute(f"UPDATE \"{ctx.guild.id}\" SET RoleDisable = ? WHERE UserID = 123", f"{_disabled_roles}")
                embed=Embed(color=Color.green(), title="Successfully Disabled!", description=f"{ctx.author.mention} disabled roles in {role.mention}. Users' messages with {role.mention} roles sent will not be tracked here.")
                embed.set_footer(text="To enable disabled role, type /enable role.", icon_url=ctx.author.avatar.url)
            else:
                embed=Embed(color=Color.red(), title="Already Disabled!", description=f"{ctx.author.mention}, the role you provided is already in the disabled list. Use `/enable role` to enable the role.")
                embed.set_footer(text="To enable disabled role, type /enable role.", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            embed=Embed(color=Color.red(), title="Permission Denied!", description=f"{ctx.author.mention}, you do not have the permission to commit this command in this server. Make sure you have the **MANAGE CHANNELS** permission or higher.")
            await ctx.send(embed=embed)

    @disable.sub_command(description="Disables user to be tracked.", option=[
        Option("user", "The user to ignore.", OptionType.channel, required=True)
    ])
    async def user(self, ctx: ApplicationCommandInteraction, user: Member):
        await ctx.response.defer()
        if ctx.author.guild_permissions.administrator:
            toggle = db.field(f"SELECT Toggle FROM \"{ctx.guild.id}\" WHERE UserID = ?", ctx.author.id)
            if toggle == 1:
                db.execute(f"UPDATE \"{ctx.guild.id}\" SET Toggle = 0 WHERE UserID = 123", ctx.author.id)
                embed=Embed(color=Color.green(), title="Successfully Disabled!", description=f"{ctx.author.mention} disabled {user.mention} to be tracked with messages.")
                embed.set_footer(text="To enable user's message tracking, type /enable user.", icon_url=ctx.author.avatar.url)
            else:
                embed=Embed(color=Color.red(), title="Already Disabled!", description=f"{ctx.author.mention}, the user you provided is already disabled to be tracked with messages. Use `/enable user` to enable the user.")
                embed.set_footer(text="To enable user's message tracking, type /enable user.", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            embed=Embed(color=Color.red(), title="Permission Denied!", description=f"{ctx.author.mention}, you do not have the permission to commit this command in this server. Make sure you have the **MANAGE CHANNELS** permission or higher.")
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Settings(client))