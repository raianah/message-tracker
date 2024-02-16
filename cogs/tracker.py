import ast, time
from disnake import Guild, Message, Client, Embed, Color
from disnake.ext import commands
from message_tracker.db import db

"""
	DATABASE STRUCTURE:
	Toggle = UserID toggle for message tracking disable
	LoggingChannel = Selected channel to log messages
	ModlogChannel = Selected channel to log user reports
	ChannelDisable = List of channel IDs to disable message tracking
	RoleDisable = List of role IDs to disable message tracking
	ReportModRole = List of role IDs to notify with user reports
	ModlogRequired = List of roles required to report users
	ChannelTypeDisable = List of channel types to disable message tracking (text, voice, news, store, stage, thread)
	MessageStorage = List of messages sent by the user

	MESSAGE STORAGE STRUCTURE:
	{channel_id:
		{message_id: 
			[author_id, timestamp, message.content, [attachments.url for attachment in message.attachments]]
		},
		...
	}
"""

class Tracker(commands.Cog):
	def __init__(self, client: Client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		print("Tracker is loaded.")
		
	@commands.Cog.listener()
	async def on_guild_join(self, guild: Guild):
		db.execute(f"""CREATE TABLE IF NOT EXISTS \"{guild.id}\" (Toggle INTEGER DEFAULT 0, UserID INTEGER DEFAULT 0, LoggingChannel INTEGER DEFAULT 0, ModlogChannel INTEGER DEFAULT 0, ModlogToggle INTEGER DEFAULT 0, ChannelDisable TEXT DEFAULT \"[]\", RoleDisable TEXT DEFAULT \"[]\", ChannelTypeDisable TEXT DEFAULT \"[]\", ModlogRequired TEXT DEFAULT \"[]\", MessageStorage TEXT DEFAULT \"[]\", ReportModRole TEXT DEFAULT \"[]\", PRIMARY KEY(UserID));""")
		try:
			await guild.owner.send("Thank you for adding me to your server! Here are some guides you need to know to use this bot.\n- To get started, use `/begin` to enable message tracker in your server. To disable message tracker, use `/stop`.\n- To see the list of commands, use `/help`.\n- Use `/areport` to report to admins anonymously.")
		except:
			pass

	@commands.Cog.listener()
	async def on_guild_remove(self, guild: Guild):
		db.execute(f"DROP TABLE IF EXISTS \"{guild.id}\"")

	@commands.Cog.listener()
	async def on_message(self, message: Message):
		db.execute(f"""CREATE TABLE IF NOT EXISTS \"{message.guild.id}\" (Toggle INTEGER DEFAULT 0, UserID INTEGER DEFAULT 0, LoggingChannel INTEGER DEFAULT 0, ModlogChannel INTEGER DEFAULT 0, ModlogToggle INTEGER DEFAULT 0, ChannelDisable TEXT DEFAULT \"[]\", RoleDisable TEXT DEFAULT \"[]\", ChannelTypeDisable TEXT DEFAULT \"[]\", MessageStorage TEXT DEFAULT \"[]\", ReportModRole TEXT DEFAULT \"[]\", PRIMARY KEY(UserID));""")
		if message.author.bot or message.guild is None:
			return
		###
		_toggle_check = db.record(f"SELECT Toggle FROM \"{message.guild.id}\"")
		if _toggle_check is None:
			db.execute(f"INSERT INTO \"{message.guild.id}\" (UserID) VALUES (?)", 123) # UNIVERSAL VALUE
		###
		member_check = db.record(f"SELECT * FROM \"{message.guild.id}\" WHERE UserID = ?", message.author.id)
		if member_check is None:
			db.execute(f"INSERT INTO \"{message.guild.id}\" (UserID) VALUES (?)", message.author.id)
		###
		toggle_check = db.field(f"SELECT Toggle FROM \"{message.guild.id}\" WHERE UserID = ?", message.author.id)
		if toggle_check == 1:
			_disabled_channels, _disabled_channel_type = db.record(f"SELECT ChannelDisable, ChannelTypeDisable FROM \"{message.guild.id}\" WHERE UserID = ?", message.author.id)
			disabled_channels, disabled_channel_type = ast.literal_eval(_disabled_channels), ast.literal_eval(_disabled_channel_type)
			if message.channel.id not in disabled_channels and str(message.channel.type) not in disabled_channel_type:
				_message_list = db.field(f"SELECT MessageStorage FROM \"{message.guild.id}\" WHERE UserID = ?", message.author.id)
				message_list = ast.literal_eval(_message_list)
				for item in message_list:
					if message.channel.id in item:
						item[message.channel.id][message.id] = [message.author.id, int(message.created_at.timestamp()), message.content, [attachment.url for attachment in message.attachments if attachment.url != ""]]
						db.execute(f"UPDATE \"{message.guild.id}\" SET MessageStorage = ? WHERE UserID = ?", f"{message_list}", message.author.id)
						return
				message_storage = {message.channel.id: {message.id: [message.author.id, int(message.created_at.timestamp()), message.content, [attachment.url for attachment in message.attachments if attachment.url != ""]]}}
				message_list.append(message_storage)
				db.execute(f"UPDATE \"{message.guild.id}\" SET MessageStorage = ? WHERE UserID = ?", f"{message_list}", message.author.id)
				return

	@commands.Cog.listener()
	async def on_message_edit(self, before: Message, after: Message):
		channel_logs = db.field(f"SELECT LoggingChannel FROM \"{before.guild.id}\" WHERE UserID = 123")
		if channel_logs > 0:
			channel = await self.client.fetch_channel(channel_logs)
			if channel.permissions_for(before.guild.me).send_messages:
				if before.content != after.content:
					embed = Embed(color=Color.blurple(), title="Message Edited", description=f"{before.author.mention} updated their [message]({before.jump_url}) in {before.channel.mention} ({before.channel.name}) <t:{int(time.time())}:R>.\n\n**Original Message**\n{before.content}\n\n**Edited Message**\n{after.content}\n**After:** {after.content}")
					await channel.send(embed=embed)
			else:
				embed = Embed(color=0xFF0000, title="Missing Permissions", description=f"{before.guild.me.mention} does not have the required permissions to send messages in {channel.mention}. Please re-configure the text channel and try again; or change the text channel by using `/set message-logs`.")
				await before.owner.send(embed=embed)
		toggle_check = db.field(f"SELECT Toggle FROM \"{before.guild.id}\" WHERE UserID = ?", before.author.id)
		if toggle_check == 1:
			_message_list = db.field(f"SELECT MessageStorage FROM \"{before.guild.id}\" WHERE UserID = ?", before.author.id)
			message_list = ast.literal_eval(_message_list)
			for item in message_list:
				if before.channel.id in item and before.content != after.content:
					message_list[before.channel.id][before.id][2] = after.content
					db.execute(f"UPDATE \"{before.guild.id}\" SET MessageStorage = ? WHERE UserID = ?", f"{message_list}", before.author.id)

	@commands.Cog.listener()
	async def on_message_delete(self, message: Message):
		channel_logs = db.field(f"SELECT LoggingChannel FROM \"{message.guild.id}\" WHERE UserID = 123")
		if channel_logs > 0:
			channel = await self.client.fetch_channel(channel_logs)
			if channel.permissions_for(message.guild.me).send_messages:
				embed = Embed(color=Color.red(), title="Message Deleted", description=f"{message.author.mention} deleted their message in {message.channel.mention} ({message.channel.name}).\n\n**Message Content**\n{message.content}")
				await channel.send(embed=embed)
			else:
				embed = Embed(color=0xFF0000, title="Missing Permissions", description=f"{message.guild.me.mention} does not have the required permissions to send messages in {channel.mention}. Please re-configure the text channel and try again; or change the text channel by using `/set message-logs`.")
				await message.author.send(embed=embed)
		toggle_check = db.field(f"SELECT Toggle FROM \"{message.guild.id}\" WHERE UserID = ?", 123) # UNIVERSAL VALUE
		if toggle_check == 1:
			_message_list = db.field(f"SELECT MessageStorage FROM \"{message.guild.id}\" WHERE UserID = ?", message.author.id)
			message_list = ast.literal_eval(_message_list)
			for item in message_list:
				if message.id in item[message.channel.id]:
					item[message.channel.id].pop(message.id)
					db.execute(f"UPDATE \"{message.guild.id}\" SET MessageStorage = ? WHERE UserID = ?", f"{message_list}", message.author.id)

def setup(client):
	client.add_cog(Tracker(client))