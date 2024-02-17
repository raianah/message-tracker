import ast, datetime, time
from disnake import Embed, Color, ApplicationCommandInteraction, TextChannel, Option, OptionType, Member
from disnake.ext import commands
from message_tracker.db import db

from properties.pagination import MessageListPages

def convert_duration(time_length):
	new_list = []
	length = datetime.datetime.fromtimestamp(time_length)
	if int(time_length) >= 3600:
		h, m, s = length.strftime("%Hh").lstrip("0"), length.strftime("%Mm").lstrip("0"), length.strftime("%Ss").lstrip("0")
		for i in [h, m, s]:
			if i in ["0h", "0m", "0s", "h", "m", "s"]:
				pass
			else:
				new_list.append(i)
	else:
		m, s = length.strftime("%Mm").lstrip("0"), length.strftime("%Ss").lstrip("0")
		for i in [m, s]:
			if i in ["0m", "0s", "m", "s"]:
				pass
			else:
				new_list.append(i)
	timestamp = " ".join([item for item in new_list])
	return timestamp

class Utility(commands.Cog):
	def __init__(self, client):
		self.client = client
		global start_time
		start_time = time.time()


	@commands.Cog.listener()
	async def on_ready(self):
		print("Utility is loaded.")

	@commands.slash_command(name="view-messages", description="Show the list of messages sent by the user.", option=[
		Option("channel", "The channel to retrieve messages.", OptionType.channel, required=False),
		#Option("message_id", "The message ID to retrieve.", OptionType.integer, required=False)
	])
	async def view_messages(self, ctx: ApplicationCommandInteraction, channel: TextChannel = None): #message_id: int = None):
		await ctx.response.defer()
		new_list = []
		channel = channel or ctx.channel
		_messages = db.field(f"SELECT MessageStorage FROM \"{channel.guild.id}\" WHERE UserID = ?", ctx.author.id)
		messages = ast.literal_eval(_messages)
		for message in messages:
			if isinstance(channel, TextChannel):
				if channel.id in message:
					all_messages = [message[channel.id]]
					for msg in all_messages:
						keys = list(msg.keys())
						if len(keys) > 1:
							for k in keys:
								_date = datetime.datetime.fromtimestamp(msg[k][1])
								date = _date.strftime("%Y-%m-%d | %H:%M:%S")
								_msg = msg[k][2].replace(msg[k][2][150:], "...") if len(msg[k][2]) > 60 else msg[k][2]
								new_list.append(f"**[{date}]** - <@{msg[k][0]}>: {_msg}")
						else:
							_date = datetime.datetime.fromtimestamp(msg[keys[0]][1])
							date = _date.strftime("%Y-%m-%d | %H:%M:%S")
							_msg = msg[keys[0]][2].replace(msg[keys[0]][2][150:], "...") if len(msg[keys[0]][2]) > 60 else msg[keys[0]][2]
							new_list.append(f"**[{date}]** - <@{msg[keys[0]][0]}>: {_msg}")
			else:
				embed=Embed(color=Color.red(), title="Invalid Channel!", description=f"{ctx.author.mention}, the channel you provided is not a text channel. Please include only text channels.")
				embed.set_footer(text="Please make sure that the channel you select is an instance of TEXT CHANNEL.", icon_url=ctx.author.avatar.url)
				await ctx.send(embed=embed)
		if len(new_list) > 0:
			paginator = MessageListPages(new_list[:200], ctx, channel)
			await paginator.start()
		else:
			embed = Embed(color=Color.red(), title="Empty Channel?", description=f"No saved messages were found in {channel.mention}. Try using `/raw-messages` to retrieve messages directly from discord.")
			await ctx.send(embed=embed)

	@commands.slash_command(name="raw-messages", description="Show the list of raw messages sent by the user.", option=[
		Option("channel", "The channel to retrieve messages.", OptionType.channel, required=False)
	])
	async def raw_messages(self, ctx: ApplicationCommandInteraction, channel: TextChannel = None):
		await ctx.response.defer()
		new_list, _message_list = [], []
		channel = channel or ctx.channel
		if channel.permissions_for(ctx.guild.me).read_message_history:
			if isinstance(channel, TextChannel):
				async for message in channel.history(limit=200):
					if message.author != self.client.user:
						_message_list.append(message)
				for message in _message_list:
					_date = datetime.datetime.fromtimestamp(int(message.created_at.timestamp()))
					date = _date.strftime("%Y-%m-%d | %H:%M:%S")
					_msg = message.content.replace(message.content[150:], "...") if len(message.content) > 150 else message.content
					new_list.append(f"**[{date}]** - {message.author.mention}: {_msg}")
			if len(new_list) > 0:
				paginator = MessageListPages(new_list[:200], ctx, channel)
				await paginator.start()
			else:
				embed = Embed(color=Color.red(), title="Empty Channel?", description=f"No raw messages were found in {channel.mention}. Try using `/view-messages` to retrieve messages from our system.")
				await ctx.send(embed=embed)
		else:
			embed = Embed(color=Color.red(), title="No Permission!", description=f"The bot does not have `Read Message History` permission in this server. Enable this permission first then try again.")
			embed.set_footer(text="Please make sure that you have the required permission to use this command.", icon_url=ctx.author.avatar.url)
			await ctx.send(embed=embed)

	@commands.slash_command(description="Report to the moderators!", option=[
		Option("message", "The message to report.", OptionType.string, required=True)
	])
	async def report(self, ctx: ApplicationCommandInteraction, message: str):
		await ctx.response.defer()
		toggle = db.field(f"SELECT ModlogToggle FROM \"{ctx.guild.id}\" WHERE UserID = 123")
		if toggle == 1:
			_report_channel, _mod_role, _required_role = db.record(f"SELECT ModlogChannel, ReportModRole, ModlogRequired FROM \"{ctx.guild.id}\" WHERE UserID = 123")
			report_channel, mod_role, required_role = ctx.guild.get_channel(_report_channel), ctx.guild.get_role(_mod_role), ctx.guild.get_role(_required_role)
			if required_role is not None:
				if required_role in ctx.author.roles:
					if report_channel is not None:
						if mod_role is not None:
							embed = Embed(color=Color.blurple(), title="New Report!", description=f"{ctx.author.mention} has created a report.\n\n**Message:** {message}")
							embed.set_footer(text="Please take action immediately.", icon_url=ctx.author.avatar.url)
							await report_channel.send(content=mod_role.mention, embed=embed)
						else:
							embed = Embed(color=Color.blurple(), title="New Report!", description=f"{ctx.author.mention} has created a report.\n\n**Message:** {message}")
							embed.set_footer(text="Please take action immediately.", icon_url=ctx.author.avatar.url)
							await report_channel.send(embed=embed)
					else:
						if mod_role is not None:
							for member in ctx.guild.members:
								if mod_role in member.roles:
									await member.send(f"{ctx.author.mention} has created a report.\n\n**Message:** {message}")
						else:
							for member in ctx.guild.members:
								if member.guild_permissions.administrator:
									await member.send(f"{ctx.author.mention} has created a report.\n\n**Message:** {message}")
					await ctx.send("Report sent to the moderators!")
				else:
					embed = Embed(color=Color.red(), title="No Permission!", description=f"{ctx.author.mention}, you are not allowed to use this command. Only members with {required_role.mention} role can use this command.")
					embed.set_footer(text="Please make sure that you have the required role to use this command.", icon_url=ctx.author.avatar.url)
					await ctx.send(embed=embed)
			else:
				if mod_role is not None:
					embed = Embed(color=Color.blurple(), title="New Report!", description=f"{ctx.author.mention} has created a report.\n\n**Message:** {message}")
					embed.set_footer(text="Please take action immediately.", icon_url=ctx.author.avatar.url)
					await report_channel.send(content=mod_role.mention, embed=embed)
				else:
					embed = Embed(color=Color.blurple(), title="New Report!", description=f"{ctx.author.mention} has created a report.\n\n**Message:** {message}")
					embed.set_footer(text="Please take action immediately.", icon_url=ctx.author.avatar.url)
					await report_channel.send(content=mod_role.mention, embed=embed)
		else:
			embed = Embed(color=Color.red(), title="Modlog Disabled!", description=f"{ctx.author.mention}, this command is currently disabled. Please ask your local server moderators/administrators to enable this command.")
			embed.set_footer(text="Please make sure that this command is enabled before using this command.", icon_url=ctx.author.avatar.url)
			await ctx.send(embed=embed)

	@commands.slash_command(description="Report to the moderators anonymously!", option=[
		Option("message", "The message to report.", OptionType.string, required=True)
	])
	async def areport(self, ctx: ApplicationCommandInteraction, message: str):
		await ctx.response.defer(ephemeral=True)
		toggle = db.field(f"SELECT ModlogToggle FROM \"{ctx.guild.id}\" WHERE UserID = 123")
		if toggle == 1:
			_report_channel, _mod_role, _required_role = db.record(f"SELECT ModlogChannel, ReportModRole, ModlogRequired FROM \"{ctx.guild.id}\" WHERE UserID = 123")
			report_channel, mod_role, required_role = ctx.guild.get_channel(_report_channel), ctx.guild.get_role(_mod_role), ctx.guild.get_role(_required_role)
			if required_role is not None:
				if required_role in ctx.author.roles:
					if report_channel is not None:
						if mod_role is not None:
							embed = Embed(color=Color.blurple(), title="New Report!", description=f"A member has created a report anonymously.\n\n**Message:** {message}")
							embed.set_footer(text="Please take action immediately.", icon_url=ctx.author.avatar.url)
							await report_channel.send(content=mod_role.mention, embed=embed)
						else:
							embed = Embed(color=Color.blurple(), title="New Report!", description=f"A member has created a report anonymously.\n\n**Message:** {message}")
							embed.set_footer(text="Please take action immediately.", icon_url=ctx.author.avatar.url)
							await report_channel.send(embed=embed)
					else:
						if mod_role is not None:
							for member in ctx.guild.members:
								if mod_role in member.roles:
									await member.send(f"A member has created a report anonymously.\n\n**Message:** {message}")
						else:
							for member in ctx.guild.members:
								if member.guild_permissions.administrator:
									await member.send(f"A member has created a report anonymously.\n\n**Message:** {message}")
					await ctx.send("Report sent to the moderators!")
				else:
					embed = Embed(color=Color.red(), title="No Permission!", description=f"{ctx.author.mention}, you are not allowed to use this command. Only members with {required_role.mention} role can use this command.")
					embed.set_footer(text="Please make sure that you have the required role to use this command.", icon_url=ctx.author.avatar.url)
					await ctx.send(embed=embed)
			else:
				if mod_role is not None:
					embed = Embed(color=Color.blurple(), title="New Report!", description=f"A member has created a report anonymously.\n\n**Message:** {message}")
					embed.set_footer(text="Please take action immediately.", icon_url=ctx.author.avatar.url)
					await report_channel.send(content=mod_role.mention, embed=embed)
				else:
					embed = Embed(color=Color.blurple(), title="New Report!", description=f"A member has created a report anonymously.\n\n**Message:** {message}")
					embed.set_footer(text="Please take action immediately.", icon_url=ctx.author.avatar.url)
					await report_channel.send(embed=embed)
		else:
			embed = Embed(color=Color.red(), title="Modlog Disabled!", description=f"{ctx.author.mention}, this command is currently disabled. Please ask your local server moderators/administrators to enable this command.")
			embed.set_footer(text="Please make sure that this command is enabled before using this command.", icon_url=ctx.author.avatar.url)
			await ctx.send(embed=embed)

	@commands.slash_command(description="Retrieve the last message sent.")
	async def snipe(self, ctx: ApplicationCommandInteraction):
		await ctx.response.defer()
		if ctx.channel.permissions_for(ctx.guild.me).read_message_history:
			async for message in ctx.channel.history(limit=200):
				if message.author != self.client.user:
					_date = datetime.datetime.fromtimestamp(int(message.created_at.timestamp()))
					date = _date.strftime("%Y-%m-%d | %H:%M:%S")
					_msg = message.content.replace(message.content[2048:], "...") if len(message.content) > 2048 else message.content
					embed = Embed(color=Color.blurple(), title="Sniped Message", description=f"- **Date:** {date}\n- **Message Author:** {message.author.mention}\n- **Message Content:** {_msg}")
					embed.set_footer(text="Bullseye!", icon_url=ctx.author.avatar.url).set_thumbnail(url=message.author.avatar.url)
					return await ctx.send(embed=embed)
		else:
			embed = Embed(color=Color.red(), title="No Permission!", description=f"The bot does not have `Read Message History` permission in this server. Enable this permission first then try again.")
			embed.set_footer(text="Please make sure that you have the required permission to use this command.", icon_url=ctx.author.avatar.url)
			await ctx.send(embed=embed)

	@commands.slash_command(description="Retrieve the last message sent in the specified channel.")
	async def invite(self, ctx: ApplicationCommandInteraction):
		await ctx.response.defer()
		embed = Embed(color=Color.blurple(), title="Invite Message Tracker to your server!", description="https://discord.com/api/oauth2/authorize?client_id=954930077815144499&permissions=275146468368&scope=bot")
		embed.set_footer(text="Thank you for choosing Message Tracker!", icon_url=ctx.author.avatar.url)
		await ctx.send(embed=embed)

	@commands.slash_command(description="Pong!")
	async def ping(self, ctx: ApplicationCommandInteraction):
		await ctx.response.defer()
		embed = Embed(color=Color.blurple(), title="Pong!", description=f"Latency: {round(self.client.latency * 1000)}ms")
		embed.set_footer(text="Pong!", icon_url=ctx.author.avatar.url)
		await ctx.send(embed=embed)

	@commands.slash_command(description="GitHub link.")
	async def github(self, ctx: ApplicationCommandInteraction):
		await ctx.response.defer()
		embed = Embed(color=Color.blurple(), title="GitHub Repository", description="https://github.com/raianah/message-tracker")
		await ctx.send(embed=embed)

	@commands.slash_command(description="Show the bot's uptime.")
	async def uptime(self, ctx: ApplicationCommandInteraction):
		await ctx.response.defer()
		timestamp = convert_duration(int(time.time()) - start_time)
		embed = Embed(color=Color.blurple(), title="Uptime", description=f"Message Tracker has been online for {timestamp}.")
		embed.set_footer(text="Contribute here: https://github.com/raianah/message-tracker", icon_url=ctx.author.avatar.url)
		await ctx.send(embed=embed)

	@commands.slash_command(description="Shows user avatar.", option=[
		Option("user", "The user to retrieve avatar.", OptionType.user, required=False)
	])
	async def avatar(self, ctx: ApplicationCommandInteraction, user: Member = None):
		await ctx.response.defer()
		user = user or ctx.author
		if user.avatar != user.display_avatar:
			embed0=Embed(color=Color.blurple(), title=f"{user.name}'s Avatar", url=user.avatar.url).set_image(url=user.avatar.url)
			embed1=Embed(url=user.avatar.url).set_image(url=user.display_avatar.url)
			await ctx.send(embeds=[embed0, embed1])
		else:
			embed=Embed(color=Color.blurple(), title=f"{user.name}'s Avatar").set_image(url=user.avatar.url)
			await ctx.send(embed=embed)

def setup(client):
	client.add_cog(Utility(client))