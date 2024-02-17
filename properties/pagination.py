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

import asyncio
from disnake import Embed, ApplicationCommandInteraction, Interaction, ButtonStyle, Message, Color
from disnake.ui import View, Button, button
from disnake.utils import maybe_coroutine
from disnake.ext.menus import PageSource, ListPageSource
from typing import Dict, Any, Optional

# PAGINATION
class ViewPages(View): # GLOBAL USE
	def __init__(self, source: PageSource, *, ctx: ApplicationCommandInteraction, check_embeds: bool = True, compact: bool = False):
		super().__init__(timeout=None)
		self.source: PageSource = source
		self.check_embeds: bool = check_embeds
		self.ctx: ApplicationCommandInteraction = ctx
		self.message: Optional[Message] = None
		self.current_page: int = 0
		self.compact: bool = compact
		self.input_lock = asyncio.Lock()
		self.clear_items()
		self.fill_items()

	def fill_items(self) -> None:

		if self.source.is_paginating():
			max_pages = self.source.get_max_pages()
			use_last_and_first = max_pages is not None and max_pages >= 2
			if use_last_and_first:
				self.add_item(self.go_to_first_page)
			self.add_item(self.go_to_previous_page)
			if not self.compact:
				self.add_item(self.go_to_current_page)
			self.add_item(self.go_to_next_page)
			if use_last_and_first:
				self.add_item(self.go_to_last_page)

	async def _get_kwargs_from_page(self, page: int) -> Dict[str, Any]:
		value = await maybe_coroutine(self.source.format_page, self, page)
		if isinstance(value, dict):
			return value
		elif isinstance(value, str):
			return {"content": value, "embed": None}
		elif isinstance(value, Embed):
			return {"embed": value, "content": None}
		else:
			return {}

	async def show_page(self, interaction: Interaction, page_number: int) -> None:
		page = await self.source.get_page(page_number)
		self.current_page = page_number
		kwargs = await self._get_kwargs_from_page(page)
		self._update_labels(page_number)
		if kwargs:
			if interaction.response.is_done():
				if self.message:
					await self.message.edit(**kwargs, view=self)
			else:
				await interaction.response.edit_message(**kwargs, view=self)

	def _update_labels(self, page_number: int) -> None:
		self.go_to_first_page.disabled = page_number == 0
		max_pages = self.source.get_max_pages()
		if self.compact:
			self.go_to_last_page.disabled = (
				max_pages is None or (page_number + 1) >= max_pages
			)
			self.go_to_next_page.disabled = (
				max_pages is not None and (page_number + 1) >= max_pages
			)
			self.go_to_previous_page.disabled = page_number == 0
			return

		self.go_to_current_page.label = f"{str(page_number + 1)} / {max_pages}"
		self.go_to_next_page.disabled = False
		self.go_to_previous_page.disabled = False
		self.go_to_first_page.disabled = False

		if max_pages is not None:
			self.go_to_last_page.disabled = (page_number + 1) >= max_pages
			if (page_number + 1) >= max_pages:
				self.go_to_next_page.disabled = True
			if page_number == 0:
				self.go_to_first_page.disabled = True
				self.go_to_previous_page.disabled = True

	async def show_checked_page(self, interaction: Interaction, page_number: int) -> None:
		max_pages = self.source.get_max_pages()
		try:
			if max_pages is None:
				await self.show_page(interaction, page_number)
			elif max_pages > page_number >= 0:
				await self.show_page(interaction, page_number)
		except IndexError:
			pass

	async def interaction_check(self, interaction: Interaction) -> bool:
		if interaction.user and interaction.user.id in (
			self.ctx.bot.owner_id,
			self.ctx.author.id,
		):
			return True
		await interaction.response.send_message(
			"This is not your menu.", ephemeral=True
		)
		return False

	async def start(self) -> None:
		if (self.check_embeds and not self.ctx.channel.permissions_for(self.ctx.me).embed_links):
			await self.ctx.send("Bot does not have embed links permission in this channel. Reconfigure it first then try again.")
			return

		await self.source._prepare_once()
		page = await self.source.get_page(0)
		kwargs = await self._get_kwargs_from_page(page)
		self._update_labels(0)
		self.message = await self.ctx.send(**kwargs, view=self)

	@button(label="≪", style=ButtonStyle.green)
	async def go_to_first_page(self, button: Button, interaction: Interaction):
		await self.show_page(interaction, 0)

	@button(label="<", style=ButtonStyle.green)
	async def go_to_previous_page(self, button: Button, interaction: Interaction):
		await self.show_checked_page(interaction, self.current_page - 1)

	@button(label="Current", style=ButtonStyle.grey, disabled=True)
	async def go_to_current_page(self, button: Button, interaction: Interaction):
		pass

	@button(label=">", style=ButtonStyle.green)
	async def go_to_next_page(self, button: Button, interaction: Interaction):
		await self.show_checked_page(interaction, self.current_page + 1)

	@button(label="≫", style=ButtonStyle.green)
	async def go_to_last_page(self, button: Button, interaction: Interaction):
		await self.show_page(interaction, self.source.get_max_pages() - 1)

# PAGINATION
class MessageListPage(ListPageSource):
	def __init__(self, ctx, data, channel):
		self.ctx = ctx
		self.channel = channel

		super().__init__(data, per_page=10)

	async def format_page(self, menu, entries):
		pages = []
		for index, entry in enumerate(entries, start=menu.current_page * self.per_page):
			pages.append(f"- {entry}")

		menu.embed.description = "\n".join(pages)
		menu.embed.set_footer(text=f"Total Messages: {len(self.entries)} (Page {int(menu.current_page + 1)} / {self.get_max_pages()}) | The bot only allows a maximum of 200 messages to display.", icon_url=self.ctx.author.display_avatar.url)
		menu.embed.title = f"{self.channel.mention} Message History"
		return menu.embed

class MessageListPages(ViewPages):
	def __init__(self, entries, ctx: ApplicationCommandInteraction, channel, per_page: int = 10):
		super().__init__(MessageListPage(ctx, data=entries, channel=channel), ctx=ctx)
		self.embed = Embed(colour=Color.blurple())
